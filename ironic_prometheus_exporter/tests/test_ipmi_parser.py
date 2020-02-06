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
from ironic_prometheus_exporter.parsers import ipmi
from prometheus_client import CollectorRegistry


sample_file = os.path.join(
    os.path.dirname(ironic_prometheus_exporter.__file__),
    'tests', 'json_samples', 'notification-ipmi-1.json')

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

    def test_management_parser(self):
        management_category_info = ipmi.CATEGORY_PARAMS['management'].copy()
        management_category_info['data'] = \
            self.node_message['payload']['Management'].copy()
        management_category_info['node_name'] = self.node_name
        management_category_info['node_uuid'] = self.node_uuid
        management_category_info['instance_uuid'] = self.instance_uuid

        management_metrics_name = ipmi.metric_names(management_category_info)
        self.assertEqual(len(management_metrics_name), 1)
        self.assertIn('baremetal_front_led_panel', management_metrics_name)

        ipmi.prometheus_format(management_category_info,
                               self.metric_registry,
                               management_metrics_name)
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_front_led_panel',
            {'node_name': 'knilab-master-u9',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'sensor_id': 'Front LED Panel (0x23)'}))

    def test_temperature_parser(self):
        temperature_category_info = ipmi.CATEGORY_PARAMS['temperature'].copy()
        temperature_category_info['data'] = \
            self.node_message['payload']['Temperature'].copy()
        temperature_category_info['node_name'] = self.node_name
        temperature_category_info['node_uuid'] = self.node_uuid
        temperature_category_info['instance_uuid'] = self.instance_uuid

        temperature_metrics_name = ipmi.metric_names(temperature_category_info)
        self.assertEqual(len(temperature_metrics_name), 3)
        self.assertIn('baremetal_temp_celsius', temperature_metrics_name)
        self.assertIn('baremetal_exhaust_temp_celsius',
                      temperature_metrics_name)
        self.assertIn('baremetal_inlet_temp_celsius', temperature_metrics_name)

        ipmi.prometheus_format(temperature_category_info,
                               self.metric_registry,
                               temperature_metrics_name)
        self.assertEqual(21.0, self.metric_registry.get_sample_value(
            'baremetal_inlet_temp_celsius',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'sensor_id': 'Inlet Temp (0x5)',
             'status': 'ok'}
        ))
        self.assertEqual(36.0, self.metric_registry.get_sample_value(
            'baremetal_exhaust_temp_celsius',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'sensor_id': 'Exhaust Temp (0x6)',
             'status': 'ok'}))
        self.assertEqual(44.0, self.metric_registry.get_sample_value(
            'baremetal_temp_celsius', {'node_name': self.node_name,
                                       'sensor_id': 'Temp (0x1)',
                                       'node_uuid': self.node_uuid,
                                       'instance_uuid': self.instance_uuid,
                                       'entity_id': '3.1 (Processor)',
                                       'status': 'ok'}))
        self.assertEqual(43.0, self.metric_registry.get_sample_value(
            'baremetal_temp_celsius', {'node_name': self.node_name,
                                       'sensor_id': 'Temp (0x2)',
                                       'node_uuid': self.node_uuid,
                                       'instance_uuid': self.instance_uuid,
                                       'entity_id': '3.2 (Processor)',
                                       'status': 'ok'}))

    def test_system_parser(self):
        system_category_info = ipmi.CATEGORY_PARAMS['system'].copy()
        system_category_info['data'] = \
            self.node_message['payload']['System'].copy()
        system_category_info['node_name'] = self.node_name
        system_category_info['node_uuid'] = self.node_uuid
        system_category_info['instance_uuid'] = self.instance_uuid

        system_metrics_name = ipmi.metric_names(system_category_info)
        self.assertEqual(len(system_metrics_name), 2)
        self.assertIn('baremetal_system_unknown', system_metrics_name)
        self.assertIn('baremetal_system_post_err', system_metrics_name)

        ipmi.prometheus_format(system_category_info,
                               self.metric_registry,
                               system_metrics_name)
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_system_unknown',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'Unknown (0x8)'}
        ))
        self.assertEqual(None, self.metric_registry.get_sample_value(
            'baremetal_system_post_err',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'POST Err (0x1e)'}
        ))

    def test_current_parser(self):
        current_category_info = ipmi.CATEGORY_PARAMS['current'].copy()
        current_category_info['data'] = \
            self.node_message['payload']['Current'].copy()
        current_category_info['node_name'] = self.node_name
        current_category_info['node_uuid'] = self.node_uuid
        current_category_info['instance_uuid'] = self.instance_uuid

        current_metrics_name = ipmi.metric_names(current_category_info)
        self.assertEqual(len(current_metrics_name), 2)
        self.assertIn('baremetal_current', current_metrics_name)
        self.assertIn('baremetal_pwr_consumption', current_metrics_name)

        ipmi.prometheus_format(current_category_info,
                               self.metric_registry,
                               current_metrics_name)
        self.assertEqual(264.0, self.metric_registry.get_sample_value(
            'baremetal_pwr_consumption',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'sensor_id': 'Pwr Consumption (0x76)',
             'status': 'ok'}
        ))
        self.assertEqual(0.600, self.metric_registry.get_sample_value(
            'baremetal_current',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '10.1 (Power Supply)',
             'sensor_id': 'Current 1 (0x6b)',
             'status': 'ok'}
        ))
        self.assertEqual(0.600, self.metric_registry.get_sample_value(
            'baremetal_current',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '10.2 (Power Supply)',
             'sensor_id': 'Current 2 (0x6c)',
             'status': 'ok'}
        ))

    def test_version_parser(self):
        version_category_info = ipmi.CATEGORY_PARAMS['version'].copy()
        version_category_info['data'] = \
            self.node_message['payload']['Version'].copy()
        version_category_info['node_name'] = self.node_name
        version_category_info['node_uuid'] = self.node_uuid
        version_category_info['instance_uuid'] = self.instance_uuid

        version_metrics_name = ipmi.metric_names(version_category_info)
        self.assertEqual(len(version_metrics_name), 3)
        self.assertIn('baremetal_tpm_presence', version_metrics_name)
        self.assertIn('baremetal_hdwr_version_err', version_metrics_name)
        self.assertIn('baremetal_chassis_mismatch', version_metrics_name)

        ipmi.prometheus_format(version_category_info,
                               self.metric_registry,
                               version_metrics_name)
        self.assertEqual(1.0, self.metric_registry.get_sample_value(
            'baremetal_tpm_presence',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'TPM Presence (0x41)'}
        ))
        self.assertEqual(None, self.metric_registry.get_sample_value(
            'baremetal_hdwr_version_err',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'Hdwr version err (0x1f)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_chassis_mismatch',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'Chassis Mismatch (0x37)'}
        ))

    def test_memory_parser(self):
        memory_category_info = ipmi.CATEGORY_PARAMS['memory'].copy()
        memory_category_info['data'] = \
            self.node_message['payload']['Memory'].copy()
        memory_category_info['node_name'] = self.node_name
        memory_category_info['node_uuid'] = self.node_uuid
        memory_category_info['instance_uuid'] = self.instance_uuid

        memory_metrics_name = ipmi.metric_names(memory_category_info)
        self.assertEqual(len(memory_metrics_name), 10)
        self.assertIn('baremetal_memory_ecc_corr_err', memory_metrics_name)
        self.assertIn('baremetal_idpt_mem_fail', memory_metrics_name)
        self.assertIn('baremetal_memory_ecc_uncorr_err',
                      memory_metrics_name)
        self.assertIn('baremetal_memory_mirrored', memory_metrics_name)
        self.assertIn('baremetal_mem_ecc_warning', memory_metrics_name)
        self.assertIn('baremetal_memory_b', memory_metrics_name)
        self.assertIn('baremetal_memory_a', memory_metrics_name)
        self.assertIn('baremetal_memory_usb_over_current',
                      memory_metrics_name)
        self.assertIn('baremetal_memory_post_pkg_repair',
                      memory_metrics_name)
        self.assertIn('baremetal_memory_spared', memory_metrics_name)

        ipmi.prometheus_format(memory_category_info,
                               self.metric_registry,
                               memory_metrics_name)
        self.assertEqual(None, self.metric_registry.get_sample_value(
            'baremetal_mem_ecc_warning',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'Mem ECC Warning (0x1b)'}
        ))
        self.assertEqual(1.0, self.metric_registry.get_sample_value(
            'baremetal_memory_post_pkg_repair',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'POST Pkg Repair (0x45)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_idpt_mem_fail',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'iDPT Mem Fail (0x2b)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_memory_spared',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'Memory Spared (0x11)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_memory_mirrored',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'Memory Mirrored (0x12)'}
        ))
        self.assertEqual(None, self.metric_registry.get_sample_value(
            'baremetal_memory_usb_over_current',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'USB Over-current (0x1d)'}
        ))
        self.assertEqual(1.0, self.metric_registry.get_sample_value(
            'baremetal_memory_ecc_uncorr_err',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'ECC Uncorr Err (0x2)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_memory_b',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '32.1 (Memory Device)',
             'sensor_id': 'B  (0xd6)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_memory_a',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '32.1 (Memory Device)',
             'sensor_id': 'A  (0xca)'}
        ))
        self.assertEqual(1.0, self.metric_registry.get_sample_value(
            'baremetal_memory_ecc_corr_err',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'ECC Corr Err (0x1)'}
        ))

    def test_power_parser(self):
        power_category_info = ipmi.CATEGORY_PARAMS['power'].copy()
        power_category_info['data'] = \
            self.node_message['payload']['Power'].copy()
        power_category_info['node_name'] = self.node_name
        power_category_info['node_uuid'] = self.node_uuid
        power_category_info['instance_uuid'] = self.instance_uuid

        power_metrics_name = ipmi.metric_names(power_category_info)
        self.assertEqual(len(power_metrics_name), 2)
        self.assertIn('baremetal_power_ps_redundancy', power_metrics_name)
        self.assertIn('baremetal_power_status', power_metrics_name)

        ipmi.prometheus_format(power_category_info,
                               self.metric_registry,
                               power_metrics_name)
        self.assertEqual(None, self.metric_registry.get_sample_value(
            'baremetal_power_ps_redundancy',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'sensor_id': 'PS Redundancy (0x77)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_power_status', {'node_name': self.node_name,
                                       'sensor_id': 'Status (0x86)',
                                       'node_uuid': self.node_uuid,
                                       'instance_uuid': self.instance_uuid,
                                       'entity_id': '10.2 (Power Supply)'}))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_power_status', {'node_name': self.node_name,
                                       'sensor_id': 'Status (0x85)',
                                       'node_uuid': self.node_uuid,
                                       'instance_uuid': self.instance_uuid,
                                       'entity_id': '10.1 (Power Supply)'}))

    def test_watchdog2_parser(self):
        watchdog2_category_info = ipmi.CATEGORY_PARAMS['watchdog2'].copy()
        watchdog2_category_info['data'] = \
            self.node_message['payload']['Watchdog2'].copy()
        watchdog2_category_info['node_name'] = self.node_name
        watchdog2_category_info['node_uuid'] = self.node_uuid
        watchdog2_category_info['instance_uuid'] = self.instance_uuid

        watchdog2_metrics_name = ipmi.metric_names(watchdog2_category_info)
        self.assertEqual(len(watchdog2_metrics_name), 2)
        self.assertIn('baremetal_os_watchdog_time', watchdog2_metrics_name)
        self.assertIn('baremetal_os_watchdog', watchdog2_metrics_name)

        ipmi.prometheus_format(watchdog2_category_info,
                               self.metric_registry,
                               watchdog2_metrics_name)
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_os_watchdog_time',
            {'node_name': self.node_name,
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '34.1 (BIOS)',
             'sensor_id': 'OS Watchdog Time (0x23)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_os_watchdog', {'node_name': self.node_name,
                                      'node_uuid': self.node_uuid,
                                      'instance_uuid': self.instance_uuid,
                                      'entity_id': '7.1 (System Board)',
                                      'sensor_id': 'OS Watchdog (0x71)'}
        ))

    def test_fan_parser(self):
        fan_category_info = ipmi.CATEGORY_PARAMS['fan'].copy()
        fan_category_info['data'] = \
            self.node_message['payload']['Fan'].copy()
        fan_category_info['node_name'] = self.node_name
        fan_category_info['node_uuid'] = self.node_uuid
        fan_category_info['instance_uuid'] = self.instance_uuid

        fan_metrics_name = ipmi.metric_names(fan_category_info)
        self.assertEqual(len(fan_metrics_name), 2)
        self.assertIn('baremetal_fan_redundancy', fan_metrics_name)
        self.assertIn('baremetal_fan_rpm', fan_metrics_name)

        ipmi.prometheus_format(fan_category_info,
                               self.metric_registry,
                               fan_metrics_name)
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_fan_redundancy',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'Fan Redundancy (0x78)'}
        ))
        self.assertEqual(9960.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan4A (0x3b)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(5520.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan1B (0x40)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(5520.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan8B (0x47)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(9360.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan3A (0x3a)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(9360.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan2A (0x39)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(5520.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan6B (0x45)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(9720.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan5A (0x3c)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(5520.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan3B (0x42)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(9360.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan7A (0x3e)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(5520.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan7B (0x46)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(5880.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan4B (0x43)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(9360.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan1A (0x38)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(9360.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan6A (0x3d)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(5520.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan2B (0x41)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(5640.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan5B (0x44)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))
        self.assertEqual(9240.0, self.metric_registry.get_sample_value(
            'baremetal_fan_rpm',
            {'node_name': self.node_name,
             'sensor_id': 'Fan8A (0x3f)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'status': 'ok'}))

    def test_voltage_manager(self):
        voltage_category_info = ipmi.CATEGORY_PARAMS['voltage'].copy()
        voltage_category_info['data'] = \
            self.node_message['payload']['Voltage'].copy()
        voltage_category_info['node_name'] = self.node_name
        voltage_category_info['node_uuid'] = self.node_uuid
        voltage_category_info['instance_uuid'] = self.instance_uuid

        voltage_metrics_name = ipmi.metric_names(voltage_category_info)
        self.assertEqual(len(voltage_metrics_name), 19)
        expected_metrics = [
            'baremetal_voltage_mem_vtt_pg',
            'baremetal_voltage_sw_pg',
            'baremetal_voltage_vsa_pg',
            'baremetal_voltage_vcore_pg',
            'baremetal_voltage_volts',
            'baremetal_voltage_dimm_pg',
            'baremetal_voltage_vsbm_sw_pg',
            'baremetal_voltage_ndc_pg',
            'baremetal_voltage_ps_pg_fail',
            'baremetal_voltage_vccio_pg',
            'baremetal_voltage_vsb_sw_pg',
            'baremetal_voltage_mem_vddq_pg',
            'baremetal_voltage_bp_pg',
            'baremetal_voltage_a_pg',
            'baremetal_voltage_fivr_pg',
            'baremetal_voltage_pvnn_sw_pg',
            'baremetal_voltage_mem_vpp_pg',
            'baremetal_voltage_pfault_fail_safe',
            'baremetal_voltage_b_pg'
        ]
        for metric in expected_metrics:
            self.assertIn(metric, voltage_metrics_name)

        ipmi.prometheus_format(voltage_category_info,
                               self.metric_registry,
                               voltage_metrics_name)
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vddq_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM012 VDDQ PG (0x24)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vddq_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM345 VDDQ PG (0x27)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vddq_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM012 VDDQ PG (0x2e)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vddq_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM345 VDDQ PG (0x31)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_vccio_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'VCCIO PG (0x2a)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_vccio_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'VCCIO PG (0x34)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_pvnn_sw_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'PVNN SW PG (0x11)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_sw_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': '1.8V SW PG (0xe)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_sw_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': '2.5V SW PG (0xf)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_sw_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': '5V SW PG (0x10)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_a_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': '3.3V A PG (0x14)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_bp_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'BP2 PG (0xd)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_bp_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'BP1 PG (0xc)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_bp_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'BP0 PG (0xb)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_ps_pg_fail',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'PS1 PG FAIL (0x9)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_ps_pg_fail',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'PS2 PG FAIL (0xa)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_fivr_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'FIVR PG (0x2c)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_fivr_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'FIVR PG (0x36)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_vsa_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'VSA PG (0x2d)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_vsa_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'VSA PG (0x37)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vtt_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM012 VTT PG (0x26)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vtt_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM345 VTT PG (0x29)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vtt_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM012 VTT PG (0x30)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vtt_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM345 VTT PG (0x33)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_vsbm_sw_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'VSBM SW PG (0x13)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_b_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': '3.3V B PG (0x15)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_vsb_sw_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'VSB11 SW PG (0x12)'}
        ))

        self.assertEqual(208.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_volts',
            {'node_name': self.node_name,
             'entity_id': '10.2 (Power Supply)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'Voltage 2 (0x6e)',
             'status': 'ok'}
        ))
        self.assertEqual(208.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_volts',
            {'node_name': self.node_name,
             'entity_id': '10.1 (Power Supply)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'Voltage 1 (0x6d)',
             'status': 'ok'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_ndc_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'NDC PG (0x8)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_vcore_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'VCORE PG (0x35)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_vcore_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'VCORE PG (0x2b)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vpp_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM345 VPP PG (0x32)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vpp_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM012 VPP PG (0x25)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vpp_pg',
            {'node_name': self.node_name,
             'entity_id': '3.2 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM012 VPP PG (0x2f)'}
        ))
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_mem_vpp_pg',
            {'node_name': self.node_name,
             'entity_id': '3.1 (Processor)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'MEM345 VPP PG (0x28)'}
        ))

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_voltage_dimm_pg',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'DIMM PG (0x7)'}
        ))

        self.assertEqual(None, self.metric_registry.get_sample_value(
            'baremetal_voltage_pfault_fail_safe',
            {'node_name': self.node_name,
             'entity_id': '7.1 (System Board)',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'sensor_id': 'Pfault Fail Safe (0x74)'}
        ))

    def test_none_instance_uuid(self):
        sample_file2 = os.path.join(
            os.path.dirname(ironic_prometheus_exporter.__file__),
            'tests', 'json_samples',
            'notification-ipmi-none-instance_uuid.json')
        msg2 = json.load(open(sample_file2))
        self.assertIsNone(msg2['payload']['instance_uuid'])
        valid_labels = ipe_utils.update_instance_uuid(msg2['payload'])
        self.assertEqual(valid_labels['instance_uuid'],
                         msg2['payload']['node_uuid'])

        management_category_info = ipmi.CATEGORY_PARAMS['management'].copy()
        management_category_info['data'] = \
            msg2['payload']['payload']['Management'].copy()
        management_category_info['node_name'] = msg2['payload']['node_name']
        management_category_info['node_uuid'] = msg2['payload']['node_uuid']
        management_category_info['instance_uuid'] = \
            msg2['payload']['instance_uuid']

        management_metrics_name = ipmi.metric_names(management_category_info)
        self.assertEqual(len(management_metrics_name), 1)
        self.assertIn('baremetal_front_led_panel', management_metrics_name)

        ipmi.prometheus_format(management_category_info,
                               self.metric_registry,
                               management_metrics_name)
        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_front_led_panel',
            {'node_name': 'knilab-master-u9',
             'node_uuid': msg2['payload']['node_uuid'],
             'instance_uuid': msg2['payload']['node_uuid'],
             'entity_id': '7.1 (System Board)',
             'sensor_id': 'Front LED Panel (0x23)'}))
