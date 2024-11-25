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
MQTT_TOPIC_WEBCAM = "esp/webcam"

# MQTT connection setup
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))


def main():
    # Create MQTT client
    mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)   
    mqtt_client.username_pw_set(username="test", password="test")
    mqtt_client.tls_set(ca_certs="cert.crt")

    # Attach callback functions
    mqtt_client.on_connect = on_connect

    # Connect to the MQTT broker
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # Start the MQTT loop in a non-blocking way
    mqtt_client.loop_start()

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
        
        time.sleep(1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
