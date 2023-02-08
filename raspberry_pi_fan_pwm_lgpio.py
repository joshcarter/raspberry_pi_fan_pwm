#!/usr/bin/python3

# NOTE: this version uses lgpio instead of gpiozero. It will consume a lot of CPU because lgpio uses software PWM.
# Only use if pigpiod is not available.

import math
import os
import sys
import lgpio
import time
import psutil

FAN = 18        # PWM output; GPIO18/PWM0/physical pin 12
FREQ = 10000    # PWM frequency; 10KHz. Noctua NF-A4x10 PWM fan works well at this frequency.
                # Docs say 25KHz is ideal but Pi GPIO won't do 25KHz.
TEMP_LOW = 40   # Turn off fan below this value
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
    last_temp = 0.0
    h = lgpio.gpiochip_open(0)

    try:
        while True:
            temp = current_temp()
            if math.fabs(temp - last_temp) < 2.0:
                # don't change fan speed if temp hasn't changed much
                log(f'temp: {temp}, last_temp: {last_temp}, pwm: unchanged')
                time.sleep(5)
                continue

            # scale pwm output from 20% to 100% based on temp range
            pwm: float = 20 + (temp - TEMP_LOW) * 80 / (TEMP_HIGH - TEMP_LOW)
            if temp > TEMP_HIGH:
                pwm = 100.0
            elif temp < TEMP_LOW:
                pwm = 0.0

            log(f'temp: {temp}, pwm: {pwm}')
            lgpio.tx_pwm(h, FAN, FREQ, math.floor(pwm + 0.5))
            last_temp = temp
            time.sleep(5)
    except KeyboardInterrupt:
        lgpio.tx_pwm(h, FAN, FREQ, 50)
    finally:
        lgpio.gpiochip_close(h)


if __name__ == '__main__':
    run()
