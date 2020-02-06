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

import json
import os
import unittest

import ironic_prometheus_exporter
from ironic_prometheus_exporter import utils as ipe_utils
from ironic_prometheus_exporter.parsers import header
from prometheus_client import CollectorRegistry


sample_file = os.path.join(
    os.path.dirname(ironic_prometheus_exporter.__file__),
    'tests', 'json_samples', 'notification-header.json')

DATA = json.load(open(sample_file))


class TestPayloadsParser(unittest.TestCase):

    def setUp(self):
        self.node_message = DATA['payload']
        self.node_name = DATA['payload']['node_name']
        self.node_uuid = DATA['payload']['node_uuid']
        self.instance_uuid = DATA['payload']['instance_uuid']
        self.timestamp = DATA['payload']['timestamp']
        self.payload = DATA['payload']['payload']
        self.metric_registry = CollectorRegistry()

    def test_timestamp_metric(self):
        header.timestamp_registry(self.node_message, self.metric_registry)

        self.assertEqual(1553890342.0, self.metric_registry.get_sample_value(
            'baremetal_last_payload_timestamp_seconds',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid}
        ))

    def test_none_for_instance_uuid(self):
        sample_file_2 = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples', 'notification-header-with-none.json')
        msg2 = json.load(open(sample_file_2))
        self.assertIsNone(msg2['payload']['instance_uuid'])
        valid_labels = ipe_utils.update_instance_uuid(msg2['payload'])
        self.assertEqual(valid_labels['instance_uuid'],
                         msg2['payload']['node_uuid'])

        header.timestamp_registry(msg2['payload'], self.metric_registry)
        self.assertEqual(1553890342.0, self.metric_registry.get_sample_value(
            'baremetal_last_payload_timestamp_seconds',
            {'node_name': msg2['payload']['node_name'],
             'node_uuid': msg2['payload']['node_uuid'],
             'instance_uuid': msg2['payload']['node_uuid']}
        ))
