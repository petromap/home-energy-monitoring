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

        client.connect(app.cfg.mqtt.host, app.cfg.mqtt.port, 180)
        return client

    @staticmethod
    def on_log(client, userdata, level, buf):
        _log.log(level, buf)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        _log.info("Connected with result code " + str(rc))

    @staticmethod
    def on_message(client, userdata, msg):
        _log.info(msg.topic + " " + str(msg.payload))

    #@staticmethod
    #async def run_the_app():
    #    await hemon.app.main()

    def test_receive_rejected_all_values(self, mqtt_client, caplog):

        #TODO: assert runtime

        mqtt_client.loop_start()

        print()
        print(f"started at {time.strftime('%X')}")
        #asyncio.run(TestReceiveData.run_the_app())
        #asyncio.run(hemon.app.main())
        #await hemon.app.main()
        thread = threading.Thread(target=hemon.app.main)
        thread.start()
        print(f"..app started at {time.strftime('%X')}")

        # TODO: publish
        # TODO: wait a second or two
        time.sleep(2)
        print(f"finished at {time.strftime('%X')}")

        mqtt_client.loop_stop()
        mqtt_client.disconnect()

        # join after configured lifetime
        thread.join(timeout=1)

        # then, some validations what just happened
        assert ("root", logging.INFO, "successfully read configuration") in caplog.record_tuples
