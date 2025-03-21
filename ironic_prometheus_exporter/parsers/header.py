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

from datetime import datetime

from prometheus_client import Gauge

from ironic_prometheus_exporter.parsers import descriptions
from ironic_prometheus_exporter import utils as ipe_utils


def timestamp_registry(node_information, metric_registry):
    """Injects a last updated timestamp for a node."""
    metric = 'baremetal_last_payload_timestamp_seconds'
    node_uuid = node_information.get('node_uuid') \
        or node_information.get('uuid')
    labels = {'node_uuid': node_uuid,
              'instance_uuid': node_information.get('instance_uuid')}
    if node_information.get('node_name') or node_information.get('name'):
        labels['node_name'] = node_information.get('node_name') \
            or node_information.get('name')
    dt_1970 = datetime(1970, 1, 1, 0, 0, 0)
    dt_timestamp = datetime.strptime(node_information['timestamp'],
                                     '%Y-%m-%dT%H:%M:%S.%f')
    value = int((dt_timestamp - dt_1970).total_seconds())

    desc = descriptions.get_metric_description('header', metric)

    g = Gauge(
        metric, desc, labelnames=labels,
        registry=metric_registry)

    valid_labels = ipe_utils.update_instance_uuid(labels)
    g.labels(**valid_labels).set(value)


def timestamp_conductor_registry(payload, metric_registry):
    """Injets a last updated at timestamp for a conductor."""
    metric = 'conductor_service_last_payload_timestamp_seconds'
    labels = {'hostname': payload['hostname']}
    dt_1970 = datetime(1970, 1, 1, 0, 0, 0)
    dt_timestamp = datetime.strptime(payload['timestamp'],
                                     '%Y-%m-%dT%H:%M:%S.%f')
    value = int((dt_timestamp - dt_1970).total_seconds())

    desc = descriptions.get_metric_description('header', metric)

    g = Gauge(
        metric, desc, labelnames=labels,
        registry=metric_registry)

    g.labels(labels).set(value)
