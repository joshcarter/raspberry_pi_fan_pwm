# Raspberry Pi 4 PWM Fan Control

This is a script to control the fan speed of a Raspberry Pi 4 based on the CPU temperature. It uses libraries
available in Ubuntu Server 22.04 LTS. It has been tested on a Raspberry Pi 4 and Noctua NF-A4x10 5V PWM (4 pin) fan.

It seems like there should be something built into Ubuntu which does proper PWM fan control, but I was having problems
with everything google suggested to me, so I wrote this.

## Hardware

The Noctua NF-A4x10 5V PWM (4 pin) fan is connected to the Raspberry Pi 4 GPIO pins as follows:

1. 5V (yellow wire) to physical pin 4
2. GND (black wire) to physical pin 6
3. PWM (blue wire) to physical pin 12

## Software

This uses the pigpio and gpiozero libraries. First, install required build tools and Python libraries:

    apt install python3-gpiozero python3-pigpio python3-psutil unzip build-essential

### pigpio download and service

pigpio requires its own deamon to be running, and for some reason there's no prebuilt package for this. Download and
install using directions here:

https://abyz.me.uk/rpi/pigpio/download.html

I also create a service for the daemon. Create service file `/lib/systemd/system/pigpiod.service`:

	[Unit]
	Description=Daemon required to control GPIO pins via pigpio
	[Service]
	ExecStart=/usr/local/bin/pigpiod -l -m -s 10
	ExecStop=/bin/systemctl kill -s SIGKILL pigpiod
	Type=forking
	[Install]
	WantedBy=multi-user.target

NOTE: this service file disables pigpiod alert sampling and also decreases the polling interval. If you have other uses
for GPIO you may need to take out the `-l -m -s 10` options in the service file above. 

Run the service using:

    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod

### fan_control service

Install the provided script like so:

    chmod u+x raspberry_pi_fan_pwm.py 
    sudo cp raspberry_pi_fan_pwm.py /usr/local/bin/fan_control

Create service file `/lib/systemd/system/fan_control.service`:

    [Unit]
    Description=Fan Control
    After=pigpiod.service
    [Service]
    Type=simple
    ExecStart=/usr/local/bin/fan_control
    Restart=on-success
    [Install]
    WantedBy=multi-user.target

Run the service using:

    sudo systemctl enable fan_control
    sudo systemctl start fan_control

## License

This script is released under the MIT license terms; see `LICENSE` for details.
