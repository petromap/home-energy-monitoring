# Docker Instructions

Copy *stack.example.yml* to *stack.yml* and replace ${HOME} by absolute path 
to users home directory. If willing to use other root path mind to change 
following commands respectively.


```bash
mkdir -p ~/test-io-net/data/postgres
mkdir -p ~/test-io-net/data/pgadmin
mkdir -p ~/test-io-net/data/grafana
mkdir -p ~/test-io-net/data/mosquitto/config
mkdir -p ~/test-io-net/data/mosquitto/data
mkdir -p ~/test-io-net/data/mosquitto/logs

cp docker/mosquitto.conf ~/test-io-net/data/mosquitto/config/mosquitto.conf
cp docker/pgadmin4.servers.json ~/test-iot-net/data/pgadmin/servers.json
cp sql/schema.sql ~/test-iot-net/data/postgres/schema.sql

docker swarm init
docker stack deploy --compose-file docker/stack.yml test-io-net
docker stack ps test-io-net --no-trunc
docker stack services test-io-net
```

After started services successfully one can continue configuring the database, load sample data etc. as described 
in [preparing the test environment](../README.md#Configuring-and-preparing-the-test-environment).

To operate with Docker swarm and this service stack, see [Docker reference documentation](https://docs.docker.com/reference/).
