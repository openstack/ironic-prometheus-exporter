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
from ironic_prometheus_exporter.parsers import ironic


sample_file = os.path.join(
    os.path.dirname(ironic_prometheus_exporter.__file__),
    'tests', 'json_samples', 'notification-ironic.json')
expected_file = os.path.join(
    os.path.dirname(ironic_prometheus_exporter.__file__),
    'tests', 'json_samples',
    './expected_ironic_parser_entries.json')

DATA = json.load(open(sample_file))

# Helper to dump the output upon major changes, since
# it is a lot of JSON.
DUMP_JSON = False

if not DUMP_JSON:
    EXPECTED = json.load(open(expected_file))
else:
    EXPECTED = None


class TestIronicPayloadParser(unittest.TestCase):

    def setUp(self):
        self.message = DATA['payload']

    def test_category_registry(self):
        registry = CollectorRegistry()

        ironic.category_registry(self.message, registry)
        entry_count = 0
        for entry in registry.collect():
            # NOTE(TheJulia): We don't get the results back in any order
            # which makes sense.
            sample = entry.samples[0]
            name = sample.name
            labels = sample.labels
            value = sample.value
            documentation = entry.documentation
            entry_type = entry.type
            if not DUMP_JSON:
                for expected_entry in EXPECTED:
                    # Find the entry, since access order is unreliable,
                    # and to compare so much data back and forth is otherwise
                    # not really feasible.
                    if name == expected_entry['name']:
                        break
            else:
                expected_entry = None

            # NOTE(TheJulia): The lines below are just to help regenerate
            # the known data set, but we don't get a reliable access order
            # from the prometheus client registry collection object.
            if DUMP_JSON:
                print('    {')
                print(f'        \"name\": \"{sample.name}\",')
                print('        \"labels\": %s,' % json.dumps(sample.labels))
                print(f'        \"value\": {sample.value},')
                print(f'        \"docs\": \"{entry.documentation}\",')
                print(f'        \"type\": \"{entry.type}\"')
                print('    },')
            else:
                self.assertEqual(name, expected_entry['name'])
                self.assertDictEqual(labels, expected_entry['labels'])
                self.assertEqual(value, expected_entry['value'])
                self.assertEqual(documentation, expected_entry['docs'])
                self.assertEqual(entry_type, expected_entry['type'])
                assert any(char.isupper() for char in sample.name) is not True
            entry_count = entry_count + 1
        if not DUMP_JSON:
            self.assertEqual(len(EXPECTED), entry_count)
