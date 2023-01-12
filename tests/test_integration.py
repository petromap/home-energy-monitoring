# -*- coding: utf-8 -*-
import os
import logging
import pytest
from paho.mqtt import client as mqtt
from pathlib import Path

from hemon import config as app
from hemon.config import load_configuration


_log = logging.getLogger(__name__)

fixture_data_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent / "tests" / "data"


@pytest.mark.load_data
class TestReceiveData:

    @staticmethod
    @pytest.fixture
    def mqtt_client():
        load_configuration(open(str(fixture_data_dir / "int.tests.cfg.yaml")))  # noqa
        client = mqtt.Client()
        client.username_pw_set(app.cfg.mqtt.username, app.cfg.mqtt.password)
        client.on_connect = TestReceiveData.on_connect
        client.on_message = TestReceiveData.on_message

        client.connect(app.cfg.mqtt.host, app.cfg.mqtt.port, 180)
        return client

    @staticmethod
    def on_log(client, userdata, level, buf):
        _log.log(level, buf)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        _log.info("Connected with result code " + str(rc))

        client.subscribe(app.cfg.mqtt.topic_prefix + "/#")

    @staticmethod
    def on_message(client, userdata, msg):
        _log.info(msg.topic + " " + str(msg.payload))

    def test_receive_rejected_all_values(self, mqtt_client, caplog):
        #client = mqtt.Client()
        #client.username_pw_set(app.cfg.mqtt.username, app.cfg.mqtt.password)
        #client.on_connect = self.on_connect
        #client.on_message = self.on_message

        #client.connect(app.cfg.mqtt.host, app.cfg.mqtt.port, 180)

        mqtt_client.loop_start()
        # TODO: publish
        # TODO: wait a second
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

        assert ("root", logging.INFO, "log level set to: INFO") in caplog.record_tuples
