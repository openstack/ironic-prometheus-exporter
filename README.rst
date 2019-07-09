Ironic Prometheus Exporter
==========================

Overview
--------
Tool to expose hardware sensor data in the `Prometheus <https://prometheus.io/>`_ format through an HTTP endpoint.

The hardware sensor data come from bare metal machines deployed
using `OpenStack Bare Metal Service (ironic) <https://docs.openstack.org/ironic/latest/>`_.

* License: Apache License, Version 2.0
* Documentation: https://docs.openstack.org/ironic-prometheus-exporter/
* Source: https://opendev.org/openstack/ironic-prometheus-exporter
* Bugs: https://storyboard.openstack.org/#!/project/openstack/ironic-prometheus-exporter


Installation
------------

1 - Install ironic-prometheus-exporter
::

   $ pip install --user ironic-prometheus-exporter

2- Verify if the driver is installed
::

   $ pip install entry_point_inspector --user <user>
   $ epi group show oslo.messaging.notify.drivers


- Output in case of a successful instalation: `prometheus_exporter` is listed in the `Name` column and the `Error` column should be empty.
- Output in case of an unsuccessful instalation: `prometheus_exporter` is listed in the `Name` column and the `Error` column will have more information.


Configuration
-------------

After install the driver you will need to update the `ironic.conf` and add the following information:

::

  [conductor]
  send_sensor_data=true

  [oslo_messaging_notifications]
  driver = prometheus_exporter
  transport_url = fake://
  location=/tmp/ironic_prometheus_exporter



Running exporter application
----------------------------

The Flask Application is responsible to merge all the metrics files present in the directory
set in `[oslo_messaging_notifications]/location`.

.. note:: If you want to deploy in production please check the Flask `documentation <http://flask.pocoo.org/docs/dev/deploying/>`_

To run the Flask Application follow the steps listed below:
1 - open the repository directory
::

   $ cd ironic-prometheus-exporter/

2- set the `FLASK_*` environment variables and the location of the `ironic.conf` file.
::

   $ export IRONIC_CONFIG=/etc/ironic/ironic.conf
   $ export FLASK_APP=ironic_prometheus_exporter/app/exporter.py
   $ export FLASK_RUN_HOST=$HOST_IP
   $ export FLASK_RUN_PORT=5000

3- run the Flask Application
::

$ python -m flask run &


**Running under uWSGI**

Reproduce the Steps 1 and 2 (You don't need to set `FLASK_APP` variable) and run the command below:
::

$ uwsgi --plugin python --http-socket ${FLASK_RUN_HOST}:${FLASK_RUN_PORT} --module ironic_prometheus_exporter.app.wsgi:application


Contributing
------------

* Pull requests: `Gerrit
  <https://review.opendev.org/#/q/project:openstack/ironic-prometheus-exporter>`_
  (see `developer's guide
  <https://docs.openstack.org/infra/manual/developers.html>`_)
* Bugs and RFEs:  `StoryBoard
  <https://storyboard.openstack.org/#!/project/openstack/ironic-prometheus-exporter>`_
  (please do NOT report bugs to Github)
