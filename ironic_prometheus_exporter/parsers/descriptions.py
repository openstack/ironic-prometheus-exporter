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
import os
import pkg_resources

DESCRIPTIONS = {}

LOG = logging.getLogger(__name__)


def get_metric_description(source, metric_name):
    if source not in DESCRIPTIONS:
        try:
            json_file = pkg_resources.resource_filename(
                __name__, os.path.join(
                    'metrics_information', source + '.json'))

            with open(json_file) as fl:
                DESCRIPTIONS[source] = json.load(fl)

        except Exception as exc:
            LOG.warning(
                'Failed to load metrics descriptions '
                'for metrics source %s: %s', source, exc)

    return DESCRIPTIONS.get(source, {}).get(metric_name, '')
