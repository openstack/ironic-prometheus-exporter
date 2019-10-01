#!/usr/bin/env bash
# plugin.sh - DevStack plugin.sh dispatch script template

IRONIC_PROMETHEUS_EXPORTER_DIR=${IRONIC_PROMETHEUS_EXPORTER_DIR:-$DEST/ironic-prometheus-exporter}
IRONIC_PROMETHEUS_EXPORTER_PORT=${IRONIC_PROMETHEUS_EXPORTER_PORT:-9608}
IRONIC_PROMETHEUS_EXPORTER_DATA_DIR=""$DATA_DIR/ironic-prometheus-exporter""
IRONIC_PROMETHEUS_EXPORTER_SYSTEMD_SERVICE="devstack@ironic-prometheus-exporter.service"
# Location where the metrics from the baremetal nodes will be stored
IRONIC_PROMETHEUS_EXPORTER_LOCATION=${IRONIC_PROMETHEUS_EXPORTER_LOCATION:-$IRONIC_VM_LOG_DIR}
COLLECT_DATA_UNDEPLOYED_NODES=$(trueorfalse True COLLECT_DATA_UNDEPLOYED_NODES)
IRONIC_CONFIG=${IRONIC_CONFIG:-$IRONIC_CONF_FILE}
IPE_ACCESS_LF="$IRONIC_VM_LOG_DIR/ipe_access.log"
IPE_ERROR_LF="$IRONIC_VM_LOG_DIR/ipe_errors.log"

function install_ironic_prometheus_exporter {
    git_clone_by_name "ironic-prometheus-exporter"
    setup_dev_lib "ironic-prometheus-exporter"
}

function configure_ironic_prometheus_exporter {
    # Update ironic configuration file to use the exporter
    iniset $IRONIC_CONF_FILE conductor send_sensor_data true
    iniset $IRONIC_CONF_FILE conductor send_sensor_data_for_undeployed_nodes $COLLECT_DATA_UNDEPLOYED_NODES
    iniset $IRONIC_CONF_FILE conductor send_sensor_data_interval 90
    iniset $IRONIC_CONF_FILE oslo_messaging_notifications driver prometheus_exporter
    iniset $IRONIC_CONF_FILE oslo_messaging_notifications transport_url fake://
    iniset $IRONIC_CONF_FILE oslo_messaging_notifications location $IRONIC_PROMETHEUS_EXPORTER_LOCATION

    local gunicorn_ipe_cmd

    gunicorn_ipe_cmd=$(which gunicorn3)
    gunicorn_ipe_cmd+=" -b ${HOST_IP}:${IRONIC_PROMETHEUS_EXPORTER_PORT}"
    gunicorn_ipe_cmd+=" --env IRONIC_CONFIG=$IRONIC_CONFIG"
    gunicorn_ipe_cmd+=" --env FLASK_DEBUG=1 -w 4"
    gunicorn_ipe_cmd+=" --access-logfile=$IPE_ACCESS_LF --error-logfile=$IPE_ERROR_LF"
    gunicorn_ipe_cmd+=" -D ironic_prometheus_exporter.app.wsgi:application"

    write_user_unit_file $IRONIC_PROMETHEUS_EXPORTER_SYSTEMD_SERVICE "$gunicorn_ipe_cmd" "" "$STACK_USER"

    enable_service $IRONIC_PROMETHEUS_EXPORTER_SYSTEMD_SERVICE
}

function start_ironic_prometheus_exporter {
    start_service $IRONIC_PROMETHEUS_EXPORTER_SYSTEMD_SERVICE
}

function stop_ironic_prometheus_exporter {
    stop_service $IRONIC_PROMETHEUS_EXPORTER_SYSTEMD_SERVICE
}

function cleanup_ironic_prometheus_exporter {
    stop_ironic_prometheus_exporter

    disable_service $IRONIC_PROMETHEUS_EXPORTER_SYSTEMD_SERVICE

    sudo rm -rf $IRONIC_PROMETHEUS_EXPORTER_DATA_DIR

    local unitfile="$SYSTEMD_DIR/$IRONIC_PROMETHEUS_EXPORTER_SYSTEMD_SERVICE"
    sudo rm -f $unitfile

    $SYSTEMCTL daemon-reload
}

function wait_for_data {
    # Sleep for more than the [conductor]send_sensor_data_interval value
    # to verify if we can get data from the baremetal
    # FIXME(iurygregory): Add some logic to verify if the data already exists
    sleep 240
}

function check_data {
    local node_file="node-0-hardware.redfish.metrics"
    if [ -f "$IRONIC_PROMETHEUS_EXPORTER_LOCATION/$node_file" ]; then
        echo "Found $node_file in $IRONIC_PROMETHEUS_EXPORTER_LOCATION"
        if curl -s --head  --request  GET "http://$HOST_IP:$IRONIC_PROMETHEUS_EXPORTER_PORT/metrics" | grep "200 OK" > /dev/null; then
            echo "Data successfully retrived from ironic-prometheus-exporter application"
        else
            die $LINENO "Couldn't get data from ironic-prometheus-exporter application"
        fi
    else
        die $LINENO "Couldn't find $node_file in $IRONIC_PROMETHEUS_EXPORTER_LOCATION"
    fi
}

echo_summary "ironic-prometheus-exporter devstack plugin.sh called: $1/$2"

if is_service_enabled ironic-prometheus-exporter; then

    if [[ "$1" == "stack" ]]; then
        case "$2" in
            install)
                echo_summary "Installing Ironic Prometheus Exporter"
                install_ironic_prometheus_exporter
                ;;
            post-config)
                echo_summary "Configuring Ironic Prometheus Exporter Application"
                configure_ironic_prometheus_exporter
                ;;
            extra)
                echo_summary "Starting Ironic Prometheus Exporter Application"
                start_ironic_prometheus_exporter
                echo_summary "Give time to baremetal to provide data"
                wait_for_data
                check_data
                ;;
        esac
    fi

    if [[ "$1" == "unstack" ]]; then
        echo_summary "Stopping Ironic Prometheus Exporter Application"
        stop_ironic_prometheus_exporter
        echo_summary "Cleaning Ironic Prometheus Exporter"
        cleanup_ironic_prometheus_exporter
    fi

fi
