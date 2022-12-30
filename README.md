# Home Energy Monitoring

This and sensor node projects discussed in here aims to help monitoring your environment and energy consumption at home.

ecodan-modbus-mqtt
home-energy-monitoring

https://github.com/timescale/examples/blob/master/air-quality/schema.sql


### dev containers
https://github.com/garystafford/iot-analytics-at-the-edge/tree/main/docker
 * https://docs.timescale.com/install/latest/installation-docker/
 * https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html
 * https://hub.docker.com/_/eclipse-mosquitto
 * https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/


https://github.com/fhemberger/mqtt_exporter

https://programmaticponderings.com/tag/timescaledb/

https://github.com/timescale/examples/tree/master/air-quality

https://docs.timescale.com/timescaledb/latest/quick-start/python/

### MQTT

$SYS/broker/load/messages/received/+
(see: mosquitto man)

### project struct

https://github.com/jiisaa/Mitsubishi

https://github.com/SwiCago/HeatPump

https://github.com/tuomassiren/esp8266-dht22-mqtt-sensor/blob/master/src/main.cpp
https://github.com/ycardon/esp8266-dht22-mqtt
https://github.com/Obighbyd/ESP8266_MQTT_DHT22/blob/master/MQTT_ESP8266_temperature_humidity.ino

### testing

https://pypi.org/project/pytest-postgresql/

https://gist.github.com/graphaelli/906b624c18f77f50da5cd0cd4211c3c8

## TODO:
 * entry points in pyproject.toml
 * double check pyproject.toml URLs etc.

*******************

## Try it

On live environment there must be at least TimescaleDB and MQTT broker and this application.
And to be useful, some data collectors and reporting system as well.
All this is modeled in docker swarm, see [Docker Instructions](docker/README.md). 
Such swarm stack can be used to test and play with this messaging and reporting consept.

### Configuring and preparing the test environment

First create the database schema:
```bash
docker exec -it $(docker ps -q -f name=timescaledb) psql -U postgres -d test_iot -a -f /var/lib/postgresql/data/schema.sql
```

123.456

TODO!!!
conn.adapters.register_loader("numeric", psycopg.types.numeric.FloatLoader)
sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
conn.info.encoding
it stores a timestamp always in UTC
https://www.psycopg.org/psycopg3/docs/basic/from_pg2.html#multiple-statements-in-the-same-query
TODO!!!

## Development

### Development Environment Creation

Fork the repository and clone your fork to you computer.

```bash
git clone https://github.com/<username>/home-energy-monitoring.git
cd home-energy-monitoring
```
We recommend using the `venv` module for creating virtual environment for this development.
```bash
python3.10 -n venv venv
source venv/bin/activate
# or venv/Scripts/activate (Windows)
pip install .
pip install .[tests]
pip install -e .[dev]
```
Before making changes willing to contribute, create a different branch with a name that should be unique.
```bash
git switch -c my-new-feature
```
When you're ready to submit the pull request, please do so via the GitHub.

### Testing
To run the test suite, after installing dependencies (mind the `tests` extra) run
```bash
pytest
```

### Integration testing

TODO!!
