#ifndef COMPASS_HPP
#define COMPASS_HPP

#include <Arduino.h>

class motor
{
private:
    int pwm_pin;
    int ch;
public:
    motor(int pwm_pin, int ch);
    void init(int value);
    void set_freq(int value);
};
#endif
