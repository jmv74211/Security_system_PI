# Security_system_PI

## Security system for control and video surveillance implemented on a raspberry PI

### Author: jmv74211

### Date: 29-04-2019

---

![Status](https://img.shields.io/badge/-RasperryPI-red.svg)
![Status](https://img.shields.io/badge/-Python-green.svg)
![Status](https://img.shields.io/badge/-Telegram-blue.svg)

![Status](https://img.shields.io/badge/Status-implementing-orange.svg)
![Status](https://img.shields.io/badge/Status-documenting-orange.svg)

# 1. Introduction

Security system PI is an application that allows us to build a security system based on low-cost video surveillance using a raspberry PI, a camera and a motion sensor.

The idea is to be able to control this device through a telegram bot connected to our API that controls the main system. The main functions are the following:
- Automatic system of alerts generated when capturing movement.
- Manual system to capture video or a photo instantly.
- Streaming system to visualize the image in real time.

---

# 2. Getting started.

## 2.1 Telegram bot

First of all, you'll need to create a telegram bot and get the **BOT API key**. If you don't know how to do it, you can read the following documentation: https://www.sohamkamani.com/blog/2016/09/21/making-a-telegram-bot/


## 2.2 APP
Tested with python version 3.5.3. The necessary libraries are indicated in the file [requeriments.txt](https://github.com/jmv74211/Security_system_PI/blob/master/requeriments.txt)

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