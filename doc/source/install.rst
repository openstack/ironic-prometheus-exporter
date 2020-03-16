Installation
============

Pre-Requisites
--------------

Before installing the exporter you need to have Ironic already installed,
to know about the limitations check :doc:`limitations`

Supported OS:

* CentOS/RHEL 8
* Ubuntu Bionic


Ironic Prometheus Exporter Installation
---------------------------------------

The ironic-prometheus-exporter is available as pip package and as rpm package
on RDO.

#. Package Installation

   #. Using pip::

      $ pip install --user ironic-prometheus-exporter


   #. Using rpm from RDO::

      $ dnf install -y python3-ironic-prometheus-exporter

#. Verify the Installation::

   $ pip install entry_point_inspector --user <user>
   $ epi group show oslo.messaging.notify.drivers

- Output in case of a successful installation: `prometheus_exporter` is listed in the `Name` column and the `Error` column should be empty.
- Output in case of an unsuccessful installation: `prometheus_exporter` is listed in the `Name` column and the `Error` column will have more information.
