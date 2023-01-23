#!/bin/bash

STACK_HOME=~

mkdir -p $STACK_HOME/test-iot-net/data/postgres
mkdir -p $STACK_HOME/test-iot-net/data/pgadmin
mkdir -p $STACK_HOME/test-iot-net/data/grafana
mkdir -p $STACK_HOME/test-iot-net/data/grafana/provisioning/datasources
mkdir -p $STACK_HOME/test-iot-net/data/grafana/provisioning/dashboards
mkdir -p $STACK_HOME/test-iot-net/data/mosquitto/config
mkdir -p $STACK_HOME/test-iot-net/data/mosquitto/data
mkdir -p $STACK_HOME/test-iot-net/data/mosquitto/logs

cp docker/mosquitto.conf $STACK_HOME/test-iot-net/data/mosquitto/config/mosquitto.conf
cp docker/mosquitto.pwfile $STACK_HOME/test-iot-net/data/mosquitto/config/pwfile
cp docker/pgadmin4.servers.json $STACK_HOME/test-iot-net/data/pgadmin/servers.json
cp docker/grafana-datasource.yml $STACK_HOME/test-iot-net/data/grafana/provisioning/datasources/datasource.yml
cp docker/grafana-dashboard.yml $STACK_HOME/test-iot-net/data/grafana/provisioning/dashboards/dashboard.yml
cp docker/grafana-dashboard-example.json $STACK_HOME/test-iot-net/data/grafana/provisioning/dashboards/grafana-dashboard-example.json
cp sql/schema.sql $STACK_HOME/test-iot-net/data/postgres/schema.sql
cp sql/sample_data.sql $STACK_HOME/test-iot-net/data/postgres/sample_data.sql

echo "Service configurations copied successfully."