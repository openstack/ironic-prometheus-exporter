from ironic_prometheus_exporter.parsers import ipmi


class ParserManager(object):

    def __init__(self, data):
        self.driver_information = []
        if data['event_type'] == 'hardware.ipmi.metrics':
            self.driver_information = self._ipmi_driver(data)

    def _ipmi_driver(self, data):
        node_name = data['payload']['node_name']
        payload = data['payload']['payload']
        ipmi_information = []
        for category in payload:
            if hasattr(ipmi, category.lower()):
                category_output = getattr(ipmi, category.lower())(
                    payload[category], node_name)
                ipmi_information.append(category_output)
        return ipmi_information

    def merge_information(self):
        info = ''
        for obj in self.driver_information:
            info += obj + '\n'
        return info.rstrip('\n')
