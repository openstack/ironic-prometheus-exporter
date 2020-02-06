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

from ironic_prometheus_exporter import utils as ipe_utils
from ironic_prometheus_exporter.parsers import descriptions


def timestamp_registry(node_information, ipmi_metric_registry):
    metric = 'baremetal_last_payload_timestamp_seconds'
    labels = {'node_name': node_information['node_name'],
              'node_uuid': node_information['node_uuid'],
              'instance_uuid': node_information['instance_uuid']}
    dt_1970 = datetime(1970, 1, 1, 0, 0, 0)
    dt_timestamp = datetime.strptime(node_information['timestamp'],
                                     '%Y-%m-%dT%H:%M:%S.%f')
    value = int((dt_timestamp - dt_1970).total_seconds())

    desc = descriptions.get_metric_description('header', metric)

    g = Gauge(
        metric, desc, labelnames=labels,
        registry=ipmi_metric_registry)

    valid_labels = ipe_utils.update_instance_uuid(labels)
    g.labels(**valid_labels).set(value)
