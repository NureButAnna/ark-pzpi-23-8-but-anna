#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <MPU6050.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

/* ---------- CONFIG ---------- */
const char* ssid = "Wokwi-GUEST";
const char* password = "";

const char* API_URL = "https://ecofy-beta.vercel.app/devices/telemetry";
const char* DEVICE_SERIAL = "ESP32_KHARKIV_002";

/* ---------- DS18B20 ---------- */
#define TEMP_PIN 4

OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

/* ---------- HC-SR04 ---------- */
#define TRIG_PIN 5
#define ECHO_PIN 18

MPU6050 mpu;

/* ---------- CONTAINER ---------- */
const float containerHeightCm = 100.0;

/* ---------- SETTINGS ---------- */
const uint32_t SEND_INTERVAL_MS = 5000;
const int MAX_RETRIES = 3;

uint32_t lastSend = 0;

/* ---------- HTTP ---------- */
bool postTelemetry(const String& body) {
  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  int code = http.POST(body);

  Serial.print("HTTP code: ");
  Serial.println(code);

  String resp = http.getString();
  if (resp.length() > 0) {
    Serial.print("Response body: ");
    Serial.println(resp);
  }

  http.end();
  return (code >= 200 && code < 300);
}

bool sendTelemetryWithRetry(float fill, float temperature, bool tilted, int battery) {
  StaticJsonDocument<256> json;
  json["serial_number"] = DEVICE_SERIAL;
  json["fill_level"] = fill;
  json["temperature"] = temperature;
  json["tilted"] = tilted;
  json["battery_level"] = battery;

  String body;
  serializeJson(json, body);

  for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    Serial.print("POST attempt ");
    Serial.print(attempt);
    Serial.println("...");

    if (postTelemetry(body)) {
      Serial.println("Telemetry delivered");
      return true;
    }

    delay(500 * (1 << (attempt - 1)));
  }

  Serial.println("Failed to deliver telemetry");
  return false;
}

/* ---------- SENSORS ---------- */
float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return -1;

  return duration * 0.034 / 2.0;
}

float readFillLevelPercent() {
  float distance = readDistanceCm();
  if (distance < 0) return -1;

  float fill = (containerHeightCm - distance) / containerHeightCm * 100.0;
  return constrain(fill, 0, 100);
}

bool readTilted() {
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);

  float fx = ax / 16384.0;
  float fy = ay / 16384.0;

  return (abs(fx) > 0.3 || abs(fy) > 0.3);
}

float readTemperature() {
  tempSensor.requestTemperatures();
  float temp = tempSensor.getTempCByIndex(0);

  if (temp == DEVICE_DISCONNECTED_C) {
    Serial.println("Temperature sensor disconnected");
    return -100;
  }

  return temp;
}

/* ---------- SETUP ---------- */
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("--- Booting Device ---");

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi OK");

  Wire.begin(21, 22);
  mpu.initialize();

  tempSensor.begin();
  Serial.println("DS18B20 initialized");

  Serial.println(mpu.testConnection() ? "MPU6050 OK" : "MPU6050 NOT FOUND");
  delay(2000);
}

/* ---------- LOOP ---------- */
void loop() {
  if (millis() - lastSend >= SEND_INTERVAL_MS) {
    lastSend = millis();

    float fill = readFillLevelPercent();
    bool tilted = readTilted();
    float temperature = readTemperature();
    int battery = random(60, 100);

    if (fill < 0) fill = 0;
    if (temperature < -50) temperature = 0; // fallback

    Serial.println("\n--- Sensor Readings ---");
    Serial.print("Fill level (%): ");
    Serial.println(fill);

    Serial.print("Temperature (°C): ");
    Serial.println(temperature);

    Serial.print("Tilted: ");
    Serial.println(tilted ? "YES" : "NO");

    Serial.print("Battery: ");
    Serial.println(battery);

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n--- Sending telemetry ---");
      sendTelemetryWithRetry(fill, temperature, tilted, battery);
    }
  }
}

