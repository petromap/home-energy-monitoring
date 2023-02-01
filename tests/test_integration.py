# -*- coding: utf-8 -*-
import os
import logging
import threading
import time

import pytest
from paho.mqtt import client as mqtt
from pathlib import Path

import hemon.app
from hemon import config as app
from hemon.config import load_configuration


_log = logging.getLogger(__name__)

fixture_data_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent / "tests" / "data"


@pytest.mark.load_data
class TestReceiveData:

    @staticmethod
    @pytest.fixture
    def mqtt_client(monkeypatch):
        cfg_file = "int.tests.cfg.yaml"
        load_configuration(open(str(fixture_data_dir / cfg_file)))  # noqa
        monkeypatch.setattr("sys.argv", ["prog", "--config", str(fixture_data_dir / cfg_file)])

        client = mqtt.Client()
        client.username_pw_set(app.cfg.mqtt.username, app.cfg.mqtt.password)
        client.on_connect = TestReceiveData.on_connect
        client.on_message = TestReceiveData.on_message

        client.connect(host=app.cfg.mqtt.host, port=app.cfg.mqtt.port, keepalive=180)
        return client

    @staticmethod
    def on_log(client, userdata, level, buf):
        _log.log(level, buf)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        _log.info("connected with result code " + str(rc))

    @staticmethod
    def on_message(client, userdata, msg):
        _log.info(msg.topic + " " + str(msg.payload))

    def test_receive_rejected_all_values(self, mqtt_client, caplog):

        mqtt_client.loop_start()

        TestReceiveData.wait_for_conn_ack(mqtt_client)

        # TODO: remove debug print
        print()

        #thread = threading.Thread(target=hemon.app.main)
        #thread.start()

        # TODO: proper publish
        #mqtt_client.publish(topic=app.cfg.mqtt.topic_prefix + "/kitchen", payload=b"Foo!")
        mqtt_client.publish(topic=app.cfg.mqtt.topic_prefix, retain=True, payload="Foo-2S!")
        print(f"published at {time.strftime('%X')}")

        # TODO: wait a second or two
        time.sleep(2)

        mqtt_client.loop_stop()
        mqtt_client.disconnect()

        # then the actual app kicks in
        print(f"..app starting at {time.strftime('%X')}")
        hemon.app.main()

        print(f"finished at {time.strftime('%X')}")

        # then, some validations what just happened
        assert ("test_integration", logging.INFO, "connected with result code 0") in caplog.record_tuples
        assert ("hemon.app", logging.DEBUG, "message 1 dropped, no accepted values") in caplog.record_tuples

    @staticmethod
    def wait_for_conn_ack(mqtt_client):
        # wait for conn ack
        must_end = time.time() + 5
        while time.time() < must_end:
            if mqtt_client.is_connected():
                break
            time.sleep(.1)
        assert mqtt_client.is_connected()
