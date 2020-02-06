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

import collections
import logging

from prometheus_client import Gauge

from ironic_prometheus_exporter import utils as ipe_utils
from ironic_prometheus_exporter.parsers import descriptions


LOG = logging.getLogger(__name__)


def _build_labels(node_message):
    return {
        k: node_message[k]
        for k in ('node_name', 'node_uuid', 'instance_uuid')
    }


def build_temperature_metrics(node_message):
    """Build Prometheus temperature metrics from Oslo message.

    Takes Oslo notification message carrying Redfish sensor data and
    produces a data structure suitable for submitting to Prometheus.

    :param node_message: Oslo notification message

    Examples::

        .. code-block:: python

        {
            # metric name
            'baremetal_temp_cpu_celsius':
                [
                    # metric value
                    42,
                    # metric instance in form of Prometheus labels
                    {
                        'node_name': 'kninode',
                        'node_uuid', 'XXX-YYY-ZZZ',
                        'instance_uuid': 'ZZZ-YYY-XXX',
                        'entity_id': 'CPU',
                        'sensor_id': '1'
                    }
                ]
            ]
        }
    """
    payload = node_message

    for key in ('payload', 'Temperature'):
        payload = payload.get(key, {})

    metrics = collections.defaultdict(list)

    for sensor_id, sensor_data in payload.items():
        metric = 'baremetal_temp_%s_celsius' % (
            sensor_data['physical_context'].lower())

        labels = _build_labels(node_message)

        labels['entity_id'] = sensor_data['physical_context']
        labels['sensor_id'] = sensor_data['sensor_number']

        value = sensor_data['reading_celsius']

        metrics[metric].append((value, labels))

    return metrics


def build_power_metrics(node_message):
    """Build Prometheus power metrics from Oslo message.

    Takes Oslo notification message carrying Redfish sensor data and
    produces a data structure suitable for submitting to Prometheus.

    :param node_message: Oslo notification message

    Examples::

        .. code-block:: python

        {
            # metric name
            'baremetal_power_status':
                [
                    # metric value (0 - OK, 1 - on fire)
                    0,
                    # metric instance in form of Prometheus labels
                    {
                        'node_name': 'kninode',
                        'node_uuid', 'XXX-YYY-ZZZ',
                        'instance_uuid': 'ZZZ-YYY-XXX',
                        'entity_id': 'PSU',
                        'sensor_id': '0:Power@ZZZ-YYY-XXX'
                    }
                ]
            ]
        }
    """
    payload = node_message

    for key in ('payload', 'Power'):
        payload = payload.get(key, {})

    metrics = collections.defaultdict(list)

    for sensor_id, sensor_data in payload.items():
        metric = 'baremetal_power_status'

        labels = _build_labels(node_message)

        labels['entity_id'] = 'PSU'
        labels['sensor_id'] = sensor_id

        value = sensor_data['health'] != 'OK' and 1 or 0

        metrics[metric].append((value, labels))

    return metrics


def build_fan_metrics(node_message):
    """Build Prometheus fan metrics from Oslo message.

    Takes Oslo notification message carrying Redfish sensor data and
    produces a data structure suitable for submitting to Prometheus.

    :param node_message: Oslo notification message

    Examples::

        .. code-block:: python

        {
            # metric name
            'baremetal_fan_status':
                [
                    # metric value (0 - OK, 1 - on fire)
                    0,
                    # metric instance in form of Prometheus labels
                    {
                        'node_name': 'kninode',
                        'node_uuid', 'XXX-YYY-ZZZ',
                        'instance_uuid': 'ZZZ-YYY-XXX',
                        'entity_id': 'CPU',
                        'sensor_id': '0:Power@ZZZ-YYY-XXX'
                    }
                ]
            ]
        }
    """
    payload = node_message

    for key in ('payload', 'Fan'):
        payload = payload.get(key, {})

    metrics = collections.defaultdict(list)

    for sensor_id, sensor_data in payload.items():
        metric = 'baremetal_fan_status'

        labels = _build_labels(node_message)

        labels['entity_id'] = sensor_data['physical_context']
        labels['sensor_id'] = sensor_data['identity']

        value = sensor_data['health'] != 'OK' and 1 or 0

        metrics[metric].append((value, labels))

    return metrics


def build_drive_metrics(node_message):
    """Build Prometheus drive metrics from Oslo message.

    Takes Oslo notification message carrying Redfish sensor data and
    produces a data structure suitable for submitting to Prometheus.

    :param node_message: Oslo notification message

    Examples::

        .. code-block:: python

        {
            # metric name
            'baremetal_drive_status':
                [
                    # metric value (0 - OK, 1 - on fire)
                    0,
                    # metric instance in form of Prometheus labels
                    {
                        'node_name': 'kninode',
                        'node_uuid', 'XXX-YYY-ZZZ',
                        'instance_uuid': 'ZZZ-YYY-XXX',
                        'entity_id': 'HDD',
                        'sensor_id': '32ADF365C6C1B7BD'
                    }
                ]
            ]
        }
    """
    payload = node_message

    for key in ('payload', 'Drive'):
        payload = payload.get(key, {})

    metrics = collections.defaultdict(list)

    for sensor_id, sensor_data in payload.items():
        metric = 'baremetal_drive_status'

        labels = _build_labels(node_message)

        labels['entity_id'] = 'HDD'
        labels['sensor_id'] = sensor_id

        value = sensor_data['health'] != 'OK' and 1 or 0

        metrics[metric].append((value, labels))

    return metrics


def category_registry(node_message, metrics_registry):
    """Parse Redfish metrics and submit them to Prometheus

    :param node_message: Oslo notification message
    :param metrics_registry: Prometheus registry
    """
    metrics = build_temperature_metrics(node_message)
    metrics.update(build_power_metrics(node_message))
    metrics.update(build_fan_metrics(node_message))
    metrics.update(build_drive_metrics(node_message))

    for metric, details in metrics.items():

        LOG.debug('Creating metric %s', metric)
        LOG.debug('Details of the metric: %s', details)
        # details is a list of tuples that contains 2 elements (value, labels)
        # let's get the first tuple and the dict of labels to extract the
        # list of labels necessary for the Gauge
        metric_labels = details[0][1]
        desc = descriptions.get_metric_description('redfish', metric)
        gauge = Gauge(metric, desc, labelnames=list(metric_labels),
                      registry=metrics_registry)

        for value, labels in details:
            valid_labels = ipe_utils.update_instance_uuid(labels)
            gauge.labels(**valid_labels).set(value)
