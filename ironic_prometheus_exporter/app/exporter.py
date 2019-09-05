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

import configparser
import logging
import os

from flask import abort, Flask, Response
application = Flask(__name__)
LOG = logging.getLogger(__name__)


@application.route('/metrics', methods=['GET'])
def prometheus_metrics():
    try:
        config = configparser.ConfigParser()
        config.read(os.environ.get('IRONIC_CONFIG'))
        DIR = config['oslo_messaging_notifications']['location']
    except Exception:
        LOG.error('Unexpected error')
        abort(500)

    all_files = [os.path.join(DIR, name) for name in os.listdir(DIR)
                 if os.path.isfile(os.path.join(DIR, name))]

    def merge_content():
        for file_name in all_files:
            with open(file_name, 'r') as file:
                yield file.read()
    return Response(merge_content(), mimetype='text/plain')


if __name__ == '__main__':
    application.run()
