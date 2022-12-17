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

docker swarm init
docker stack deploy --compose-file docker/stack.yml test-io-net
docker stack ps test-io-net --no-trunc
docker stack services test-io-net
```

