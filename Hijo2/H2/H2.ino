#include <Wire.h>
#include <DS1302.h>

// Pines del RTC DS1302
#define RST_PIN 7
#define DAT_PIN 6
#define CLK_PIN 5

DS1302 rtc(RST_PIN, DAT_PIN, CLK_PIN);

#define TILT1_PIN 2
#define TILT2_PIN 3
#define MIC_PIN   A0

void setup() {
  Wire.begin(8); // Dirección I2C del Hijo 2
  Wire.onRequest(requestEvent);

  pinMode(TILT1_PIN, INPUT);
  pinMode(TILT2_PIN, INPUT);
  pinMode(MIC_PIN, INPUT);

  rtc.halt(false);      // Inicia el RTC si estaba detenido
  rtc.writeProtect(false);
}

void loop() {
  delay(1000);
}

void requestEvent() {
  uint8_t tilt1 = digitalRead(TILT1_PIN);
  uint8_t tilt2 = digitalRead(TILT2_PIN);
  uint16_t mic  = analogRead(MIC_PIN);

  // Obtener la hora actual correctamente
  Time t = rtc.time();

  // Generar timestamp simple: hhmmss
  uint32_t timestamp = (uint32_t)t.hr * 10000 + t.min * 100 + t.sec;

  // Enviar 8 bytes por I2C
  Wire.write(tilt1);
  Wire.write(tilt2);
  Wire.write((mic >> 8) & 0xFF);
  Wire.write(mic & 0xFF);
  Wire.write((timestamp >> 24) & 0xFF);
  Wire.write((timestamp >> 16) & 0xFF);
  Wire.write((timestamp >> 8) & 0xFF);
  Wire.write(timestamp & 0xFF);
}
