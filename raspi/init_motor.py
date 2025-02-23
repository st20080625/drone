import pigpio
from time import sleep
from threading import Thread

pwm_pin1 = 12
pwm_pin2 = 13
pwm_pin3 = 18
pwm_pin4 = 19
pi = pigpio.pi()

#1000hzでDuty比のvalueが32~65の範囲でESCが動作(32より下なら回転しない)
pwm_freq = 1000
class Motor:
    def __init__(self, pin, freq):
        self.pin = pin
        self.pwm_freq = freq
        self.duty_cycle = 0
        self.value = 0

    def set_throttle(self, value):
        self.value = value
        self.duty_cycle = int((self.value / 255) * 1000000)
        pi.hardware_PWM(self.pin, self.pwm_freq, self.duty_cycle)

    def init_motor(self):
        print("ESC 初期化開始...")
        self.set_throttle(255)  # 最大スロットル
        sleep(5)
        self.set_throttle(10)   # 最小スロットル
        sleep(5)
        print("ESC 初期化完了")

motor1 = Motor(pwm_pin1, pwm_freq)
motor2 = Motor(pwm_pin2, pwm_freq)
motor3 = Motor(pwm_pin3, pwm_freq)
motor4 = Motor(pwm_pin4, pwm_freq)

def init_motor(motor):
    motor.init_motor()

init_thread1 = Thread(target=init_motor, args=(motor1,))
init_thread2 = Thread(target=init_motor, args=(motor2,))
init_thread3 = Thread(target=init_motor, args=(motor3,))
init_thread4 = Thread(target=init_motor, args=(motor4,))

init_thread1.start()
init_thread2.start()
init_thread3.start()
init_thread4.start()

init_thread1.join()
init_thread2.join()
init_thread3.join()
init_thread4.join()

def main(motor):
    for i in range(32, 65, 1):
        motor.set_throttle(i)
        sleep(1)

main_thread1 = Thread(target=main, args=(motor1,))
main_thread2 = Thread(target=main, args=(motor2,))
main_thread3 = Thread(target=main, args=(motor3,))
main_thread4 = Thread(target=main, args=(motor4,))

main_thread1.start()
main_thread2.start()
main_thread3.start()
main_thread4.start()

main_thread1.join()
main_thread2.join()
main_thread3.join()
main_thread4.join()