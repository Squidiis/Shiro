<h1 align="center">
    This project is currently in development!<br>
</h1>

<h4 align="center">
    Owner and developer is <a href="https://github.com/Squidiis">Squidi</a>
    <br>Official discord server for the Shiro discord bot project
</h4>

<h4 align="center">
    <a href="https://discord.gg/Zv5JtYhd9r"><img src="https://img.shields.io/discord/1040624306062889032?color=blue&label=Discord&logo=discord&logoColor=white&style=for-the-badge" alt="Discord"></a>
</h4>

## 👋 About

Shiro is a Discord bot that stands out for its wide range of commands and customization options. 
You can customize pretty much anything, all commands are very user-friendly and always have explanations!

If you wish, you can invite the bot to your own server by clicking [here](https://discord.com/oauth2/authorize?client_id=928073958891347989&scope=bot&permissions=8)

## ⌨ Functions

* Level System
    - Individual blacklist commands to exclude individual channels, categories, roles or users from the level system.
    - Blacklist manager to quickly manage the entire blacklist.
    - Commands to manage and change the statistics of individual users.
    - Ranking command to show how far users are in the level system.
    - Ranking list of the top 10 users.
    - Commands to set how much XP is awarded per message.
    - Commands to give individual XP bonuses to individual channels, categories, roles and users.
    - Level role system to reward users with roles when they reach a certain level (level roles can be customized).
    - Commands to create custom level-up messages and also some to create a level-up channel to which all level-up messages are sent.
    
* Moderation System
    - ban, kick, mute, unmute, clear commands
    - server-info, user-info commands
    - anti discord invite link system 

* Fun commands
    - RPS (Rock, Paper, Scissors)
    - Tik Tak Toe
    - Coin flip game with gifs
    - cocktail command that gives you a random cocktail recipe 
    - Anime gif commands (kiss, hug, lick, punch, idk, dance, slap, fbi, embarres, pet) uses all the [tenor API](https://tenor.com/gifapi/documentation)
    - Anime meme command with the [reddit API](https://www.reddit.com/dev/api/)

## 📝 Requirements

- [mysql-connector-python 8.1.0](https://pypi.org/project/mysql-connector-python/)
- [Pillow 10.0.0](https://pypi.org/project/Pillow/)
- [py-cord 2.4.1](https://pypi.org/project/py-cord/)
- [python-dotenv 1.0.0](https://pypi.org/project/python-dotenv/)
- [requests 2.31.0](https://pypi.org/project/requests/)
- [ui 0.1.4](https://pypi.org/project/ui/)


## All commands

| Command | Description |
| --- | --- |
|give XP|Gives a user a quantity of XP that you choose.|
|remove XP|Removes a user a quantity of XP chosen by you.|
|give level|Gives a user a quantity of level that you choose|
|remove level|Removes a user a quantity of level chosen by you|
|reset level|Resets the forward step of all users on the server to 0|
|rank|Shows the progress of a user in the level system with the help of a rank card, for example [press here](https://github.com/Squidiis/Discord-bot-Shiro/blob/master/assets/rank-card/example_rank_card.png?raw=true)|
|leaderboard|Zeigt die 10 besten auf den server|
|level system settings|Schaltet das level system aus oder ein|
|add level blacklist channel|Fügt einen channel auf die Level system blacklist hinzu dieser wird dann vom level system ausgeschlossen und man erhält in diesen channel kein XP|
|remove level blacklist channel|Streiche einen channel von der Blacklist und lasse in wieder am level system teilnehmen man erhält in diesen channel dann wieder XP|
|add level blacklist category|Fügt eine Kategorie auf die level blacklist hinzu alle aktivitäten in den channel der Kategorie werden nicht mit XP belohnt|
    