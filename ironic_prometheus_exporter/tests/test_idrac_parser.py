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
from ironic_prometheus_exporter.parsers import redfish as idrac_redfish


sample_file = os.path.join(
    os.path.dirname(ironic_prometheus_exporter.__file__),
    'tests', 'json_samples', 'notification-idrac.json')

DATA = json.load(open(sample_file))


class TestIDRACPayloadsParser(unittest.TestCase):

    def setUp(self):
        self.node_message = DATA['payload']
        self.node_name = DATA['payload']['node_name']
        self.node_uuid = DATA['payload']['node_uuid']
        self.instance_uuid = DATA['payload']['instance_uuid']

    def test_build_temperature_metrics(self):
        metrics = idrac_redfish.build_temperature_metrics(self.node_message)

        expected_metric_name = 'baremetal_temperature_status'
        self.assertIn(expected_metric_name, metrics)
        self.assertEqual(0, metrics[expected_metric_name][0][0])
        expected_labels = {
            'identity': '0',
            'sensor_id': '0@System.Embedded.1',
            'physical_context': 'CPU',
            'reading_celsius': 49,
            'instance_uuid': '235e4d8a-0f1a-87a0-ea81-8a1b0277cd87',
            'node_name': 'r640-u12',
            'node_uuid': 'fe81395b-1999-4ab4-8eb0-235e1ab02778',
            'sensor_number': 1,
            'state': 'Enabled',
            'health': 'OK'
        }
        self.assertEqual(
            expected_labels, metrics[expected_metric_name][0][1])

        self.assertEqual(1, metrics[expected_metric_name][2][0])
        expected_labels2 = {
            'identity': '2',
            'sensor_id': '2@System.Embedded.1',
            'physical_context': 'SystemBoard',
            'reading_celsius': 80,
            'instance_uuid': '235e4d8a-0f1a-87a0-ea81-8a1b0277cd87',
            'node_name': 'r640-u12',
            'node_uuid': 'fe81395b-1999-4ab4-8eb0-235e1ab02778',
            'sensor_number': 5,
            'state': 'Enabled',
            'health': 'Warning'
        }
        self.assertEqual(
            expected_labels2, metrics[expected_metric_name][2][1])

        self.assertEqual(2, metrics[expected_metric_name][3][0])
        expected_labels3 = {
            'identity': '3',
            'sensor_id': '3@System.Embedded.1',
            'physical_context': 'SystemBoard',
            'reading_celsius': 100,
            'instance_uuid': '235e4d8a-0f1a-87a0-ea81-8a1b0277cd87',
            'node_name': 'r640-u12',
            'node_uuid': 'fe81395b-1999-4ab4-8eb0-235e1ab02778',
            'sensor_number': 6,
            'state': 'Enabled',
            'health': 'Critical'
        }
        self.assertEqual(
            expected_labels3, metrics[expected_metric_name][3][1])

    def test_build_power_metrics(self):
        metrics = idrac_redfish.build_power_metrics(self.node_message)

        expected_metric = 'baremetal_power_status'

        self.assertIn(expected_metric, metrics)

        self.assertEqual(0, metrics[expected_metric][0][0])

        expected_labels = {
            'instance_uuid': '235e4d8a-0f1a-87a0-ea81-8a1b0277cd87',
            'last_power_output_watts': 148,
            'line_input_voltage': 208,
            'power_capacity_watts': 750,
            'node_name': 'r640-u12',
            'node_uuid': 'fe81395b-1999-4ab4-8eb0-235e1ab02778',
            'sensor_id': '0:Power@System.Embedded.1',
            'serial_number': 'CNDED0089IA7W5',
            'state': 'Enabled',
            'health': 'OK'
        }

        self.assertEqual(
            expected_labels, metrics[expected_metric][0][1])

    def test_build_fan_metrics(self):
        metrics = idrac_redfish.build_fan_metrics(self.node_message)

        expected_metric = 'baremetal_fan_status'

        self.assertIn(expected_metric, metrics)

        self.assertEqual(0, metrics[expected_metric][0][0])

        expected_labels = {
            'identity': '0',
            'instance_uuid': '235e4d8a-0f1a-87a0-ea81-8a1b0277cd87',
            'node_name': 'r640-u12',
            'node_uuid': 'fe81395b-1999-4ab4-8eb0-235e1ab02778',
            'physical_context': 'SystemBoard',
            'reading': 9600,
            'reading_units': 'RPM',
            'sensor_id': '0@System.Embedded.1',
            'state': 'Enabled',
            'health': 'OK'
        }

        self.assertEqual(
            expected_labels, metrics[expected_metric][0][1])

    def test_build_drive_metrics(self):
        metrics = idrac_redfish.build_drive_metrics(self.node_message)

        expected_metric = 'baremetal_drive_status'

        self.assertIn(expected_metric, metrics)

        self.assertEqual(0, metrics[expected_metric][0][0])

        expected_labels = {
            'model': 'Dell Express Flash NVMe P4500 1.0TB SFF',
            'name': 'PCIe SSD in Slot 9 in Bay 1',
            'instance_uuid': '235e4d8a-0f1a-87a0-ea81-8a1b0277cd87',
            'node_name': 'r640-u12',
            'node_uuid': 'fe81395b-1999-4ab4-8eb0-235e1ab02778',
            'sensor_id': 'PCIe SSD in Slot 9 in Bay 1:CPU.1@System.Embedded.1',
            'capacity_bytes': 1000204886016,
            'state': 'Enabled',
            'health': 'OK'
        }

        self.assertEqual(
            expected_labels, metrics[expected_metric][0][1])

    def test_category_registry(self):
        metrics_registry = CollectorRegistry()

        idrac_redfish.category_registry(self.node_message, metrics_registry)

        label = {
            'node_name': 'r640-u12',
            'node_uuid': 'fe81395b-1999-4ab4-8eb0-235e1ab02778',
            'instance_uuid': '235e4d8a-0f1a-87a0-ea81-8a1b0277cd87',
            'name': 'PCIe SSD in Slot 9 in Bay 1',
            'model': 'Dell Express Flash NVMe P4500 1.0TB SFF',
            'capacity_bytes': '1000204886016',
            'state': 'Enabled',
            'health': 'OK',
            'sensor_id': 'PCIe SSD in Slot 9 in Bay 1:CPU.1@System.Embedded.1'
        }
        sensor_value = metrics_registry.get_sample_value(
            'baremetal_drive_status', label)
        self.assertEqual(0, sensor_value)
