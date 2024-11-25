import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import whisper
import sounddevice as sd
import numpy as np
import time
import os
import cv2
import time
from ultralytics import YOLO
import logging

# Suppress logging below WARNING level
logging.getLogger("ultralytics").setLevel(logging.WARNING)

# MQTT settings
MQTT_BROKER = "ee9de197.ala.us-east-1.emqxsl.com"  # Replace with your broker IP
MQTT_PORT = 8883  # Default MQTT port
MQTT_TOPIC_TEMPERATURE = "esp/temperature"
MQTT_TOPIC_VOICE = "esp/voice"
MQTT_TOPIC_WEBCAM = "esp/webcam"
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

    # Load the YOLOv8 model (default is the pretrained COCO model)
    model = YOLO('yolov8n.pt')  # You can use 'yolov8s.pt', 'yolov8m.pt', etc., for larger models
    
    # Open the webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Webcam not found!")
        return

    print("Starting webcam detection. Reading frames every 1 second. Press Ctrl+C to stop.")

    while True:  # Run indefinitely

        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture frame.")
            break

        # Perform detection
        results = model(frame)
        
        # Extract and display detected objects
        detected_objects = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)  # Class ID of the object
                confidence = box.conf  # Confidence score
                class_name = model.names[class_id]  # Class name (e.g., 'person', 'car')
                detected_objects.append(class_name)


        detected_objects_str = ', '.join(detected_objects) if detected_objects else 'None'
        print(f"Detected objects: {detected_objects_str}")
        
        # Publish detected objects as plain text to MQTT
        mqtt_client.publish(MQTT_TOPIC_WEBCAM, detected_objects_str)
        
        # Annotate frame with detection results (optional, not displayed here)
        annotated_frame = results[0].plot()
        

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
        mqtt_client.publish(MQTT_TOPIC_VOICE, transcription)

        # Delay between recordings
        time.sleep(1)  # Adjust as necessary

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
