# -*- coding: utf-8 -*-
import logging
import pathlib
from dataclasses import dataclass, field
from io import IOBase

from mashumaro.mixins.yaml import DataClassYAMLMixin
from yaml.error import YAMLError

_log = logging.getLogger(__name__)


@dataclass
class Configuration(DataClassYAMLMixin):
    """ Configuration for this application, persisted as YAML."""

    logging_config: str  # ok, being lazy in here and using just single magic string


cfg: Configuration  # pylint: disable=C0103


def load_configuration(io_stream: IOBase) -> None:
    """
    Load configuration from YAML formatted file and deserialize it into
    dictionary. An instance of Configuration will be created from this
    dictionary.
    """

    global cfg  # pylint: disable=C0103
    try:
        cfg = Configuration.from_yaml(io_stream.read())
    except (YAMLError, ValueError):
        _log.error("Failed to parse configuration. Exit.")
    finally:
        io_stream.close()
