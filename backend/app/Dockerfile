# Use an image based on Debian
FROM python:3.9-slim

# Install additional packages
RUN apt-get update && apt-get install -y mosquitto

# Set the working directory in the container
WORKDIR /app

# Copy your Python script and requirements file into the container
COPY pyserial.py requirements.txt ./

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the MQTT configuration file into the container
COPY ./mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf

# Expose MQTT and WebSocket ports
EXPOSE 1883
EXPOSE 8765

# Run your Python script
CMD ["python3", "pyserial.py"]
