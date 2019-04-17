import json
import unittest

from ironic_prometheus_exporter.parsers import ipmi, manager


DATA = json.load(open('./ironic_prometheus_exporter/tests/data.json'))


class TestPayloadsParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']

    def test_management_parser(self):
        management_metrics_name = ipmi.metric_names(self.payload['Management'],
                                                    'baremetal_', '')
        self.assertEqual(len(management_metrics_name), 1)
        self.assertIn('baremetal_front_led_panel', management_metrics_name)
        management_parser = ipmi.category('management',
                                          self.payload['Management'],
                                          self.node_name)
        self.assertEqual(len(management_parser.split('\n')), 2)

    def test_temperature_parser(self):
        temperature_metrics_name = ipmi.metric_names(
            self.payload['Temperature'], 'baremetal_', '_celcius')
        self.assertEqual(len(temperature_metrics_name), 3)
        self.assertIn('baremetal_temp_celcius', temperature_metrics_name)
        self.assertIn('baremetal_exhaust_temp_celcius',
                      temperature_metrics_name)
        self.assertIn('baremetal_inlet_temp_celcius', temperature_metrics_name)

        temperature_parser = ipmi.category('temperature',
                                           self.payload['Temperature'],
                                           self.node_name)
        self.assertEqual(len(temperature_parser.split('\n')), 7)

    def test_system_parser(self):
        system_metrics_name = ipmi.metric_names(self.payload['System'],
                                                'baremetal_system_', '')
        self.assertEqual(len(system_metrics_name), 2)
        self.assertIn('baremetal_system_unknown', system_metrics_name)
        self.assertIn('baremetal_system_post_err', system_metrics_name)

        system_parser = ipmi.category('system', self.payload['System'],
                                      self.node_name)
        self.assertEqual(len(system_parser.split('\n')), 2)

    def test_current_parser(self):
        current_metrics_name = ipmi.metric_names(self.payload['Current'],
                                                 'baremetal_', '')
        self.assertEqual(len(current_metrics_name), 2)
        self.assertIn('baremetal_current', current_metrics_name)
        self.assertIn('baremetal_pwr_consumption', current_metrics_name)

        current_parser = ipmi.category('current', self.payload['Current'],
                                       self.node_name)
        self.assertEqual(len(current_parser.split('\n')), 5)

    def test_version_parser(self):
        version_metrics_name = ipmi.metric_names(self.payload['Version'],
                                                 'baremetal_', '')
        self.assertEqual(len(version_metrics_name), 3)
        self.assertIn('baremetal_tpm_presence', version_metrics_name)
        self.assertIn('baremetal_hdwr_version_err', version_metrics_name)
        self.assertIn('baremetal_chassis_mismatch', version_metrics_name)

        version_parser = ipmi.category('version', self.payload['Version'],
                                       self.node_name)
        self.assertEqual(len(version_parser.split('\n')), 4)

    def test_memory_parser(self):
        memory_metrics_name = ipmi.metric_names(self.payload['Memory'],
                                                'baremetal_', '',
                                                **{'special_label': 'memory'})
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

        memory_parser = ipmi.category('memory', self.payload['Memory'],
                                      self.node_name)
        self.assertEqual(len(memory_parser.split('\n')), 16)

    def test_power_parser(self):
        power_metrics_name = ipmi.metric_names(self.payload['Power'],
                                               'baremetal_power_', '')
        self.assertEqual(len(power_metrics_name), 2)
        self.assertIn('baremetal_power_ps_redundancy', power_metrics_name)
        self.assertIn('baremetal_power_status', power_metrics_name)

        power_parser = ipmi.category('power', self.payload['Power'],
                                     self.node_name)
        self.assertEqual(len(power_parser.split('\n')), 3)

    def test_watchdog2_parser(self):
        watchdog2_metrics_name = ipmi.metric_names(self.payload['Watchdog2'],
                                                   'baremetal_', '')
        self.assertEqual(len(watchdog2_metrics_name), 2)
        self.assertIn('baremetal_os_watchdog_time', watchdog2_metrics_name)
        self.assertIn('baremetal_os_watchdog', watchdog2_metrics_name)

        watchdog_parser = ipmi.category('watchdog2', self.payload['Watchdog2'],
                                        self.node_name)
        self.assertEqual(len(watchdog_parser.split('\n')), 4)

    def test_fan_parser(self):
        fan_metrics_name = ipmi.metric_names(self.payload['Fan'], 'baremetal_',
                                             '', **{'extract_unit': True,
                                                    'special_label': 'fan'})
        self.assertEqual(len(fan_metrics_name), 2)
        self.assertIn('baremetal_fan_redundancy_rpm', fan_metrics_name)
        self.assertIn('baremetal_fan_rpm', fan_metrics_name)

        fan_parser = ipmi.category('fan', self.payload['Fan'], self.node_name)
        self.assertEqual(len(fan_parser.split('\n')), 19)


class TestIpmiManager(unittest.TestCase):

    def test_manager(self):
        node_manager = manager.ParserManager(DATA)
        node_metrics = node_manager.merge_information()
        self.assertEqual(len(node_metrics.split('\n')), 62)
