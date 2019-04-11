import re

# NOTE (iurygregory): most of the sensor readings come in the ipmi format
# each type of sensor consider a different range of values that aren't integers
# (eg: 0h, 2eh), 0h will be published as 0 and the other values as 1, this way
# we will be able to create prometheus alerts.
# Documentation: https://www.intel.com/content/www/us/en/servers/ipmi/
# ipmi-second-gen-interface-spec-v2-rev1-1.html


def add_prometheus_type(name, metric_type):
    return '# TYPE %s %s' % (name, metric_type)


def metric_names(payload, prefix, sufix, extract_unit=False,
                 special_label=None):
    metric_dic = {}
    for entry in payload:
        if special_label == 'fan':
            e = re.sub(r'[\d].*$', '', entry.lower())
            e = re.sub(r'[\(\)]', '', e).split()
            label = '_'.join(e)
        else:
            e = re.sub(r"[\d]+", "", entry).lower().split()
            label = '_'.join(e[:-1]).replace('-', '_')

        if extract_unit:
            sensor_read = payload[entry]['Sensor Reading'].split()
            if len(sensor_read) > 1:
                sufix = '_' + sensor_read[-1].lower()

        if special_label == 'memory':
            if 'mem' not in label and 'memory' not in label:
                label = 'memory_' + label

        metric_name = prefix + label + sufix
        if metric_name in metric_dic:
            metric_dic[metric_name].append(entry)
        else:
            metric_dic[metric_name] = [entry]
    return metric_dic


def extract_labels(entries, payload, node_name):
    default_label = 'node_name="%s"' % node_name
    if len(entries) == 1:
        return {entries[0]: '{%s}' % default_label}
    entries_labels = {}
    for entry in entries:
        try:
            sensor = payload[entry]['Sensor ID'].split()
            sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
            metric_label = [default_label,
                            'sensor="%s"' % (sensor[0] + sensor_id)]
            entries_labels[entry] = '{%s}' % ','.join(metric_label)
        except Exception as e:
            print(e)
    return entries_labels


def extract_values(entries, payload):
    values = {}
    for entry in entries:
        try:
            no_values = ['No Reading', 'Disabled']
            if payload[entry]['Sensor Reading'] in no_values:
                values[entry] = None
            else:
                sensor_values = payload[entry]['Sensor Reading'].split()
                if len(sensor_values) > 1:
                    values[entry] = sensor_values[0]
                elif sensor_values[0] == "0h":
                    values[entry] = 0
                else:
                    values[entry] = 1
        except Exception as e:
            print(e)
    return values


class Management(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = metric_names(self.payload, 'baremetal_', '')

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = extract_labels(entries, self.payload, self.node_name)
            values = extract_values(entries, self.payload)
            for e in entries:
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class Temperature(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def _extract_values(self, entries):
        entries_values = {}
        for entry in entries:
            try:
                value = self.payload[entry]['Sensor Reading'].split()
                if not re.search(r'(\d+(\.\d*)?|\.\d+)', value[0]):
                    raise Exception("No valid value in Sensor Reading")
                entries_values[entry] = value[0]
            except Exception as e:
                print(e)
        return entries_values

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = metric_names(self.payload, 'baremetal_',
                                         '_celcius')

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = extract_labels(entries, self.payload, self.node_name)
            values = self._extract_values(entries)
            for e in entries:
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class System(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = metric_names(self.payload, 'baremetal_system_', '')

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = extract_labels(entries, self.payload, self.node_name)
            values = extract_values(entries, self.payload)
            for e in entries:
                if values[e] is None:
                    continue
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class Current(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def _extract_values(self, entries):
        entries_values = {}
        for entry in entries:
            try:
                value = self.payload[entry]['Sensor Reading'].split()
                if not re.search(r'(\d+(\.\d*)?|\.\d+)', value[0]):
                    raise Exception("No valid value in Sensor Reading")
                entries_values[entry] = value[0]
            except Exception as e:
                print(e)
        return entries_values

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = metric_names(self.payload, 'baremetal_', '', True)

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = extract_labels(entries, self.payload, self.node_name)
            values = self._extract_values(entries)
            for e in entries:
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class Version(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = metric_names(self.payload, 'baremetal_', '')

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = extract_labels(entries, self.payload, self.node_name)
            values = extract_values(entries, self.payload)
            for e in entries:
                if values[e] is None:
                    continue
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class Memory(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = metric_names(self.payload, 'baremetal_', '',
                                         special_label='memory')

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = extract_labels(entries, self.payload, self.node_name)
            values = extract_values(entries, self.payload)
            for e in entries:
                if values[e] is None:
                    continue
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class Power(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = metric_names(self.payload, 'baremetal_power_', '')

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = extract_labels(entries, self.payload, self.node_name)
            values = extract_values(entries, self.payload)
            for e in entries:
                if values[e] is None:
                    continue
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class Watchdog2(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = metric_names(self.payload, 'baremetal_', '')

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = extract_labels(entries, self.payload, self.node_name)
            values = extract_values(entries, self.payload)
            for e in entries:
                if values[e] is None:
                    continue
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class Fan(object):
    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = metric_names(self.payload, 'baremetal_', '',
                                         extract_unit=True,
                                         special_label='fan')

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = extract_labels(entries, self.payload, self.node_name)
            values = extract_values(entries, self.payload)
            for e in entries:
                if values[e] is None:
                    continue
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)
