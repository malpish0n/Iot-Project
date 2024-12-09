# Project Documentation: IoT Data Integration System with Docker

## Project Description
This project integrates data from multiple sources, including temperature readings from IoT devices (via MQTT), video analysis (YOLO), and speech transcription (Whisper). 
The data is processed, stored in an InfluxDB database, and published to relevant MQTT topics. 

The project also includes the functionality to send processed data to an Arduino microcontroller via Serial communication, where it is displayed on an LCD screen. Docker is used for containerization, ensuring easier deployment and portability.
## Running the Project
### 1. Prerequisites
   
a) Tools:

Docker and Docker Compose (installed on your system).

Python 3.8+.

Git.

b) Database and MQTT Broker:

MQTT Broker

InfluxDB (locally hosted or in a Docker container).

c) Hardware:

Microphone.

Webcam.

### 2. Setup Instructions

a) Clone the repository

b) Configure environment variables
Create a .env file with the required environment variables:
```
MQTT_BROKER=broker_url
MQTT_PORT=mqtt_port
INFLUXDB_URL=influxdb_url
INFLUXDB_TOKEN=your_token
INFLUXDB_ORG=your_organization
INFLUXDB_BUCKET=your_bucket
```
c) Run with Docker

d) Verify system functionality

Open your browser and navigate to http://localhost:8086

## 1. Handling MQTT Messages
    def on_message(client, userdata, message):
    try:
        # Decode and convert payload to float
        temperature = float(message.payload.decode("utf-8"))
        print(f"Received temperature: {temperature}")

        # Save the temperature to InfluxDB
        save_to_influxdb(temperature)

    except Exception as e:
        print(f"Error: {e}")

## 2. Writing Data to InfluxDB
```
    def save_to_influxdb(temperature):
    point = Point("temperature_reading").field("value", temperature)
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)
```
## 3. YOLO Object Detection
```
 results = model(frame)

# Extract and display detected objects
detected_objects = []
for result in results:
    for box in result.boxes:
        class_id = int(box.cls)  # Class ID of the object
        confidence = box.conf  # Confidence score
        class_name = model.names[class_id]  # Class name (e.g., 'person', 'car')
        detected_objects.append(class_name)
```
## 4. Whisper Transcription
   ```
    def get_transcribe(audio_data, language: str = 'pl'):
    return model.transcribe(audio=audio_data, language=language, verbose=True)
   ```


## Final Integration Workflow
### Data Sources:

Temperature readings (MQTT), detected objects (YOLO), or transcriptions (Whisper) are processed in the Python application.
### MQTT Communication:

Data is published to relevant MQTT topics and stored in the InfluxDB database.
Arduino Integration:

Processed data is sent via Serial communication to an Arduino.
The Arduino displays the received information on an LCD screen.

### Dockerized System:

The entire application is containerized with Docker, ensuring ease of deployment and portability.

## Flowchart


![pobrany plik](https://github.com/user-attachments/assets/a380ad31-0f16-493f-9408-6b2f8fdb8036)

## Authors:
Arkadiusz Kasztelan, Hubert Marek
