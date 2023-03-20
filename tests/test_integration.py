# -*- coding: utf-8 -*-
import os
import json
import logging
import time
import typing

import pytest
from paho.mqtt import client as mqtt
from pathlib import Path
from psycopg.rows import dict_row

import hemon.app
from hemon import config as app
from hemon import db
from hemon.config import load_configuration


_log = logging.getLogger(__name__)

fixture_data_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent / "tests" / "data"


@pytest.mark.load_data
class TestReceiveData:

    @staticmethod
    @pytest.fixture
    def mqtt_client(monkeypatch):
        # capture as much log messages as possible...
        log_level_str = "DEBUG"
        log_level = logging.getLevelName(log_level_str)
        logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s")
        logging.getLogger().setLevel(log_level)
        # ...from the app also
        hemon.app.LOG_LEVEL_DEFAULT = log_level_str

        cfg_file = "int.tests.cfg.yaml"
        load_configuration(open(str(fixture_data_dir / cfg_file)))  # noqa
        monkeypatch.setattr("sys.argv", ["prog", "--config", str(fixture_data_dir / cfg_file)])

        client = mqtt.Client(client_id="test_integration",
                             clean_session=False,
                             transport="tcp",
                             protocol=mqtt.MQTTv311)
        client.username_pw_set(app.cfg.mqtt.username, app.cfg.mqtt.password)
        client.on_connect = TestReceiveData._on_connect
        client.on_log = TestReceiveData._on_log

        client.connect(host=app.cfg.mqtt.host, port=app.cfg.mqtt.port, keepalive=180,
                       clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY)

        client.loop_start()
        return client

    @staticmethod
    def _on_log(client, userdata, level, buf):
        _log.log(level, buf)

    @staticmethod
    def _on_connect(client, userdata, flags, rc):
        _log.info("connected with result code " + str(rc))

    def test_receive_rejected_all_values(self, caplog, mqtt_client):
        TestReceiveData.wait_for_conn_ack(mqtt_client)

        measurement_count_before_test = self.db_select_measurement_count()[0]["count"]

        # TODO: proper publish
        msg1 = {"foo": "Bar!"}
        mqtt_client.publish(topic=app.cfg.mqtt.topic_prefix, qos=app.cfg.mqtt.qos, retain=True, payload=json.dumps(msg1))
        mqtt_client.loop()
        time.sleep(.5)

        # send message which should end into database
        msg2 = {"time": 1, "node": "backyard", "values": {"T": -0.5}}
        mqtt_client.publish(topic=app.cfg.mqtt.topic_prefix, qos=app.cfg.mqtt.qos, retain=True, payload=json.dumps(msg2))
        mqtt_client.loop()
        time.sleep(.5)

        # wait a second (to publish)
        time.sleep(1)

        mqtt_client.loop_stop()
        mqtt_client.disconnect()

        # then the actual app kicks in, loop_time defined by configuration
        hemon.app.main()

        # then, some validations what just happened
        assert ("hemon.app", logging.INFO, "connected with result code 0") in caplog.record_tuples
        assert ("hemon.app", 16, "Sending SUBSCRIBE (d0, m1) [(b'hemon/sensor/#', 2)]") in caplog.record_tuples
        assert bool([rec.message for rec in caplog.records if ("received [hemon/sensor]: b'{\"foo\": \"Bar!\"}'" in rec.message)])
        assert bool([rec.message for rec in caplog.records if ("dropped, missing measure time" in rec.message)])
        assert not bool([rec.message for rec in caplog.records if ("unknown node \"backyard\"" in rec.message)])

        # final check against database
        measurement_count_after_test = self.db_select_measurement_count()[0]["count"]
        assert measurement_count_after_test >= measurement_count_before_test + 1  # at least has the one just sent over

    @staticmethod
    def wait_for_conn_ack(mqtt_client):
        # wait for conn ack
        must_end = time.time() + 5
        while time.time() < must_end:
            if mqtt_client.is_connected():
                break
            time.sleep(.1)
        assert mqtt_client.is_connected()

    @staticmethod
    def db_select_measurement_count() -> typing.List[typing.Dict[str, typing.Any]]:
        with db.Cursor() as cursor:
            cursor.row_factory = dict_row
            cursor.execute("select count(*) from measurements me join locations l on me.location_id = l.location_id where l.sensor_name = 'backyard'")
            cnt = cursor.fetchall()
            return cnt
