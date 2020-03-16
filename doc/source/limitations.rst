Limitations
===========

* The only hardware types that have support for sensor data are `ipmi` and
  `redfish` (If a new hardware type adds support we need to add a parser for
  it).
* We can only deal with `Gauge metrics
  <https://prometheus.io/docs/practices/instrumentation/#counter-vs-gauge-summary-vs-histogram>`_.
* The set of metrics that will be available depends on the hardware type.
