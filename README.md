<img draggable="false" src="https://github.com/Squidiis/Discord-bot-Shiro/blob/master/assets/images/Shiro_banner4.png"></a>


<h1 align="center">
    This project is currently in development!<br>
</h1>

<h4 align="center">
    Owner and developer is <a href="https://github.com/Squidiis">Squidi</a>
    <br>Official discord server for the Shiro discord bot project
</h4>

<h4 align="center">
    <a href="https://discord.gg/Zv5JtYhd9r"><img src="https://img.shields.io/discord/1040624306062889032?color=blue&label=Discord&logo=discord&logoColor=white&style=for-the-badge" alt="Discord"></a>
    <br>Start of development Tue, Jan 04, 2022
</h4>

## 👋 About

Shiro is a Discord bot that stands out for its wide range of commands and customization options. 
You can customize pretty much anything, all commands are very user-friendly and always have explanations!

If you wish, you can invite the bot to your own server by clicking [here](https://discord.com/oauth2/authorize?client_id=928073958891347989&scope=bot&permissions=8)


## ⌨ Functions

* Level System
    - Individual blacklist commands to exclude individual channels, categories, roles or users from the level system.
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
    - RPS (Rock, Paper, Scissors) alone against a bot or against your friends
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
|give-xp|Gives a user a quantity of XP that you choose.|
|remove-xp|Removes a user a quantity of XP chosen by you.|
|give-level|Gives a user a quantity of level that you choose|
|remove-level|Removes a user a quantity of level chosen by you|
|reset-level|Resets the forward step of all users on the server to 0|
|reset-user-stats||
|rank|Shows the progress of a user in the level system with the help of a rank card, for example [press here](https://github.com/Squidiis/Discord-bot-Shiro/blob/master/assets/rank-card/example_rank_card.png?raw=true)|
|leaderboard|Shows the 10 best on the server|
|level-system-settings|Enables the level system to be set|
|add-level-blacklist|Excludes a channel, category, role or user from the level system, after which activities in the channel or categories and by users or role holders are no longer rewarded with XP|
|remove-level-blacklist|Deletes a channel, category, role or user from the level system blacklist then you can get XP again by being active|
|show-level-blacklist|Shows everything that is on the blacklist|
|reset-level-blacklist|Resets the entire blacklist|
|add-level-role|Adds a level role when you reach a certain level that you can freely choose, this is then awarded|
|remove-level-role|Removes a role as a level role|
|show-level-roles|Displays all level roles|
|set-level-up-channel|Defines a channel as the level up channel to which all level up messages are then sent|
|disable-level-up-channel|Resets the channel set as level up then the level up notifications are always set to the channel in which the last activity took place|
|show-level-up-channel|Shows the currently set level up channel|
|set-xp-rate|Sets a value for how much XP should be awarded per message|
|default-xp-rate|Sets the value of XP to be awarded per message back to default: 20 XP per message|
|show-xp-rate|Shows the current value of how much XP is awarded per message|
|add-bonus-xp-channel||
|remove-bonus-xp-channel||
|add-bonus-xp-category||
|remove-bonus-xp-category||
|add-bonus-xp-role||
|remove-bonus-xp-role||
|add-bonus-xp-user||
|remove-bonus-xp-user||
|show-bonus-xp-list|Shows all channels, categories, roles and users that are rewarded with extra XP for activities|
|reset-bonus-xp-list|Resets the entire bonus XP list|
|set-bonus-xp-percentage|Defines a stadart bonus XP percentage how much more XP should be awarded as a percentage per activity (only applies to channels, categories, roles and users on the bonus XP list)|
|default-bonus-xp-percentage|Resets the bonus XP percentage to default: 10% more XP per activity (this percentage only applies to the channels, categories, roles and users on the bonus XP list)|
|show-bonus-xp-percentage|Shows you the bonus XP percentage|
|set-level-up-message|Defines an individual level up message for a server: 2 arguments are given (user and level)|
|default-level-up-message|Resets the level up message to default|
|show-level-up-message|Shows the current level up message|