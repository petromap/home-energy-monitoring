# -*- coding: utf-8 -*-
import argparse
import json
import logging
import logging.config
import os
import time

import yaml
from enum import IntEnum
from paho.mqtt.client import MQTTMessage
from pathlib import Path

from hemon import db
from hemon import config as app

_log = logging.getLogger(__name__)


class MessageResult(IntEnum):
    """Result of handling  MQTT message."""
    NO_VALUES = -4
    NO_SUCH_NODE = -3
    INVALID_PAYLOAD = -2
    NOT_OWN_TOPIC = -1
    SUCCESS = 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=argparse.FileType("r"))
    args = parser.parse_args()
    print(args)

    if not args.config:
        path = Path(os.getcwd()) / "hemon.cfg.yaml"
        if not path.exists():
            raise ValueError("Missing configuration")
        args.config = open(str(path), "r", encoding="utf-8")  # pylint: disable=R1732

    # TODO: remove debug print
    print("")
    print(args)

    app.load_configuration(args.config)
    if not hasattr(app, "cfg"):
        return

    # TODO: remove debug print
    print(app.cfg)
    print(f"..app running at {time.strftime('%X')}")

    _setup_logging(app.cfg.logging_config)
    _log.info("successfully read configuration from: %s", args.config.name)

    _update_metadata_configuration()

    # TODO: new mwtt client with reconnect_on_failure=True

    time.sleep(5)


#TODO: logging of incoming message

def _handle_message(msg: MQTTMessage) -> MessageResult:
    if not msg.topic.startswith(app.cfg.mqtt.topic_prefix):
        return MessageResult.NOT_OWN_TOPIC
    try:
        _log.debug("Message received [%s]: %s", msg.topic, str(msg.payload))
        doc = json.loads(msg.payload)
    except ValueError as e:
        _log.warning("message %s dropped due to invalid payload, cause: %s", str(msg.mid), repr(e))
        return MessageResult.INVALID_PAYLOAD

    # some validations..
    # ... there should be time when values are measured
    if "time" not in doc.keys() or doc["time"] <= 0:
        return MessageResult.INVALID_PAYLOAD
    # ... sensor must be known
    if not bool([sl for sl in app.cfg.sensor_locations if (doc["node"] == sl.node_name)]):
        return MessageResult.NO_SUCH_NODE

    # iterate through values and accept those with known parameter
    values = []
    for m in doc["values"]:
        if bool([p for p in app.cfg.parameters if (m == p.key)]):
            values.append((m, doc["values"][m]))
    if len(values) == 0:
        return MessageResult.NO_VALUES

    # accepted message with some known values...
    measurements = []
    sensor = [sl for sl in app.cfg.sensor_locations if (doc["node"] == sl.node_name)][0]
    for v in values:
        parameter = [p for p in app.cfg.parameters if (v[0] == p.key)][0]
        measurements.append((doc["time"], sensor.id, parameter.id, v[1]))
    db.insert_measurements(measurements)
    return MessageResult.SUCCESS


def _setup_logging(cfg_yaml: str = None):
    if cfg_yaml and len(cfg_yaml) > 0:
        c = yaml.safe_load(cfg_yaml)
        logging.config.dictConfig(c)
        _log.info("log level set to: %s", logging.getLevelName(logging.getLogger().level))
    else:
        log_level_str = "INFO"
        log_level = logging.getLevelName(log_level_str)
        logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s")
        logging.getLogger().setLevel(log_level)
        logging.info("log level set to: %s", log_level_str)


def _update_metadata_configuration():
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
    #_log.info(params)
    print("##########")
    print(params)

    _log.info("successfully updated and read metadata tables")


if __name__ == "__main__":
    main()
