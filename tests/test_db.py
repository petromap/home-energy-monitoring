# -*- coding: utf-8 -*-
import logging
import os
import pytest
from pathlib import Path
from unittest import mock

from hemon import config as app
from hemon import db
from hemon.config import SensorParameter, load_configuration

fixture_data_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent / "tests" / "data"


class TestDatabaseModule:
    @mock.patch('psycopg.connect')
    def test_cursor_context_manager(self, mock_connect, monkeypatch):
        load_configuration(open(str(fixture_data_dir / "msg.known_sensor_with_parameters.yaml")))  # noqa

        p1 = SensorParameter(key="T", name="Temperature", unit="°C")
        p2 = SensorParameter(key="RH", name="Relative humidity", unit="%rh")
        db.insert_parameters([p1, p2])

        mock_connect.assert_called_once()

    @mock.patch('psycopg.connect')
    def test_cursor_context_manager_rollback(self, mock_connect, caplog):
        load_configuration(open(str(fixture_data_dir / "msg.known_sensor_with_parameters.yaml")))  # noqa

        with pytest.raises(TypeError):
            db.insert_parameters(None)  # noqa

        mock_connect.assert_called_once()
        assert ("hemon.db", logging.WARNING, "rollback, cause: 'NoneType' object is not iterable") in caplog.record_tuples

    def test_get_connection_str(self):
        load_configuration(open(str(fixture_data_dir / "msg.known_sensor_with_parameters.yaml")))  # noqa

        assert db.Cursor._get_connection_str() == "postgres://postgres:postgres1234@localhost:5432/tsdb"
