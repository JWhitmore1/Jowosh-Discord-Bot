# Jowosh Discord Bot
The source code for a small project of working on a discord bot called Jowosh with interactions, games and utilities. This project is primarily built using the [Hikari](https://github.com/hikari-py/hikari) and [Lightbulb](https://github.com/tandemdude/hikari-lightbulb) libraries.

## Invite
Invite our bot to be a part of your server [here](https://discord.com/api/oauth2/authorize?client_id=994903279127511040&permissions=8&scope=bot%20applications.commands)! 

## Features
- [x] Interacts
  - [x] Hug
  - [x] Kiss
  - [x] Slap
  - [x] Bite
  - [x] Pat
  - [x] Database counters
- [x] Inspire API
- [x] Communication 
  - [x] Banner
  - [x] Say
  - [x] guydisintegratinggif
- [ ] Voice
  - [x] Join voice channel
  - [x] Leave voice channel
  - [ ] Lavalink wrapper for music
  - [ ] Soundboard
- [ ] Economy
  - [ ] Embed and styling
  - [ ] Bank features
    - [x] Deposit
    - [x] Withdraw
    - [x] Interest
    - [ ] Information
    - [ ] Upgrade
  - [ ] User interaction
    - [ ] Paying other users
  - [ ] Purchaseable features
    - [ ] Delete messages
    - [ ] Server roles
- [ ] Server preferences
  - [ ] Customizable daily reset times
- [ ] Website


## Prerequisites
All the libraries required for the project can be found in the requirements.txt file and can be installed locally using:
```sh
pip install -r requirements.txt
```

## Running
To launch your own bot running this backend, get a bot token from the [discord developer portal](https://discord.com/developers/applications/), and create and invite link under the Oauth2 menu > URL Generator. From here, select the "bot" and "applications.commands" scopes and select the bots permissions (if you are unsure, admin will select all). Use the URL generated to invite the bot to your server.

Finally, create a .env file in the codebase with the following variable:
```
bot_token = "<your token>"
```
then run the bot.py file.
