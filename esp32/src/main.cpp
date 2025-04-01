#include <Arduino.h>
#include <Adafruit_BNO08x.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include "motor.hpp"

#define SDA_PIN 21
#define SCL_PIN 22

int pwm1 = 13;
int pwm2 = 12;
int pwm3 = 14;
int pwm4 = 27;

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
  int no_data_counter = 0;   // データが受信されなかった回数をカウント
  const int max_no_data_loops = 10; // 10ループ（約500ms）

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
        int M1 = jsonDoc["M1"];
        int M2 = jsonDoc["M2"];
        int M3 = jsonDoc["M3"];
        int M4 = jsonDoc["M4"];

        Serial.print("M1: ");
        Serial.println(M1);
        Serial.print("M2: ");
        Serial.println(M2);
        Serial.print("M3: ");
        Serial.println(M3);
        Serial.print("M4: ");
        Serial.println(M4);

        motor1.set_freq(M1);
        motor2.set_freq(M2);
        motor3.set_freq(M3);
        motor4.set_freq(M4);

        // データが受信されたのでカウンタをリセット
        no_data_counter = 0;
      }
      else
      {
        Serial.println("JSON does not contain required keys (M1, M2, M3, M4).");
      }
    }
    else
    {
      // データが受信されなかった場合、カウンタを増加
      no_data_counter++;

      // カウンタが10ループに達した場合、モーターを33に設定
      if (no_data_counter >= max_no_data_loops)
      {
        motor1.set_freq(32);
        motor2.set_freq(32);
        motor3.set_freq(32);
        motor4.set_freq(32);

        Serial.println("No data received for 10 loops. Motors set to 33.");
        no_data_counter = 0; // カウンタをリセット
      }
    }

    vTaskDelay(pdMS_TO_TICKS(50)); // 遅延を効率化
  }
}

IPAddress esp_ip(192,168,1,38);
IPAddress gateway(192,168,1,1);
IPAddress subnet(255,255,255,0);

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
  ledcSetup(0, 1000, 8);
  ledcSetup(1, 1000, 8);
  ledcSetup(2, 1000, 8);
  ledcSetup(3, 1000, 8);

  ledcAttachPin(pwm1, 0);
  ledcAttachPin(pwm2, 1);
  ledcAttachPin(pwm3, 2);
  ledcAttachPin(pwm4, 3);

  //motor_freq max 67 , min 33
  motor1.set_freq(255);
  motor2.set_freq(255);
  motor3.set_freq(255);
  motor4.set_freq(255);

  delay(3000);
  motor1.set_freq(2);
  motor2.set_freq(2);
  motor3.set_freq(2);
  motor4.set_freq(2);
  
  delay(1000);

  // WiFi接続（リトライ制限なし）
  WiFi.config(esp_ip, gateway, subnet);
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

  xTaskCreate(send_sensor_task, "send_sensor", 2048, NULL, 1, NULL);
  xTaskCreate(controll_motor_task, "controll_motor", 2048, NULL, 1, NULL);
}
void loop(){
}