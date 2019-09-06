#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os

from ironic_prometheus_exporter.parsers import ipmi
from ironic_prometheus_exporter.parsers import header
from ironic_prometheus_exporter.parsers import redfish
from oslo_config import cfg
from oslo_messaging.notify import notifier
from prometheus_client import write_to_textfile, CollectorRegistry

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
            registry = CollectorRegistry()

            event_type = message['event_type']
            node_message = message['payload']
            header.timestamp_registry(node_message, registry)

            if event_type == 'hardware.ipmi.metrics':
                ipmi.category_registry(node_message, registry)

            elif event_type == 'hardware.redfish.metrics':
                redfish.category_registry(node_message, registry)

            nodeFile = os.path.join(
                self.location,
                node_message['node_name'] + '-' + event_type)
            write_to_textfile(nodeFile, registry)

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
