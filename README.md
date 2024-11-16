# About:
A discord bot that uses [v2.4 of discord.py](https://discordpy.readthedocs.io/en/latest/) to send daily randomized affirmations to your server!

# How to use:
I don't have a public bot to invite, so you'll have to run this on your own bot. To do this, follow the installation instructions below.

# Installation:
If you are wanting to run this on your own bot, here is what you need to do:
## Clone the repo
```bash
git clone https://github.com/BeeMoe5/affirmation-bot.git
```
## install ffmpeg for voice affirmations
You'll need ffmpeg installed and add to path on your system to play voice affirmations.
Additionally, for voice affirmations to work properly, you need to make a "sounds" folder in the /assets directory and put your voice affirmations in there.

## set up .env
Create a .env file in the root of the repository, if you haven't already:
```bash
touch .env
```
Then, add the following to the .env file:
```bash
DISCORD_TOKEN=your_bot_token
AFFIRM_TEXT_CHANNEL_ID=your_text_channel_id
AFFIRM_VOICE_CHANNEL_ID=your_voice_channel_id
AFFIRM_ROLE_ID=your_role_id
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
