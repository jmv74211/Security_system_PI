#! /bin/bash

####################### LOCATION VARS ###########################


APP_PATH="src/app/"
REQUERIMENTS_PATH="./requeriments.txt"


#################################################################



echo "======================================================== \n"
echo "Installing dependencies... \n"
echo "======================================================== \n"

pip3 install -r $REQUERIMENTS_PATH

cd $APP_PATH

echo "======================================================== \n"
echo "Running main agent... \n"
echo "======================================================== \n"

python3 main_agent.py &


echo "======================================================== \n"
echo "Running telegram bot... \n"
echo "======================================================== \n"

python3 telegram_bot.py &
