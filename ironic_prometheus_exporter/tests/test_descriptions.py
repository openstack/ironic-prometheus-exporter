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

from ironic_prometheus_exporter.parsers import descriptions

from oslo_messaging.tests import utils as test_utils


class TestMetricsDescriptions(test_utils.BaseTestCase):

    def test_good_source_good_metrics(self):
        desc = descriptions.get_metric_description(
            'header', 'baremetal_last_payload_timestamp_seconds')

        expected = 'Timestamp of the last received payload'

        self.assertEqual(expected, desc)

    def test_good_source_bad_metrics(self):
        desc = descriptions.get_metric_description(
            'header', 'bad_metrics')

        expected = ''

        self.assertEqual(expected, desc)

    def test_bad_source_bad_metrics(self):
        desc = descriptions.get_metric_description(
            'bad_source', 'bad_metrics')

        expected = ''

        self.assertEqual(expected, desc)
