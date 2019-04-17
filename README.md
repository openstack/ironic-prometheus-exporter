# Ironic Prometheus Exporter #


### Installation ###

1 - Clone the repository in the machine where ironic is installed.
```
$ git clone https://github.com/metalkube/ironic-prometheus-exporter
```
2 - Install the driver (may require sudo permisions)
```
$ cd ironic-prometheus-exporter
$ python setup.py install
```
3- Verify if the driver is installed
```
$ pip install entry_point_inspector --user <user>
$ epi group show oslo.messaging.notify.drivers

```
Output in case of a successful instalation:
`prometheus_exporter` is listed in the `Name` column and the `Error` column should be empty.
Output in case of an unsuccessful instalation:
`prometheus_exporter` is listed in the `Name` column and the `Error` column will have more information.


### Configuration ###

After install the driver you will need to update the `ironic.conf` and add the below information.

```
[conductor]
send_sensor_data=true

[oslo_messaging_notifications]
driver = prometheus_exporter
transport_url = fake://
location=/tmp/ironic_prometheus_exporter
```


### Running exporter application ###

The Flask Application is responsible to merge all the metrics files present in the directory
set in `[oslo_messaging_notifications]/location`.

**NOTE:** if you want to deploy in production please check the Flask [documentation](http://flask.pocoo.org/docs/dev/deploying/)

To run the Flask Application follow the steps listed below:
1 - open the repository directory
```
$ cd ironic-prometheus-exporter/
```
2- set the `FLASK_*` environment variables and the location of the `ironic.conf` file.
```
$ export IRONIC_CONFIG=/etc/ironic/ironic.conf
$ export FLASK_APP=ironic_prometheus_exporter/app/exporter.py
$ export FLASK_RUN_HOST=$HOST_IP
$ export FLASK_RUN_PORT=5000
```
3- run the Flask Application
```
$ python -m flask run &
```
