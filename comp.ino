#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include <DHT.h>
#include <Servo.h>

// Create motor shield object
Adafruit_MotorShield AFMS = Adafruit_MotorShield();

Adafruit_DCMotor *fanMotor = AFMS.getMotor(1);  // Fan connected to M1
Adafruit_DCMotor *pumpMotor = AFMS.getMotor(2); // Pump connected to M2

// Pins
const int ledPin = 3;
const int buzzerPin = 6;
Servo ventServo;

const int soilPin = A0;
const int ldrPin = A1;
const int dhtPin = 2;

// DHT setup
#define DHTTYPE DHT11
DHT dht(dhtPin, DHTTYPE);

// Thresholds
const int soilThreshold = 400;
const int ldrThreshold = 300;
const float tempThresholdFan = 30;
const float tempThresholdVent = 28;
const float humThreshold = 70;

// Manual override flags
bool manualFan = false;
bool manualPump = false;
bool manualLED = false;
bool manualBuzzer = false;
bool manualVent = false;

String inputString = "";
bool inputComplete = false;

void setup() {
  Serial.begin(9600);
  AFMS.begin();  // Start motor shield

  pinMode(soilPin, INPUT);
  pinMode(ldrPin, INPUT);

  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  ventServo.attach(9);

  dht.begin();

  inputString.reserve(50);

  allOff();
}

void loop() {
  readSerial();

  int soil = analogRead(soilPin);
  int ldr = analogRead(ldrPin);
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  // Automation logic
  if (!manualFan) setFan(temp > tempThresholdFan);
  if (!manualPump) setPump(soil < soilThreshold);
  if (!manualLED) setLED(ldr < ldrThreshold);
  if (!manualBuzzer) setBuzzer(hum > humThreshold);
  if (!manualVent) setVent(temp > tempThresholdVent);

  // Send sensor data every 2 seconds
  static unsigned long lastTime = 0;
  if (millis() - lastTime > 2000) {
    lastTime = millis();
    Serial.print(soil); Serial.print(",");
    Serial.print(ldr); Serial.print(",");
    Serial.print(temp); Serial.print(",");
    Serial.println(hum);
  }

  delay(100);
}

void readSerial() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') {
      inputComplete = true;
      parseCommand(inputString);
      inputString = "";
    } else {
      inputString += c;
    }
  }
}

void parseCommand(String cmd) {
  cmd.trim();
  int sep = cmd.indexOf(':');
  if (sep == -1) return;

  String device = cmd.substring(0, sep);
  String state = cmd.substring(sep + 1);
  device.toLowerCase();
  state.toLowerCase();

  if (device == "fan") {
    manualFan = true;
    setFan(state == "on");
  } else if (device == "pump") {
    manualPump = true;
    setPump(state == "on");
  } else if (device == "led") {
    manualLED = true;
    setLED(state == "on");
  } else if (device == "buzzer") {
    manualBuzzer = true;
    setBuzzer(state == "on");
  } else if (device == "vent") {
    manualVent = true;
    setVent(state == "open");
  } else if (device == "reset") {
    manualFan = manualPump = manualLED = manualBuzzer = manualVent = false;
  }
}

void setFan(bool on) {
  if (on) {
    fanMotor->setSpeed(255);  // Max speed
    fanMotor->run(FORWARD);
  } else {
    fanMotor->run(RELEASE);
  }
}

void setPump(bool on) {
  if (on) {
    pumpMotor->setSpeed(255);
    pumpMotor->run(FORWARD);
  } else {
    pumpMotor->run(RELEASE);
  }
}

void setLED(bool on) {
  digitalWrite(ledPin, on ? HIGH : LOW);
}

void setBuzzer(bool on) {
  digitalWrite(buzzerPin, on ? HIGH : LOW);
}

void setVent(bool open) {
  ventServo.write(open ? 90 : 0);
}

void allOff() {
  setFan(false);
  setPump(false);
  setLED(false);
  setBuzzer(false);
  setVent(false);
}
