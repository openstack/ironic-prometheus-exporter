import stevedore

driver_list = stevedore.ExtensionManager(
    'oslo.messaging.notify.drivers',
    invoke_on_load=False,
    propagate_map_exceptions=True
)

if 'prometheus_exporter' in driver_list.names():
    print('prometheus_exporter driver found.')
else:
    print('prometheus_exporter driver not found.')
    print('Available drivers: %s' % driver_list.names())
