import configparser
import logging
import os

from flask import abort, Flask
app = Flask(__name__)
LOG = logging.getLogger(__name__)


@app.route('/metrics', methods=['GET'])
def prometheus_metrics():
    try:
        config = configparser.ConfigParser()
        config.read(os.environ.get('IRONIC_CONFIG'))
        DIR = config['oslo_messaging_notifications']['location']
    except Exception as e:
        LOG.error(e)
        abort(404)

    all_files = [os.path.join(DIR, name) for name in os.listdir(DIR)
                 if os.path.isfile(os.path.join(DIR, name))]
    content = ''
    for file_name in all_files:
        with open(file_name, 'r') as file:
            content += ''.join(file.readlines())
    return app.response_class(content, mimetype='text/plain')


if __name__ == '__main__':
    app.run()
