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
level_settings = ""
remove_xp = ""
give_xp = ""
give_level = ""
remove_level = ""
show_level_role = ""
add_level_role = ""
remove_level_role = ""

economy_settings = ""
# Blacklist
add_blacklist_economy_channel = "</add-channel-economy-blacklist:1095096748323635261>"
remove_blacklist_economy_channel = "</remove-channel-economy-blacklist:1095421561839816786>"
add_blacklist_economy_category = "</add_category_economy_blacklist:1095443187562192987>" # Ändern
remove_blacklist_economy_category = "</remove-category-economyblacklist:1095699949963989073>"
add_blacklist_economy_role = "</add-role-economy-blacklist:1096038008534351962>"
remove_blacklist_economy_role = "</remove-role-economy-blacklist:1096038008534351964>"
add_blacklist_economy_user = "</add-user-economy-blacklist:1096038008534351965>"
remove_blacklist_economy_user = "</remove-user-economy-blacklist:1096038008534351966>"
show_blacklist_economy = "</show-economy-blacklist:1095437293143195658>"

# Blacklist level
add_blacklist_level_channel = ""
remove_blacklist_level_channel = ""
add_blacklist_level_category = "" # Ändern
remove_blacklist_level_category = ""
add_blacklist_level_role = ""
remove_blacklist_level_role = ""
add_blacklist_level_user = ""
remove_blacklist_level_user = ""
show_blacklist_level = ""

# Give/Remove money

give_money = ""
remove_money = ""


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


bot.remove_command("help")


add = SlashCommandGroup(name = "add", description = "add something to someone", default_member_permissions = discord.Permissions(administrator=True))
remove = SlashCommandGroup(name = "remove", description = "remove something away from someone", default_member_permissions = discord.Permissions(administrator=True))
show = SlashCommandGroup(name = "show", description="Display something")

# level up message
def level_message(guild_id:int, user_id:int, level:int):

    user = f"<@{user_id}>"
    level_up_message = eval("f'{}'".format((DatabaseCheck.check_bot_settings(guild_id=guild_id)[4])))
    return level_up_message

# The red colour for the fail / error embeds
error_red = discord.Colour.brand_red()

# The bot color, each embed has this color
bot_colour = data["Bot_colour"]

# Fail / error embeds
no_permissions_emb = discord.Embed(title="You are not authorized", description=f"You are not allowed to press this button only admins are allowed to interact with this command {Emojis.fail_emoji}",color = error_red)

user_bot_emb = discord.Embed(title=f"The user is a bot {Emojis.fail_emoji}", 
    description=f"The user you have selected is a bot and cannot be selected in this command!", color=error_red)

user_not_found_emb = discord.Embed(title=f"The user was not found {Emojis.fail_emoji}", 
    description=f"{Emojis.dot_emoji} No entry was found the user is also no longer on the server {Emojis.exclamation_mark_emoji}", color=error_red)

no_entry_emb = discord.Embed(title=f"{Emojis.help_emoji} No entry found", 
    description=f"{Emojis.dot_emoji} Therefore, one was created just try again.", color=bot_colour) 
# Help command
class Help_menu(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def help (self, ctx):

        embed = discord.Embed(
        title= f"This is the Help menu from {bot.user.name}",
        description= f"The help menu is divided into several sections **the Prifix is $**",
        color= discord.Colour.orange())
        embed.add_field(name="Funcommands", value=f"`lick` `idk` `fbi` `kiss` `hug` `puch` `marry`\n `dance` `gif` `aboutme ` `RPS` `coinflip` `surprise` `wink` `pat` `feed` `cuddle` `animememe`", inline=False)
        
        embed.add_field(name="Moderationtolls", value=f"`dm` `ban` `kick` `clear` `say`", inline=False)
        embed.add_field(name="Summer event", value=f"`cocktails`", inline=False)
        await ctx.send (embed=embed)


     
bot.add_cog(Help_menu(bot))




