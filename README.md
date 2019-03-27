# Ironic Prometheus Exporter



### Configuration

After install the driver you will need to update the :ironic.conf: and add
:file_path: option (the file extension should be .json) 

```
[oslo_messaging_notifications]
driver = prometheus_exporter
transport_url = fake://
file_path=/tmp/ironic_prometheus_exporter/metrics.json
```
