Configuration
=============

To enable the ironic-prometheus-exporter to collect the sensor data from Ironic,
it's necessary to enable some configuration parameters in the ``ironic.conf``.
Below you can see an example of the required configuration, the table
:ref:`ipe_conf` shows all the available configuration options.


Example of configuration

.. code-block:: ini

    [conductor]
    send_sensor_data = true
    send_sensor_data_interval = 300

    [oslo_messaging_notifications]
    driver = prometheus_exporter
    transport_url = fake://
    location = /opt/stack/node_metrics



.. _ipe_conf:

.. list-table:: Configuration options for the ironic-prometheus-exporter in Ironic
   :widths: 15 15 10 50 10
   :header-rows: 1

   * - Section
     - Setting
     - Value
     - Description
     - Required
   * - conductor
     - send_sensor_data
     - true
     - Enable sending sensor data message via the notification bus.
     - ``Yes``
   * - conductor
     - send_sensor_data_interval
     - 600 (`default`)
     - Seconds between conductor sending sensor data message via the
       notification bus.
     - ``Yes``
   * - conductor
     - send_sensor_data_for_undeployed_nodes
     - false (`default`)
     - When set to true, the conductor will collect sensor information from
       all nodes when sensor data collection is enabled via the
       ``send_sensor_data``  setting.
     - No
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
   After doing the modifications in the ``ironic.conf`` don't forget to re-start
   the ironic-conductor service
