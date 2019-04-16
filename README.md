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
$ pip install entry_point_inspector
$ epi group show oslo.messaging.notify.drivers

```
Output in case of a successful instalation:
`prometheus_exporter` is listed in the `Name` column and the `Error` column should be empty.
Output in case of an unsuccessful instalation:
`prometheus_exporter` is listed in the `Name` column and the `Error` column will have more information.


### Configuration ###

After install the driver you will need to update the :ironic.conf: and add
:file_path: option (the file extension should be .json)

```
[conductor]
send_sensor_data=true

[oslo_messaging_notifications]
driver = prometheus_exporter
transport_url = fake://
location=/tmp/ironic_prometheus_exporter
```
