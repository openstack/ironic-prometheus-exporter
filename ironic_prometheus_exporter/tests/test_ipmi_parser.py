import json
import unittest

from ironic_prometheus_exporter.parsers import ipmi
from prometheus_client import CollectorRegistry


DATA = json.load(open('./ironic_prometheus_exporter/tests/data.json'))


class TestPayloadsParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.node_uuid = DATA['payload']['node_uuid']
        self.instance_uuid = DATA['payload']['instance_uuid']
        self.timestamp = DATA['payload']['timestamp']
        self.payload = DATA['payload']['payload']
        self.metric_registry = CollectorRegistry()

    def test_management_parser(self):
        prefix = ipmi.CATEGORY_PARAMS['management']['prefix']
        sufix = ipmi.CATEGORY_PARAMS['management']['sufix']
        extra = ipmi.CATEGORY_PARAMS['management']['extra_params']
        ipmi_format = ipmi.CATEGORY_PARAMS['management']['use_ipmi_format']

        management_metrics_name = ipmi.metric_names(self.payload['Management'],
                                                    prefix, sufix, **extra)
        self.assertEqual(len(management_metrics_name), 1)
        self.assertIn('baremetal_front_led_panel', management_metrics_name)

        ipmi.prometheus_format(self.payload['Management'], self.node_name,
                               self.node_uuid, self.instance_uuid,
                               self.metric_registry,
                               management_metrics_name, ipmi_format)

        self.assertEqual(0.0, self.metric_registry.get_sample_value(
            'baremetal_front_led_panel',
            {'node_name': 'knilab-master-u9',
             'node_uuid': self.node_uuid,
             'instance_uuid': self.instance_uuid,
             'entity_id': '7.1 (System Board)',
             'sensor_id': 'Front LED Panel (0x23)'}))

    def test_temperature_parser(self):
        prefix = ipmi.CATEGORY_PARAMS['temperature']['prefix']
        sufix = ipmi.CATEGORY_PARAMS['temperature']['sufix']
        extra = ipmi.CATEGORY_PARAMS['temperature']['extra_params']
        ipmi_format = ipmi.CATEGORY_PARAMS['temperature']['use_ipmi_format']
        temperature_metrics_name = ipmi.metric_names(
            self.payload['Temperature'], prefix, sufix, **extra)
        self.assertEqual(len(temperature_metrics_name), 3)
        self.assertIn('baremetal_temp_celsius', temperature_metrics_name)
        self.assertIn('baremetal_exhaust_temp_celsius',
                      temperature_metrics_name)
        self.assertIn('baremetal_inlet_temp_celsius', temperature_metrics_name)

        ipmi.prometheus_format(self.payload['Temperature'], self.node_name,
                               self.node_uuid, self.instance_uuid,
                               self.metric_registry,
                               temperature_metrics_name, ipmi_format)
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
        prefix = ipmi.CATEGORY_PARAMS['system']['prefix']
        sufix = ipmi.CATEGORY_PARAMS['system']['sufix']
        extra = ipmi.CATEGORY_PARAMS['system']['extra_params']
        ipmi_format = ipmi.CATEGORY_PARAMS['system']['use_ipmi_format']
        system_metrics_name = ipmi.metric_names(self.payload['System'],
                                                prefix, sufix, **extra)
        self.assertEqual(len(system_metrics_name), 2)
        self.assertIn('baremetal_system_unknown', system_metrics_name)
        self.assertIn('baremetal_system_post_err', system_metrics_name)

        ipmi.prometheus_format(self.payload['System'], self.node_name,
                               self.node_uuid, self.instance_uuid,
                               self.metric_registry,
                               system_metrics_name, ipmi_format)
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
        prefix = ipmi.CATEGORY_PARAMS['current']['prefix']
        sufix = ipmi.CATEGORY_PARAMS['current']['sufix']
        extra = ipmi.CATEGORY_PARAMS['current']['extra_params']
        ipmi_format = ipmi.CATEGORY_PARAMS['current']['use_ipmi_format']
        current_metrics_name = ipmi.metric_names(self.payload['Current'],
                                                 prefix, sufix, **extra)
        self.assertEqual(len(current_metrics_name), 2)
        self.assertIn('baremetal_current', current_metrics_name)
        self.assertIn('baremetal_pwr_consumption', current_metrics_name)

        ipmi.prometheus_format(self.payload['Current'], self.node_name,
                               self.node_uuid, self.instance_uuid,
                               self.metric_registry,
                               current_metrics_name, ipmi_format)
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
        prefix = ipmi.CATEGORY_PARAMS['version']['prefix']
        sufix = ipmi.CATEGORY_PARAMS['version']['sufix']
        extra = ipmi.CATEGORY_PARAMS['version']['extra_params']
        ipmi_format = ipmi.CATEGORY_PARAMS['version']['use_ipmi_format']

        version_metrics_name = ipmi.metric_names(self.payload['Version'],
                                                 prefix, sufix, **extra)
        self.assertEqual(len(version_metrics_name), 3)
        self.assertIn('baremetal_tpm_presence', version_metrics_name)
        self.assertIn('baremetal_hdwr_version_err', version_metrics_name)
        self.assertIn('baremetal_chassis_mismatch', version_metrics_name)

        ipmi.prometheus_format(self.payload['Version'], self.node_name,
                               self.node_uuid, self.instance_uuid,
                               self.metric_registry,
                               version_metrics_name, ipmi_format)
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
        prefix = ipmi.CATEGORY_PARAMS['memory']['prefix']
        sufix = ipmi.CATEGORY_PARAMS['memory']['sufix']
        extra = ipmi.CATEGORY_PARAMS['memory']['extra_params']
        ipmi_format = ipmi.CATEGORY_PARAMS['memory']['use_ipmi_format']
        memory_metrics_name = ipmi.metric_names(self.payload['Memory'], prefix,
                                                sufix, **extra)

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

        ipmi.prometheus_format(self.payload['Memory'], self.node_name,
                               self.node_uuid, self.instance_uuid,
                               self.metric_registry,
                               memory_metrics_name, ipmi_format)

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
        prefix = ipmi.CATEGORY_PARAMS['power']['prefix']
        sufix = ipmi.CATEGORY_PARAMS['power']['sufix']
        extra = ipmi.CATEGORY_PARAMS['power']['extra_params']
        ipmi_format = ipmi.CATEGORY_PARAMS['power']['use_ipmi_format']
        power_metrics_name = ipmi.metric_names(self.payload['Power'], prefix,
                                               sufix, **extra)
        self.assertEqual(len(power_metrics_name), 2)
        self.assertIn('baremetal_power_ps_redundancy', power_metrics_name)
        self.assertIn('baremetal_power_status', power_metrics_name)

        ipmi.prometheus_format(self.payload['Power'], self.node_name,
                               self.node_uuid, self.instance_uuid,
                               self.metric_registry,
                               power_metrics_name, ipmi_format)

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
        prefix = ipmi.CATEGORY_PARAMS['watchdog2']['prefix']
        sufix = ipmi.CATEGORY_PARAMS['watchdog2']['sufix']
        extra = ipmi.CATEGORY_PARAMS['watchdog2']['extra_params']
        ipmi_format = ipmi.CATEGORY_PARAMS['watchdog2']['use_ipmi_format']
        watchdog2_metrics_name = ipmi.metric_names(self.payload['Watchdog2'],
                                                   prefix, sufix, **extra)
        self.assertEqual(len(watchdog2_metrics_name), 2)
        self.assertIn('baremetal_os_watchdog_time', watchdog2_metrics_name)
        self.assertIn('baremetal_os_watchdog', watchdog2_metrics_name)

        ipmi.prometheus_format(self.payload['Watchdog2'], self.node_name,
                               self.node_uuid, self.instance_uuid,
                               self.metric_registry,
                               watchdog2_metrics_name, ipmi_format)

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
        prefix = ipmi.CATEGORY_PARAMS['fan']['prefix']
        sufix = ipmi.CATEGORY_PARAMS['fan']['sufix']
        extra = ipmi.CATEGORY_PARAMS['fan']['extra_params']
        ipmi_format = ipmi.CATEGORY_PARAMS['fan']['use_ipmi_format']
        fan_metrics_name = ipmi.metric_names(self.payload['Fan'], prefix,
                                             sufix, **extra)

        self.assertEqual(len(fan_metrics_name), 2)
        self.assertIn('baremetal_fan_redundancy', fan_metrics_name)
        self.assertIn('baremetal_fan_rpm', fan_metrics_name)

        ipmi.prometheus_format(self.payload['Fan'], self.node_name,
                               self.node_uuid, self.instance_uuid,
                               self.metric_registry,
                               fan_metrics_name, ipmi_format)

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
