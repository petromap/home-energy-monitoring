# -*- coding: utf-8 -*-
import logging
from dataclasses import dataclass
from io import IOBase
from typing import List, Optional

from mashumaro.mixins.yaml import DataClassYAMLMixin

_log = logging.getLogger(__name__)


@dataclass
class SensorParameter(DataClassYAMLMixin):
    """
    Configuration for sensor parameter.
    Incoming values without matching (pre-defined) parameters will be skipped.
    """

    name: str
    unit: str
    key: str  # key in MQTT message
    id: Optional[int] = None


@dataclass
class SensorNode(DataClassYAMLMixin):
    """Configuration for sensor node. Only messages from known nodes will be accepted."""

    node_name: str
    location_name: str
    id: Optional[int] = None


@dataclass
class MQTT(DataClassYAMLMixin):
    """Configuration for connecting to MQTT broker, topic settings etc."""

    topic_prefix: str  # subscribe all topics from this one
    host: str
    port: int
    username: str
    password: str


@dataclass
class Database(DataClassYAMLMixin):
    """Configuration for connecting to database"""

    dbname: str
    host: str
    port: int
    username: str
    password: str


@dataclass
class Configuration(DataClassYAMLMixin):
    """Configuration for this application, persisted as YAML."""

    logging_config: str  # ok, being lazy in here and using just single magic string
    mqtt: MQTT
    db: Database
    sensor_locations: List[SensorNode]
    parameters: List[SensorParameter]


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
    except Exception as e:  # noqa
        _log.exception("Failed to parse configuration. %s", repr(e))
    finally:
        io_stream.close()
