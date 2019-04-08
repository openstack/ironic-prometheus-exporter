import re

# NOTE (iurygregory): most of the sensor readings come in the ipmi format
# each type of sensor consider a different range of values that aren't integers
# (eg: 0h, 2eh), 0h will be published as 0 and the other values as 1, this way
# we will be able to create prometheus alerts.
# Documentation: https://www.intel.com/content/www/us/en/servers/ipmi/
# ipmi-second-gen-interface-spec-v2-rev1-1.html


def add_prometheus_type(name, metric_type):
    return '# TYPE %s %s' % (name, metric_type)


class Management(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def _metric_names(self):
        prefix = 'baremetal_'
        metric_dic = {}
        for entry in self.payload:
            e = entry.lower().split()
            label = '_'.join(e[:-1])
            metric_name = prefix + label
            if metric_name in metric_dic:
                metric_dic[metric_name].append(entry)
            else:
                metric_dic[metric_name] = [entry]
        return metric_dic

    def _extract_labels(self, entries):
        deafult_label = 'node_name="%s"' % self.node_name
        if len(entries) == 1:
            return {entries[0]: '{%s}' % deafult_label}
        entries_labels = {}
        for entry in entries:
            try:
                sensor = self.payload[entry]['Sensor ID'].split()
                sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
                metric_label = [deafult_label,
                                'sensor="%s"' % (sensor[0] + sensor_id)]
                entries_labels[entry] = '{%s}' % ','.join(metric_label)
            except Exception as e:
                print(e)
        return entries_labels

    def _extract_values(self, entries):
        entries_values = {}
        for entry in entries:
            try:
                if self.payload[entry]['Sensor Reading'] == "0h":
                    entries_values[entry] = 0
                else:
                    entries_values[entry] = 1
            except Exception as e:
                print(e)
        return entries_values

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = self._metric_names()

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = self._extract_labels(entries)
            values = self._extract_values(entries)
            for e in entries:
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class Temperature(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def _metric_names(self):
        prefix = 'baremetal_'
        sufix = 'temp_celcius'
        metric_dic = {}
        for entry in self.payload:
            e = entry.split()[0]
            label = e.lower()
            metric_name = prefix + sufix
            if label not in sufix:
                metric_name = prefix + label + "_" + sufix
            if metric_name in metric_dic:
                metric_dic[metric_name].append(entry)
            else:
                metric_dic[metric_name] = [entry]
        return metric_dic

    def _extract_labels(self, entries):
        deafult_label = 'node_name="%s"' % self.node_name
        if len(entries) == 1:
            return {entries[0]: '{%s}' % deafult_label}
        entries_labels = {}
        for entry in entries:
            try:
                sensor = self.payload[entry]['Sensor ID'].split()
                sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
                metric_label = [deafult_label,
                                'sensor="%s"' % (sensor[0] + sensor_id)]
                entries_labels[entry] = '{%s}' % ','.join(metric_label)
            except Exception as e:
                print(e)
        return entries_labels

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
        available_metrics = self._metric_names()

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = self._extract_labels(entries)
            values = self._extract_values(entries)
            for e in entries:
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class System(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def _metric_names(self):
        prefix = 'baremetal_system_'
        metric_dic = {}
        for entry in self.payload:
            e = entry.lower().split()
            label = '_'.join(e[:-1])
            metric_name = prefix + label
            if metric_name in metric_dic:
                metric_dic[metric_name].append(entry)
            else:
                metric_dic[metric_name] = [entry]
        return metric_dic

    def _extract_labels(self, entries):
        deafult_label = 'node_name="%s"' % self.node_name
        if len(entries) == 1:
            return {entries[0]: '{%s}' % deafult_label}
        entries_labels = {}
        for entry in entries:
            try:
                sensor = self.payload[entry]['Sensor ID'].split()
                sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
                metric_label = [deafult_label,
                                'sensor="%s"' % (sensor[0] + sensor_id)]
                entries_labels[entry] = '{%s}' % ','.join(metric_label)
            except Exception as e:
                print(e)
        return entries_labels

    def _extract_values(self, entries):
        entries_values = {}
        for entry in entries:
            try:
                if self.payload[entry]['Sensor Reading'] == 'No Reading':
                    entries_values[entry] = None
                else:
                    if self.payload[entry]['Sensor Reading'] == "0h":
                        entries_values[entry] = 0
                    else:
                        entries_values[entry] = 1
            except Exception as e:
                print(e)
        return entries_values

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = self._metric_names()

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = self._extract_labels(entries)
            values = self._extract_values(entries)
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

    def _metric_names(self):
        prefix = 'baremetal_'
        metric_dic = {}
        for entry in self.payload:
            e = re.sub(r'[\d]', '', entry.lower()).split()
            label = '_'.join(e[:-1])
            sufix = '_' + self.payload[entry]['Sensor Reading'].split()[-1]
            metric_name = prefix + label + sufix.lower()
            if metric_name in metric_dic:
                metric_dic[metric_name].append(entry)
            else:
                metric_dic[metric_name] = [entry]
        return metric_dic

    def _extract_labels(self, entries):
        deafult_label = 'node_name="%s"' % self.node_name
        if len(entries) == 1:
            return {entries[0]: '{%s}' % deafult_label}
        entries_labels = {}
        for entry in entries:
            try:
                sensor = self.payload[entry]['Sensor ID'].split()
                sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
                metric_label = [deafult_label,
                                'sensor="%s"' % (sensor[0] + sensor_id)]
                entries_labels[entry] = '{%s}' % ','.join(metric_label)
            except Exception as e:
                print(e)
        return entries_labels

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
        available_metrics = self._metric_names()

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = self._extract_labels(entries)
            values = self._extract_values(entries)
            for e in entries:
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)


class Version(object):

    def __init__(self, payload, node_name):
        self.payload = payload
        self.node_name = node_name

    def _metric_names(self):
        prefix = 'baremetal_'
        metric_dic = {}
        for entry in self.payload:
            e = entry.lower().split()
            label = '_'.join(e[:-1])
            metric_name = prefix + label
            if metric_name in metric_dic:
                metric_dic[metric_name].append(entry)
            else:
                metric_dic[metric_name] = [entry]
        return metric_dic

    def _extract_labels(self, entries):
        deafult_label = 'node_name="%s"' % self.node_name
        if len(entries) == 1:
            return {entries[0]: '{%s}' % deafult_label}
        entries_labels = {}
        for entry in entries:
            try:
                sensor = self.payload[entry]['Sensor ID'].split()
                sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
                metric_label = [deafult_label,
                                'sensor="%s"' % (sensor[0] + sensor_id)]
                entries_labels[entry] = '{%s}' % ','.join(metric_label)
            except Exception as e:
                print(e)
        return entries_labels

    def _extract_values(self, entries):
        entries_values = {}
        for entry in entries:
            try:
                if self.payload[entry]['Sensor Reading'] == 'No Reading':
                    entries_values[entry] = None
                else:
                    if self.payload[entry]['Sensor Reading'] == "0h":
                        entries_values[entry] = 0
                    else:
                        entries_values[entry] = 1
            except Exception as e:
                print(e)
        return entries_values

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = self._metric_names()

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = self._extract_labels(entries)
            values = self._extract_values(entries)
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

    def _metric_names(self):
        prefix = 'baremetal_'
        metric_dic = {}
        for entry in self.payload:
            e = entry.lower().split()
            label = '_'.join(e[:-1])
            if 'memory' not in label:
                label = 'memory_' + label
            metric_name = prefix + label.replace('-', '_')
            if metric_name in metric_dic:
                metric_dic[metric_name].append(entry)
            else:
                metric_dic[metric_name] = [entry]
        return metric_dic

    def _extract_labels(self, entries):
        deafult_label = 'node_name="%s"' % self.node_name
        if len(entries) == 1:
            return {entries[0]: '{%s}' % deafult_label}
        entries_labels = {}
        for entry in entries:
            try:
                sensor = self.payload[entry]['Sensor ID'].split()
                sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
                metric_label = [deafult_label,
                                'sensor="%s"' % (sensor[0] + sensor_id)]
                entries_labels[entry] = '{%s}' % ','.join(metric_label)
            except Exception as e:
                print(e)
        return entries_labels

    def _extract_values(self, entries):
        entries_values = {}
        for entry in entries:
            try:
                if self.payload[entry]['Sensor Reading'] == 'No Reading':
                    entries_values[entry] = None
                else:
                    if self.payload[entry]['Sensor Reading'] == "0h":
                        entries_values[entry] = 0
                    else:
                        entries_values[entry] = 1
            except Exception as e:
                print(e)
        return entries_values

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = self._metric_names()

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = self._extract_labels(entries)
            values = self._extract_values(entries)
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

    def _metric_names(self):
        prefix = 'baremetal_power_'
        metric_dic = {}
        for entry in self.payload:
            e = entry.lower().split()
            label = '_'.join(e[:-1])
            metric_name = prefix + label.replace('-', '_')
            if metric_name in metric_dic:
                metric_dic[metric_name].append(entry)
            else:
                metric_dic[metric_name] = [entry]
        return metric_dic

    def _extract_labels(self, entries):
        deafult_label = 'node_name="%s"' % self.node_name
        if len(entries) == 1:
            return {entries[0]: '{%s}' % deafult_label}
        entries_labels = {}
        for entry in entries:
            try:
                sensor = self.payload[entry]['Sensor ID'].split()
                sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
                metric_label = [deafult_label,
                                'sensor="%s"' % (sensor[0] + sensor_id)]
                entries_labels[entry] = '{%s}' % ','.join(metric_label)
            except Exception as e:
                print(e)
        return entries_labels

    def _extract_values(self, entries):
        entries_values = {}
        for entry in entries:
            try:
                no_values = ['No Reading', 'Disabled']
                if self.payload[entry]['Sensor Reading'] in no_values:
                    entries_values[entry] = None
                else:
                    if self.payload[entry]['Sensor Reading'] == "0h":
                        entries_values[entry] = 0
                    else:
                        entries_values[entry] = 1
            except Exception as e:
                print(e)
        return entries_values

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = self._metric_names()

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = self._extract_labels(entries)
            values = self._extract_values(entries)
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

    def _metric_names(self):
        prefix = 'baremetal_'
        metric_dic = {}
        for entry in self.payload:
            e = entry.lower().split()
            label = '_'.join(e[:-1])
            metric_name = prefix + label.replace('-', '_')
            if metric_name in metric_dic:
                metric_dic[metric_name].append(entry)
            else:
                metric_dic[metric_name] = [entry]
        return metric_dic

    def _extract_labels(self, entries):
        deafult_label = 'node_name="%s"' % self.node_name
        if len(entries) == 1:
            return {entries[0]: '{%s}' % deafult_label}
        entries_labels = {}
        for entry in entries:
            try:
                sensor = self.payload[entry]['Sensor ID'].split()
                sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
                metric_label = [deafult_label,
                                'sensor="%s"' % (sensor[0] + sensor_id)]
                entries_labels[entry] = '{%s}' % ','.join(metric_label)
            except Exception as e:
                print(e)
        return entries_labels

    def _extract_values(self, entries):
        entries_values = {}
        for entry in entries:
            try:
                no_values = ['No Reading', 'Disabled']
                if self.payload[entry]['Sensor Reading'] in no_values:
                    entries_values[entry] = None
                else:
                    if self.payload[entry]['Sensor Reading'] == "0h":
                        entries_values[entry] = 0
                    else:
                        entries_values[entry] = 1
            except Exception as e:
                print(e)
        return entries_values

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = self._metric_names()

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = self._extract_labels(entries)
            values = self._extract_values(entries)
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

    def _metric_names(self):
        prefix = 'baremetal_'
        metric_dic = {}
        for entry in self.payload:
            sufix = ''
            e = re.sub(r'[\d].*$', '', entry.lower())
            e = re.sub(r'[\(\)]', '', e).split()
            label = '_'.join(e)
            label_unit = self.payload[entry]['Sensor Reading'].split()
            if len(label_unit) > 1:
                sufix = '_' + label_unit[-1].lower()
            metric_name = prefix + label.replace('-', '_') + sufix
            if metric_name in metric_dic:
                metric_dic[metric_name].append(entry)
            else:
                metric_dic[metric_name] = [entry]
        return metric_dic

    def _extract_labels(self, entries):
        deafult_label = 'node_name="%s"' % self.node_name
        if len(entries) == 1:
            return {entries[0]: '{%s}' % deafult_label}
        entries_labels = {}
        for entry in entries:
            try:
                sensor = self.payload[entry]['Sensor ID'].split()
                sensor_id = str(int(re.sub(r'[\(\)]', '', sensor[-1]), 0))
                metric_label = [deafult_label,
                                'sensor="%s"' % (sensor[0] + sensor_id)]
                entries_labels[entry] = '{%s}' % ','.join(metric_label)
            except Exception as e:
                print(e)
        return entries_labels

    def _extract_values(self, entries):
        entries_values = {}
        for entry in entries:
            try:
                no_values = ['No Reading', 'Disabled']
                if self.payload[entry]['Sensor Reading'] in no_values:
                    entries_values[entry] = None
                else:
                    values = self.payload[entry]['Sensor Reading'].split()
                    if len(values) > 1:
                        entries_values[entry] = values[0]
                    elif values[0] == "0h":
                        entries_values[entry] = 0
                    else:
                        entries_values[entry] = 1
            except Exception as e:
                print(e)
        return entries_values

    def prometheus_format(self):
        prometheus_info = []
        available_metrics = self._metric_names()

        for metric in available_metrics:
            prometheus_info.append(add_prometheus_type(metric, 'gauge'))
            entries = available_metrics[metric]
            labels = self._extract_labels(entries)
            values = self._extract_values(entries)
            for e in entries:
                if values[e] is None:
                    continue
                prometheus_info.append("%s%s %s" % (metric, labels[e],
                                                    values[e]))
        return '\n'.join(prometheus_info)
