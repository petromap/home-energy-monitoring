# Systemd service for hemon package

A python virtual environment allows you to create the exact environment 
necessary to run python projects. 
And to run program in such isolated environment 
the virtual environment’s python executable must be used in service unit.

To start, you want copy the [example service file](hemon_mqtt_to_tsdb.service) 
or create such in place to the
`systemd/system` folder:
```bash
sudo cp hemon_mqtt_to_tsdb.service /etc/systemd/system/
```
And edit it to use correct path to virtual environment, Python executable etc.
Mind the user which will run the process.

Next, have systemd reload all of its service files with
```bash
sudo systemctl daemon-reload
```
To get the service running, run the following two commands:
```bash
sudo systemctl start hemon_mqtt_to_tsdb.service
sudo systemctl enable hemon_mqtt_to_tsdb.service
```
The first one activates the service and second ensures that it is 
activated on boot.
