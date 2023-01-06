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

from oslo_config import cfg
from oslo_messaging.notify import notifier
from prometheus_client import CollectorRegistry
from prometheus_client import write_to_textfile

from ironic_prometheus_exporter.parsers import header
from ironic_prometheus_exporter.parsers import ipmi
from ironic_prometheus_exporter.parsers import ironic as ironic_parser
from ironic_prometheus_exporter.parsers import redfish


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
            payload = message['payload']
            if event_type == 'ironic.metrics':
                # We know this message payload is from a conductor itself
                # and not for node drivers.
                header.timestamp_conductor_registry(payload, registry)
                ironic_parser.category_registry(payload, registry)

            else:
                header.timestamp_registry(payload, registry)
                if event_type == 'hardware.ipmi.metrics':
                    ipmi.category_registry(payload, registry)

                elif event_type == 'hardware.redfish.metrics':
                    redfish.category_registry(payload, registry)

            # Order of preference is for a node Name, UUID, or
            # payload hostname field to be used (i.e. for conductor
            # message payloads).
            field = (
                payload.get('node_name') or
                payload.get('node_uuid') or
                payload.get('hostname')
            )
            statFile = os.path.join(
                self.location, field + '-' + event_type)

            # Writes to file for server pickup
            write_to_textfile(statFile, registry)

        except Exception as e:
            LOG.error(e)
            raise


class SimpleFileDriver(notifier.Driver):

    def __init__(self, conf, topics, transport):
        self.location = conf.oslo_messaging_notifications.location
        if not os.path.exists(self.location):
            os.makedirs(os.path.dirname(self.location))
        super(SimpleFileDriver, self).__init__(conf, topics, transport)

    def notify(self, ctx, message, priority, retry):
        with open(os.path.join(self.location, 'simplefile'), 'w') as file:
            file.write(message)
