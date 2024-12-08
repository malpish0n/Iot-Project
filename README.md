# Project Documentation: IoT Data Integration System with Docker

## Project Description
This project integrates data from multiple sources, including temperature readings from IoT devices (via MQTT), video analysis (YOLO), and speech transcription (Whisper). 
The data is processed, stored in an InfluxDB database, and published to relevant MQTT topics.
The project uses Docker for containerization.
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
