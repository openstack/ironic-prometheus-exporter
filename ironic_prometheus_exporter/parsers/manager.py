from ironic_prometheus_exporter.parsers import ipmi


class ParserManager(object):

    def __init__(self, data):

        node_name = data['payload']['node_name']
        payload = data['payload']['payload']
        self.ipmi_objects = [
            ipmi.Management(payload['Management'], node_name),
            ipmi.Temperature(payload['Temperature'], node_name),
            ipmi.System(payload['System'], node_name),
            ipmi.Current(payload['Current'], node_name),
            ipmi.Version(payload['Version'], node_name),
            ipmi.Memory(payload['Memory'], node_name),
            ipmi.Power(payload['Power'], node_name),
            ipmi.Watchdog2(payload['Watchdog2'], node_name),
            ipmi.Fan(payload['Fan'], node_name)
        ]

    def merge_information(self):
        info = ''
        for obj in self.ipmi_objects:
            info += obj.prometheus_format() + '\n'
        return info.rstrip('\n')
