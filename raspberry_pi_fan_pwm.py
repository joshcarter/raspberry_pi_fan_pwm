#!/usr/bin/python3

from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import PWMOutputDevice
import math
import psutil
import time
import os
import sys

FAN = 18        # PWM output; GPIO18/PWM0/physical pin 12
FREQ = 10000    # PWM frequency; 10KHz. Noctua NF-A4x10 PWM fan works well at this frequency.
                # Docs say 25KHz is ideal but Pi GPIO won't do 25KHz.
TEMP_LOW = 40   # Turn off fan below this value (celcius)
TEMP_HIGH = 70  # Run fan at 100% above this value; Pi 4 throttles around 80C
SHOULD_LOG = os.isatty(sys.stdout.fileno())  # Print log messages if running from interactive shell


def log(msg: str):
    if SHOULD_LOG:
        print(msg)

# Use if psutil is not available
# def current_temp() -> float:
#     with open('/sys/class/thermal/thermal_zone0/temp') as f:
#         return int(f.read()) / 1000.0

def current_temp() -> float:
    return psutil.sensors_temperatures()['cpu_thermal'][0].current


def run():
    pin = PWMOutputDevice(FAN, pin_factory=PiGPIOFactory(), frequency=FREQ)
    last_temp = 0.0

    try:
        while True:
            temp = current_temp()
            if math.fabs(temp - last_temp) < 2.0:
                # don't change fan speed if temp hasn't changed much
                log(f'temp: {temp}, last_temp: {last_temp}, pwm: unchanged')
                time.sleep(5)
                continue

            # scale pwm output from 20% to 100% based on temp range
            pwm: float = 0.2 + (temp - TEMP_LOW) * 0.8 / (TEMP_HIGH - TEMP_LOW)
            if temp > TEMP_HIGH:
                pwm = 1.0
            elif temp < TEMP_LOW:
                pwm = 0.0

            log(f'temp: {temp}, pwm: {pwm}')
            pin.value = pwm
            last_temp = temp
            time.sleep(5)
    except KeyboardInterrupt:
        pin.value = 0.5
    finally:
        pin.close()


if __name__ == '__main__':
    run()
