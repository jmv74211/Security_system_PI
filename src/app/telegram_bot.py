import telebot            # Telegram API
import os                 # Environment vars 
from telebot import types # Import to use telegram buttons
import requests,json      # Imports to make an decode requests
import time               # Import to use sleep

# TOKEN API telegram. It is added in environmet vars. 
TOKEN = os.environ['SECURITY_CAMERA_TELEGRAM_BOT_TOKEN']

# Credentials for module login. They are added in enviroment vars.
security_user = os.environ.get('SECURITY_USER')
password_security_user = os.environ.get('SECURITY_CAMERA_USER_PASSWORD')

# Host URL and port
main_agent_host = "http://192.168.1.100:10000"

# Bot instance
bot = telebot.TeleBot(TOKEN)

# Bot mode
mode = "manual"

# Time (in seconds) to make request and check if exist an alert in main agent caused by
# motion agent. It is specified in automatic mode.
time_refresh_check_alert = 1

print("Bot is running!")

##############################################################################################

"""
    Function to get parameter arguments
"""

def extract_arg(arg):
    return arg.split()[1:]

##############################################################################################

"""
    Take a photo and send it using /photo command
"""

@bot.message_handler(commands=['photo'])
def send_photo(message):
    chat_id = message.chat.id

    payload = {'username':security_user,'password':password_security_user}

    photo_request = requests.post(main_agent_host + "/take_photo", json = payload)

    print("A photo has been taken...")

    photo_path_request = requests.get(main_agent_host + "/give_last_photo_path", json = payload)

    photo_path_data_response = photo_path_request.json()

    photo_path = photo_path_data_response['response']

    photo = open(photo_path, 'rb')

    print("Sending photo....")

    bot.send_photo(chat_id, photo)
    
    print("Photo has been sent")
    
##############################################################################################

"""
    Record a video and send it using /video command. it can be specified a time parameter
    in seconds to recording
"""

@bot.message_handler(commands=['video'])
def send_video(message):
    
    # Extract arguments list command
    argument_list = extract_arg(message.text)
    
    record_time = 10 # Default record time = 10 seconds
    
    chat_id = message.chat.id
    
    if len(argument_list) > 0: # Means that video command has one or more parameters
        record_time = int(argument_list[0]) # Get the time parameters in seconds
        payload = {'username':security_user,'password':password_security_user,'recordtime':record_time}
    else:
        payload = {'username':security_user,'password':password_security_user}

    bot.send_message(chat_id, "It is going to be recorded a video with {} seconds length".format(record_time))

    video_request = requests.post(main_agent_host + "/record_video", json = payload)

    print("A video with {} seconds length has been recorded...".format(record_time))

    video_path_request = requests.get(main_agent_host + "/give_last_video_path", json = payload)

    video_path_data_response = video_path_request.json()

    video_path = video_path_data_response['response']

    video = open(video_path, 'rb')

    print("Sending video...")
    
    bot.send_message(chat_id, "Video has been recording. Sending...")
    
    bot.send_video(chat_id, video)
    
    print("Video has been sent")

##############################################################################################

"""
    Enable automatic mode. It activates the motion agent and checks if exist and alert, in
    that case send an alert message.
"""

@bot.message_handler(commands=['automatic'])
def enable_automatic_mode(message):
    
    global mode
    chat_id = message.chat.id
    payload = {'username':security_user,'password':password_security_user}
    
    if mode == "manual":
        mode = "automatic"
        # request to activate the motion agent
        activate_motion_agent_request = requests.post(main_agent_host + "/activate_motion_agent", json = payload)
        print("Mode selected: Automatic")
        bot.send_message(chat_id, "Mode selected: Automatic")
    else:
        bot.send_message(chat_id, "You are already in automatic mode!")
        
    while mode == "automatic":
        # request to check if there is a motion agent alert
        check_motion_agent_request = requests.get(main_agent_host + "/check_motion_agent_alert", json = payload)

        check_motion_agent_data_response = check_motion_agent_request.json()

        alert = check_motion_agent_data_response['alert']
                
        if alert == True:
            bot.send_message(chat_id, "Alert!")
        
        time.sleep(time_refresh_check_alert)
        
        
        

##############################################################################################
  
"""
    Enable manual mode. It deactivates the motion agent.
"""  
  
@bot.message_handler(commands=['manual'])
def enable_manual_mode(message):
    
    global mode
    chat_id = message.chat.id
    payload = {'username':security_user,'password':password_security_user}
    
    if mode == "automatic":
        mode = "manual"
        # request to deactivate the motion agent.
        deactivate_motion_agent_request = requests.post(main_agent_host + "/deactivate_motion_agent", json = payload)
        print("Mode selected: Manual")
        bot.send_message(chat_id, "Mode selected: Manual")
    else:
        bot.send_message(chat_id, "You are already in manual mode!")
        
# bot running
bot.polling()