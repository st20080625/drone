#include <Arduino.h>
#include <Adafruit_BNO08x.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include "motor.hpp"

#define SDA_PIN 21
#define SCL_PIN 22

int pwm1 = 14;
int pwm2 = 15;
int pwm3 = 16;
int pwm4 = 17;

motor motor1(pwm1, 0);
motor motor2(pwm2, 1);
motor motor3(pwm3, 2);
motor motor4(pwm4, 3);

Adafruit_BNO08x bno08x;

const char *ssid = "Synology-home";
const char *password = "Wi.LL'-ad6es4";

const char *send_ip = "192.168.1.23";

const uint16_t send_port1 = 5000;
const uint16_t send_port2 = 5001;
const uint16_t recv_port1 = 5002;

WiFiUDP udp;
// シャットダウンの際のリセット等は不要であれば設定不要
#define BNO08X_RESET -1

IPAddress myip;

float r, i, j, k;

void send_sensor_task(void *pvParameters)
{
  while (true)
  {
    sh2_SensorValue_t sensorValue;

    if (bno08x.getSensorEvent(&sensorValue))
    {
      if (sensorValue.sensorId == SH2_ARVR_STABILIZED_RV)
      {
        r = sensorValue.un.rotationVector.real;
        i = sensorValue.un.rotationVector.i;
        j = sensorValue.un.rotationVector.j;
        k = sensorValue.un.rotationVector.k;
      }

      StaticJsonDocument<128> jsonDoc; // サイズを最適化
      jsonDoc["r"] = r;
      jsonDoc["i"] = i;
      jsonDoc["j"] = j;
      jsonDoc["k"] = k;

      char jsonBuffer[128]; // バッファサイズを縮小
      size_t len = serializeJson(jsonDoc, jsonBuffer);

      udp.beginPacket(send_ip, send_port1);
      udp.write((uint8_t *)jsonBuffer, len);
      udp.endPacket();

      udp.beginPacket(send_ip, send_port2);
      udp.write((uint8_t *)jsonBuffer, len);
      udp.endPacket();

      vTaskDelay(pdMS_TO_TICKS(50)); // 遅延を効率化
    }
  }
}

void controll_motor_task(void *pvParameters)
{
  char incoming_packet[128]; // バッファサイズを縮小
  while (true)
  {
    int packet_size = udp.parsePacket();

    if (packet_size)
    {
      int len = udp.read(incoming_packet, sizeof(incoming_packet) - 1);
      if (len > 0)
      {
        incoming_packet[len] = '\0';
      }

      Serial.print("received packet:");
      Serial.println(incoming_packet);

      StaticJsonDocument<128> jsonDoc; // サイズを最適化
      DeserializationError error = deserializeJson(jsonDoc, incoming_packet);
      if (error)
      {
        Serial.print("Json parse error: ");
        Serial.println(error.c_str());
        continue;
      }

      if (jsonDoc.containsKey("M1") && jsonDoc.containsKey("M2") &&
          jsonDoc.containsKey("M3") && jsonDoc.containsKey("M4"))
      {
        float M1 = jsonDoc["M1"];
        float M2 = jsonDoc["M2"];
        float M3 = jsonDoc["M3"];
        float M4 = jsonDoc["M4"];

        Serial.print("M1: ");
        Serial.println(M1);
        Serial.print("M2: ");
        Serial.println(M2);
        Serial.print("M3: ");
        Serial.println(M3);
        Serial.print("M4: ");
        Serial.println(M4);
      }
      else
      {
        Serial.println("JSON does not contain required keys (M1, M2, M3, M4).");
      }
    }


    vTaskDelay(pdMS_TO_TICKS(50)); // 遅延を効率化
  }
}

void setup()
{
  Serial.begin(115200);
  while (!Serial)
    delay(10);

  Wire.begin(SDA_PIN, SCL_PIN);

  if (!bno08x.begin_I2C(0x4B))
  {
    Serial.println("BNO08x not detected");
    while (1)
      delay(10);
  }
  Serial.println("BNO08x detected!");

  if (!bno08x.enableReport(SH2_ARVR_STABILIZED_RV, 500))
  {
    Serial.println("Failed to enable stabilized remote vector");
    while (1)
      delay(10);
  }
  Serial.println("Rotation Vector Report Enabled!");

  //motor_freq max 67 , min 33
  motor1.init();
  //motor2.init();
  //motor3.init();
  //motor4.init();

  // WiFi接続（リトライ制限なし）
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected!");

  myip = WiFi.localIP();
  Serial.print("myip:");
  Serial.println(myip);

  udp.begin(recv_port1);
  Serial.print("Listening on UDP port ");
  Serial.println(recv_port1);

  //xTaskCreate(send_sensor_task, "send_sensor", 2048, NULL, 2, NULL);
  //xTaskCreate(controll_motor_task, "controll_motor", 2048, NULL, 1, NULL);
}
void loop(){
  motor1.set_freq(45);
}