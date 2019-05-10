import RPi.GPIO as GPIO    # Import to manage PIN board
from time import sleep     # Import to sleep function
import os                  # Import to get environments vars value
import requests            # Import to make requests to main API
import sys                 # Import to read params program

##############################################################################################

# Set pin recognition.The other method is #GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)

# Set the pin where sensor is connected. #sensor = 23
sensor = 16

# Time to wait until check movement sensor status
refresh_time = 0.5

# Credentials for module login. They are added in enviroment vars.
security_user = os.environ.get('SECURITY_USER')
password_security_user = os.environ.get('SECURITY_CAMERA_USER_PASSWORD')

# main agent host URL
main_agent_host = "http://192.168.1.100:10000"

# Set pin mode as input
GPIO.setup(sensor,GPIO.IN)

# Motion_agent_mode
motion_agent_mode = "photo"

##############################################################################################

"""
The motion agent idea is:
 1. Dectect a sensor movement
 2. Send a request to take a picture/video
 3. Send a request to obtain the picture/video path
 4. Send a request to generate an alert in main agent
"""

# If program has a video parameter
if len(sys.argv) > 1 and sys.argv[1] == "video":
    motion_agent_mode = "video"    

while True:
    sleep(refresh_time)
    if GPIO.input(16):
        print("ACTIVADOO!")
        payload = {'username':security_user,'password':password_security_user}
        
        if motion_agent_mode == "photo": # photo mode
            photo_request = requests.post(main_agent_host + "/take_photo", json = payload)
            photo_path_request = requests.get(main_agent_host + "/give_last_photo_path", json = payload)
            photo_path_data_response = photo_path_request.json()
            file_path = photo_path_data_response['response']
        else: # video mode
            video_request = requests.post(main_agent_host + "/record_video", json = payload)
            sleep(15) # Wait 15 seconds until the video capture is complete.
            video_path_request = requests.get(main_agent_host + "/give_last_video_path", json = payload)
            video_path_data_response = video_path_request.json()
            file_path = video_path_data_response['response']
        
        payload = {'username':security_user,'password':password_security_user, "file_path":file_path}
        motion_agent_request = requests.post(main_agent_host + "/generate_motion_agent_alert", json = payload)
        
    else:
        print("OFF")
    