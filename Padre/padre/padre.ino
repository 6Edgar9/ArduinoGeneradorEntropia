#include <Wire.h>
#include <MPU6050.h>

#define H2_I2C_ADDRESS 0x08

#define LM35_PIN A0
#define NIVEL_PIN A1

MPU6050 mpu;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 no conectado");
  }

  pinMode(NIVEL_PIN, INPUT); // Recomendado
}

void loop() {
  // Leer datos del hijo 2
  Wire.requestFrom(H2_I2C_ADDRESS, 8);
  if (Wire.available() < 8) return; // Previene errores si falla I2C

  uint8_t tilt1 = Wire.read();
  uint8_t tilt2 = Wire.read();
  uint16_t mic = (Wire.read() << 8) | Wire.read();
  uint32_t timestamp_h2 = 0;
  for (int i = 0; i < 4; i++) {
    timestamp_h2 = (timestamp_h2 << 8) | Wire.read();
  }

  // Sensores locales
  float tempC = analogRead(LM35_PIN) * (5.0 / 1023.0) * 100.0;
  int nivel = digitalRead(NIVEL_PIN);

  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);

  // Serial JSON
  Serial.print("{\"timestamp_h2\":");
  Serial.print(timestamp_h2);
  Serial.print(",\"tilt1\":");
  Serial.print(tilt1);
  Serial.print(",\"tilt2\":");
  Serial.print(tilt2);
  Serial.print(",\"mic\":");
  Serial.print(mic);
  Serial.print(",\"temp_c\":");
  Serial.print(tempC, 1);
  Serial.print(",\"nivel\":");
  Serial.print(nivel);
  Serial.print(",\"mpu\":{");
  Serial.print("\"x\":"); Serial.print(ax);
  Serial.print(",\"y\":"); Serial.print(ay);
  Serial.print(",\"z\":"); Serial.print(az);
  Serial.println("}}");

  delay(3000);
}
