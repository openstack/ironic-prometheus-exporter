# Ironic Prometheus Exporter #


### Installation ###

1 - Clone the repository in the machine where ironic is installed.
```
$ git clone https://github.com/metal3-io/ironic-prometheus-exporter
```
2 - Install the driver (may require sudo permisions)
```
$ cd ironic-prometheus-exporter
$ python setup.py install
```
3- Verify if the driver is installed
```
$ python verify_installation.py
```
Output in case of a successful instalation:
`prometheus_exporter driver found.`
Output in case of an unsuccessful instalation:
`prometheus_exporter driver not found.`
`Available drivers: ['log', 'messagingv2', 'noop', 'routing', 'test', 'messaging']`


### Configuration ###

After install the driver you will need to update the :ironic.conf: and add
:file_path: option (the file extension should be .json)

```
[oslo_messaging_notifications]
driver = prometheus_exporter
transport_url = fake://
file_path=/tmp/ironic_prometheus_exporter/metrics.json
```
