# -*- coding: utf-8 -*-
import json
import logging
import os
import pytest

from paho.mqtt.client import MQTTMessage
from pathlib import Path
from unittest import mock

from hemon import config as app
from hemon.app import MessageResult, _setup_logging, _handle_message
from hemon.config import load_configuration

fixture_data_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent / "tests" / "data"


class TestMessageApproval:
    @staticmethod
    def to_bytes(s: str):
        return bytes(s, "UTF-8")

    def test_topic_not_own(self, monkeypatch):
        load_configuration(open(str(fixture_data_dir / "msg.no_sensors.yaml")))  # noqa

        msg = MQTTMessage(1, b"")
        assert _handle_message(msg) == MessageResult.NOT_OWN_TOPIC

        msg = MQTTMessage(1, TestMessageApproval.to_bytes("/sensor/a/b/c"))
        assert _handle_message(msg) == MessageResult.NOT_OWN_TOPIC

    def test_topic_own(self, monkeypatch):
        load_configuration(open(str(fixture_data_dir / "msg.no_sensors.yaml")))  # noqa

        msg = MQTTMessage(1, TestMessageApproval.to_bytes(app.cfg.mqtt.topic_prefix))
        assert _handle_message(msg) != MessageResult.NOT_OWN_TOPIC

        msg = MQTTMessage(1, TestMessageApproval.to_bytes(app.cfg.mqtt.topic_prefix + "sensor/a/b/c"))
        assert _handle_message(msg) != MessageResult.NOT_OWN_TOPIC

    def test_invalid_payload(self, monkeypatch):
        load_configuration(open(str(fixture_data_dir / "msg.no_sensors.yaml")))  # noqa

        # incorrect format
        msg = MQTTMessage(1, TestMessageApproval.to_bytes(app.cfg.mqtt.topic_prefix))
        msg.payload = TestMessageApproval.to_bytes("{node:\"kitchen\"}")
        assert _handle_message(msg) == MessageResult.INVALID_PAYLOAD

        # missing req. timestamp
        msg = MQTTMessage(1, TestMessageApproval.to_bytes(app.cfg.mqtt.topic_prefix))
        payload = {"node": "kitchen"}
        msg.payload = TestMessageApproval.to_bytes(json.dumps(payload))
        assert _handle_message(msg) == MessageResult.INVALID_PAYLOAD

        # sensor time unset
        msg = MQTTMessage(1, TestMessageApproval.to_bytes(app.cfg.mqtt.topic_prefix))
        payload = {"node": "kitchen", "time": 0}
        msg.payload = TestMessageApproval.to_bytes(json.dumps(payload))
        assert _handle_message(msg) == MessageResult.INVALID_PAYLOAD

    def test_no_such_node(self, monkeypatch):
        load_configuration(open(str(fixture_data_dir / "msg.no_sensors.yaml")))  # noqa

        msg = MQTTMessage(1, TestMessageApproval.to_bytes(app.cfg.mqtt.topic_prefix))
        msg.payload = TestMessageApproval.to_bytes("{\"node\":\"kitchen\", \"time\": 1672953813}")
        assert _handle_message(msg) == MessageResult.NO_SUCH_NODE

    def test_no_such_parameters(self, monkeypatch):
        load_configuration(open(str(fixture_data_dir / "msg.known_sensor_no_parameters.yaml")))  # noqa

        msg = MQTTMessage(1, TestMessageApproval.to_bytes(app.cfg.mqtt.topic_prefix))
        payload = {"node": "kitchen", "time": 1672953813, "values": {"quality": "1"}}
        msg.payload = TestMessageApproval.to_bytes(json.dumps(payload))
        assert _handle_message(msg) == MessageResult.NO_VALUES

    @mock.patch('hemon.db.Cursor')
    def test_handle_insert_values(self, mock_cursor, monkeypatch, caplog):
        load_configuration(open(str(fixture_data_dir / "msg.known_sensor_with_parameters.yaml")))  # noqa

        app.cfg.sensor_locations[0].id = 3
        app.cfg.parameters[1].id = 5

        msg = MQTTMessage(1, TestMessageApproval.to_bytes(app.cfg.mqtt.topic_prefix))
        payload = {"node": "kitchen", "time": 1672953813, "values": {"T": 20.57, "RH": 44.12}}
        msg.payload = TestMessageApproval.to_bytes(json.dumps(payload))
        assert _handle_message(msg) == MessageResult.SUCCESS
        mock_cursor.return_value.__enter__.return_value.execute.assert_called_with(
            "insert into measurements(measure_time, location_id, parameter_id, v) values (%s, %s, %s, %s)",
            [1672953813, 3, 5, 20.57]
        )
