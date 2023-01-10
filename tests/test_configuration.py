# -*- coding: utf-8 -*-
import logging
import os
import pytest
from pathlib import Path
from unittest import mock

import hemon.app
from hemon import config as app
from hemon.config import SensorParameter, load_configuration


fixture_data_dir = Path(os.path.dirname(os.path.realpath(__file__))).parent / "tests" / "data"


@pytest.fixture()
def change_test_dir(monkeypatch):
    monkeypatch.chdir(fixture_data_dir)


class TestProgramArguments:
    def test_no_arguments_no_config(self, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog"])
        with pytest.raises(ValueError) as e:
            hemon.app.main()
        assert "Missing configuration" in str(e.value)

    def test_empty_config(self, change_test_dir, caplog, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog"])
        hemon.app.main()

        assert ("root", logging.INFO, "log level set to: INFO") in caplog.record_tuples
        res = [rec.message for rec in caplog.records if ("successfully read configuration" in rec.message)]
        assert bool(res)

    def test_named_config_file(self, caplog, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog", "--config", str(fixture_data_dir / "hemon.cfg.yaml")])
        hemon.app.main()

        assert ("root", logging.INFO, "log level set to: INFO") in caplog.record_tuples
        assert bool([rec.message for rec in caplog.records if ("hemon.cfg.yaml" in rec.message)])
        assert bool([rec.message for rec in caplog.records if ("successfully read configuration" in rec.message)])


class TestConfiguration:

    def test_non_parseable_config(self, caplog, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog", "--config", str(fixture_data_dir / "cfg.non_parseable.yaml")])
        hemon.app.main()

        assert bool([rec.message for rec in caplog.records if ("Failed to parse configuration" in rec.message)])
        assert bool([rec.message for rec in caplog.records if ("did not find expected key" in rec.message)])


# TODO: mqtt parameters, unit test via mocked broker

class TestManageMetadata:

    @mock.patch('hemon.db.Cursor')
    def test_manage_metadata(self, mock_cursor, monkeypatch, caplog):
        load_configuration(open(str(fixture_data_dir / "msg.known_sensor_with_parameters.yaml")))  # noqa

        mock_select_parameters = mock.patch("hemon.db.select_locations")
        mock_select_parameters.__enter__().return_value = [
            {"location_id": 1, "location_name": "in the house", "sensor_name": "sink"},
            {"location_id": 2, "location_name": "in the house", "sensor_name": "kitchen"},
        ]
        mock_select_parameters = mock.patch("hemon.db.select_parameters")
        mock_select_parameters.__enter__().return_value = [{"parameter_id": 3, "parameter_name": "Temperature"}]

        hemon.app._update_metadata_configuration()

        execute = mock_cursor.return_value.__enter__.return_value.execute
        assert execute.call_count == 3
        assert "insert into locations(location_name, sensor_name) values (%s, %s)" in execute.call_args_list[0].args[0]
        assert execute.call_args_list[0].args[1] == ['in the house', 'kitchen']
        assert "insert into measurement_types(parameter_name, unit) values (%s, %s)" in execute.call_args_list[1].args[0]
        assert execute.call_args_list[1].args[1] == ['E consumption', 'kWh']
        assert execute.call_args_list[2].args[1] == ['Temperature', '°C']

        assert app.cfg.sensor_locations[0].id == 2
        assert app.cfg.parameters[0].id is None
        assert app.cfg.parameters[1].id == 3
        assert ("hemon.app", logging.INFO, "successfully updated and read metadata tables") in caplog.record_tuples
