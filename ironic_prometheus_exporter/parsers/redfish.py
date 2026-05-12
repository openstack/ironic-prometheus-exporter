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

from ironic_prometheus_exporter.parsers import descriptions
from ironic_prometheus_exporter import utils as ipe_utils


LOG = logging.getLogger(__name__)


HEALTH_MAP = {
    'OK': 0,
    'Warning': 1,
    'Critical': 2
}


def _build_labels(node_message):
    fields = ['node_name', 'node_uuid', 'instance_uuid']
    if not node_message['node_name']:
        fields.remove('node_name')

    labels = {}
    extra = node_message.get('payload', {}).get('Extra', {})

    for k, v in extra.items():
        # Renaming uuid to avoid confusion with another labels.
        if k.lower() == 'uuid':
            labels['redfish_system_uuid'] = v
            continue
        labels[k.lower()] = v

    labels.update({k: node_message[k] for k in fields})

    return labels


def _build_sensor_labels(sensor_labels, sensor_id, sensor_data, ignore_keys):
    for k, v in sensor_data.items():
        if k not in ignore_keys and v is not None:
            sensor_labels[k] = v
    sensor_labels['sensor_id'] = sensor_id
    return sensor_labels


def _extract_sensor_payload(node_message, sensor_type):
    """Extract sensor payload from node message.

    :param node_message: Oslo notification message
    :param sensor_type: Type of sensor (Temperature, Power, Fan, Drive)
    :returns: Sensor payload dictionary
    """
    payload = node_message
    for key in ('payload', sensor_type):
        payload = payload.get(key, {})
    return payload


def _build_generic_sensor_metrics(
        node_message, sensor_type, metrics_builder_fn, ignore_keys=None):
    """Generic function to build sensor metrics from Oslo message.

    :param node_message: Oslo notification message
    :param sensor_type: Type of sensor (Temperature, Power, Fan, Drive)
    :param metrics_builder_fn: Function to build metrics dict from sensor_data
    :param ignore_keys: List of keys to ignore when building sensor labels
    :returns: Dictionary of metrics with (value, labels) tuples
    """
    if ignore_keys is None:
        ignore_keys = []

    payload = _extract_sensor_payload(node_message, sensor_type)
    metrics = collections.defaultdict(list)

    for sensor_id, sensor_data in payload.items():
        try:
            state = sensor_data.get('state')
            if not state:
                LOG.debug('Skipping %s sensor %s: missing state field',
                          sensor_type, sensor_id)
                continue
            if state.lower() != 'enabled':
                LOG.debug('Skipping %s sensor %s: state is %s',
                          sensor_type, sensor_id, state)
                continue

            # Build metrics using the provided function
            sensor_metrics = metrics_builder_fn(sensor_data)
            if sensor_metrics is None:
                continue

            # Build labels
            labels = _build_labels(node_message)
            _build_sensor_labels(labels, sensor_id, sensor_data, ignore_keys)

            # Add metrics to result
            for name, value in sensor_metrics.items():
                metrics[name].append((value, labels))

        except Exception as e:
            LOG.exception('Error processing %s sensor %s: %s',
                          sensor_type, sensor_id, e)
            continue

    return metrics


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
                    # metric instance in form of Prometheus labels example
                    {
                        'node_name': 'kninode',
                        'node_uuid', 'XXX-YYY-ZZZ',
                        'instance_uuid': 'ZZZ-YYY-XXX',
                        'entity_id': 'CPU',
                        'sensor_id': '1'
                    }
                ]
            # baremetal_temperature_status:
                # metric value (0 - OK, 1 - Warning, 2- Critical)
                0,
                # metric labels
                {
                        'node_name': 'kninode',
                        'node_uuid', 'XXX-YYY-ZZZ',
                        'instance_uuid': 'ZZZ-YYY-XXX',
                        'entity_id': 'CPU',
                        'sensor_id': '1'
                }
            ]
        }
    """
    def _build_temp_metrics(sensor_data):
        physical_context = sensor_data.get('physical_context')
        reading_celsius = sensor_data.get('reading_celsius')
        health = sensor_data.get('health')

        if not physical_context:
            LOG.debug('Missing physical_context in temperature sensor')
            return None
        if reading_celsius is None:
            LOG.debug('Missing reading_celsius in temperature sensor')
            return None

        metric_name = 'baremetal_temp_%s_celsius' % physical_context.lower()
        health_value = HEALTH_MAP.get(health)

        return {
            metric_name: reading_celsius,
            'baremetal_temperature_status': health_value
        }

    return _build_generic_sensor_metrics(
        node_message,
        'Temperature',
        _build_temp_metrics,
        ignore_keys=['reading_celsius']
    )


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
                    # metric value (0 - OK, 1 - Warning, 2- Critical)
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
    def _build_power_metrics(sensor_data):
        health = sensor_data.get('health')
        if not health:
            LOG.debug('Missing health field in power sensor')
            return None
        health_value = HEALTH_MAP.get(health)
        if health_value is None:
            LOG.debug('Unknown health value %s in power sensor', health)
            return None
        return {'baremetal_power_status': health_value}

    return _build_generic_sensor_metrics(
        node_message,
        'Power',
        _build_power_metrics,
        ignore_keys=['last_power_output_watts', 'line_input_voltage']
    )


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
                    # metric value (0 - OK, 1 - Warning, 2- Critical)
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
    def _build_fan_metrics(sensor_data):
        health = sensor_data.get('health')
        if not health:
            LOG.debug('Missing health field in fan sensor')
            return None
        health_value = HEALTH_MAP.get(health)
        if health_value is None:
            LOG.debug('Unknown health value %s in fan sensor', health)
            return None
        return {'baremetal_fan_status': health_value}

    return _build_generic_sensor_metrics(
        node_message,
        'Fan',
        _build_fan_metrics,
        ignore_keys=['reading', 'reading_units']
    )


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
    def _build_drive_metrics(sensor_data):
        health = sensor_data.get('health')
        if not health:
            LOG.debug('Missing health field in drive sensor')
            return None
        health_value = HEALTH_MAP.get(health)
        if health_value is None:
            LOG.debug('Unknown health value %s in drive sensor', health)
            return None
        return {'baremetal_drive_status': health_value}

    return _build_generic_sensor_metrics(
        node_message,
        'Drive',
        _build_drive_metrics,
        ignore_keys=[]
    )


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
            if value is not None:
                gauge.labels(**valid_labels).set(value)
