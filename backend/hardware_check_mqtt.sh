#!/bin/bash

# Variables de configuración MQTT
MQTT_BROKER="localhost"
MQTT_TOPIC="hardware_status"
ALERT_THRESHOLD=5  # Threshold for consecutive unstable connections before generating an alert
CONNECTION_STATUS="stable"
UNSTABLE_COUNT=0

# Output file to store the data
OUTPUT_FILE="$HOME/hardware_status.txt"

while true; do
    # Obtener la salida de xrandr y ifconfig
    XRANDR_OUTPUT=$(xrandr)
    IFCONFIG_OUTPUT=$(ifconfig)
    #TOP_OUTPUT=$(top)

    # Verificar si la pantalla está encendida o apagada
    SCREEN_STATUS=$(echo "$XRANDR_OUTPUT" | grep " connected" | awk '{print $2}')
    if [ "$SCREEN_STATUS" == "connected" ]; then
        SCREEN_STATUS_MSG="pantalla led: status 200. ok"
    else
        SCREEN_STATUS_MSG="pantalla led: failed"
    fi

    # Verificar si la conexión es estable
    if ping -c 1 google.com &> /dev/null; then
        CONNECTION_STATUS="stable"
        UNSTABLE_COUNT=0
    else
        ((UNSTABLE_COUNT++))
        if [ $UNSTABLE_COUNT -ge $ALERT_THRESHOLD ]; then
            CONNECTION_STATUS="unstable"
            # Enviar alerta por MQTT
            mosquitto_pub -h $MQTT_BROKER -t $MQTT_TOPIC -m "failed."
        fi
    fi

    # Enviar datos por MQTT
    mosquitto_pub -h $MQTT_BROKER -t $MQTT_TOPIC -m "$SCREEN_STATUS_MSG\n$XRANDR_OUTPUT\n$IFCONFIG_OUTPUT\nEstado de la conexión de red: $CONNECTION_STATUS"

    # Send the result to the output file
    echo -e "$SCREEN_STATUS_MSG\n$XRANDR_OUTPUT\n$IFCONFIG_OUTPUT\nEstado de la conexión de red: $CONNECTION_STATUS" > $OUTPUT_FILE
    # llamar el script de python
    # Esperar 3 segundos antes de enviar la próxima actualización
    sleep 3
done
