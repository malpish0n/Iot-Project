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
