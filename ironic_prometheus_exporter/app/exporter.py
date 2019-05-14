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
