import paho.mqtt.client as mqtt
from influxdb_client.client.write_api import SYNCHRONOUS
import whisper
import sounddevice as sd
import time
import time



# MQTT settings
MQTT_BROKER = "ee9de197.ala.us-east-1.emqxsl.com"  # Replace with your broker IP
MQTT_PORT = 8883  # Default MQTT port
MQTT_TOPIC_VOICE = "esp/voice"

# Load the Whisper model
model = whisper.load_model('medium')

def get_transcribe(audio_data, language: str = 'pl'):
    return model.transcribe(audio=audio_data, language=language, verbose=True)


# MQTT connection setup
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    # Subscribe to the desired topic



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
        mqtt_client.publish(MQTT_TOPIC_VOICE, transcription)

        # Delay between recordings
        time.sleep(1)  # Adjust as necessary

if __name__ == "__main__":
    main()
