#include <DHT.h>
#include <Servo.h>

#define SOIL_MOISTURE_PIN A0
#define LDR_PIN A1
#define DHT_PIN 2
#define BUZZER_PIN 10
#define LED_PIN 11

#define MOTOR1_PWM 3    // Fan motor PWM
#define MOTOR1_IN1 4
#define MOTOR1_IN2 5

#define MOTOR2_PWM 6    // Pump motor PWM
#define MOTOR2_IN3 7
#define MOTOR2_IN4 8

#define SERVO_PIN 9

DHT dht(DHT_PIN, DHT11);
Servo ventServo;

void setup() {
  Serial.begin(9600);

  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  pinMode(MOTOR1_PWM, OUTPUT);
  pinMode(MOTOR1_IN1, OUTPUT);
  pinMode(MOTOR1_IN2, OUTPUT);

  pinMode(MOTOR2_PWM, OUTPUT);
  pinMode(MOTOR2_IN3, OUTPUT);
  pinMode(MOTOR2_IN4, OUTPUT);

  ventServo.attach(SERVO_PIN);

  dht.begin();

  stopMotor1();
  stopMotor2();
  ventServo.write(0); // Vent closed initially
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  int soilMoisture = analogRead(SOIL_MOISTURE_PIN);
  int ldrValue = analogRead(LDR_PIN);
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Brightness levels (4-level scale)
  int brightnessLevel = 0;
  if (ldrValue < 200) brightnessLevel = 1;       // Dark
  else if (ldrValue < 400) brightnessLevel = 2;  // Dim
  else if (ldrValue < 700) brightnessLevel = 3;  // Moderate
  else brightnessLevel = 4;                       // Bright

  Serial.print("Soil Moisture: "); Serial.print(soilMoisture);
  Serial.print(" | LDR Level: "); Serial.print(brightnessLevel);
  Serial.print(" | Temp: "); Serial.print(temperature);
  Serial.print(" | Humidity: "); Serial.println(humidity);

  // Control vent servo based on temperature
  if (temperature > 28) {          // If temp > 28°C, open vent halfway
    ventServo.write(45);
  } else if (temperature > 32) {   // If temp > 32°C, open vent fully
    ventServo.write(90);
  } else {
    ventServo.write(0);            // Otherwise close vent
  }

  // Control fan (Motor 1) based on temperature or humidity
  if (temperature > 30 || humidity > 80) {
    motor1Forward();
  } else {
    stopMotor1();
  }

  // Control pump (Motor 2) based on soil moisture threshold
  if (soilMoisture < 400) { // dry soil
    motor2Forward();
    digitalWrite(LED_PIN, HIGH); // Indicate watering
  } else {
    stopMotor2();
    digitalWrite(LED_PIN, LOW);
  }

  // Buzzer alert if very high temperature
  if (temperature > 35) {
    digitalWrite(BUZZER_PIN, HIGH);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }

  delay(2000); // wait 2 seconds before next read
}

// Motor 1 - Fan control
void motor1Forward() {
  digitalWrite(MOTOR1_IN1, HIGH);
  digitalWrite(MOTOR1_IN2, LOW);
  analogWrite(MOTOR1_PWM, 255);
}

void stopMotor1() {
  digitalWrite(MOTOR1_IN1, LOW);
  digitalWrite(MOTOR1_IN2, LOW);
  analogWrite(MOTOR1_PWM, 0);
}

// Motor 2 - Pump control
void motor2Forward() {
  digitalWrite(MOTOR2_IN3, HIGH);
  digitalWrite(MOTOR2_IN4, LOW);
  analogWrite(MOTOR2_PWM, 255);
}

void stopMotor2() {
  digitalWrite(MOTOR2_IN3, LOW);
  digitalWrite(MOTOROR2_IN4, LOW);
  analogWrite(MOTOR2_PWM, 0);
}
