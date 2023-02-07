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

Then import sample data:
```bash
docker exec -it $(docker ps -q -f name=timescaledb) psql -U postgres -d test_iot -a -f /var/lib/postgresql/data/sample_data.sql
```

Now, one should be able login into grafana and see some data in there or 
browse it with pgadmin.

To get more samples to play with, there is pytest module for loading data for 
previous week.
This step is not needed unlike previous ones to run integration tests or to 
see stack in live.

Loading 7*24h sample data run following command:
* Warning: removes old data from named sensor
* If docker stack is modified, change the code respectively
```bash
pytest -m load_data
```

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
https://github.com/1technophile/OpenMQTTGateway/blob/development/main/main.ino


Let predefined users to publish and subscribe MQTT messages (multiple calls will render the password file unusable):
```bash
docker exec -it $(docker ps -q -f name=mosquitto) mosquitto_passwd -U /mosquitto/config/pwfile
```


Note:
* Removes old data from named sensor(s)
* If docker stack is modified, change the code respectively
