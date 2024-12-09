#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <time.h>
#include <LiquidCrystal_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const char *ssid = "iPhone (Arek)"; // WiFi name
const char *password = "1234567f"; // WiFi password

// MQTT Broker settings
const char *mqtt_broker = "ee9de197.ala.us-east-1.emqxsl.com"; // EMQX broker endpoint
const char *temperature_topic = "esp/temperature"; // MQTT topic for temperature
const char *voice_topic = "esp/voice"; // MQTT topic for voice messages
const char *webcam_topic = "esp/webcam"; // MQTT topic for voice messages
const char *mqtt_username = "test"; // MQTT username
const char *mqtt_password = "test"; // MQTT password
const int mqtt_port = 8883; // MQTT port (TCP)

// NTP Server settings
const char *ntp_server = "pool.ntp.org"; // NTP server
const long gmt_offset_sec = 0; // GMT offset
const int daylight_offset_sec = 0; // Daylight saving time offset

// WiFi and MQTT client initialization
BearSSL::WiFiClientSecure espClient;
PubSubClient mqtt_client(espClient);

// Set the LCD number of columns and rows
int lcdColumns = 16;
int lcdRows = 2;

// Set LCD address, number of columns and rows
LiquidCrystal_I2C lcd(0x27, lcdColumns, lcdRows);
const int oneWireBus = 0;
OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

// SSL certificate for MQTT broker
static const char ca_cert[]
PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
MIIDrzCCApegAwIBAgIQCDvgVpBCRrGhdWrJWZHHSjANBgkqhkiG9w0BAQUFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBD
QTAeFw0wNjExMTAwMDAwMDBaFw0zMTExMTAwMDAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IENBMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4jvhEXLeqKTTo1eqUKKPC3eQyaKl7hLOllsB
CSDMAZOnTjC3U/dDxGkAV53ijSLdhwZAAIEJzs4bg7/fzTtxRuLWZscFs3YnFo97
nh6Vfe63SKMI2tavegw5BmV/Sl0fvBf4q77uKNd0f3p4mVmFaG5cIzJLv07A6Fpt
43C/dxC//AH2hdmoRBBYMql1GNXRor5H4idq9Joz+EkIYIvUX7Q6hL+hqkpMfT7P
T19sdl6gSzeRntwi5m3OFBqOasv+zbMUZBfHWymeMr/y7vrTC0LUq7dBMtoM1O/4
gdW7jVg/tRvoSSiicNoxBN33shbyTApOB6jtSj1etX+jkMOvJwIDAQABo2MwYTAO
BgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUA95QNVbR
TLtm8KPiGxvDl7I90VUwHwYDVR0jBBgwFoAUA95QNVbRTLtm8KPiGxvDl7I90VUw
DQYJKoZIhvcNAQEFBQADggEBAMucN6pIExIK+t1EnE9SsPTfrgT1eXkIoyQY/Esr
hMAtudXH/vTBH1jLuG2cenTnmCmrEbXjcKChzUyImZOMkXDiqw8cvpOp/2PV5Adg
06O/nVsJ8dWO41P0jmP6P6fbtGbfYmbW0W5BjfIttep3Sp+dWOIrWcBAI+0tKIJF
PnlUkiaY4IBIqDfv8NZ5YBberOgOzW6sRBc4L0na4UU+Krk2U886UAb3LujEV0ls
YSEY1QSteDwsOoBrp+uvFRTp2InBuThs4pFsiv9kuXclVzDAGySj4dzp30d8tbQk
CAUw7C29C79Fv1C5qfPrmAESrciIxpg0X40KPMbp1ZWVbd4=
-----END CERTIFICATE-----
)EOF";

// Function declarations
void connectToWiFi();
void connectToMQTT();
void syncTime();
void mqttCallback(char *topic, byte *payload, unsigned int length);

void setup() {
    Serial.begin(115200);
    sensors.begin();
    lcd.init(); // Initialize LCD
    lcd.backlight(); // Turn on LCD backlight
    connectToWiFi();
    syncTime(); // Synchronize time
    mqtt_client.setServer(mqtt_broker, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    connectToMQTT();
}

void connectToWiFi() {
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
}

void syncTime() {
    configTime(gmt_offset_sec, daylight_offset_sec, ntp_server);
    Serial.print("Waiting for NTP time sync: ");
    while (time(nullptr) < 8 * 3600 * 2) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("Time synchronized");
}

void connectToMQTT() {
    BearSSL::X509List serverTrustedCA(ca_cert);
    espClient.setTrustAnchors(&serverTrustedCA);
    while (!mqtt_client.connected()) {
        String client_id = "esp8266-client-" + String(WiFi.macAddress());
        Serial.printf("Connecting to MQTT Broker as %s.....\n", client_id.c_str());
        if (mqtt_client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
            Serial.println("Connected to MQTT broker");
            // Subscribe to both topics
            //mqtt_client.subscribe(temperature_topic);
            mqtt_client.subscribe(voice_topic);
            mqtt_client.subscribe(webcam_topic);
            
            //mqtt_client.publish(temperature_topic, "Hi EMQX I'm ESP8266 ^^");
        } else {
            Serial.print("Failed to connect to MQTT broker, rc=");
            Serial.println(mqtt_client.state());
            delay(5000);
        }
    }
}

void mqttCallback(char *topic, byte *payload, unsigned int length) {
    Serial.print("Message received on topic: ");
    Serial.print(topic);
    Serial.print("]: ");

    // Print the payload to the Serial Monitor
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    Serial.println(message);

    // Handle messages based on the topic
    if (strcmp(topic, webcam_topic) == 0) {
        //lcd.clear(); // Clear the LCD
        lcd.setCursor(0, 0); // Set cursor to the first line
        lcd.print("                ");
        lcd.setCursor(0, 0); // Set cursor to the first line
        lcd.print(message); // Print the message on the LCD
    }
    // Handle messages based on the topic
    if (strcmp(topic, voice_topic) == 0) {
        //lcd.clear(); // Clear the LCD
        lcd.setCursor(0, 1); // Set cursor to the first line
        lcd.print("                ");
        lcd.setCursor(0, 1); // Set cursor to the first line
        lcd.print(message); // Print the message on the LCD
    }
}

void loop() {
    mqtt_client.loop(); // Process MQTT messages
    static unsigned long lastTemperaturePublish = 0;
    unsigned long currentMillis = millis();

    // Publish temperature every second
    if (currentMillis - lastTemperaturePublish >= 1000) {
        lastTemperaturePublish = currentMillis;
        sensors.requestTemperatures();
        String temperature = String(sensors.getTempCByIndex(0));
        Serial.println(temperature);
        mqtt_client.publish(temperature_topic, temperature.c_str());
    }
}
