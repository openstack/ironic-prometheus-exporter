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

import fixtures
import json
import os
import oslo_messaging

import ironic_prometheus_exporter
from ironic_prometheus_exporter.messaging import PrometheusFileDriver
from oslo_messaging.tests import utils as test_utils


class TestPrometheusFileNotifier(test_utils.BaseTestCase):

    def setUp(self):
        super(TestPrometheusFileNotifier, self).setUp()

    def test_instantiate(self):
        temp_dir = self.useFixture(fixtures.TempDir()).path
        self.config(location=temp_dir,
                    group='oslo_messaging_notifications')
        transport = oslo_messaging.get_notification_transport(self.conf)
        oslo_messaging.Notifier(transport, driver='prometheus_exporter',
                                topics=['my_topics'])

        self.assertEqual(self.conf.oslo_messaging_notifications.location,
                         temp_dir)
        self.assertTrue(os.path.isdir(
            self.conf.oslo_messaging_notifications.location))

    def test_messages_from_same_node(self):
        temp_dir = self.useFixture(fixtures.TempDir()).path
        self.config(location=temp_dir,
                    group='oslo_messaging_notifications')
        transport = oslo_messaging.get_notification_transport(self.conf)
        driver = PrometheusFileDriver(self.conf, None, transport)

        sample_file_1 = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples', 'notification-ipmi-1.json')

        sample_file_2 = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples', 'notification-ipmi-2.json')

        msg1 = json.load(open(sample_file_1))
        node1 = msg1['payload']['node_name']
        msg2 = json.load(open(sample_file_2))
        # Override data2 node_name, node_uuid, instance_uuid
        msg2['payload']['node_name'] = node1
        msg2['payload']['node_uuid'] = msg1['payload']['node_uuid']
        msg2['payload']['instance_uuid'] = msg1['payload']['instance_uuid']
        node2 = msg2['payload']['node_name']
        self.assertNotEqual(msg1['payload']['timestamp'],
                            msg2['payload']['timestamp'])

        driver.notify(None, msg1, 'info', 0)
        driver.notify(None, msg2, 'info', 0)

        DIR = self.conf.oslo_messaging_notifications.location
        all_files = [name for name in os.listdir(DIR)
                     if os.path.isfile(os.path.join(DIR, name))]
        self.assertEqual(node1, node2)
        self.assertEqual(len(all_files), 1)
        self.assertIn(node1 + '-hardware.ipmi.metrics', all_files)
        self.assertIn(node2 + '-hardware.ipmi.metrics', all_files)

    def test_messages_from_different_nodes(self):
        temp_dir = self.useFixture(fixtures.TempDir()).path
        self.config(location=temp_dir,
                    group='oslo_messaging_notifications')
        transport = oslo_messaging.get_notification_transport(self.conf)
        driver = PrometheusFileDriver(self.conf, None, transport)

        sample_file_1 = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples', 'notification-ipmi-1.json')

        sample_file_2 = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples', 'notification-ipmi-2.json')

        msg1 = json.load(open(sample_file_1))
        node1 = msg1['payload']['node_name']
        msg2 = json.load(open(sample_file_2))
        node2 = msg2['payload']['node_name']
        self.assertNotEqual(msg1['payload']['timestamp'],
                            msg2['payload']['timestamp'])

        driver.notify(None, msg1, 'info', 0)
        driver.notify(None, msg2, 'info', 0)

        DIR = self.conf.oslo_messaging_notifications.location
        all_files = [name for name in os.listdir(DIR)
                     if os.path.isfile(os.path.join(DIR, name))]
        self.assertEqual(len(all_files), 2)
        self.assertIn(node1 + '-hardware.ipmi.metrics', all_files)
        self.assertIn(node2 + '-hardware.ipmi.metrics', all_files)

    def test_messages_of_different_types(self):
        temp_dir = self.useFixture(fixtures.TempDir()).path
        self.config(location=temp_dir,
                    group='oslo_messaging_notifications')
        transport = oslo_messaging.get_notification_transport(self.conf)
        driver = PrometheusFileDriver(self.conf, None, transport)

        sample_file_1 = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples', 'notification-ipmi-1.json')

        sample_file_2 = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples', 'notification-redfish.json')

        msg1 = json.load(open(sample_file_1))
        node1 = msg1['payload']['node_name']
        msg2 = json.load(open(sample_file_2))
        node2 = msg2['payload']['node_name']

        driver.notify(None, msg1, 'info', 0)
        driver.notify(None, msg2, 'info', 0)

        DIR = self.conf.oslo_messaging_notifications.location
        all_files = [name for name in os.listdir(DIR)
                     if os.path.isfile(os.path.join(DIR, name))]
        self.assertEqual(len(all_files), 2)
        self.assertIn(node1 + '-hardware.ipmi.metrics', all_files)
        self.assertIn(node2 + '-hardware.redfish.metrics', all_files)
