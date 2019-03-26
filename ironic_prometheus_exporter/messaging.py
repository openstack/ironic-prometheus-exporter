import os

from oslo_config import cfg
from oslo_messaging.notify import notifier

prometheus_opts = [
    cfg.StrOpt('file_name', required=True),
    cfg.StrOpt('file_dir', required=True)
]


class PrometheusFileDriver(notifier.Driver):

    "Publish notifications into a File to be used by Prometheus"

    def __init__(self, conf, topics, transport):
        conf.register_opts(prometheus_opts,
                           group='oslo_messaging_notifications')
        self.conf = conf
        if not os.path.exists(self.conf.oslo_messaging_notifications.file_dir):
            os.makedirs(self.conf.oslo_messaging_notifications.file_dir)
        self.file_dir = self.conf.oslo_messaging_notifications.file_dir
        self.file_name = self.conf.oslo_messaging_notifications.file_name
        super(PrometheusFileDriver, self).__init__(conf, topics, transport)

    def notify(self, ctxt, message, priority, retry):
        prometheus_file = open((self.file_dir + '/' + self.file_name), 'w')
        prometheus_file.write(str(message))
        prometheus_file.close()
