### Welcome to TriviaBot!

To install me, you will need to set up a discord bot, then pull the code form this repo with

    git clone https://github.com/ethanshealey/TriviaBot

then, install all the needed packages

    pip3 install -r requirements.txt

next, create the database by running

    python3 create_database.py

and finally, create a file called `.env` and place 

   #.env
   DISCORD_TOKEN=<TOKEN>

then lauch the bot with

   python3 TriviaBot.py
