import oslo_messaging

from oslo_messaging.tests import utils as test_utils


class TestPrometheusFileNotifier(test_utils.BaseTestCase):

    def setUp(self):
        super(TestPrometheusFileNotifier, self).setUp()

    def test_notifier(self):
        transport = oslo_messaging.get_notification_transport(self.conf)
        my_notifier = oslo_messaging.Notifier(transport,
                                              driver='prometheus_exporter',
                                              topics=['my_topics'])
        self.config(file_name='test.txt',
                    file_dir='/tmp/ironic_prometheus_exporter',
                    group='oslo_messaging_notifications')
        self.assertEqual(self.conf.oslo_messaging_notifications.file_name,
                         "test.txt")
        self.assertEqual(self.conf.oslo_messaging_notifications.file_dir,
                         '/tmp/ironic_prometheus_exporter')
        my_notifier.debug({}, "My Event", 'Payload')
