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

import logging

from prometheus_client import Gauge


LOG = logging.getLogger(__name__)


def category_registry(message, metrics_registry):
    """Parse ironic metrics and submit them to Prometheus

    :param node_message: Oslo notification message
    :param metrics_registry: Prometheus registry
    """

    hostname = message.get('hostname')
    payload = message.get('payload')
    service = 'ironic'
    for key in payload.keys():
        value = payload[key]
        metric_type = value['type']
        driver = None
        labels = {'hostname': hostname,
                  'service': service}

        if key.startswith('ironic.api'):
            # This is only *really* to be expected in a combined single
            # process mode, or if someone is using the exporter coupled
            # with the API service itself.
            formatted_key = key.replace(
                'ironic.api.controllers.',
                'ironic_rest_api_')
            labels['component'] = 'api'

        if key.startswith('ironic.drivers.modules'):
            # Deconstruct driver entries/counters to be more sane and attach
            # labeling to them.

            # TODO(TheJulia): Once the minimum python version is 3.9, change
            # to str.removeprefix.
            formatted_key = key.replace(
                'ironic.drivers.modules.',
                'ironic.')

            for driver_label in ['ipmi', 'redfish', 'agent', 'pxe',
                                 'ilo', 'drac', 'irmc', 'inspector', 'ansible',
                                 'ibmc', 'xclarity']:
                if driver_label in key:
                    # since Dell's driver name doesn't match the code
                    # classpath drac, driver name is idrac.
                    driver = driver_label
            # NOTE(TheJulia): WRT, drac, Technically this should be idrac

            # To have the names of the metrics make sense, we need to handle
            # structural folder names in the file/driver structure, which
            # varies from driver to driver.
            for driver_dir in ['redfish', 'ipmi', 'network', 'storage', 'drac',
                               'ilo', 'irmc', 'intel_ipmi', 'ansible', 'ibmc',
                               'xclarity']:
                if driver_dir in formatted_key:
                    formatted_key = formatted_key.replace(
                        f'.{driver_dir}.', '.')
                    # Everything here should be one and done...
                    # Famous. Last. Words.
                    break

            # Now remove the filenames. This is extraineous ironic internal
            # structural information where the classes are housed, not the
            # actual methods or class names.
            for filename in ['boot', 'raid', 'power', 'bios', 'inspect',
                             'management', 'agent_base', 'agent_client',
                             'agent', 'deploy_utils', 'deploy', 'ipmitool',
                             'pxe_base', 'pxe', 'ramdisk', 'vendor_passthru',
                             'vendor']:
                if filename in formatted_key:
                    formatted_key = formatted_key.replace(f'.{filename}.', '.')
                    break

            labels['component'] = 'driver'
            labels['driver'] = driver

        if key.startswith('ironic.conductor'):
            # Catches entries from:
            # - ironic.conductor.manager
            # - ironic.conductor.deployments
            # TODO(TheJulia): Once the minimum python version is 3.9, change
            # to str.removeprefix.
            labels['component'] = 'conductor'

            formatted_key = key.replace('ironic.conductor.manager.', 'ironic_')
            for filename in ['manager', 'deployments', 'allocations']:
                if filename in key:
                    formatted_key = key.replace(f'conductor.{filename}', '')
                    break

        # Prometheus does not use dot delimited data structures
        # so we need to rename it to be underscore delimited.
        # Downside of this is we end up with things like double
        # underscores from method names, but it should be still clear
        # where something is coming from.
        # i.e.
        # In: ironic.conductor.manager.ConductorManager.do_sync_power_state
        # Out: ironic_conductormanager_do_sync_power_state

        formatted_key = formatted_key.replace('.', '_')
        if '__' in formatted_key:
            # Remove entries introduced via private methods with metrics
            # decorators defined on them.
            formatted_key = formatted_key.replace('__', '_')
        formatted_key = formatted_key.lower()
        # Remove ConductorManager, because it gets confusing as that is the
        # Internal class name

        LOG.debug(f'Creating metric {key} using {formatted_key}.')

        # Always process timer first. The bulk of our Metrics in Ironic
        # are timer counters.
        if metric_type == 'timer':
            # NOTE(TheJulia): So this doesn't use the promethus_client
            # histogram format as it requires the existence of sample buckets
            # inside of it's data structure or the entry of individual
            # instances into the running history.
            # Instead, we will return two counters, a sum and count gauge,
            # Hopefully this will be useful. The reason it is not just
            # two counter values, is each counter value in prometheus_client
            # gets a _created child sample, which creates a lot of confusion.
            LOG.debug(f'Details of the metric {formatted_key} with labels '
                      '{labels}, sum: %s, count: %s', value['sum'],
                      value['count'])
            metric = Gauge(formatted_key + '_time', 'Total time (ms) spent.',
                           labelnames=list(labels.keys()),
                           registry=metrics_registry)
            metric.labels(**labels).set(value['sum'])
            metric = Gauge(formatted_key + '_call_count',
                           'Sum of calls recorded.',
                           labelnames=list(labels.keys()),
                           registry=metrics_registry)
            metric.labels(**labels).set(value['count'])
            LOG.debug(f'Details of the metric {formatted_key} with labels '
                      '{labels}, sum: %s, count: %s', value['sum'],
                      value['count'])
            next

        elif metric_type == 'gauge':
            metric = Gauge(formatted_key, 'Point in time count of data point.',
                           labelnames=list(labels.keys()),
                           registry=metrics_registry)
            metric.labels(**labels).set(value['value'])
            LOG.debug(f'Details of the metric {formatted_key} with labels '
                      '{labels}, value: %s', value['value'])

        elif metric_type == 'counter':
            # NOTE(TheJulia): We use a gauge instead of of a counter because
            # the prometheus client library automatcially renames our value
            # by adding _total to it, and adds a _created child sample value
            # which is just the time. Unfortunately the later is just noise.
            metric = Gauge(formatted_key,
                           'Counter representing the method or data point.',
                           labelnames=list(labels.keys()),
                           registry=metrics_registry)
            # Prometheus_client doesn't directly expose a counter method
            # to set a counter value directly.
            metric.labels(**labels).set(value['count'])
            LOG.debug(f'Details of the metric {formatted_key} with labels '
                      '{labels}, value: %s', value['count'])
