import telebot            # Telegram API
import os                 # Environment vars 
from telebot import types # Import to use telegram buttons
import requests,json      # Imports to make an decode requests

# TOKEN API telegram. It is added in environmet vars. 
TOKEN = os.environ['SECURITY_CAMERA_TELEGRAM_BOT_TOKEN']

# Credentials for module login. They are added in enviroment vars.
security_user = os.environ.get('SECURITY_USER')
password_security_user = os.environ.get('SECURITY_CAMERA_USER_PASSWORD')

main_agent_host = "http://192.168.1.100:10000"

# Bot instance
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['take'])
def start2(message):
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

print("El bot se está ejecutando!")

# Ejecutamos el programa
bot.polling()
