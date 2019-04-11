import json
import unittest

from ironic_prometheus_exporter.parsers import ipmi, manager


DATA = json.load(open('./ironic_prometheus_exporter/tests/data.json'))


class TestPayloadManagementParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']['Management']

    def test_parser(self):
        management_parser = ipmi.Management(self.payload, self.node_name)
        metrics = management_parser.prometheus_format()
        self.assertEqual(len(metrics.split('\n')), 2)


class TestPayloadTemperatureParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']['Temperature']

    def test_parser(self):
        temperature_parser = ipmi.Temperature(self.payload, self.node_name)
        metrics = temperature_parser.prometheus_format()
        self.assertEqual(len(metrics.split('\n')), 7)


class TestPayloadSystemParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']['System']

    def test_parser(self):
        system_parser = ipmi.System(self.payload, self.node_name)
        metrics = system_parser.prometheus_format()
        self.assertEqual(len(metrics.split('\n')), 3)


class TestPayloadCurrentParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']['Current']

    def test_parser(self):
        current_parser = ipmi.Current(self.payload, self.node_name)
        metrics = current_parser.prometheus_format()
        self.assertEqual(len(metrics.split('\n')), 5)


class TestPayloadVersionParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']['Version']

    def test_parser(self):
        version_parser = ipmi.Version(self.payload, self.node_name)
        metrics = version_parser.prometheus_format()
        self.assertEqual(len(metrics.split('\n')), 5)


class TestPayloadMemoryParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']['Memory']

    def test_parser(self):
        memory_parser = ipmi.Memory(self.payload, self.node_name)
        metrics = memory_parser.prometheus_format()
        self.assertEqual(len(metrics.split('\n')), 18)


class TestPayloadPowerParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']['Power']

    def test_parser(self):
        power_parser = ipmi.Power(self.payload, self.node_name)
        metrics = power_parser.prometheus_format()
        self.assertEqual(len(metrics.split('\n')), 4)


class TestPayloadWatchdog2Parser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']['Watchdog2']

    def test_parser(self):
        watchdog_parser = ipmi.Watchdog2(self.payload, self.node_name)
        metrics = watchdog_parser.prometheus_format()
        self.assertEqual(len(metrics.split('\n')), 4)


class TestPayloadFanParser(unittest.TestCase):

    def setUp(self):
        self.node_name = DATA['payload']['node_name']
        self.payload = DATA['payload']['payload']['Fan']

    def test_parser(self):
        fan_parser = ipmi.Fan(self.payload, self.node_name)
        metrics = fan_parser.prometheus_format()
        self.assertEqual(len(metrics.split('\n')), 19)


class TestIpmiManager(unittest.TestCase):

    def test_manager(self):
        node_manager = manager.ParserManager(DATA)
        node_metrics = node_manager.merge_information()
        self.assertEqual(len(node_metrics.split('\n')), 67)
