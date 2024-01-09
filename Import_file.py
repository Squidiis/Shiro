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
bot.remove_command("help")

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


class HelpDropdown(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Choose what you want to apply as", min_values=1, max_values=1, custom_id="interaction:aplication", options = [

        discord.SelectOption(label="Mod Commands", description="Hier siehst du alle Moderations Commands aufgelistet", value="mod"),
        discord.SelectOption(label="Level System", description="Hier sind alle Level System Commands aufgelistet", value="level"),
        discord.SelectOption(label="Fun Commands", description="Hier sind alle Fun Commands aufgelistet", value="fun"),
        discord.SelectOption(label="Gif commands", description="Hier sind alle Role play gif commands aufgelistet", value="gif"),
        discord.SelectOption(label="Main menu", description="Hier kommst du zurück zum Hauptmenu", value="main")
    ])
    async def callback(self, select, interaction:discord.Interaction): 

        if select.values[0] == "mod":

            emb = discord.Embed(
                title="Mod commands", 
                description="""
                **/set-anti-link**
                Stelle das anti link system ein damit du hast ein paar parameter mit denen du einstellen kannst welche links gelöscht werden sollen
                **/ban**
                Banne einen nutzer von deinem server
                **/unban**
                Hebe den Ban eines nutzers auf
                **/kick**
                Kicke einen nutzer von deinem server
                **/timeout**
                Schicke einen Nutzer in den Timeout
                **/remove-timeout**
                Hebe den Timeout eines users auf
                **/clear**
                Löscht nachrichten du kannst die menge frei wählen
                **/server-info**
                Zeigt dir alle Relevanten informationen zum Server
                **/ghost-ping-settings**
                Schalte das Ghost ping system entweder ein oder aus
                **/userinfo**
                Zeigt die alle Relevanten infos zu einem user an
                """, color = bot_colour)
            
            await interaction.response.edit_message(embed=emb)

        elif select.values[0] == "level":

            emb = discord.Embed()

        elif select.values[0] == "fun":

            emb = discord.Embed()

        elif select.values[0] == "gif":

            emb = discord.Embed()

        elif select.values[0] == "main":

            emb = discord.Embed()



# Help command
class Help_menu(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def help (self, ctx:commands.Context):

        embed = discord.Embed(
        title= f"This is the Help menu from {bot.user.name}",
        description= f"The help menu is divided into several sections **the Prifix is $**",
        color= discord.Colour.orange())
        await ctx.send (embed=embed)


     
bot.add_cog(Help_menu(bot))




