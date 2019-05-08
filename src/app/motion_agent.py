import RPi.GPIO as GPIO
from time import sleep

#GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)

sensor = 16
refresh_time = 0.1

#GPIO.setup(23,GPIO.IN)
GPIO.setup(sensor,GPIO.IN)

while True:
    sleep(refresh_time)
    if GPIO.input(16):
        print("ACTIVADOO!")
    else:
        print("OFF")
    