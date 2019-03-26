from oslo_config import cfg

from ironic_prometheus_exporter import messaging

CONF = cfg.CONF

messaging.register_opts(CONF)
