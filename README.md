<img draggable="false" src="https://github.com/Squidiis/Discord-bot-Shiro/blob/master/assets/images/Shiro_banner4.png"></a>


<h1 align="center">
    This project is currently in development!<br>
</h1>

<h4 align="center">
    Owner and developer is <a href="https://github.com/Squidiis">Squidi</a>
    <br>Official discord server for the Shiro discord bot project
</h4>

<h4 align="center">
    <a href="https://discord.gg/UKZkmeJYsA"><img src="https://img.shields.io/discord/1040624306062889032?color=blue&label=Discord&logo=discord&logoColor=white&style=for-the-badge" alt="Discord"></a>
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
    - anti link system (with whitelist function)
    - anti ghost ping system
    - invite tracker

* Fun commands
    - RPS (Rock, Paper, Scissors) alone against a bot or against your friends
    - Coin flip game with gifs
    - cocktail command that gives you a random cocktail recipe 
    - Anime gif commands (kiss, hug and much more) uses all the [tenor API](https://tenor.com/gifapi/documentation)
    - Anime meme command with the [reddit API](https://www.reddit.com/dev/api/)

## 📝 Requirements

- [mysql-connector-python 8.1.0](https://pypi.org/project/mysql-connector-python/)
- [Pillow 10.0.0](https://pypi.org/project/Pillow/)
- [py-cord 2.4.1](https://pypi.org/project/py-cord/)
- [python-dotenv 1.0.0](https://pypi.org/project/python-dotenv/)
- [requests 2.31.0](https://pypi.org/project/requests/)
- [ui 0.1.4](https://pypi.org/project/ui/)

# How to set up

Setting up the bot has been made as simple as possible.

There is a file named [`config.yaml`](config.yaml) in which you can make the necessary adjustments to make everything the way you want it

To run the code on your bot customize the [`.env`](.env) file simply fill in all the given variables

|Variable|Explanation|
| --- | --- |
|TOKEN|Insert your token for your bot here you can find it [here](https://discord.com/login?redirect_to=%2Fdevelopers%2Fapplications) just log in and copy the token if no application has been created yet you have to do this to get the token.|
|API_KEY|Paste the API key from the Tenor API here you get it [here](https://tenor.com/developer/dashboard) just log in or register if you don't have an account yet.|
|sql_password|Enter the password that belongs to your MySQL database.|
|host|Enter the host here this can be an ip or `localhost` if you run the database locally on your device.|
|user|Enter the user name of your MySQL database here this can be `root` if you run it locally or a custom name of your choice.|
|discord_db|Here the name of the database schema.|

In the [`ultils.py`](ultils.py) file add the emojis to the variables [emojis](emojis)

# How to start?

Once you have configured everything and adjusted the required variables in [`config.yaml`](config.yaml) and [`.env`](.env), all you have to do is install the required packages
```
python -m pip install -r requirements.txt
```

After that you can start it with

```
python bot.py
```
If you encounter problems use the discord server linked above or press [here](https://discord.gg/UKZkmeJYsA) to be redirected directly to in.

## All commands

| Command | Description |
| --- | --- |
|help|Shows all the commands the bot has and explains what they can do.|
|give-xp|Gives a user a quantity of XP that you choose.|
|remove-xp|Removes a user a quantity of XP chosen by you.|
|give-level|Gives a user a quantity of level that you choose.|
|remove-level|Removes a user a quantity of level chosen by you.|
|reset-level|Resets the forward step of all users on the server to 0|
|reset-user-stats|Resets all stats of a user to 0.|
|rank|Shows the progress of a user in the level system with the help of a rank card, for example [press here](https://github.com/Squidiis/Discord-bot-Shiro/blob/master/assets/rank-card/example_rank_card.png?raw=true).|
|leaderboard|Shows the 10 best on the server.|
|level-system-settings|Enables the level system to be set.|
|add-level-blacklist|Excludes a channel, category, role or user from the level system, after which activities in the channel or categories and by users or role holders are no longer rewarded with XP.|
|remove-level-blacklist|Deletes a channel, category, role or user from the level system blacklist then you can get XP again by being active.|
|show-level-blacklist|Shows everything that is on the blacklist.|
|reset-level-blacklist|Resets the entire blacklist.|
|add-level-role|Adds a level role when you reach a certain level that you can freely choose, this is then awarded.|
|remove-level-role|Removes a role as a level role.|
|reset-level-role|Removes all level roles|
|show-level-roles|Displays all level roles.|
|add-bonus-xp-list|Reward activities in a category or channel with more XP you can also select roles and users the percentage rate for the bonus XP items can be chosen freely.|
|remove-bonus-xp-list|Remove categories, channels, roles and users from the Bonus XP list.|
|show-bonus-xp-list|Shows all channels, categories, roles and users that are rewarded with extra XP for activities.|
|reset-bonus-xp-list|Resets the entire bonus XP list.|
|rps|Play rock, paper, scissors against another user or a bot.|
|cocktails|Send a recipe of a random cocktail.|
|coinflip|Toss a coin where heads or tails can come out.|
|gif kiss|Send an anime gif of someone being kissed (a user can also be tagged).|
|gif hug|Send an anime gif where someone is hugged (a user can also be marked).|
|gif lick|Send an anime gif where someone is put down (a user can also be tagged).|
|gif feed|Send an anime gif where someone is being fed (a user can also be tagged).|
|gif idk|Send an anime gif that expresses cluelessness (you can also mark a user).|
|gif dance|Send an anime gif with dancing characters (a user can also be tagged).|
|gif slap|Send an anime slap gif (a user can also be tagged).|
|gif fbi|Send an anime FBI gif (a user can also be tagged).|
|gif embarres|Send an anime gif (You can also mark a user).|
|gif pet|Send an anime gif of a head pet (a user can also be tagged).|
|animememe|Displays a random anime meme from Reddit.|
|set-antilink-system|Deletes all messages with a link you can choose what to delete (options: Everything, only invite links to other servers, everything except pictures and vidoes, nothing).|
|show-antilink-settings|Shows you how the antilink system is set up|
|add-antilink-whitelist|Excludes channels, categories, roles and users from the antilink system|
|remove-antilink-whitelist|Deletes channels, categories, roles and users from the antilyk system white list|
|show-antilink-whitelist|Shows what is already listed on the antilink white list|
|reset-antilink-whitelist|Resets the antilink whitelist|
|ban|Bans a user of your choice who can no longer enter the server.|
|unban|Unban a user of your choice.|
|kick|Kicks a user from the server.|
|timeout|Sends a user to a timeout for a time specified by you.|
|remove-timeout|Removes a timeout of a user of your choice.|
|clear|Deletes a number of messages of your choice.|
|serverinfo-slash|Displays all relevant information about the server.|
|userinfo|Displays all relevant information about a user.|
|ghost-ping-settings|Set the ghost ping system if someone tags you and deletes the message a message will be sent with the content and the sender can be turned on/off.|
|show-invites|Shows how many members a user has invited|

