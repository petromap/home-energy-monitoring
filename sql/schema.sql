CREATE TABLE measurement_types (
  parameter_id SMALLSERIAL PRIMARY KEY,
  parameter_name TEXT NOT NULL,
  unit TEXT NOT NULL,
  UNIQUE(parameter, unit)
);

CREATE TABLE locations (
  location_id SMALLSERIAL PRIMARY KEY,
  location_name TEXT NOT NULL,
  sensor_name TEXT NOT NULL,
  UNIQUE(location_name, sensor_name)
);

CREATE TABLE measurements (
  measure_time TIMESTAMPTZ,
  parameter_id SMALLINT REFERENCES measurement_types(parameter_id),
  location_id SMALLINT REFERENCES locations(location_id),
  v FLOAT
);


CREATE INDEX ON measurements (parameter_id, measure_time);
SELECT create_hypertable('measurements', 'measure_time');

-- Continuous Aggregates Example

CREATE MATERIALIZED VIEW measurements_hourly
WITH (timescaledb.continuous)
AS
SELECT
  time_bucket('1 hour', measure_time) as bucket,
  parameter_id,
  avg(v) as avg_value,
  max(v) as max_value,
  min(v) as min_value
FROM
  measurements
GROUP BY bucket, parameter_id;

CREATE MATERIALIZED VIEW measurements_daily
WITH (timescaledb.continuous)
AS
SELECT
  time_bucket('1 day', measure_time) as bucket,
  parameter_id,
  avg(v) as avg_value,
  max(v) as max_value,
  min(v) as min_value
FROM
  measurements
GROUP BY bucket, parameter_id;

SELECT add_continuous_aggregate_policy('measurements_hourly',
  start_offset => INTERVAL '1 month',
  end_offset => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour');
SELECT add_continuous_aggregate_policy('measurements_daily',
  start_offset => INTERVAL '1 month',
  end_offset => INTERVAL '1 day',
  schedule_interval => INTERVAL '1 day');

SELECT add_retention_policy('measurements_hourly', INTERVAL '6 months');