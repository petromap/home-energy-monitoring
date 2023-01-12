# -*- coding: utf-8 -*-
import logging
import types
import typing

import psycopg
from psycopg.rows import dict_row

from hemon import config as app
from hemon.config import SensorNode, SensorParameter

_log = logging.getLogger(__name__)


class Cursor:
    """Connect to db and get a cursor from a connection."""

    def __init__(self):
        self.connection = None
        self.cursor = None

    @staticmethod
    def _get_connection_str() -> str:
        cfg = app.cfg.db
        return f"postgres://{cfg.username}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.dbname}"

    def __enter__(self) -> psycopg.Cursor[typing.Tuple[typing.Any, ...]]:
        self.connection = psycopg.connect(Cursor._get_connection_str())
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(
        self, exc_type: typing.Type[BaseException], exc_val: BaseException, exc_tb: types.TracebackType | None
    ) -> None:
        if exc_val is not None:
            self.connection.rollback()
            _log.warning("rollback, cause: %s", exc_val, exc_info=(exc_type, exc_val, exc_tb))
        else:
            self.cursor.close()
            self.connection.commit()
        self.connection.close()


def select_locations() -> typing.List[typing.Dict[str, typing.Any]]:
    with Cursor() as cursor:
        cursor.row_factory = dict_row
        cursor.execute("select * from locations")
        return cursor.fetchall()


def insert_locations(values: typing.List[SensorNode]) -> None:
    with Cursor() as cursor:
        sql = """insert into locations(location_name, sensor_name) values (%s, %s)
                on conflict (location_name, sensor_name) do nothing"""
        for v in values:
            cursor.execute(sql, [v.location_name, v.node_name])


def select_parameters() -> typing.List[typing.Dict[str, typing.Any]]:
    with Cursor() as cursor:
        cursor.row_factory = dict_row
        cursor.execute("select * from measurement_types")
        return cursor.fetchall()


def insert_parameters(values: typing.List[SensorParameter]) -> None:
    with Cursor() as cursor:
        sql = """insert into measurement_types(parameter_name, unit) values (%s, %s)
                on conflict (parameter_name, unit) do nothing"""
        for v in values:
            cursor.execute(sql, [v.name, v.unit])


def insert_measurements(values: typing.List[typing.Tuple[float, int, int, float]]) -> None:
    with Cursor() as cursor:
        sql = "insert into measurements(measure_time, location_id, parameter_id, v) values (%s, %s, %s, %s)"
        for v in values:
            cursor.execute(sql, [v[0], v[1], v[2], v[3]])
