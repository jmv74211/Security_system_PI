import telebot              # Telegram API
import os                   # Environment vars 
from telebot import types   # Import to use telegram buttons
import requests,json        # Imports to make an decode requests
import time                 # Import to use sleep and strftime
from functools import wraps # Import to ouse decoration functions

# TOKEN API telegram. It is added in environmet vars. 
TOKEN = os.environ['SECURITY_CAMERA_TELEGRAM_BOT_TOKEN']

# Credentials for module login. They are added in enviroment vars.
security_user = os.environ.get('SECURITY_USER')
password_security_user = os.environ.get('SECURITY_CAMERA_USER_PASSWORD')

# Credentials telegram authentication.
telegram_user_id = int(os.environ.get('TELEGRAM_USER_ID'))
telegram_username = os.environ.get('TELEGRAM_USERNAME')


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
    Function to check if the user has permission to access, checking the message.from_user.id
    and message.from_user.username
"""

def authtentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        # White list of allowd users
        allowed_users = {'users':
                        [{'id':telegram_user_id,'username':telegram_username},
                        ]}
        allowed = False
        
        message = args[0]
        user_id = message.from_user.id
        username = message.from_user.username

        for item in allowed_users['users']:
            if user_id == item['id'] and username == item['username']:
                allowed = True
        
        if not allowed:
            bot.send_message(message.chat.id,"You have not permission to access to this content" )
            return -1

        return f(*args, **kwargs)

    return decorated


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
@authtentication_required
def send_photo(message):
    chat_id = message.chat.id

    payload = {'username':security_user,'password':password_security_user}

    photo_request = requests.post(main_agent_host + "/take_photo", json = payload)

    print("A photo has been taken...")

    photo_path_request = requests.get(main_agent_host + "/give_last_photo_path", json = payload)

    photo_path_data_response = photo_path_request.json()

    photo_path = photo_path_data_response['response']
    
    bot.send_message(chat_id,"Photo taken at " + time.strftime("%x") + "-" + time.strftime("%X") )

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
@authtentication_required
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
    
    bot.send_message(chat_id, "Video recorded at " + time.strftime("%x") + "-" + time.strftime("%X") )
    
    bot.send_video(chat_id, video)
    
    print("Video has been sent")

##############################################################################################

"""
    Enable automatic mode. It activates the motion agent and streaming server. IN addition,
    checks if exist and alert, in that case send a video o photo message.
"""

@bot.message_handler(commands=['automatic'])
@authtentication_required
def enable_automatic_mode(message):
    
    global mode
    chat_id = message.chat.id
    payload = {'username':security_user,'password':password_security_user}
    
    motion_agent_mode = "photo"
    # Extract arguments list command
    argument_list = extract_arg(message.text)
    if len(argument_list) > 0 and argument_list[0] == "video":
        motion_agent_mode = "video"
        
    payload = {'username':security_user,'password':password_security_user,'motion_agent_mode':motion_agent_mode}
    
    if mode == "manual" or mode == "streaming":
        
        # If we are in streaming mode, we need to deactivate the streaming server
        if mode == "streaming":
            # request to deactivate the streaming server.
            deactivate_streaming_server_request = requests.post(main_agent_host + "/deactivate_streaming_mode", json = payload)
            if deactivate_streaming_server_request.status_code == 200: # OK
                 bot.send_message(chat_id, "Streaming mode deactivated successfully!")
            else:
                bot.send_message(chat_id, "Error: Streaming mode can not be deactivated")
        
        mode = "automatic"
        # request to activate the motion agent
        activate_motion_agent_request = requests.post(main_agent_host + "/activate_motion_agent", json = payload)
        if activate_motion_agent_request.status_code != 200: # OK
                 bot.send_message(chat_id, "Error. Motion agent can not be activated!")
        
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
            
            if motion_agent_mode == "photo":
                photo_path_request = requests.get(main_agent_host + "/give_last_photo_path", json = payload)

                photo_path_data_response = photo_path_request.json()

                photo_path = photo_path_data_response['response']

                photo = open(photo_path, 'rb')

                print("Sending photo alert!....")
                
                bot.send_message(chat_id, "Alert at " + time.strftime("%x") + "-" + time.strftime("%X") )

                bot.send_photo(chat_id, photo)
            else:
                
                video_path_request = requests.get(main_agent_host + "/give_last_video_path", json = payload)

                video_path_data_response = video_path_request.json()

                video_path = video_path_data_response['response']

                video = open(video_path, 'rb')

                print("Sending video alert!....")
                
                bot.send_message(chat_id, "Alert at " + time.strftime("%x") + "-" + time.strftime("%X") )

                bot.send_video(chat_id, video)
       
        time.sleep(time_refresh_check_alert)
     
        
##############################################################################################
  
"""
    Enable manual mode. It deactivates the motion agent or streaming server.
"""  
  
@bot.message_handler(commands=['manual'])
@authtentication_required
def enable_manual_mode(message):
    
    global mode
    chat_id = message.chat.id
    payload = {'username':security_user,'password':password_security_user}
    
    if mode == "automatic" or mode == "streaming":
        
        if mode == "streaming":
            # request to deactivate the streaming server.
            deactivate_streaming_server_request = requests.post(main_agent_host + "/deactivate_streaming_mode", json = payload)
            if deactivate_streaming_server_request.status_code == 200: # OK
                 bot.send_message(chat_id, "Streaming mode deactivated successfully!")
            else:
                bot.send_message(chat_id, "Error: Streaming mode can not be deactivated")
        elif mode == "automatic":
             # request to deactivate the motion agent.
             deactivate_motion_agent_request = requests.post(main_agent_host + "/deactivate_motion_agent", json = payload)
             if deactivate_motion_agent_request.status_code == 200: # OK
                 bot.send_message(chat_id, "Automatic mode deactivated successfully!")
             else:
                bot.send_message(chat_id, "Error: Automatic mode can not be deactivated")
             
        mode = "manual"       
        print("Mode selected: Manual")
        bot.send_message(chat_id, "Mode selected: Manual")
    else:
        bot.send_message(chat_id, "You are already in manual mode!")

##############################################################################################
  
"""
    Get the current mode.
"""  
  
@bot.message_handler(commands=['gmode'])
@authtentication_required
def get_mode(message):
    
    chat_id = message.chat.id
    if mode == "automatic":
         bot.send_message(chat_id,"Current mode: Automatic")
    elif mode == "streaming":
        bot.send_message(chat_id,"Current mode: Streaming")
    else:
         bot.send_message(chat_id,"Current mode: Manual")    
    
##############################################################################################
  
"""
    Enable streaming mode. It deactivates the motion agent.
"""  
  
@bot.message_handler(commands=['streaming'])
@authtentication_required
def enable_streaming_mode(message):
    
    global mode
    chat_id = message.chat.id
    payload = {'username':security_user,'password':password_security_user}
    
    if mode == "automatic" or mode == "manual":
        
        if mode == "automatic":
            # request to deactivate the motion agent.
            deactivate_motion_agent_request = requests.post(main_agent_host + "/deactivate_motion_agent", json = payload)
            if deactivate_motion_agent_request .status_code == 200: # OK
                 bot.send_message(chat_id, "Automatic mode deactivated successfully!")
            else:
                bot.send_message(chat_id, "Error: Automatic mode can not be deactivated")
        
        mode = "streaming"
   
        activate_streaming_server_request = requests.post(main_agent_host + "/activate_streaming_mode", json = payload)
        if activate_streaming_server_request.status_code == 200: # OK
            bot.send_message(chat_id, "Mode selected: Streaming")
            print("Mode selected: Streaming")
        else:
            bot.send_message(chat_id, "Error: Streaming mode can not be deactivated")
            print("Error: Streaming mode can not be deactivated")
    else:
        bot.send_message(chat_id, "You are already in streaming mode!")


##############################################################################################
   
"""
    Return current mode
"""     
   
@bot.message_handler(commands=['chat'])
def get_chat_id(message):
    chat_id = message.chat.id
    
    bot.send_message(chat_id, chat_id)
    

##############################################################################################
#                                   BUTTONS INTERFACE                                        #        
##############################################################################################

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

start_keyboard = types.ReplyKeyboardMarkup(row_width = 2,
                                  resize_keyboard = True,
                                  one_time_keyboard = False,
                                  selective = False,
                                  )

start_keyboard_button1 = types.KeyboardButton('/photo')
start_keyboard_button2 = types.KeyboardButton('video')
start_keyboard_button3 = types.KeyboardButton('automatic')
start_keyboard_button4 = types.KeyboardButton('/streaming')

start_keyboard.add(start_keyboard_button1,start_keyboard_button2,start_keyboard_button3,start_keyboard_button4)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

automatic_mode_keyboard = types.ReplyKeyboardMarkup(row_width = 2,
                                  resize_keyboard = True,
                                  one_time_keyboard = False,
                                  selective = False,
                                  )

automatic_mode_button1 = types.KeyboardButton('/automatic photo')
automatic_mode_button2 = types.KeyboardButton('/automatic video')

automatic_mode_keyboard.add(automatic_mode_button1,automatic_mode_button2)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

video_keyboard = types.ReplyKeyboardMarkup(row_width = 2,
                                  resize_keyboard = True,
                                  one_time_keyboard = False,
                                  selective = False,
                                  )

video_button1 = types.KeyboardButton('/video 5')
video_button2 = types.KeyboardButton('/video 10')
video_button3 = types.KeyboardButton('/video 15')
video_button4 = types.KeyboardButton('/video 30')
video_button5 = types.KeyboardButton('/video 60')


video_keyboard.add(video_button1,video_button2,video_button3,video_button4,video_button5)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


mode_keyboard = types.ReplyKeyboardMarkup(row_width = 3,
                                  resize_keyboard = True,
                                  one_time_keyboard = False,
                                  selective = False,
                                  )

mode_keyboard_button1 = types.KeyboardButton('/manual')
mode_keyboard_button2 = types.KeyboardButton('/automatic')
mode_keyboard_button3 = types.KeyboardButton('/streaming')

mode_keyboard.add(mode_keyboard_button1,mode_keyboard_button2,mode_keyboard_button3)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


@bot.message_handler(commands=['start'])
def keyboard_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Choose one option:", reply_markup=start_keyboard)
          
@bot.message_handler(regexp="automatic")
def keyboard_automatic(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Choose one option:", reply_markup=automatic_mode_keyboard)
 
@bot.message_handler(regexp="video")
def keyboard_video(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Choose one option:", reply_markup=video_keyboard)
    
@bot.message_handler(commands=['mode'])
def keyboard_mode(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Choose one option:", reply_markup=mode_keyboard)


##############################################################################################


# bot running
bot.polling()