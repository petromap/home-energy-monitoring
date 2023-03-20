# -*- coding: utf-8 -*-
import argparse
import json
import logging
import logging.config
import os
import time
import typing
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path

import yaml
from paho.mqtt import client as mqtt

from hemon import config as app
from hemon import db

_log = logging.getLogger(__name__)

LOG_LEVEL_DEFAULT = "INFO"


class MessageResult(IntEnum):
    """Result of handling  MQTT message."""

    READ_ERROR = -5
    NO_VALUES = -4
    NO_SUCH_NODE = -3
    INVALID_PAYLOAD = -2
    NOT_OWN_TOPIC = -1
    SUCCESS = 0


def main() -> None:
    """Run the module app."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=argparse.FileType("r"))
    args = parser.parse_args()

    if not args.config:
        path = Path(os.getcwd()) / "hemon.cfg.yaml"
        if not path.exists():
            raise ValueError("Missing configuration")
        args.config = open(str(path), "r", encoding="utf-8")  # pylint: disable=R1732

    app.load_configuration(args.config)
    if not hasattr(app, "cfg"):
        return

    _setup_logging(app.cfg.logging_config)
    _log.info("successfully read configuration from: %s", args.config.name)
    _log.debug(app.cfg)

    _update_metadata_configuration()

    mqtt_client = mqtt.Client(client_id="hemon", reconnect_on_failure=True, clean_session=app.cfg.mqtt.client_clean_sessions())
    mqtt_client.username_pw_set(app.cfg.mqtt.username, app.cfg.mqtt.password)
    mqtt_client.on_log = _on_mqtt_log
    mqtt_client.on_connect = _on_mqtt_connect
    mqtt_client.on_message = _handle_message
    mqtt_client.connect(host=app.cfg.mqtt.host, port=app.cfg.mqtt.port, keepalive=180)

    try:
        if app.cfg.loop_time < 0:
            mqtt_client.loop_forever()
        elif app.cfg.loop_time == 0:
            mqtt_client.loop()
        else:
            mqtt_client.loop_start()
            time.sleep(app.cfg.loop_time)
            mqtt_client.loop_stop()
    finally:
        mqtt_client.disconnect()


def _on_mqtt_connect(client: mqtt.Client, userdata: typing.Any, flags: typing.Dict, rc: int):
    _log.info("connected with result code %s", str(rc))
    client.subscribe(app.cfg.mqtt.topic_prefix + "/#", qos=app.cfg.mqtt.qos)


def _on_mqtt_log(client: mqtt.Client, userdata: typing.Any, level: int, buf: object) -> None:
    _log.log(level, buf)


def _handle_message(client: mqtt.Client, userdata: typing.Any, msg: mqtt.MQTTMessage) -> MessageResult:
    if not msg.topic.startswith(app.cfg.mqtt.topic_prefix):
        return MessageResult.NOT_OWN_TOPIC
    try:
        _log.debug("Message %s received [%s]: %s", str(msg.mid), msg.topic, str(msg.payload))
        doc = json.loads(msg.payload)
    except ValueError as err:
        _log.warning("message %s dropped, invalid payload - cause: %s", str(msg.mid), repr(err))
        return MessageResult.INVALID_PAYLOAD

    # some validations..
    # ... there should be time when values are measured
    if "time" not in doc.keys() or doc["time"] <= 0:
        _log.debug("message %s dropped, missing measure time", str(msg.mid))
        return MessageResult.INVALID_PAYLOAD
    # ... if there is read (error) status, drop messages with any error code
    if "read_status" in doc.keys() and doc["read_status"] != 0:
        _log.debug("message %s dropped, read error status = %s", str(msg.mid), str(doc["read_status"]))
        return MessageResult.READ_ERROR
    # ... sensor must be known
    if "node" not in doc.keys() or not bool([sl for sl in app.cfg.sensor_locations if (doc["node"] == sl.node_name)]):
        node_name = "NODE_NAME_REQUIRED" if "node" not in doc.keys() else doc["node"]
        _log.debug('message %s dropped, unknown node "%s"', str(msg.mid), node_name)
        return MessageResult.NO_SUCH_NODE

    # iterate through values and accept those with known parameter
    values = []
    for m in doc["values"]:
        if bool([p for p in app.cfg.parameters if m == p.key]):
            values.append((m, doc["values"][m]))
    if len(values) == 0:
        _log.debug("message %s dropped, no accepted values", msg.mid)
        return MessageResult.NO_VALUES

    # accepted message with some known values...
    measurements = []
    sensor = [sl for sl in app.cfg.sensor_locations if doc["node"] == sl.node_name][0]
    for v in values:
        parameter = [p for p in app.cfg.parameters if v[0] == p.key][0]
        measurements.append((datetime.fromtimestamp(doc["time"], tz=timezone.utc), sensor.id, parameter.id, v[1]))
    db.insert_measurements(measurements)
    return MessageResult.SUCCESS


def _setup_logging(cfg_yaml: str | None = None):
    if cfg_yaml and len(cfg_yaml) > 0:
        c = yaml.safe_load(cfg_yaml)
        logging.config.dictConfig(c)
        _log.info("log level set to: %s", logging.getLevelName(logging.getLogger().level))
    else:
        log_level_str = LOG_LEVEL_DEFAULT
        log_level = logging.getLevelName(log_level_str)
        logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s")
        logging.getLogger().setLevel(log_level)
        logging.info("log level set to: %s", log_level_str)


def _update_metadata_configuration() -> None:
    if len(app.cfg.parameters) == 0 and len(app.cfg.sensor_locations) == 0:
        return
    _log.debug("updating location and parameter tables")

    # handle locations / sensors
    db.insert_locations(app.cfg.sensor_locations)
    sensors = db.select_locations()
    for p in app.cfg.sensor_locations:
        for dbs in sensors:
            if dbs["location_name"] == p.location_name and dbs["sensor_name"] == p.node_name:
                p.id = dbs["location_id"]

    # handle parameters
    db.insert_parameters(app.cfg.parameters)
    params = db.select_parameters()
    for p in app.cfg.parameters:
        for dbp in params:
            if dbp["parameter_name"] == p.name:
                p.id = dbp["parameter_id"]

    _log.info("successfully updated and read metadata tables")


if __name__ == "__main__":
    main()
