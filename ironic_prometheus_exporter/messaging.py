import logging
import os

from ironic_prometheus_exporter.parsers import manager
from oslo_config import cfg
from oslo_messaging.notify import notifier

LOG = logging.getLogger(__name__)


prometheus_opts = [
    cfg.StrOpt('location', required=True,
               help='Directory where the files will be written.')
]


def register_opts(conf):
    conf.register_opts(prometheus_opts, group='oslo_messaging_notifications')


class PrometheusFileDriver(notifier.Driver):
    """Publish notifications into a File to be used by Prometheus"""

    def __init__(self, conf, topics, transport):
        self.location = conf.oslo_messaging_notifications.location
        if not os.path.exists(self.location):
            os.makedirs(self.location)
        super(PrometheusFileDriver, self).__init__(conf, topics, transport)

    def notify(self, ctxt, message, priority, retry):
        try:
            node_parser_manager = manager.ParserManager(message)
            node_metrics = node_parser_manager.merge_information()
            node_name = message['payload']['node_name']
            with open(os.path.join(self.location, node_name), 'w') as file:
                file.write(node_metrics)
        except Exception as e:
            LOG.error(e)


class SimpleFileDriver(notifier.Driver):

    def __init__(self, conf, topics, transport):
        self.location = conf.oslo_messaging_notifications.location
        if not os.path.exists(self.location):
            os.makedirs(os.path.dirname(self.location))
        super(SimpleFileDriver, self).__init__(conf, topics, transport)

    def notify(self, ctx, message, priority, retry):
        with open(os.path.join(self.location, 'simplefile'), 'w') as file:
            file.write(message)
