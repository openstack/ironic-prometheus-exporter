import os

from oslo_config import cfg
from oslo_messaging.notify import notifier

prometheus_opts = [
    cfg.StrOpt('file_name', required=True),
    cfg.StrOpt('file_dir', required=True)
]


def register_opts(conf):
    conf.register_opts(prometheus_opts, group='oslo_messaging_notifications')


class PrometheusFileDriver(notifier.Driver):

    "Publish notifications into a File to be used by Prometheus"

    def __init__(self, conf, topics, transport):
        self.file_dir = conf.oslo_messaging_notifications.file_dir
        self.file_name = conf.oslo_messaging_notifications.file_name
        if not os.path.exists(self.file_dir):
            os.makedirs(self.file_dir)
        super(PrometheusFileDriver, self).__init__(conf, topics, transport)

    def notify(self, ctxt, message, priority, retry):
        prometheus_file = open((self.file_dir + '/' + self.file_name), 'w')
        prometheus_file.write(str(message))
        prometheus_file.close()
