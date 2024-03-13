from fastapi import FastAPI
import paho.mqtt.client as mqtt

app = FastAPI()

# Callback que se ejecuta cuando se recibe un mensaje MQTT
def on_message(client, userdata, msg):
    print(f"Mensaje recibido: {msg.payload.decode()}")

# Configuración del cliente MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect("mosquitto", 1883, 60)  # "mosquitto" es el nombre del servicio definido en Docker Compose

# Suscribirse a un tema MQTT
client.subscribe("topic/example")

# Iniciar el loop de MQTT
client.loop_start()

# Ruta de ejemplo en FastAPI para recibir mensajes MQTT
@app.post("/mqtt")
async def receive_mqtt_message(message: str):
    # Aquí puedes manejar el mensaje MQTT recibido como desees
    print(f"Mensaje recibido en la ruta /mqtt: {message}")
    return {"message": "Mensaje MQTT recibido"}

# Detener el loop de MQTT al cerrar la aplicación
@app.on_event("shutdown")
def shutdown_event():
    client.loop_stop()
