
import serial
import paho.mqtt.client as mqtt
import random
import pandas as pd
from datetime import datetime
import re
import paho.mqtt.enums as mqtt_enum
import asyncio
import websockets
import json
from aiohttp import web

# MQTT broker configuration
broker_address = "192.168.1.14"  # Replace with your MQTT broker address
broker_port = 1883  # Default MQTT port

# Serial port configuration
puerto_serial = '/dev/ttyUSB0'  # Change this to the correct serial port on your system
velocidad = 9600  # Change this to the correct baud rate

# Topics
input_topic = "hardware_status"
output_topic = "sensor/ESP32"

# Expresiones regulares para extraer valores de sensores
accelerometer_pattern = re.compile(r'Accelerometer \(g\): X = (.*), Y = (.*), Z = (.*)')
gyroscope_pattern = re.compile(r'Gyroscope \(degrees/s\): X = (.*), Y = (.*), Z = (.*)')
temperature_pattern = re.compile(r'Temperature: (.*) °C')
humidity_pattern = re.compile(r'Humidity: (.*) %')

# Variables para almacenar los valores actuales de cada variable
current_values = {}

# Callback function to handle connection established event
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code "+str(rc))
    # Subscribe to the input topic
    client.subscribe(input_topic)
    client.subscribe(output_topic)

# Callback function to handle message received event
def on_message(client, userdata, msg):
    global current_values
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    # Publish data to the output topic
    client.publish(output_topic, msg.payload)
    current_values[msg.topic] = msg.payload.decode()

# Open the serial connection
ser = serial.Serial(puerto_serial, velocidad)

# Create an empty dataframe
df = pd.DataFrame(columns=['Timestamp', 'Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z',
                           'Gyroscope_X', 'Gyroscope_Y', 'Gyroscope_Z', 'Temperature', 'Humidity'])

# Create MQTT client instance
client_id = f'python-mqtt-{random.randint(0, 1000)}'
client = mqtt.Client(callback_api_version=mqtt_enum.CallbackAPIVersion.VERSION1, client_id=client_id)

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(broker_address, broker_port)
client.loop_start()

async def websocket_server(websocket, path):
    while True:        
        await websocket.send(json.dumps(current_values))

async def cors_middleware(app, handler):
    async def middleware(request):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'  # Permitir acceso desde cualquier origen
        response.headers['Access-Control-Allow-Methods'] = '*'  # Métodos permitidos
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # Encabezados permitidos
        return response
    return middleware

try:
    while True:
        
        # Read a line of data from the serial port
        linea = ser.readline().decode().strip()

        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Extract sensor data using regular expressions
        accelerometer_match = accelerometer_pattern.search(linea)
        gyroscope_match = gyroscope_pattern.search(linea)
        temperature_match = temperature_pattern.search(linea)
        humidity_match = humidity_pattern.search(linea)

        # Check if any sensor data is not None
        if any([
            accelerometer_match, gyroscope_match, temperature_match, humidity_match
        ]):
            # Append data to dataframe
            df = df._append({
                'Timestamp': timestamp,
                'Accelerometer_X': accelerometer_match.group(1) if accelerometer_match else None,
                'Accelerometer_Y': accelerometer_match.group(2) if accelerometer_match else None,
                'Accelerometer_Z': accelerometer_match.group(3) if accelerometer_match else None,
                'Gyroscope_X': gyroscope_match.group(1) if gyroscope_match else None,
                'Gyroscope_Y': gyroscope_match.group(2) if gyroscope_match else None,
                'Gyroscope_Z': gyroscope_match.group(3) if gyroscope_match else None,
                'Temperature': temperature_match.group(1) if temperature_match else None,
                'Humidity': humidity_match.group(1) if humidity_match else None
            }, ignore_index=True)
            # Agrupar por timestamp y seleccionar el primer valor no nulo en cada grupo
            df_grouped = df.groupby('Timestamp').first().reset_index()
            # print(df_grouped)

            # Publish data to the output topic
            client.publish(output_topic, linea)

except KeyboardInterrupt:
    print('Stopping serial port reading')
    ser.close()  # Close the serial connection

    # Save dataframe to a CSV file
    df_grouped.to_csv('data.csv', index=False)

    # Stop the MQTT client loop
    client.loop_stop()

# Run WebSocket server
cors_middleware_instance = cors_middleware(web.Application(), websocket_server)
app = web.Application(middlewares=[cors_middleware_instance])
start_server = websockets.serve(websocket_server, "192.168.1.14", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()