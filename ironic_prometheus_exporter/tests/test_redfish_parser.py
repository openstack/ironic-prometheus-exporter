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

from prometheus_client import CollectorRegistry

import ironic_prometheus_exporter
from ironic_prometheus_exporter.parsers import redfish
from ironic_prometheus_exporter import utils as ipe_utils


sample_file = os.path.join(
    os.path.dirname(ironic_prometheus_exporter.__file__),
    'tests', 'json_samples', 'notification-redfish.json')

DATA = json.load(open(sample_file))


class TestPayloadsParser(unittest.TestCase):

    def setUp(self):
        self.node_message = DATA['payload']
        self.node_name = DATA['payload']['node_name']
        self.node_uuid = DATA['payload']['node_uuid']
        self.instance_uuid = DATA['payload']['instance_uuid']

    def test_build_temperature_metrics(self):
        metrics = redfish.build_temperature_metrics(self.node_message)

        expected_metric = 'baremetal_temp_cpu_celsius'

        self.assertIn(expected_metric, metrics)

        self.assertEqual(62, metrics[expected_metric][0][0])

        expected_labels = {
            'entity_id': 'CPU',
            'instance_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'node_name': 'knilab-master-u9',
            'node_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'sensor_id': 1
        }

        self.assertEqual(
            expected_labels, metrics[expected_metric][0][1])

    def test_build_power_metrics(self):
        metrics = redfish.build_power_metrics(self.node_message)

        expected_metric = 'baremetal_power_status'

        self.assertIn(expected_metric, metrics)

        self.assertEqual(0, metrics[expected_metric][0][0])

        expected_labels = {
            'entity_id': 'PSU',
            'instance_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'node_name': 'knilab-master-u9',
            'node_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'sensor_id': '0:Power@ZZZ-YYY-XXX'
        }

        self.assertEqual(
            expected_labels, metrics[expected_metric][0][1])

    def test_build_fan_metrics(self):
        metrics = redfish.build_fan_metrics(self.node_message)

        expected_metric = 'baremetal_fan_status'

        self.assertIn(expected_metric, metrics)

        self.assertEqual(0, metrics[expected_metric][0][0])

        expected_labels = {
            'entity_id': 'CPU',
            'instance_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'node_name': 'knilab-master-u9',
            'node_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'sensor_id': 'XXX-YYY-ZZZ'
        }

        self.assertEqual(
            expected_labels, metrics[expected_metric][0][1])

    def test_build_drive_metrics(self):
        metrics = redfish.build_drive_metrics(self.node_message)

        expected_metric = 'baremetal_drive_status'

        self.assertIn(expected_metric, metrics)

        self.assertEqual(0, metrics[expected_metric][0][0])

        expected_labels = {
            'entity_id': 'HDD',
            'instance_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'node_name': 'knilab-master-u9',
            'node_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'sensor_id': '32ADF365C6C1B7BD:XXX-YYY-ZZZ@ZZZ-YYY-XXX'
        }

        self.assertEqual(
            expected_labels, metrics[expected_metric][0][1])

    def test_category_registry(self):
        metrics_registry = CollectorRegistry()

        redfish.category_registry(self.node_message, metrics_registry)

        label = {
            'entity_id': 'HDD',
            'instance_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'node_name': 'knilab-master-u9',
            'node_uuid': 'ac2aa2fd-6e1a-41c8-a114-2084c8705228',
            'sensor_id': '32ADF365C6C1B7BD:XXX-YYY-ZZZ@ZZZ-YYY-XXX'
        }

        sensor_value = metrics_registry.get_sample_value(
            'baremetal_drive_status', label)

        self.assertEqual(0, sensor_value)

    def test_none_instance_uuid(self):
        sample_file2 = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples',
            'notification-redfish-none-instance_uuid.json')
        msg2 = json.load(open(sample_file2))

        self.assertIsNone(msg2['payload']['instance_uuid'])
        valid_labels = ipe_utils.update_instance_uuid(msg2['payload'])
        self.assertEqual(valid_labels['instance_uuid'],
                         msg2['payload']['node_uuid'])

        metrics = redfish.build_power_metrics(msg2['payload'])

        expected_metric = 'baremetal_power_status'

        self.assertIn(expected_metric, metrics)

        self.assertEqual(0, metrics[expected_metric][0][0])

        expected_labels = {
            'entity_id': 'PSU',
            'instance_uuid': 'c2bd00b9-9881-4179-8b7b-bf786ec3696b',
            'node_name': 'knilab-master-u9',
            'node_uuid': 'c2bd00b9-9881-4179-8b7b-bf786ec3696b',
            'sensor_id': '0:Power@ZZZ-YYY-XXX'
        }

        self.assertEqual(
            expected_labels, metrics[expected_metric][0][1])


class TestPayloadsParserNoneNodeName(unittest.TestCase):

    def setUp(self):
        sample_file_none = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples',
            'notification-redfish-none-node_name.json')
        msg = json.load(open(sample_file_none))
        self.node_message = msg['payload']
        self.node_uuid = msg['payload']['node_uuid']
        self.instance_uuid = msg['payload']['instance_uuid']

    def test_build_temperature_metrics(self):
        metrics = redfish.build_temperature_metrics(self.node_message)

        expected_metric = 'baremetal_temp_cpu_celsius'

        self.assertIn(expected_metric, metrics)

        self.assertEqual(62, metrics[expected_metric][0][0])

        expected_labels = {
            'entity_id': 'CPU',
            'instance_uuid': '85d6b2c8-fe57-432d-868a-330e0e28cf34',
            'node_uuid': 'c2bd00b9-9881-4179-8b7b-bf786ec3696b',
            'sensor_id': 1
        }

        self.assertEqual(
            expected_labels, metrics[expected_metric][0][1])
