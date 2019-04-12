import logging
import re

# NOTE (iurygregory): most of the sensor readings come in the ipmi format
# each type of sensor consider a different range of values that aren't integers
# (eg: 0h, 2eh), 0h will be published as 0 and the other values as 1, this way
# we will be able to create prometheus alerts.
# Documentation: https://www.intel.com/content/www/us/en/servers/ipmi/
# ipmi-second-gen-interface-spec-v2-rev1-1.html

LOG = logging.getLogger(__name__)


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
    """ This function extract the labels to be used by a metric

    If a metric has many entries we add the 'Sensor ID' information as label
    otherwise we will only use the default label that is the node name.

    e.g: for Temperature we have two entries for baremetal_temperature_celcius
    metric ('Temp (0x1)' and 'Temp (0x2)') and one entry for 'Inlet Temp (0x5)'
    and other for 'Exhaust Temp (0x6)', this will produce a dictionary where
    the keys are the entries and the values are the respective label to be used
    when writting the metrics in the Prometheus format.
    {'Inlet Temp (0x5)': '{node_name=...}',
     'Exhaust Temp (0x6)': '{node_name=...}',
     'Temp (0x1)': '{node_name=...,sensor=Temp1}',
     'Temp (0x2)': '{node_name=...,sensor=Temp2}'}

    """
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
            LOG.error(e)
    return entries_labels


def extract_values(entries, payload, use_ipmi_format=True):
    values = {}
    for entry in entries:
        try:
            no_values = ['No Reading', 'Disabled']
            if payload[entry]['Sensor Reading'] in no_values:
                values[entry] = None
            else:
                sensor_values = payload[entry]['Sensor Reading'].split()
                if not use_ipmi_format:
                    if not re.search(r'(\d+(\.\d*)?|\.\d+)', sensor_values[0]):
                        raise Exception("No valid value in Sensor Reading")
                    values[entry] = sensor_values[0]
                if len(sensor_values) > 1:
                    values[entry] = sensor_values[0]
                elif sensor_values[0] == "0h":
                    values[entry] = 0
                else:
                    values[entry] = 1
        except Exception as e:
            LOG.error(e)
    return values


def prometheus_format(payload, node_name, available_metrics,
                      use_ipmi_format=True):
    prometheus_info = []
    for metric in available_metrics:
        entries = available_metrics[metric]
        labels = extract_labels(entries, payload, node_name)
        values = extract_values(entries, payload,
                                use_ipmi_format=use_ipmi_format)
        if all(v is None for v in values.values()):
            continue
        prometheus_info.append(add_prometheus_type(metric, 'gauge'))
        for e in entries:
            if values[e] is None:
                continue
            prometheus_info.append("%s%s %s" % (metric, labels[e], values[e]))
    return '\n'.join(prometheus_info)


def management(payload, node_name):
    available_metrics = metric_names(payload, 'baremetal_', '')
    return prometheus_format(payload, node_name, available_metrics)


def temperature(payload, node_name):
    available_metrics = metric_names(payload, 'baremetal_', '_celcius')
    return prometheus_format(payload, node_name, available_metrics,
                             use_ipmi_format=False)


def system(payload, node_name):
    available_metrics = metric_names(payload, 'baremetal_system_', '')
    return prometheus_format(payload, node_name, available_metrics)


def current(payload, node_name):
    available_metrics = metric_names(payload, 'baremetal_', '')
    return prometheus_format(payload, node_name, available_metrics,
                             use_ipmi_format=False)


def version(payload, node_name):
    available_metrics = metric_names(payload, 'baremetal_', '')
    return prometheus_format(payload, node_name, available_metrics)


def memory(payload, node_name):
    available_metrics = metric_names(payload, 'baremetal_', '',
                                     special_label='memory')
    return prometheus_format(payload, node_name, available_metrics)


def power(payload, node_name):
    available_metrics = metric_names(payload, 'baremetal_power_', '')
    return prometheus_format(payload, node_name, available_metrics)


def watchdog2(payload, node_name):
    available_metrics = metric_names(payload, 'baremetal_', '')
    return prometheus_format(payload, node_name, available_metrics)


def fan(payload, node_name):
    available_metrics = metric_names(payload, 'baremetal_', '',
                                     extract_unit=True,
                                     special_label='fan')
    return prometheus_format(payload, node_name, available_metrics)
