# -*- coding: utf-8 -*-
import os
from pathlib import Path
from unittest import mock

import paho.mqtt.client

import hemon.app

fixture_data_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent / "tests" / "data"


@mock.patch.object(paho.mqtt.client.Client, "connect")
class TestConfiguration:

    def test_logging_config(self, mqtt_conn, caplog, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog", "--config", str(fixture_data_dir / "cfg.log_example.yaml")])
        hemon.app.main()

        captured = capsys.readouterr()
        assert len(caplog.messages) == 0
        assert "log level set to: DEBUG" in captured.out
        assert "successfully read configuration" in captured.out
        assert "cfg.log_example.yaml" in captured.out
