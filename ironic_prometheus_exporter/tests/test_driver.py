import json
import os
import oslo_messaging

from ironic_prometheus_exporter.messaging import PrometheusFileDriver
from oslo_messaging.tests import utils as test_utils


class TestPrometheusFileNotifier(test_utils.BaseTestCase):

    def setUp(self):
        super(TestPrometheusFileNotifier, self).setUp()

    def tearDown(self):
        super(TestPrometheusFileNotifier, self).tearDown()
        DIR = '/tmp/ironic_prometheus_exporter'
        all_files = [name for name in os.listdir(DIR)
                     if os.path.isfile(os.path.join(DIR, name))]
        for f in all_files:
            os.remove(os.path.join(DIR, f))

    def test_instanciate(self):
        self.config(files_dir='/tmp/ironic_prometheus_exporter',
                    group='oslo_messaging_notifications')
        transport = oslo_messaging.get_notification_transport(self.conf)
        oslo_messaging.Notifier(transport, driver='prometheus_exporter',
                                topics=['my_topics'])

        self.assertEqual(self.conf.oslo_messaging_notifications.files_dir,
                         "/tmp/ironic_prometheus_exporter")
        self.assertTrue(os.path.isdir(
            self.conf.oslo_messaging_notifications.files_dir))

    def test_messages_from_same_node(self):
        self.config(files_dir='/tmp/ironic_prometheus_exporter',
                    group='oslo_messaging_notifications')
        transport = oslo_messaging.get_notification_transport(self.conf)
        driver = PrometheusFileDriver(self.conf, None, transport)

        msg1 = json.load(open('./ironic_prometheus_exporter/tests/data.json'))
        node1 = msg1['payload']['node_name']
        msg2 = json.load(open('./ironic_prometheus_exporter/tests/data2.json'))
        # Override data2 node_name
        msg2['payload']['node_name'] = node1
        node2 = msg2['payload']['node_name']
        self.assertNotEqual(msg1['payload']['timestamp'],
                            msg2['payload']['timestamp'])

        driver.notify(None, msg1, 'info', 0)
        driver.notify(None, msg2, 'info', 0)

        DIR = self.conf.oslo_messaging_notifications.files_dir
        all_files = [name for name in os.listdir(DIR)
                     if os.path.isfile(os.path.join(DIR, name))]
        self.assertEqual(node1, node2)
        self.assertEqual(len(all_files), 1)
        self.assertTrue(node1 in all_files)
        self.assertTrue(node2 in all_files)

    def test_messages_from_different_nodes(self):
        self.config(files_dir='/tmp/ironic_prometheus_exporter',
                    group='oslo_messaging_notifications')
        transport = oslo_messaging.get_notification_transport(self.conf)
        driver = PrometheusFileDriver(self.conf, None, transport)

        msg1 = json.load(open('./ironic_prometheus_exporter/tests/data.json'))
        node1 = msg1['payload']['node_name']
        msg2 = json.load(open('./ironic_prometheus_exporter/tests/data2.json'))
        node2 = msg2['payload']['node_name']
        self.assertNotEqual(msg1['payload']['timestamp'],
                            msg2['payload']['timestamp'])

        driver.notify(None, msg1, 'info', 0)
        driver.notify(None, msg2, 'info', 0)

        DIR = self.conf.oslo_messaging_notifications.files_dir
        all_files = [name for name in os.listdir(DIR)
                     if os.path.isfile(os.path.join(DIR, name))]
        self.assertEqual(len(all_files), 2)
        self.assertTrue(node1 in all_files)
        self.assertTrue(node2 in all_files)
