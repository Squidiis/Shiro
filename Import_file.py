import asyncio
import random
import os
import json
import discord.ext
from discord.ext.commands import MissingPermissions
import discord
from discord.ext import commands
import mysql.connector
from datetime import *
import requests
from discord.ui import Select, View, Button, Modal
from discord.commands import Option, SlashCommandGroup
from PIL import Image
from sql_function import *
import yaml
from discord.ext.pages import Paginator, Page

"""
┏━━━┓ ┏━━━┓ ┏┓ ┏┓ ┏━━┓ ┏━━━┓ ┏━━┓
┃┏━┓┃ ┃┏━┓┃ ┃┃ ┃┃ ┗┫┣┛ ┗┓┏┓┃ ┗┫┣┛
┃┗━━┓ ┃┃ ┃┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┗━━┓┃ ┃┗━┛┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┃┗━┛┃ ┗━━┓┃ ┃┗━┛┃ ┏┫┣┓ ┏┛┗┛┃ ┏┫┣┓
┗━━━┛    ┗┛ ┗━━━┛ ┗━━┛ ┗━━━┛ ┗━━┛
"""

disable_level_up_channel = ""
add_level_up_channel = ""
remove_xp = ""
give_xp = ""
give_level = ""
remove_level = ""
show_level_role = ""
add_level_role = ""


# These are all emojis used in this bot the individual eimojis are stored again in this folder: discord_bot/emojis
class Emojis:

    arrow_emoji = "<a:shiro_arrow:1092443788900831355>"
    load_emoji = "<a:shiro_load:1092862133181612133>"
    fail_emoji = "<a:shiro_failed:1092862110381383762>"
    diamond_emoji = "<a:shiro_diamant:1092862078731161771>"
    fire_emoji = "<a:shiro_blueflame:1092862057432481792>"
    dot_emoji = "<:shiro_dot_blue:1092871145075781662>"
    ban_hammer_emoji = "<:shiro_hammer:1092871051500855297>"
    party_girl_emoji = "<a:shiro_partygirl:1092871048879419412>"
    settings_emoji = "<a:shiro_settings:1092871148494143499>"
    help_emoji = "<:shiro_help:1092872576017109033>"
    dollar_emoji = "<:shiro_dollar:1092876159894683712>"
    dollar_animation_emoji = "<a:shiro_dollar_animation:1092876162805534820>"
    exclamation_mark_emoji = "<a:shiro_important:1092870970785665055>"
    succesfully_emoji = "<a:shiro_successful:1092862166702510290>"
        
with open("config.yaml", 'r') as f:
    data = yaml.safe_load(f)


#Intents
intent = discord.Intents.default()
intent.members = True
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=data["Prefix"], intents=intents)


# level up message
def level_message(guild_id:int, user_id:int, level:int):

    user = f"<@{user_id}>"
    level_up_message = eval("f'{}'".format(DatabaseCheck.check_level_settings(guild_id=guild_id)[4]))
    return level_up_message


# The red colour for the fail / error embeds
error_red = discord.Colour.brand_red()


# The bot color, each embed has this color
bot_colour = data["Bot_colour"]


# Fail / error embeds
no_permissions_emb = discord.Embed(title="You are not authorized", 
    description = f"You are not allowed to press this button only admins are allowed to interact with this command {Emojis.fail_emoji}",color = error_red)

user_bot_emb = discord.Embed(title = f"The user is a bot {Emojis.fail_emoji}", 
    description = f"The user you have selected is a bot and cannot be selected in this command!", color = error_red)

user_not_found_emb = discord.Embed(title=f"The user was not found {Emojis.fail_emoji}", 
    description = f"{Emojis.dot_emoji} No entry was found the user is also no longer on the server {Emojis.exclamation_mark_emoji}", color = error_red)

no_entry_emb = discord.Embed(title=f"{Emojis.help_emoji} No entry found", 
    description = f"{Emojis.dot_emoji} Therefore, one was created just try again.", color = bot_colour) 



# Help Commands
#TODO Ein Inhaltsverzeichnis auf die erste seite 
class HelpMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.pages = [

            # Mod commands
            Page(embeds=[discord.Embed(title="Mod Commands", 
                description="All mod commands are listed on this page", color=bot_colour)
                .add_field(name="set-anti-link", 
                    value="Set the anti-link system, you can choose if only dischrd invitation links should be deleted, if everything except pictures and videos should be deleted or if everything should be deleted", inline=False)
                .add_field(name="/ban", 
                    value="Ban a user from your server who will not be able to join again", inline=False)
                .add_field(name="/unban", 
                    value="Unban a user from your server who can then rejoin the server", inline=False)
                .add_field(name="/kick", 
                    value="Kick a user from your server", inline=False)
                .add_field(name="/timeout", 
                    value="Send a user to a timeout you decide how long he needs a timeout", inline=False)
                .add_field(name="remove-timeout", 
                    value="Cancel the timeout of a user who can then write messages normally again", inline=False)
                .add_field(name="/clear", 
                    value="Delete messages you can freely specify how many should be deleted", inline=False)
                .add_field(name="/ghost-ping-settings", 
                    value="Set the anti ghost ping system when someone tags another user and then deletes the message, a message is sent stating what the user wrote and who they tagged", inline=False)
                .add_field(name="/userinfo", 
                    value="Display all important information about a user", inline=False)
                .add_field(name="/serverinfo", 
                    value="Show all important information about your server", inline=False)
                ]),

            # Fun commands
            Page(embeds=[discord.Embed(title="Fun commands", 
                description="All fun commands are listed here on this page", color=bot_colour)
                .add_field(name="/rps", 
                    value="Play rock, paper, scissors against the bot or another user", inline=False)
                .add_field(name="/coinflip", 
                    value="Flip a coin either heads or tails", inline=False)
                .add_field(name="/cocktails", 
                    value="Get a random cocktail recipe", inline=False)
                .add_field(name="/animememe", 
                    value="Show you a random anime meme from reddit", inline=False)
                .add_field(name="Role play commands", 
                    value="Here are all Role play commands", inline=False)
                .add_field(name="/anime gif (tag)",
                    value="Tags: kiss, hug, lick, feed, idk, dance, slap, fbi, embarres, pet", inline=False)
                ])
            
            ]

    def get_pages(self):
        return self.pages
    
    
    @commands.slash_command(name = "help", description = "Do you need a little help!")
    async def help(self, ctx:discord.ApplicationContext):
        
        
        paginator = Paginator(pages=self.get_pages())

        embed = discord.Embed(title="3", description="stuff3")
        embed.add_field(name="meddl", value="meddl leute")

        self.pages.append(embed)
        await paginator.respond(ctx.interaction)
     
bot.add_cog(HelpMenu(bot))




