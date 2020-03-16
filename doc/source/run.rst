Running the exporter Application
================================

The exporter application is a Flask Application responsible to merge
all the metrics files present in the directory set in
``[oslo_messaging_notifications]/location``.

The prometheus community defined the port of the Ironic Prometheus Exporter
application as ``9608`` (see `Default port allocations
<https://github.com/prometheus/prometheus/wiki/Default-port-allocations>`_),
but you can choose any port for your deployment.

The application needs to have access to the ``ironic.conf``, you need to set
the ``IRONIC_CONFIG`` environment variable to the absolute path of the file.

We will explain how you can run the application in a development environment
and in production environment.

Development Environment
-----------------------

To run the Flask Application follow the steps listed below:

#. Set the ``FLASK_*`` environment variables and the location of the
   ``ironic.conf`` file.::

   $ export IRONIC_CONFIG=/etc/ironic/ironic.conf
   $ export FLASK_APP=ironic_prometheus_exporter/app/exporter.py
   $ export FLASK_RUN_HOST=<ip address>
   $ export FLASK_RUN_PORT=9608

#. Run the Flask Application::

   $ python -m flask run

Production Environment
----------------------

To deploy the application in production you can use any application server, we
will be using `gunicorn <https://gunicorn.org/#docs>`_ since it's what we use
in our CI.

The command to execute the application using gunicorn is:
::

   $ gunicorn3 -b <ip_address>:9608 \
     --env IRONIC_CONFIG=$IRONIC_CONFIG \
     --env FLASK_DEBUG=1 -w 4 \
     --access-logfile=ipe_access.log \
     --error-logfile=ipe_errors.log \
     -D ironic_prometheus_exporter.app.wsgi:application

You can find more information about how to deploy a Flask application in
production in the `Flask documentation
<http://flask.pocoo.org/docs/dev/deploying/>`_.
