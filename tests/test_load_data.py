# -*- coding: utf-8 -*-
import pytest
import psycopg2
from pgcopy import CopyManager


@pytest.mark.load_data
class TestLoadSampleData:

    CONNECTION = "postgres://postgres:postgres1234@localhost:15432/test_iot"

    def test_load_week_of_simulated_temperature(self):
        conn = psycopg2.connect(TestLoadSampleData.CONNECTION)
        cursor = conn.cursor()

        # delete previous data
        query = """DELETE from public.measurements
                   WHERE location_id = 2
                   AND parameter_id = 3
                """
        cursor.execute(query)

        # create random data
        query = """SELECT generate_series(now() - interval '1 weeks', now(), interval '5 minute') AS measure_time,
                   2 as location_id,
                   3 as parameter_id,
                   random()*20-5 AS v
                """

        cursor.execute(query)
        values = cursor.fetchall()

        cols = ['measure_time', 'location_id', 'parameter_id', 'v']

        mgr = CopyManager(conn, 'public.measurements', cols)
        mgr.copy(values)

        # make a hole, simulate missing data
        query = """DELETE from public.measurements
                   WHERE location_id = 2
                   AND parameter_id = 3
                   AND measure_time >= now() - interval '32 hour'
                   AND measure_time < now() - interval '30 hour'
                """
        cursor.execute(query)

        conn.commit()
