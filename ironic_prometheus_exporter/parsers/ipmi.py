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
import logging
import pkg_resources
import re

from prometheus_client import Gauge

from ironic_prometheus_exporter import utils as ipe_utils
from ironic_prometheus_exporter.parsers import descriptions


# NOTE (iurygregory): most of the sensor readings come in the ipmi format
# each type of sensor consider a different range of values that aren't integers
# (eg: 0h, 2eh), 0h will be published as 0 and the other values as 1, this way
# we will be able to create prometheus alerts.
# Documentation: https://www.intel.com/content/www/us/en/servers/ipmi/
# ipmi-second-gen-interface-spec-v2-rev1-1.html

LOG = logging.getLogger(__name__)


CATEGORY_PARAMS = {
    'management': {'prefix': 'baremetal_',
                   'sufix': '',
                   'extra_params': {},
                   'use_ipmi_format': True},
    'temperature': {'prefix': 'baremetal_',
                    'sufix': '_celsius',
                    'extra_params': {},
                    'use_ipmi_format': False},
    'system': {'prefix': 'baremetal_system_',
               'sufix': '',
               'extra_params': {},
               'use_ipmi_format': True},
    'current': {'prefix': 'baremetal_',
                'sufix': '',
                'extra_params': {},
                'use_ipmi_format': False},
    'version': {'prefix': 'baremetal_',
                'sufix': '',
                'extra_params': {},
                'use_ipmi_format': True},
    'memory': {'prefix': 'baremetal_',
               'sufix': '',
               'extra_params': {'special_label': 'memory'},
               'use_ipmi_format': True},
    'power': {'prefix': 'baremetal_power_',
              'sufix': '',
              'extra_params': {},
              'use_ipmi_format': True},
    'watchdog2': {'prefix': 'baremetal_',
                  'sufix': '',
                  'extra_params': {},
                  'use_ipmi_format': True},
    'fan': {'prefix': 'baremetal_',
            'sufix': '',
            'extra_params': {'extract_unit': True, 'special_label': 'fan'},
            'use_ipmi_format': True},
    'voltage': {'prefix': 'baremetal_voltage_',
                'sufix': '',
                'extra_params': {'extract_unit': True,
                                 'special_label': 'voltage'},
                'use_ipmi_format': True}
}


IPMI_JSON = pkg_resources.resource_filename(__name__,
                                            "metrics_information/ipmi.json")
IPMI_METRICS_DESCRIPTION = json.load(open(IPMI_JSON))


def metric_names(category_info):
    metric_dic = {}
    extract_unit = category_info.get('extra_params').get('extract_unit')
    special_label = category_info.get('extra_params').get('special_label')
    payload = category_info['data']
    for entry in payload:
        if special_label == 'fan':
            # NOTE (iurygregory): regex to remove a sequence of numbers and
            # letters that comes after the fan sensor name.
            # e.g: 'Fan4B (0x43)' will be 'fan (0x43)'
            #      'Fan Redundancy (0x78)' will be 'fan redundancy (0x78)'
            e = re.sub(r'fan\d*[a-z]*', 'fan', entry.lower())
            # NOTE (iurygregory): regex to remove brackets and their content
            # e.g: 'fan (0x43)' will turn into ['fan']
            #      'fan redundancy (0x78)' will turn into ['fan', 'redundancy']
            e = re.sub(r'\(.*\)', '', e).split()
            label = '_'.join(e)
        elif special_label == 'voltage':
            # NOTE (iurygregory): regex to remove Voltage value from sensor_id
            # e.g: '3.3V B PG (0x15)' will be 'b pg (0x15)'
            #      '5V SW PG (0x10)' will be 'sw pg (0x10)'
            e = re.sub(r'([\d+]v)|([\d+].[\d*]v)', '', entry.lower())
            # NOTE (iurygregory): regex to remove all numbers
            # e.g: 'Voltage 1 (0x6d)' will turn into ['voltage', '(xd)']
            e = re.sub(r'[\d]+', '', e).lower().split()
            label = '_'.join(e[:-1]).replace('-', '_')
            if label in category_info['prefix']:
                label = ''
        else:
            # NOTE (iurygregory): regex to remove all numbers
            e = re.sub(r'[\d]+', '', entry).lower().split()
            label = '_'.join(e[:-1]).replace('-', '_')

        unit = ''
        if extract_unit and payload[entry]['Sensor Reading'] != 'No Reading':
            sensor_read = payload[entry]['Sensor Reading'].split()
            if len(sensor_read) > 1:
                unit = '_' + sensor_read[-1].lower()

        if special_label == 'memory':
            if 'mem' not in label and 'memory' not in label:
                label = 'memory_' + label

        prefix = category_info['prefix']
        sufix = category_info['sufix']
        metric_name = re.sub(r'[\W]', '_', prefix + label + sufix + unit)
        metric_name = re.sub(r'[_]+', '_', metric_name)
        if metric_name[0].isdigit():
            metric_name = metric_name.lstrip('0123456789')
        if metric_name in metric_dic:
            metric_dic[metric_name].append(entry)
        else:
            metric_dic[metric_name] = [entry]
    return metric_dic


def extract_labels(entries, category_info):
    """ This function extract the labels to be used by a metric

    If a metric has many entries we add the 'Sensor ID' information as label
    otherwise we will only use the default label that is the 'node_name' and
    'Entity ID'.

    e.g: for Temperature we have two entries for baremetal_temperature_celsius
    metric ('Temp (0x1)' and 'Temp (0x2)') and one entry for 'Inlet Temp (0x5)'
    and other for 'Exhaust Temp (0x6)', this will produce a dictionary where
    the keys are the entries and the values are the respective label to be used
    when writing the metrics in the Prometheus format.
    {'Inlet Temp (0x5)': '{node_name=...}',
     'Exhaust Temp (0x6)': '{node_name=...}',
     'Temp (0x1)': '{node_name=...,sensor=Temp1}',
     'Temp (0x2)': '{node_name=...,sensor=Temp2}'}

    returns: a dictionary of dictionaries {<entry>: {label_name: label_value}}
    """
    if len(entries) == 1:
        status = category_info['data'][entries[0]].get('Status')
        labels = {'node_name': category_info['node_name'],
                  'node_uuid': category_info['node_uuid'],
                  'instance_uuid': category_info['instance_uuid'],
                  'entity_id': category_info['data'][entries[0]]['Entity ID'],
                  'sensor_id': category_info['data'][entries[0]]['Sensor ID']}
        if status:
            labels['status'] = status
        return {entries[0]: labels}
    entries_labels = {}
    for entry in entries:
        try:
            entity_id = category_info['data'][entry]['Entity ID']
            sensor_id = category_info['data'][entry]['Sensor ID']
            status = category_info['data'][entry].get('Status')
            metric_label = {'node_name': category_info['node_name'],
                            'node_uuid': category_info['node_uuid'],
                            'instance_uuid': category_info['instance_uuid'],
                            'entity_id': entity_id,
                            'sensor_id': sensor_id}
            if status:
                metric_label['status'] = status
            entries_labels[entry] = metric_label
        except Exception as e:
            LOG.exception(e)
    return entries_labels


def extract_values(entries, category_info):
    values = {}
    for entry in entries:
        try:
            no_values = ['No Reading', 'Disabled']
            if category_info['data'][entry]['Sensor Reading'] in no_values:
                values[entry] = None
            else:
                sensor_values = (category_info['data'][entry]
                                 ['Sensor Reading'].split())
                if not category_info['use_ipmi_format']:
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


def prometheus_format(category_info, ipmi_metric_registry, available_metrics):
    for metric in available_metrics:
        entries = available_metrics[metric]
        labels = extract_labels(entries, category_info)
        values = extract_values(entries, category_info)
        if all(v is None for v in values.values()):
            continue
        desc = descriptions.get_metric_description('ipmi', metric)
        g = Gauge(metric, desc,
                  labelnames=list(labels.get(entries[0])),
                  registry=ipmi_metric_registry)
        for e in entries:
            if values[e] is None:
                continue
            valid_labels = ipe_utils.update_instance_uuid(labels[e])
            g.labels(**valid_labels).set(values[e])


def category_registry(node_message, ipmi_metric_registry):
    for ipmi_category in node_message['payload']:
        if ipmi_category.lower() in CATEGORY_PARAMS:
            category_dict = CATEGORY_PARAMS[ipmi_category.lower()].copy()
            category_dict['data'] = node_message['payload'][ipmi_category]
            category_dict['node_name'] = node_message['node_name']
            category_dict['node_uuid'] = node_message['node_uuid']
            category_dict['instance_uuid'] = node_message['instance_uuid']
            available_metrics = metric_names(category_dict)
            prometheus_format(category_dict, ipmi_metric_registry,
                              available_metrics)
