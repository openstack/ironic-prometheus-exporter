import logging
import re

from prometheus_client import Gauge

# NOTE (iurygregory): most of the sensor readings come in the ipmi format
# each type of sensor consider a different range of values that aren't integers
# (eg: 0h, 2eh), 0h will be published as 0 and the other values as 1, this way
# we will be able to create prometheus alerts.
# Documentation: https://www.intel.com/content/www/us/en/servers/ipmi/
# ipmi-second-gen-interface-spec-v2-rev1-1.html

LOG = logging.getLogger(__name__)


def metric_names(payload, prefix, sufix, **kwargs):
    LOG.info('metric_names function called with payload=%s' % str(payload))
    LOG.info('prefix=%s | sufix=%s | kwargs=%s' %
             (prefix, sufix, str(kwargs.items())))

    metric_dic = {}
    extract_unit = kwargs.get('extract_unit')
    special_label = kwargs.get('special_label')
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

        metric_name = re.sub(r'[\W]', '_', prefix + label + sufix)
        if metric_name[0].isdigit():
            metric_name = metric_name.lstrip('0123456789')
        if metric_name in metric_dic:
            metric_dic[metric_name].append(entry)
        else:
            metric_dic[metric_name] = [entry]
    return metric_dic


def extract_labels(entries, payload, node_name):
    """ This function extract the labels to be used by a metric

    If a metric has many entries we add the 'Sensor ID' information as label
    otherwise we will only use the default label that is the 'node_name' and
    'Entity ID'.

    e.g: for Temperature we have two entries for baremetal_temperature_celsius
    metric ('Temp (0x1)' and 'Temp (0x2)') and one entry for 'Inlet Temp (0x5)'
    and other for 'Exhaust Temp (0x6)', this will produce a dictionary where
    the keys are the entries and the values are the respective label to be used
    when writting the metrics in the Prometheus format.
    {'Inlet Temp (0x5)': '{node_name=...}',
     'Exhaust Temp (0x6)': '{node_name=...}',
     'Temp (0x1)': '{node_name=...,sensor=Temp1}',
     'Temp (0x2)': '{node_name=...,sensor=Temp2}'}

    returns: a dictionarty of dictionaries {<entry>: {label_name: label_value}}
    """
    LOG.info('extract_labels function called with: entries=%s | payload=%s | \
             node_name=%s' % (str(entries), str(payload), node_name))
    if len(entries) == 1:
        labels = {'node_name': node_name,
                  'entity_id': payload[entries[0]]['Entity ID']}
        return {entries[0]: labels}
    entries_labels = {}
    for entry in entries:
        try:
            entity_id = payload[entry]['Entity ID']
            sensor_id = payload[entry]['Sensor ID']
            metric_label = {'node_name': node_name,
                            'entity_id': entity_id,
                            'sensor_id': sensor_id}
            entries_labels[entry] = metric_label
        except Exception as e:
            LOG.exception(e)
    return entries_labels


def extract_values(entries, payload, use_ipmi_format=True):
    LOG.info('extract_values function called with: entries=%s | payload=%s |'
             % (str(entries), str(payload)))
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
            LOG.exception(e)
    return values


def prometheus_format(payload, node_name, ipmi_metric_registry,
                      available_metrics, use_ipmi_format):
    for metric in available_metrics:
        entries = available_metrics[metric]
        labels = extract_labels(entries, payload, node_name)
        values = extract_values(entries, payload,
                                use_ipmi_format=use_ipmi_format)
        if all(v is None for v in values.values()):
            continue
        g = Gauge(metric, '', labelnames=labels.get(entries[0]).keys(),
                  registry=ipmi_metric_registry)
        for e in entries:
            if values[e] is None:
                continue
            g.labels(**labels[e]).set(values[e])


CATEGORY_PARAMS = {
    'management': {'prefix': 'baremetal_', 'sufix': '',
                   'extra_params': {}, 'use_ipmi_format': True},
    'temperature': {'prefix': 'baremetal_', 'sufix': '_celsius',
                    'extra_params': {}, 'use_ipmi_format': False},
    'system': {'prefix': 'baremetal_system_', 'sufix': '', 'extra_params': {},
               'use_ipmi_format': True},
    'current': {'prefix': 'baremetal_', 'sufix': '', 'extra_params': {},
                'use_ipmi_format': False},
    'version': {'prefix': 'baremetal_', 'sufix': '', 'extra_params': {},
                'use_ipmi_format': True},
    'memory': {'prefix': 'baremetal_', 'sufix': '',
               'extra_params': {'special_label': 'memory'},
               'use_ipmi_format': True},
    'power': {'prefix': 'baremetal_power_', 'sufix': '', 'extra_params': {},
              'use_ipmi_format': True},
    'watchdog2': {'prefix': 'baremetal_', 'sufix': '', 'extra_params': {},
                  'use_ipmi_format': True},
    'fan': {'prefix': 'baremetal_', 'sufix': '',
            'extra_params': {'extract_unit': True, 'special_label': 'fan'},
            'use_ipmi_format': True}
}


def category_registry(category_name, payload, node_name, ipmi_metric_registry):
    if category_name in CATEGORY_PARAMS:
        prefix = CATEGORY_PARAMS[category_name]['prefix']
        sufix = CATEGORY_PARAMS[category_name]['sufix']
        extra = CATEGORY_PARAMS[category_name]['extra_params']
        available_metrics = metric_names(payload, prefix, sufix, **extra)
        use_ipmi_format = CATEGORY_PARAMS[category_name]['use_ipmi_format']
        prometheus_format(payload, node_name, ipmi_metric_registry,
                          available_metrics, use_ipmi_format)
