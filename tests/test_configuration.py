# -*- coding: utf-8 -*-
import logging
import os
import pytest
from pathlib import Path

import hemon.app


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

    def test_non_parseable_config(self, caplog, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog", "--config", str(fixture_data_dir / "cfg.non_parseable.yaml")])
        hemon.app.main()

        assert ("hemon.config", logging.ERROR, "Failed to parse configuration. Exit.") in caplog.record_tuples

    def test_logging_config(self, caplog, capsys, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog", "--config", str(fixture_data_dir / "cfg.log_example.yaml")])
        hemon.app.main()

        captured = capsys.readouterr()
        assert len(caplog.messages) == 0
        assert "log level set to: DEBUG" in captured.out
        assert "successfully read configuration" in captured.out
        assert "cfg.log_example.yaml" in captured.out
