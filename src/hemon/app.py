# -*- coding: utf-8 -*-
import argparse
import logging
import logging.config
import os
import yaml
from pathlib import Path

from hemon import config as app

_log = logging.getLogger(__name__)


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

    _setup_logging(app.cfg.logging_config)
    _log.info("successfully read configuration from: %s", args.config.name)


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


if __name__ == "__main__":
    main()
