[![build](https://github.com/petromap/home-energy-monitoring-dev/actions/workflows/build.yml/badge.svg)](https://github.com/petromap/home-energy-monitoring-dev/actions/workflows/build.yml)
[![build-dist](https://github.com/petromap/home-energy-monitoring-dev/actions/workflows/build-dist.yaml/badge.svg)](https://github.com/petromap/home-energy-monitoring-dev/actions/workflows/build-dist.yaml)

# Home Energy Monitoring

This, with help of some sensor node projects aims to help monitoring your 
environment and energy consumption at home.

This repository contains docker stack as a reference how to store time-series 
data and generate reports from measurements. But the real thing is the application 
reading MQTT topic and storing incoming values into TimescaleDB (PostgreSQL).
Let's call it as **hemon** from now on.

### Message structure
Message structure *hemon* understands and waits for is simple JSON document 
with couple meta information and measured values in dictionary.


Example of minimal accepted message when matching to [configuration](#configuration):
```json5
{
   "node": "backyard", // name of recognized sensor node
   "time": 1672953813, // time of measurement, msg will be dropped if not > 0
   "values":
   {
      "T": -0.5        // recognized measurement, key is the identifier from configuration
   },                  // .. values are expected to be float (convertible to postgres FLOAT)
   "read_status": 0    // optional: if present and nonzero message will be dropped
}
```
### Configuration
See example configuration and comments in 
[hemon.cfg.example.yaml](hemon.cfg.example.yaml).

Sensor node names and parameter value keys from incoming messages must be 
defined in configuration. Only then values will get stored.

Information of configured and nonexistent sensor nodes and parameters will 
be stored into database once the application starts up. For now there is no 
way to modify or delete these automatically, use database client tools for it.

### MQTT

*Hemon* will connect to configured broker and subscribe all topics prefixed 
with name in configuration parameter ```topic_prefix```. There is no other 
logic what comes to topic names.

### Database

*Hemon* stores received values into PostgreSQL database.
For reporting using TimescaleDB is suggested.

Expected database schema can be found from 
[sql/schema.sql](sql/schema.sql). It is written for 
TimeScaleDB but bare tables can be used without it.

## Install and run the package

Installing hemon package requires couple easy steps:
 * [Create virtual environment](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments) 
for the software.
 * Download release and install the package into this virtual environment:
   * ```venv/bin/python3.10 -m pip install home_energy_monitoring-*.whl```
 * Create a YAML configuration file, see [example](hemon.cfg.example.yaml)
   * When running the program refer to that configuration file with program argument ```--config <config file>```

To test configuration and whether MQTT broker and database can be reached, 
run:
```bash
venv/bin/python3.10 -m hemon.app --config <config file>
```

### Running as service

Unless just testing the package one may want to create a service for it.
For brief instructions how to do it using systemd, 
see [making systemd service](systemctl/README.md).

## Try it

On live environment there must be at least TimescaleDB and MQTT broker and this application.
And to be useful, some data collectors and reporting system as well.
This environment except data collectors and *hemon* itself is modeled in 
docker swarm, see [Docker Instructions](docker/README.md). 
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

Let predefined users to publish and subscribe MQTT messages (do this only once, multiple calls will render the password file unusable):
```bash
docker exec -it $(docker ps -q -f name=mosquitto) mosquitto_passwd -U /mosquitto/config/pwfile
# restart the mosquitto service
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

### Create Development Environment

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
pip install -e .[tests]
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

The integration test is rather robust and aims just to verify Docker stack can 
be used. Don't expect it tests much the application.

To run the test from command line, run:
```bash
pytest -m integration
```

**Note:**
* If docker stack is modified, change the code respectively
