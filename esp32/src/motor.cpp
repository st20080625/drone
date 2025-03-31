#include <Arduino.h>
#include "motor.hpp"

motor::motor(int pwm_pin, int ch) : pwm_pin(pwm_pin), ch(ch){}

void motor::init(){
    ledcSetup(ch, 1000, 8);
    ledcAttachPin(pwm_pin, ch);
    ledcWrite(ch, 255);
    Serial.print("init_motor ch:");
    Serial.println(ch);
    delay(5000);
    ledcWrite(ch, 1);
    delay(500);
    Serial.print("end_init_motor ch:");
    Serial.println(ch);
}

void motor::set_freq(int value){
    ledcWrite(ch, value);
}