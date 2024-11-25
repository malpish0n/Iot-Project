import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import whisper
import sounddevice as sd
import numpy as np
import time
import os

# MQTT settings
MQTT_BROKER = "ee9de197.ala.us-east-1.emqxsl.com"  # Replace with your broker IP
MQTT_PORT = 8883  # Default MQTT port
MQTT_TOPIC_TEMPERATURE = "esp/temperature"
MQTT_TOPIC_VOICE = "esp/voice"
# InfluxDB settings for 2.x
INFLUXDB_URL = 'http://172.20.10.3:8086'  # Replace with your InfluxDB URL
INFLUXDB_TOKEN = 'A22odWMhuYMPvJjM-yiGwUDKs0oLn5AcitTm_JQ0XVQZZwFMaarnliD4XPNsLoWn0T_Wu90C0fMBocSLl1pujw=='
INFLUXDB_ORG = 'admini'  # Replace with your organization name
INFLUXDB_BUCKET = 'bucket'  # Replace with your bucket name

# Create InfluxDB client for 2.x
client_influx = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = client_influx.write_api(write_options=SYNCHRONOUS)

# Load the Whisper model
model = whisper.load_model('medium')

def get_transcribe(audio_data, language: str = 'pl'):
    return model.transcribe(audio=audio_data, language=language, verbose=True)

# Function to save data to InfluxDB
def save_to_influxdb(temperature):
    point = Point("temperature_reading").field("value", temperature)
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)

# Callback for when a PUBLISH message is received from the server
def on_message(client, userdata, message):
    try:
        # Decode and convert payload to float
        temperature = float(message.payload.decode("utf-8"))
        print(f"Received temperature: {temperature}")

        # Save the temperature to InfluxDB
        save_to_influxdb(temperature)

    except Exception as e:
        print(f"Error: {e}")

# MQTT connection setup
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    # Subscribe to the desired topic
    client.subscribe(MQTT_TOPIC_TEMPERATURE)
    # client.subscribe(MQTT_TOPIC_VOICE)

def publish_transcription(mqtt_client, transcription):
    mqtt_client.publish(MQTT_TOPIC_VOICE, transcription)

def main():
    # Create MQTT client
    mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)   
    mqtt_client.username_pw_set(username="test", password="test")
    mqtt_client.tls_set(ca_certs="cert.crt")

    # Attach callback functions
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Connect to the MQTT broker
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # Start the MQTT loop in a non-blocking way
    mqtt_client.loop_start()

    # Recording settings
    duration = 3  # Duration in seconds
    fs = 16000    # Sampling rate

    while True:  # Run indefinitely
        print(f"Recording for {duration} seconds...")

        # Record audio from the microphone
        myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()  # Wait until recording is finished
        print("Recording finished.")

        # Flatten the final recorded array
        audio_data = myrecording.flatten()

        # Transcribe the audio data
        result = get_transcribe(audio_data=audio_data)
        transcription = result.get('text', '')
        print('-' * 50)
        print(transcription)

        # Publish the transcription to the MQTT broker
        publish_transcription(mqtt_client, transcription)

        # Delay between recordings
        time.sleep(1)  # Adjust as necessary

if __name__ == "__main__":
    main()
