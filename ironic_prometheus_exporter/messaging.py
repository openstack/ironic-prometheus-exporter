import os

from ironic_prometheus_exporter.parsers import manager
from oslo_config import cfg
from oslo_messaging.notify import notifier


prometheus_opts = [
    cfg.StrOpt('files_dir', required=True,
               help='Directory where the files will be written.')
]


def register_opts(conf):
    conf.register_opts(prometheus_opts, group='oslo_messaging_notifications')


class PrometheusFileDriver(notifier.Driver):
    """Publish notifications into a File to be used by Prometheus"""

    def __init__(self, conf, topics, transport):
        self.files_dir = conf.oslo_messaging_notifications.files_dir
        if not os.path.exists(self.files_dir):
            os.makedirs(os.path.dirname(self.files_dir))
        super(PrometheusFileDriver, self).__init__(conf, topics, transport)

    def notify(self, ctxt, message, priority, retry):
        try:
            node_parser_manager = manager.ParserManager(message)
            node_metrics = node_parser_manager.merge_information()
            node_name = message['payload']['node_name']
            node_file = open(os.path.join(self.files_dir, node_name), 'w')
            node_file.write(node_metrics)
            node_file.close()
        except Exception as e:
            print(e)


class SimpleFileDriver(notifier.Driver):

    def __init__(self, conf, topics, transport):
        self.files_dir = conf.oslo_messaging_notifications.files_dir
        if not os.path.exists(self.files_dir):
            os.makedirs(os.path.dirname(self.files_dir))
        super(SimpleFileDriver, self).__init__(conf, topics, transport)

    def notify(self, ctx, message, priority, retry):
        file = open(os.path.join(self.files_dir, 'simplefile'), 'w')
        file.write(message)
        file.close()
