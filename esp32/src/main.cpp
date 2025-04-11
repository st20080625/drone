#include <Arduino.h>
#include <Adafruit_BNO08x.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

#define SDA_PIN 21
#define SCL_PIN 22

int pwm_pin0 = 25;
int pwm_pin1 = 12;
int pwm_pin2 = 27;
int pwm_pin3 = 26;

int motor_value0 = 0;
int motor_value1 = 0;
int motor_value2 = 0;
int motor_value3 = 0;

Adafruit_BNO08x bno08x;

const char *ssid = "Synology-home";
const char *password = "Wi.LL'-ad6es4";

const char *send_ip = "192.168.1.23";

const uint16_t send_port1 = 5001;
const uint16_t recv_port1 = 5000;

WiFiUDP udp;

char incoming_packet[128];        // バッファサイズを縮小
int no_data_counter = 0;          // データが受信されなかった回数をカウント
const int max_no_data_loops = 10; // 10ループ（約500ms）
int packet_size = udp.parsePacket();

// シャットダウンの際のリセット等は不要であれば設定不要
#define BNO08X_RESET -1

IPAddress myip;

IPAddress esp_ip(192, 168, 1, 38);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

float r, i, j, k;

float roll, pitch, yaw;

float target_roll, target_pitch, target_yaw;
int speed = 0;

float angles[3] = {};
float target_angles[3] = {};

float error_integral_roll = 0;
float error_integral_pitch = 0;
float error_integral_yaw = 0;

float previous_error_roll = 0;
float previous_error_pitch = 0;
float previous_error_yaw = 0;

float pid_output_roll = 0;
float pid_output_pitch = 0;
float pid_output_yaw = 0;

float kp_roll = 0.05, ki_roll = 0, kd_roll = 0;
float kp_pitch = 0.05, ki_pitch = 0, kd_pitch = 0;
float kp_yaw = 0, ki_yaw = 0, kd_yaw = 0;
float dt;

unsigned long sensor_previous_time = 0;
unsigned long sensor_current_time = 0;

float offset_roll;
float offset_pitch;

float pid(float target, float current, float &integral, float &previous_error, float kp, float ki, float kd) {
    float error = target - current;

    // アンチワインドアップ: 積分項の制限
    float integral_max = 50.0; // 積分項の最大値
    float integral_min = -50.0; // 積分項の最小値

    // 条件付き積分: エラーが一定範囲内の場合のみ積分を更新
    if (abs(error) > 0.1) { // エラーが0.1を超える場合のみ積分を更新
        if (abs(integral) < integral_max) {
            integral += error;
        }
    }

    // 積分項の減衰（オプション）
    bool use_integral_decay = true; // 積分項の減衰を有効化するかどうか
    if (use_integral_decay) {
        integral *= 0.99; // 減衰率を設定（0.0～1.0）
    }

    // 微分項の計算（フィルタリング付き）
    static float previous_derivative = 0;
    float derivative = (error - previous_error) / dt * 0.9 + previous_derivative * 0.1; // フィルタリング
    previous_derivative = derivative;

    // 前回のエラーを更新
    previous_error = error;

    // PID出力の計算
    return kp * error + ki * integral + kd * derivative;
}

void set_motor(int ch, float on_pulse_rate){
    float duty = (1000 + 10*on_pulse_rate)/20000;
    uint16_t value = duty*65535;
    value = round(value);
    ledcWrite(ch, value);
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
  ledcSetup(0, 50, 16);
  ledcSetup(1, 50, 16);
  ledcSetup(2, 50, 16);
  ledcSetup(3, 50, 16);

  ledcAttachPin(pwm_pin0, 0);
  ledcAttachPin(pwm_pin1, 1);
  ledcAttachPin(pwm_pin2, 2);
  ledcAttachPin(pwm_pin3, 3);

  //set_motor(ch, float on_pulse_rate)
  set_motor(0, 100);
  set_motor(1, 100);
  set_motor(2, 100);
  set_motor(3, 100);

  delay(1000);

  set_motor(0, 0);
  set_motor(1, 0);
  set_motor(2, 0);
  set_motor(3, 0);

  delay(1000);

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
  }
  offset_roll = atan2(2 * (r * i + j * k), 1 - 2 * (i * i + j * j)) * 180 / M_PI;
  offset_pitch = asin(2 * (r * j - k * i)) * 180 / M_PI;
}

unsigned long last_reset_time = 0;

void loop()
{
  sensor_current_time = millis();
  dt = (sensor_current_time - sensor_previous_time) / 1000.0;
  sensor_previous_time = sensor_current_time;

  // センサーのデータ取得と処理
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
    roll = roll * 0.95 + (atan2(2 * (r * i + j * k), 1 - 2 * (i * i + j * j)) * 180 / M_PI) * 0.05 - offset_roll;
    pitch = pitch * 0.95 + (asin(2 * (r * j - k * i)) * 180 / M_PI) * 0.05 - offset_pitch;
    yaw = yaw * 0.95 + (atan2(2 * (r * k + i * j), 1 - 2 * (j * j + k * k)) * 180 / M_PI) * 0.05;

    target_angles[0] = target_roll;
    target_angles[1] = target_pitch;
    target_angles[2] = target_yaw;

    Serial.print("roll");
    Serial.print(roll);
    Serial.print(",  ");
    Serial.print("pitch");
    Serial.print(pitch);
    Serial.print(",  ");
    Serial.print("yaw");
    Serial.print(yaw);
    Serial.println();
  }
  packet_size = udp.parsePacket();
  if (packet_size)
  {
    int len = udp.read(incoming_packet, sizeof(incoming_packet) - 1);
    if (len > 0)
    {
      incoming_packet[len] = '\0';
    }

    StaticJsonDocument<128> jsonDoc;
    DeserializationError error = deserializeJson(jsonDoc, incoming_packet);
    if (error)
    {
      return;
    }

    if (jsonDoc.containsKey("speed") && jsonDoc.containsKey("target_roll") &&
        jsonDoc.containsKey("target_pitch") && jsonDoc.containsKey("target_yaw"))
    {
      speed = jsonDoc["speed"];
      target_roll = jsonDoc["target_roll"];
      target_pitch = jsonDoc["target_pitch"];
      target_yaw = jsonDoc["target_yaw"];
      no_data_counter = 0;
    }

    Serial.print("speed:"); //0~100% 勝手にset_motorで速度調整される
    Serial.print(speed);
    Serial.print(",  ");
    Serial.print("target_roll:");
    Serial.print(target_roll);
    Serial.print(",  ");
    Serial.print("target_pitch:");
    Serial.print(target_pitch);
    Serial.print(",  ");
    Serial.print("target_yaw:");

    pid_output_roll = pid(target_roll, roll, error_integral_roll, previous_error_roll, kp_roll, ki_roll, kd_roll);
    pid_output_pitch = pid(target_pitch, pitch, error_integral_pitch, previous_error_pitch, kp_pitch, ki_pitch, kd_pitch);
    pid_output_yaw = pid(target_yaw, yaw, error_integral_yaw, previous_error_yaw, kp_yaw, ki_yaw, kd_yaw);

    pid_output_roll = constrain(pid_output_roll, -100, 100);
    pid_output_pitch = constrain(pid_output_pitch, -100, 100);
    pid_output_yaw = constrain(pid_output_yaw, -100, 100);

    motor_value0 = speed + pid_output_roll - pid_output_pitch;// + pid_output_yaw;
    motor_value1 = speed + pid_output_roll + pid_output_pitch;// - pid_output_yaw;
    motor_value2 = speed - pid_output_roll + pid_output_pitch;// - pid_output_yaw;
    motor_value3 = speed - pid_output_roll - pid_output_pitch;// + pid_output_yaw;

    motor_value0 = constrain(motor_value0, 0, 100);
    motor_value1 = constrain(motor_value1, 0, 100);
    motor_value2 = constrain(motor_value2, 0, 100);
    motor_value3 = constrain(motor_value3, 0, 100);

    set_motor(0, motor_value0);
    set_motor(1, motor_value1);
    set_motor(2, motor_value2);
    set_motor(3, motor_value3);
      
    Serial.print("motor_value0:");
    Serial.print(motor_value0);
    Serial.print(",  ");
    Serial.print("motor_value1:");
    Serial.print(motor_value1);
    Serial.print(",  ");
    Serial.print("motor_value2:");
    Serial.print(motor_value2);
    Serial.print(",  ");
    Serial.print("motor_value3:");
    Serial.print(motor_value3);
    Serial.println();
  }
  else
  {
    no_data_counter++;
    Serial.println("No data received");
    if (no_data_counter >= max_no_data_loops)
    {
      ledcWrite(0, 0);
      ledcWrite(1, 0);
      ledcWrite(2, 0);
      ledcWrite(3, 0);
      no_data_counter = 0;
    }
  }

  StaticJsonDocument<128> jsonDoc;
  jsonDoc["r"] = r;
  jsonDoc["i"] = i;
  jsonDoc["j"] = j;
  jsonDoc["k"] = k;

  char jsonBuffer[128];
  size_t len = serializeJson(jsonDoc, jsonBuffer);

  udp.beginPacket(send_ip, send_port1);
  udp.write((uint8_t *)jsonBuffer, len);
  udp.endPacket();

  delay(10);
}