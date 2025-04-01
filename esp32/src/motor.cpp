#include <Arduino.h>
#include "motor.hpp"

motor::motor(int pwm_pin, int ch) : pwm_pin(pwm_pin), ch(ch){}
void motor::set_freq(int value){
    ledcWrite(ch, value);
}