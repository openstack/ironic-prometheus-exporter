import os

from oslo_config import cfg
from oslo_messaging.notify import notifier

prometheus_opts = [
    cfg.StrOpt('file_path', required=True),
]


def register_opts(conf):
    conf.register_opts(prometheus_opts, group='oslo_messaging_notifications')


class PrometheusFileDriver(notifier.Driver):
    """Publish notifications into a File to be used by Prometheus"""

    def __init__(self, conf, topics, transport):
        self.file_path = conf.oslo_messaging_notifications.file_path
        if not os.path.exists(os.path.dirname(self.file_path)):
            os.makedirs(os.path.dirname(self.file_path))
        super(PrometheusFileDriver, self).__init__(conf, topics, transport)

    def notify(self, ctxt, message, priority, retry):
        prometheus_file = open(self.file_path, 'w')
        prometheus_file.write(str(message))
        prometheus_file.close()
