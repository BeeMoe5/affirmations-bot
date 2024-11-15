# About:
A discord bot that uses [v2.4 of discord.py](https://discordpy.readthedocs.io/en/latest/) to send daily randomized affirmations to your server!

# How to use:
I don't have a public bot to invite, so you'll have to run this on your own bot.
Additionally, this is very specific to my server, so you'll have to make some changes to the code to make it work for your own server, if you choose to clone this repo and run it on your own bot.
I will be making this more configurable in the future, but you'll have to use the code as-is for now.

# Installation:
If you are wanting to run this on your own bot, here is what you need to do:
## Clone the repo
```bash
git clone https://github.com/BeeMoe5/affirmation-bot.git
```
## install ffmpeg for voice affirmations
You'll need ffmpeg installed and add to path on your system to play voice affirmations.
Additionally, for voice affirmations to work properly, you need to make a "sounds" folder in the /assets directory and put your voice affirmations in there.

## set DISCORD_TOKEN in .env
Create a .env file and add your DISCORD_TOKEN to it:
```bash
touch .env
```
Inside .env:
```bash
DISCORD_TOKEN=your_bot_token
```

## Install requirements
Its all in the pyproject.toml file, so for poetry users:
```bash
poetry install
```
but for pip users:
```bash
pip install .
```

## Run the bot
```bash
python src/main.py
```
