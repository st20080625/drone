#include <Arduino.h>
#include "motor.hpp"

motor::motor(int pwm_pin, int ch) : pwm_pin(pwm_pin), ch(ch){}

void motor::init(int value = 0){
    ledcSetup(ch, 1000, 8);
    ledcAttachPin(pwm_pin, ch);
    ledcWrite(ch, 255);
    Serial.print("init_motor ch:");
    Serial.println(ch);
    delay(3000);
    ledcWrite(ch, 1);
    delay(500);
    if (value == 1){
        delay(2500);
    }
    Serial.print("end_init_motor ch:");
    Serial.println(ch);
}

void motor::set_freq(int value){
    ledcWrite(ch, value);
}