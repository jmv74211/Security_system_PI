import RPi.GPIO as GPIO
from time import sleep
import os
import requests

##############################################################################################

#GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)

sensor = 16
refresh_time = 0.5

# Credentials for module login. They are added in enviroment vars.
security_user = os.environ.get('SECURITY_USER')
password_security_user = os.environ.get('SECURITY_CAMERA_USER_PASSWORD')

main_agent_host = "http://192.168.1.100:10000"

#GPIO.setup(23,GPIO.IN)
GPIO.setup(sensor,GPIO.IN)


##############################################################################################

"""
The motion agent idea is:
 1. Dectect a sensor movement
 2. Send a request to take a picture/video
 3. Send a request to obtain the picture/video path
 4. Send a request to generate an alert in main agent
"""
while True:
    sleep(refresh_time)
    if GPIO.input(16):
        print("ACTIVADOO!")
        payload = {'username':security_user,'password':password_security_user}
        photo_request = requests.post(main_agent_host + "/take_photo", json = payload)
        
        photo_path_request = requests.get(main_agent_host + "/give_last_photo_path", json = payload)
        photo_path_data_response = photo_path_request.json()
        photo_path = photo_path_data_response['response']
        
        payload = {'username':security_user,'password':password_security_user, "photo_path":photo_path}
        motion_agent_request = requests.post(main_agent_host + "/generate_motion_agent_alert", json = payload)
        
    else:
        print("OFF")
    