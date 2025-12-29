#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <MPU6050.h>
#include <WiFi.h>

/* ---------- WiFi ---------- */
const char* ssid = "Wokwi-GUEST";
const char* password = "";

/* ---------- DS18B20 ---------- */
#define TEMP_PIN 4
OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

/* ---------- HC-SR04 ---------- */
#define TRIG_PIN 5
#define ECHO_PIN 18

/* ---------- MPU6050 ---------- */
MPU6050 mpu;

/* ---------- CONTAINER ---------- */
const float containerHeightCm = 100.0;

/* ---------- SETTINGS ---------- */
const uint32_t READ_INTERVAL_MS = 3000;
uint32_t lastRead = 0;

/* ---------- ULTRASONIC ---------- */
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

/* ---------- MPU ---------- */
bool readTilted() {
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);

  float fx = ax / 16384.0;
  float fy = ay / 16384.0;

  return (abs(fx) > 0.3 || abs(fy) > 0.3);
}

/* ---------- TEMPERATURE ---------- */
float readTemperature() {
  tempSensor.requestTemperatures();
  float temp = tempSensor.getTempCByIndex(0);

  if (temp == DEVICE_DISCONNECTED_C) {
    Serial.println("DS18B20 disconnected");
    return -100;
  }
  return temp;
}

/* ---------- SETUP ---------- */
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  /* WiFi */
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  /* Sensors */
  Wire.begin(21, 22);
  mpu.initialize();
  tempSensor.begin();

  Serial.println(mpu.testConnection()
    ? "MPU6050 connected"
    : "MPU6050 NOT found");

  Serial.println("DS18B20 initialized");
  Serial.println("----------------------------------");
}

/* ---------- LOOP ---------- */
void loop() {
  if (millis() - lastRead >= READ_INTERVAL_MS) {
    lastRead = millis();

    float fill = readFillLevelPercent();
    float temperature = readTemperature();
    bool tilted = readTilted();
    int battery = random(60, 100); // емітація батареї

    if (fill < 0) fill = 0;
    if (temperature < -50) temperature = 0;

    Serial.println("\n--- SENSOR DATA ---");

    Serial.print("Fill level: ");
    Serial.print(fill);
    Serial.println(" %");

    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");

    Serial.print("Tilted: ");
    Serial.println(tilted ? "YES" : "NO");

    Serial.print("Battery: ");
    Serial.print(battery);
    Serial.println(" %");

    Serial.print("WiFi status: ");
    Serial.println(WiFi.status() == WL_CONNECTED ? "CONNECTED" : "DISCONNECTED");

    Serial.println("-------------------");
  }
}

