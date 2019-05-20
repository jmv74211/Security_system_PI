# Security_system_PI

## Security system for control and video surveillance implemented on a raspberry PI

### Author: jmv74211

### Date: 29-04-2019

---

![Status](https://img.shields.io/badge/-RasperryPI-red.svg)
![Status](https://img.shields.io/badge/-Python-green.svg)
![Status](https://img.shields.io/badge/-Telegram-blue.svg)

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/Security_system_PI/master/images/raspytel.png">
</p>

![Status](https://img.shields.io/badge/Status-implementing-orange.svg)
![Status](https://img.shields.io/badge/Status-documenting-orange.svg)

---

# 1. Introduction

Security system PI is an application that allows us to build a security system based on low-cost video surveillance using a raspberry PI, a camera and a motion sensor.

The idea is to be able to control this device through a telegram bot connected to our API that controls the main system. The main functions are the following:
- Automatic system of alerts generated when capturing movement.
- Manual system to capture video or a photo instantly.
- Streaming system to visualize the image in real time.

---

# 2. Getting started.

## 2.1 Hardware required

As hardware devices to create our security system, we need the following components:

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/Security_system_PI/master/images/hardware_required.png">
</p>

When we talk about raspberry PI, we mean the set of elements necessary for it to work (Normally, it's always included in a pack), such as they are the power cord and SD card where we have installed an SO (in this case Raspbian).

### 2.1.1 Installation Guide

- First, you need to connect the raspicam to the raspberry PI and configure it to detect the camera. If you don't know how to do it, you can watch the following tutorial: https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera

- Once you have installed the camera and tested that it works, the next step is to install the motion sensor. To do this we have to connect the jumper wires as indicated in the following figure (pay attention to the colors that indicate where each pin has been connected)

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/Security_system_PI/master/images/hardware_connections.png">
</p>

- And that's it. Put the camera and sensor where you want to watch. For example, I have placed it as follows:

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/Security_system_PI/master/images/raspberry_place.png">
</p>

## 2.2 Telegram bot

First of all, you'll need to create a telegram bot and get the **BOT API key**. If you don't know how to do it, you can read the following documentation: https://www.sohamkamani.com/blog/2016/09/21/making-a-telegram-bot/

## 2.3 APP
Tested with python version 3.5.3 on Raspbian 9. The necessary libraries are indicated in the file [requeriments.txt](https://github.com/jmv74211/Security_system_PI/blob/master/requeriments.txt)

**Automatic deployment**

- Clone this repository.
- Go to the *config.yml* file located at `src/app/config.yml` and modify the parameters as indicated in the comments.
- Give execution permissions to the *deployment.sh* file with `sudo chmod u+x deployment.sh`.
- Execute the script *deployment.sh*, and the **main agent** and **telegram bot** processes will be executed in the background.

**Manual deployment**
- Clone this repository.
- Go to the *config.yml* file located at `src/app/config.yml` and modify the parameters as indicated in the comments.
- Install the dependencies indicated at [requeriments.txt](https://github.com/jmv74211/Security_system_PI/blob/master/requeriments.txt)
- Launch a shell, and run the *main_agent.py* process located at `src/app/main_agent.py`
- Launch another shell, and run the *telegram_bot.py* process located at `src/app/telegram_bot.py` (**Note: It is important that the main_agent is executed first and then telegram_bot**).

---

# 3. API Documentation

Once you have deployed and executed the application, you can make the following requests to your bot:

**Note:** All the following commands have to be executed in the conversation with the bot, and it will only attend to the user requests allowed in the white list of users (Located in [config.yml](https://github.com/jmv74211/Security_system_PI/blob/master/src/app/config.yml) or in allowed_users of the file [telegram_bot.py](https://github.com/jmv74211/Security_system_PI/blob/master/src/app/telegram_bot.py))

## 3.1 Modes
- `/manual`: The bot will be passive and will only attend to the following requests:

   - `/photo`: Take a picture and sends it to the telegram chat.
   - `/video <seconds>`: Record a video with the specified duration and send it to the telegram chat. If senconds params is not specified, duration will be 10 seconds by default.

   **\*Important:** The bot cannot send files weighter than 50MB, so videos longer than 25 seconds will only be stored locally on the server and will not be sent to the telegram chat.

- `/automatic`: The motion agent will be activated, and it will be active. In case of detecting movement, a photo or video (specified parameter) will be made automatically, it will generate an alert and will send this alert with the photo/video to the telegram chat.

   - `/automatic photo`: Activates automatic mode, and takes a picture when an alert is generated.
   - `/automatic video`: Activates automatic mode, and record a video with 15 seconds duration when an alert is generated.

   \**Note*: If no parameter is specified, by default it activates the automatic photo mode.

- `/streaming`: Make a live visualization of the video captured by the camera. The content can be accessed through the IP address of the server (in this case raspberry PI), using *8082* port.

## 3.2 How to use it
The application is very easy to use, but a number of considerations must be taken into account in order to use it correctly:

- **Only one mode can be active at a time**. We can move from one mode to another. through the commands:
 - `/manual`: Set manual mode
 - `/automatic`: Set automatic mode
 - `/streaming`: Set streaming mode

   If you need to know the active mode, the bot will tell you when it receives the command `/gmode`

- **You cannot send an action `/photo` or `/video` while the video recording is in progress**. It is easy, until you finish using the camera resource , we will not be able to use it again

- **Be careful when specifying the video recording duration**, because the camera resource will not be available until it is finished, and no further requests can be made. In addition, videos longer than 25 seconds cannot be sent to telegram conversation (although they will be stored locally).

- If typing commands is uncomfortable, **you can use the button interface** that has been designed. To activate this interface you need to enter the command `/start`.

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/Security_system_PI/master/images/buttons_interface.png">
</p>
