# Docker Instructions

If not done already, clone this repository or download the source code.

Copy *stack.example.yml* to *stack.yml* and replace each ${HOME} by absolute 
path to users home directory. If willing to use other root path mind to change 
it in *setup-stack-services.sh* script respectively.

First setup stack configuration, copy service configurations etc.:

```bash
./docker/setup-stack-services.sh
```

Then setup docker stack:

```bash
docker swarm init
docker stack deploy --compose-file docker/stack.yml test-io-net
docker stack ps test-io-net --no-trunc
docker stack services test-io-net
```

After started services successfully one can continue configuring the database, load sample data etc. as described 
in [preparing the test environment](../README.md#Configuring-and-preparing-the-test-environment).

To operate with Docker swarm and this service stack, see [Docker reference documentation](https://docs.docker.com/reference/).
