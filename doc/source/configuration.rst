Configuration
=============

To enable the ironic-prometheus-exporter to collect the sensor data from
Ironic, it's necessary to enable some configuration parameters in the
``ironic.conf``.
Below you can see an example of the required configuration, the table
:ref:`ipe_conf` shows all the available configuration options.


Example of configuration

.. code-block:: ini

    [oslo_messaging_notifications]
    driver = prometheus_exporter
    transport_url = fake://
    location = /opt/stack/node_metrics

    [sensor_data]
    send_sensor_data = true
    interval = 600

    [metrics]
    backend = collector


.. _ipe_conf:

.. list-table:: Configuration options for the ironic-prometheus-exporter
   in Ironic
   :widths: 15 15 10 50 10
   :header-rows: 1

   * - Section
     - Setting
     - Value
     - Description
     - Required
   * - sensor_data
     - send_sensor_data
     - true
     - Enable sending sensor data message via the notification bus.
     - ``Yes``
   * - sensor_data
     - interval
     - 600 (``default``)
     - Seconds between conductor sending sensor data message via the
       notification bus.
     - No
   * - sensor_data
     - enable_for_undeployed_nodes
     - false (``default``)
     - When set to true, the conductor will collect sensor
       information from all nodes when sensor data collection is
       enabled via the ``send_sensor_data`` setting.
     - No
   * - metrics
     - backend
     - collector
     - When set to collector, the metrics system collects metrics
       data and saves it in memory for use by the running
       application and emits to the configured
       ``oslo_messaging_notifications`` notification bus
       when sensor data collection is enabled via the
       ``send_sensor_data`` setting.
     - ``Yes``
   * - oslo_messaging_notifications
     - driver
     - prometheus_exporter
     - The Drivers(s) to handle sending notifications.
     - ``Yes``
   * - oslo_messaging_notifications
     - transport_url
     - fake://
     - A URL representing the messaging driver to use for notifications.
       If not set, we fall back to the same configuration used for RPC.
     - ``Yes``
   * - oslo_messaging_notifications
     - location
     - <dir_path>
     - Directory where the files will be written.
     - ``Yes``


.. note::
   After doing the modifications in the ``ironic.conf`` don't forget to
   re-start the ironic-conductor service

.. note::
   You can find additional ``[sensor_data]`` and ``[metrics]`` options
   in the `Ironic sample config`_

.. _Ironic sample config: https://docs.openstack.org/ironic/latest/configuration/sample-config.html
