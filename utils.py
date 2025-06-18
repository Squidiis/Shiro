import asyncio
import random
import os
import json
import discord.ext
from discord.ext.commands import MissingPermissions
import discord
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Select, View, Button, Modal
from discord.commands import Option, SlashCommandGroup, option
from PIL import Image
from sql_function import *
import yaml
from discord.ext.pages import Paginator, Page
from datetime import timedelta, timezone, datetime
import re
from datetime import UTC
from urllib.parse import urlsplit, urlparse
import aiohttp
import aiomysql



"""
┏━━━┓ ┏━━━┓ ┏┓ ┏┓ ┏━━┓ ┏━━━┓ ┏━━┓
┃┏━┓┃ ┃┏━┓┃ ┃┃ ┃┃ ┗┫┣┛ ┗┓┏┓┃ ┗┫┣┛
┃┗━━┓ ┃┃ ┃┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┗━━┓┃ ┃┗━┛┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┃┗━┛┃ ┗━━┓┃ ┃┗━┛┃ ┏┫┣┓ ┏┛┗┛┃ ┏┫┣┓
┗━━━┛    ┗┛ ┗━━━┛ ┗━━┛ ┗━━━┛ ┗━━┛
"""


# These are all emojis used in this bot the individual eimojis are stored again in this folder: discord_bot/emojis
class Emojis:

    arrow_emoji = "<a:shiro_arrow:1092443788900831355>"
    fail_emoji = "<a:shiro_failed:1092862110381383762>"
    dot_emoji = "<:shiro_dot_blue:1092871145075781662>"
    settings_emoji = "<a:shiro_settings:1092871148494143499>"
    help_emoji = "<:shiro_help:1092872576017109033>"
    exclamation_mark_emoji = "<a:shiro_important:1092870970785665055>"
    succesfully_emoji = "<a:shiro_successful:1092862166702510290>"

    # user info emojis
    phone = "<:phone:1274727307902455943>"
    partner = "<:partner:1274727306438377594>"
    online = "<:online:1274727305125564557>"
    invisible = "<:invisible:1274727303808815124>"
    idle = "<:idle:1274727302596395028>"
    hypesquad_brilliance = "<:hypesquad_brilliance:1274727325149429792>"
    hypesquad_bravery = "<:hypesquad_bravery:1274727560856735796>"
    hypesquad_balance = "<:hypesquad_balance:1274727321898586144>"
    earlysupporter = "<:earlysupporter:1274727559611027558>"
    dnd = "<:dnd:1274727317528121394>"
    dev = "<:dev:1274727557928976435>"
    bughunter2 = "<:bughunter2:1274727314084724737>"
    bughunter = "<:bughunter:1274727312583163905>"
    botdev = "<:botdev:1274727311186595911>"
    boost = "<:boost:1274727309672452126>"
    staff = "<:staff:1274729786685657118>"
    spotify = "<:spotify:1274729775214104637>"
    
with open("config.yaml", 'r') as f:
    data = yaml.safe_load(f)


#Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=data["Prefix"], intents=intents, activity = discord.Game(name="developed by squidi"))

# The red colour for the fail / error embeds
error_red = discord.Colour.brand_red()


# The bot color, each embed has this color
bot_colour = data["Bot_colour"]


# Fail / error embeds
no_permissions_emb = discord.Embed(title=f"You are not authorized {Emojis.fail_emoji}", 
    description = f"You are not allowed to press this button only admins are allowed to interact with this command",color = error_red)

user_bot_emb = discord.Embed(title = f"The user is a bot {Emojis.fail_emoji}", 
    description = f"The user you have selected is a bot and cannot be selected in this command!", color = error_red)

user_not_found_emb = discord.Embed(title=f"The user was not found {Emojis.fail_emoji}", 
    description = f"{Emojis.dot_emoji} No entry was found the user is also no longer on the server", color = error_red)

no_entry_emb = discord.Embed(title=f"{Emojis.help_emoji} No entry found", 
    description = f"{Emojis.dot_emoji} Therefore, one was created just try again.", color = bot_colour)

# default message for level up message system
default_message = 'Oh nice {user} you have a new level, your newlevel is {level}' 

no_page = discord.Embed(description=f"""## An error has occurred
    {Emojis.dot_emoji} This interaction has been updated and therefore no pages can be accessed
    {Emojis.dot_emoji} Please try again later by calling the command again""", color=bot_colour)

'''
Checks a message for a channel ID

Parameters:
-----------
- text: The message to be checked
'''
async def extracts_channel_id(text:str):

    match = re.search(r"<#(\d+)>", text)
    return int(match.group(1)) if match else None


# File formats (required for antu-link system and auto-reaction)
formats = ['png', 'jpg', 'gif' , 'webp', 'jpeg', 'jpg' , 'jpeg' ,'jfif' ,'pjpeg' , 'pjp', 'svg', 'bmp', 'mp4', 'avi', 'mkv', 'mov', 'wmv', '.mp3', 'wav', 'ogg', 'aac', 'flac']


'''
Checks whether the URL leads to a gif or image

Parameters:
-----------
- url: Link from the image or gif
'''
async def validate_image_url(url:str = None):
    
    if not url:
        return True

    try:

        parsed_url = urlparse(url)
        if parsed_url.scheme not in ['http', 'https'] or not parsed_url.netloc:
            return False
        
    except Exception as e:
        return False

    try:

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                
                if 'image' not in response.headers.get('Content-Type', ''):
                    return False
                if response.status != 200:
                    return False
                
    except aiohttp.ClientError as e:
        return False

    return True



# Embeds that are used multiple times within the bot
class GetEmbed():

    '''
    Parameters:
    ------------
        - embed_index
            If an index is passed which then leads to the correct embed
                0: Bonus XP procentage
                1: User not found 
                2: Help menu main text
                3: Message leaderboard text
                4: Channel for message leaderboard exits
                5: Same channel message leaderboard
                6: Interval has been set
                7: General message leaderboard
                8: Settings message leaderboard
                9: Antilink violation
                10: Error embed for overrides
                11: Mod role (for leaderboard system)
                12: Start page cannot be changed 
                13: No sticky messages defined yet
                14: No auto-messages defined yet
                15: systems explained
        - settings
            The correct information that must be inserted in the embed
        - settings2 (same as settings)
        - settings3 (same as settings)

    Info:
        - embed_idex must be specified
    '''
    def get_embed(
        embed_index, 
        settings = None, 
        settings2 = None, 
        settings3 = None
        ):

        if embed_index == 0:

            emb = discord.Embed(description=f"""### {Emojis.help_emoji} The bonus XP percentage you want to set is already set
                {Emojis.dot_emoji} The percentage is already set to {settings} %.""", color=bot_colour)


        elif embed_index == 1:

            emb = discord.Embed(description=f"""## The user was not found
                {Emojis.dot_emoji} No entry was found for **{settings}**, so one was created
                {Emojis.dot_emoji} **{settings}** now starts at level 0 with 0 XP""", color=bot_colour)
            
        
        elif embed_index == 2:

            emb = discord.Embed(description=f"""# {Emojis.settings_emoji} Help menu
                {Emojis.dot_emoji} Here you can see all the commands that {bot.user.name} has
                ```Please use the Buttons below to explore the\ncorresponding commands```\n### Table of contents:
                > {Emojis.dot_emoji} Mod commands
                > {Emojis.dot_emoji} Fun commands
                > {Emojis.dot_emoji} Level System commands part 1
                > {Emojis.dot_emoji} Level System commands part 2
                > {Emojis.dot_emoji} Statistics system commands
                > {Emojis.dot_emoji} Anti-link system commands
                > {Emojis.dot_emoji} Auto-reaction commands
                > {Emojis.dot_emoji} Message system commands
                > {Emojis.dot_emoji} Other system commands

                **Bot links:**
                {Emojis.dot_emoji} Support server: https://discord.gg/9kJaPrWdwM
                {Emojis.dot_emoji} Githup: https://github.com/Squidiis
                """, color=bot_colour)
            
        elif embed_index == 3:
            
            emb = f"""
            {Emojis.dot_emoji} With the dropdown menu below you can select which leaderboard should be sent to this channel
            {Emojis.dot_emoji} The leaderboard differs in the duration after how much time the stats are updated
            {Emojis.help_emoji} You can also select several intervals, in which case several different leaderboards will be sent
            """

        elif embed_index == 4:

            emb = discord.Embed(description=f"""## Channel for the leaderboard has been defined
                {Emojis.dot_emoji} From now on, the leaderboard is sent in {settings}{GetEmbed.get_embed(embed_index=3)}""", color=bot_colour)
        
        elif embed_index == 5:

            emb = discord.Embed(description=f"""## This channel has already been set as a leaderboard channel
                {Emojis.dot_emoji} This channel has already been set for the {'message' if settings == 'message' else 'invite'} leaderboard
                {Emojis.dot_emoji} Would you like to continue setting the {'message' if settings == 'message' else 'invite'} leaderboard (the channel will not be changed) or re-execute the command and set a different channel for the {'message' if settings == 'message' else 'invite'} leaderboard""", color=bot_colour)
    
        elif embed_index == 6:

            emb = discord.Embed(description=f"""## Interval has been set
                {Emojis.dot_emoji} The following leaderboard option{'s' if len(settings) != 1 else ''}
                    {"".join(settings2)}
                {Emojis.dot_emoji} The leaderboard{'s is' if len(settings) == 1 else ''} sent in {settings3}
                {Emojis.help_emoji} The leaderboard only become full leaderboard after the first interval""", color=bot_colour)

        elif embed_index == 7:

            emb = discord.Embed(description=f"""## This is the general leaderboard
                {Emojis.dot_emoji} Here you can see which users have {'written' if settings == 'message' else 'invited'} the most {'messages' if settings == 'message' else 'users'} in total
                {Emojis.help_emoji} It is updated daily and will be edited into the correct leaderboard on <t:{int((datetime.now() + timedelta(days=1)).timestamp())}>""", color=bot_colour)
        
        elif embed_index == 8:

            emb = discord.Embed(description=f"""## Here you can see the settings of the {settings} leaderboard
                {Emojis.dot_emoji} The message leaderboard is currently {'switched off' if settings2[1] == 0 or settings2[1] == None else 'switched on'}.
                {Emojis.dot_emoji} Currently no channel or intervals have been defined for the message leaderboard
                {Emojis.help_emoji} If you want to set the message leaderboard use the `set-{settings}-leaderboard` command""", color=bot_colour)
            
        elif embed_index == 9:

            anti_link_text = {
                0:"discord invitation link",
                1:"link or a discord invitations",
                2:"link or an image / video",
                3:""
            }
            
            emb = discord.Embed(title=f'{Emojis.help_emoji} {settings.author.name} you have violated the anti-link system', 
                description=f"""{Emojis.dot_emoji} You have violated the anti-link system on {settings.guild.name}
                {Emojis.dot_emoji} `You have sent an {anti_link_text[settings2[3]]} to this chat`
                {f"{Emojis.dot_emoji} That's why you got a timeout for {settings2[4]} minutes" if settings2[4] != 0 else ''}""", colour=bot_colour)
            emb.set_footer(text=f'{settings.author.name}', icon_url=settings.author.display_avatar.url if settings.author.display_avatar != None else settings.guild.icon.url)

        elif embed_index == 10:

            emb = discord.Embed(description=f"""## An error has occurred
                {Emojis.dot_emoji} The {settings} could not be overwritten this happens if the option remains unanswered for too long or if I lose the connection
                {Emojis.dot_emoji} If you want {settings2}, you just have to execute the command `/{settings3}` again""", color=bot_colour)
            
        elif embed_index == 11:

            emb = discord.Embed(description=f"""## This role cannot be set as a leaderboard role
                {Emojis.dot_emoji} This role has admin or moderation rights, so it would be too dangerous to assign them through the leaderboard
                {Emojis.help_emoji} If you want to set a different role as leaderboard-role just run the command again""", color=bot_colour)

        elif embed_index == 12:

            emb = discord.Embed(description=f"""## You cannot change the start page
                {Emojis.dot_emoji} No changes can be made to the start page, please select another page""", color=bot_colour)
            
        elif embed_index == 13:

            emb = discord.Embed(description=f"""## No sticky messages have been defined yet
                {Emojis.dot_emoji} No sticky messages have been set for this server
                {Emojis.dot_emoji} If you want to set some use the `add-sticky-message` command""", color=bot_colour)
            
        elif embed_index == 14:

            emb = discord.Embed(description=f"""## No auto-messages have been defined yet
                {Emojis.dot_emoji} No auto-messages have been set for this server
                {Emojis.dot_emoji} If you want to set some use the `add-auto-message` command""", color=bot_colour)
            
        elif embed_index == 15:

            emb = discord.Embed(description=f"""## Overview of all systems with explanation
                {Emojis.dot_emoji} Here you can see all the systems, including more detailed explanations of the individual commands and the systems themselves

                ```Table of contents```
                > 1. Level system
                > 2. Mod commands
                > 3. Fun commands
                > 4. Statistic system
                > 5. Anti-link system
                > 6. Auto reaction system
                > 7. Message system
                > 8. Other systems

                {Emojis.help_emoji} If you use the commands, you will be told exactly how which system works and how you can set it up""", color=bot_colour)

        else:
            
            with open("config.yaml", 'r') as f:
                data = yaml.safe_load(f)
            emb = discord.Embed(description=f"""## An error has occurred
                {Emojis.dot_emoji} Please try again, if this problem persists please inform an admin on {data['Support_server_inv']}""", color=bot_colour)
            
        return emb
    
    

#########################################  Cancel Button  ########################################


class CancelButton(discord.ui.Button):
    
    def __init__(self, system):
        self.system = system
        super().__init__(
            label = "Cancel setting",
            style = discord.ButtonStyle.danger,
            custom_id = "cancel_button"
        )

    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Setting canceled
                {Emojis.dot_emoji} The setting of the {'system' if self.system == None else self.system} was canceled.
                {Emojis.dot_emoji} If you change your mind, you can always execute the command again.""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class HelpMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name = "help", description = "Do you need a small overview!")
    async def help(self, ctx:discord.ApplicationContext):
            
        emb = GetEmbed.get_embed(embed_index = 2)
        
        file = discord.File('assets/images/shiro_help_banner.png', filename='shiro_help_banner.png')
        emb.set_image(url=f"attachment://shiro_help_banner.png")
        await ctx.respond(embed=emb, view=HelpMenuSelect(), file=file)


class HelpMenuSelect(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder = "Choose from which system you want to see the help menu!",
        max_values = 1,
        min_values = 1,
        options = [
            discord.SelectOption(label="Mod commands", description="Shows you all commands that belong to the mod system", value="mod"),
            discord.SelectOption(label="Fun commands", description="Shows you all commands that belong to the Fun system", value="fun"),
            discord.SelectOption(label="Level system commands part 1", description="Shows you all commands that belong to the level system part 1", value="level_one"),
            discord.SelectOption(label="Level system commands part 2", description="Shows you all commands that belong to the level system part 2", value="level_two"),
            discord.SelectOption(label="Statistics system commands", description="Shows you all commands that belong to the statistics system", value="statistic"),
            discord.SelectOption(label="Anti-link system commands", description="Shows you all commands that belong to the anti-link system", value="antilink"),
            discord.SelectOption(label="Auto-reaction commands", description="Shows you all commands that belong to the auto-reaction system", value="auto_reaction"),
            discord.SelectOption(label="Message system commands", description="Shows you all commands that belong to the auto-reaction system", value="message_system"),
            discord.SelectOption(label="Other system commands", description="Shows you all commands that belong to the other systems", value="other_systems")
        ],
        custom_id = "help_menu_select")
    
    async def help_menue_select(self, select, interaction:discord.Interaction):

        if select.values[0] == "mod":

            emb = discord.Embed(description="## Mod commands", color=bot_colour)
            emb.add_field(name="/ban", 
                value="Ban a user", inline=True)
            emb.add_field(name="/unban", 
                value="Cancel the ban of a user", inline=True)
            emb.add_field(name="/kick", 
                value="Kick a user", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/timeout", 
                value="Give a user a timeout", inline=True)
            emb.add_field(name="remove-timeout", 
                value="Cancel the timeout of a user", inline=True)
            emb.add_field(name="/clear", 
                value="Delete messages in a channel", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/give-role", 
                value="Gives a user a role chosen by you", inline=True)
            emb.add_field(name="/remove-role", 
                value="Removes a user a role chosen by you", inline=True)

            await interaction.response.send_message(embed=emb, ephemeral=True)
            

        if select.values[0] == "fun":

            emb = discord.Embed(description=f"""## Fun commands""", color=bot_colour)
            emb.add_field(name="/rps", 
                value="Play rock, paper, scissors", inline=True)
            emb.add_field(name="/coinflip", 
                value="Flip a coin", inline=True)
            emb.add_field(name="/cocktails", 
                value="Get a random cocktail recipe", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/animememe", 
                value="Show you a random anime meme", inline=True)
            emb.add_field(name="/anime gif (tag)",
                value="Tags: kiss, hug, lick, feed, idk, dance, slap, fbi, embarres, pet", inline=True)
            await interaction.response.send_message(embed=emb, ephemeral=True)


        if select.values[0] == "level_one":

            emb = discord.Embed(description=f"""## Level system commands from part 1""", color=bot_colour)
            emb.add_field(name="/give-xp", 
                value="Give a user XP", inline=True)
            emb.add_field(name="/remove-xp", 
                value="Remove XP from a user", inline=True)
            emb.add_field(name="/give-level", 
                value="Enter a user level", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/remove-level", 
                value="Remove a user level", inline=True)
            emb.add_field(name="/reset-level", 
                value="Reset the level of all users", inline=True)
            emb.add_field(name="/reset-user-stats", 
                value="Reset the level of a user", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/rank", 
                value="Shows which level a user is", inline=True)
            emb.add_field(name="/leaderboard-level", 
                value="Shows 10 users with the highest level", inline=True)
            emb.add_field(name="/add-level-blacklist", 
                value="Add something to the level blacklist", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/remove-level-blacklist", 
                value="Remove something from the level blacklist", inline=True)
            emb.add_field(name="/show-level-blacklist", 
                value="Shows you the level blacklist", inline=True)
            emb.add_field(name="/reset-level-blacklist", 
                value="Resets the level blacklist", inline=True)
            await interaction.response.send_message(embed=emb, ephemeral=True)


        if select.values[0] == "level_two":

            emb = discord.Embed(description=f"""## Level system commands of part 2""", color=bot_colour)
            emb.add_field(name="/set-level-system", 
                value="Set the level system", inline=True)
            emb.add_field(name="/add-level-role", 
                value="Define roles as level roles", inline=True)
            emb.add_field(name="/remove-level-role", 
                value="Remove role as level roles", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/show-level-roles", 
                value="Shows you all level roles", inline=True)
            emb.add_field(name="/reset-level-roles", 
                value="Reset all level roles", inline=True)
            emb.add_field(name="/add-bonus-xp-list", 
                value="Add items to the bonus XP list", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/remove-bonus-xp-list", 
                value="Remove items from the bonus xp list", inline=True)
            emb.add_field(name="/show-bonus-xp-list", 
                value="Shows you the bonus xp list", inline=True)
            emb.add_field(name="/reset-bonus-xp-list", 
                value="Resets the bonus xp list", inline=True)
            await interaction.response.send_message(embed=emb, ephemeral=True)


        if select.values[0] == "statistic":

            emb = discord.Embed(description="""## Statistics system commands """, color=bot_colour)
            emb.add_field(name="/set-message-leaderboard",
                value="Set the message leaderboard", inline=True),
            emb.add_field(name="/show-message-leaderboard-setting",
                value="Shows you how the message leaderboard is set", inline=True),
            emb.add_field(name="/add-message-leaderboard-role",
                value="Adds a role to the message leaderboard", inline=True),
            emb.add_field(name=" ", value=" ", inline=False),
            emb.add_field(name="/remove-message-leaderboard-role",
                value="Removes a role from the message leaderboard", inline=True),
            emb.add_field(name="/show-message-leaderboard-roles",
                value="Shows all roles that are set for the message leaderbaord", inline=True),
            emb.add_field(name="/reset-message-leaderboard-roles",
                value="Resets all message leaderboard roles", inline=True),
            emb.add_field(name=" ", value=" ", inline=False),
            emb.add_field(name="/add-invite-leaderboard-role",
                value="Add a role to the invite leaderboard", inline=True),
            emb.add_field(name="/remove-invite-leaderboard-role",
                value="Removes a role from the invite leaderboard", inline=True),
            emb.add_field(name="/show-invite-leaderboard-roles",
                value="Shows all roles from the invite leaderboard", inline=True),
            emb.add_field(name=" ", value=" ", inline=False),
            emb.add_field(name="/reset-invite-leaderboard-roles",
                value="Resets all invite leaderboard roles", inline=True),
            emb.add_field(name="/show-invites",
                value="Shows how many users have been invited by a specific user", inline=True),
            emb.add_field(name="/userinfo", 
                value="Display all information about a user", inline=True)
            emb.add_field(name=" ", value=" ", inline=False),
            emb.add_field(name="/serverinfo", 
                value="Show all information about your server", inline=True)
            await interaction.response.send_message(embed=emb, ephemeral=True)

        
        if select.values[0] == "antilink":

            emb = discord.Embed(description=f"""## Anti-link system commands""", color=bot_colour)
            emb.add_field(name="/set-anti-link", 
                value="Set the anti-link system", inline=True)
            emb.add_field(name="/show-antilink-settings", 
                value="Shows how the antilin system is set", inline=True)
            emb.add_field(name="/add-antilink-whitelist", 
                value="Adds items to the whitelist", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/remove-antilink-whitelist", 
                value="Removes items from the whitelist", inline=True)
            emb.add_field(name="/show-antilink-whitelist", 
                value="Shows what is on the white list", inline=True)
            emb.add_field(name="/reset-antilink-whitelist", 
                value="Resets the whitelist", inline=True)
            
        
        if select.values[0] == "auto_reaction":

            emb = discord.Embed(description=f"""## Auto-reaction system commands""", color=bot_colour)
            emb.add_field(name="/set-auto-reaction",
                value="Sets the auto-reaction system", inline=True)
            emb.add_field(name="/add-auto-reaction",
                value="Adds auto-reactions to the server", inline=True)
            emb.add_field(name="/remove-auto-reaction",
                value="Removes auto-reactions from the server", inline=True)
            emb.add_field(name="", value="", inline=False)
            emb.add_field(name="/show-auto-reactions",
                value="Shows all auto-reactions that are set on the server", inline=True)
            emb.add_field(name="/reset-auto-reactions",
                value="Resets all auto-reactions that are set for the server", inline=True)
        

        if select.values[0] == "message_system":

            emb = discord.Embed(description=f"""## Message system commands""", color=bot_colour)
            emb.add_field(name="/set-sticky-message", 
                value="Sets the sticky message system", inline=True)
            emb.add_field(name="/add-sticky-message", 
                value="Adds a sticky message", inline=True)
            emb.add_field(name="/remove-sticky-message", 
                value="Removes a sticky message", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/show-sticky-message", 
                value="Shows all sticky messages", inline=True)
            emb.add_field(name="/reset-sticky-message", 
                value="Deletes all sticky messages", inline=True)
            emb.add_field(name="/set-auto-message", 
                value="Sets the auto message system", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/add-auto-message", 
                value="Adds a auto message", inline=True)
            emb.add_field(name="/remove-auto-message", 
                value="Removes a auto message", inline=True)
            emb.add_field(name="/show-auto-message", 
                value="Shows all auto messages", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/reset-auto-message", 
                value="Deletes all auto messages", inline=True)


        if select.values[0] == "other_systems":

            emb = discord.Embed(description="""## Other system commands""", color=bot_colour)
            emb.add_field(name="/ghost-ping-settings", 
                value="Set the ghost ping system", inline=True)
            emb.add_field(name="/set-booster-channel", 
                value="Sets the booster channel system", inline=True)
            emb.add_field(name="/add-booster-channel", 
                value="Defines a channel as a booster channel", inline=True)
            emb.add_field(name=" ", value=" ", inline=False)
            emb.add_field(name="/remove-booster-channel", 
                value="Removes the booster channel", inline=True)
            emb.add_field(name="/show-booster-channel", 
                value="Shows which channel is set as the booster channel", inline=True)
            emb.add_field(name="/set-ticket-system",
                value="Sets the ticket system", inline=True)
                        
            await interaction.response.send_message(embed=emb, ephemeral=True)


    @discord.ui.button(
            label="✕ Close",
            style=discord.ButtonStyle.blurple,
            custom_id="close_button"
        )
    
    async def callback(self, interaction:Interaction):
        
        await interaction.message.delete()

    @discord.ui.button(
        label="Explanation of the systems",
        style=discord.ButtonStyle.blurple,
        custom_id="explanation_button"
    )

    async def help_menu_explanation_button(self, button, interaction:discord.Interaction):

        emb = GetEmbed.get_embed(embed_index=15)

        await interaction.response.send_message(embed=emb, view=PaginatorViewHelpMenu(), ephemeral=True)



class PaginatorViewHelpMenu(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.pages = [
            GetEmbed.get_embed(embed_index=15),
            discord.Embed(
                description=f"""## Level system explained
                    {Emojis.dot_emoji} The level system allows users to level up by collecting XP, there is a cooldown of 20 seconds

                    ```General information on the level system```
                    > `set-level-system` Configure the level system. Set a level-up channel for notifications, adjust the XP earned per message, and define bonus XP values in the bonus list.
                    > `/give-xp` `/remove-xp` `/give-level` `/remove-level` `/reset-user-stats` `/rank` `/leaderboard-level`
                
                    ```Level roles```
                    {Emojis.dot_emoji} Level roles are roles that are assigned to users when they reach a certain level

                    > `/add-level-role` Adds a level role
                    > `/remove-level-role` Deletes a level role
                    > `/show-level-roles` Shows all active level roles
                    > `/reset-level-roles` Deletes all level roles
                
                    ```Level Blacklist```
                    {Emojis.dot_emoji} Users, channels, roles and categories can be blacklisted, if an item is blacklisted no messages will be rewarded with XP

                    > `/add-level-blacklist` Adds something to the level blacklist
                    > `/remove-level-blacklist` Deletes something from the level blacklist
                    > `/show-level-blacklist` Shows everything that is listed on the blacklist
                    > `/reset-level-blacklist` Deletes all entries from the blacklist
                
                    ```Bonus XP list```
                    {Emojis.dot_emoji} Users, channels, roles and categories can be added to the XP bonus list, the items that are on the list are rewarded with extra XP this is calculated as a percentage
                    
                    > `/add-bonus-xp-list` Adds something to the bonus XP list 
                    > `/remove-bonus-xp-list` Delete something from the bonus XP list
                    > `/show-bonus-xp-list` Shows everything on the bonus XP list
                    > `/reset-bonus-xp-list` Deletes all entries from the bonus XP list
                    """, color=bot_colour
            ),
            discord.Embed(
                description=f"""## Mod commands explained
                    {Emojis.dot_emoji} There are many different mod commands, here is an overview with more detailed explanations
                    
                    > `/ban` Bans a user who can then no longer join the server even by invitation
                    > `/unban` Cancels the ban of a user, but the user ID is required for this
                    > `/kick` Kicks a user from the server, but he can join again if he receives an invitation
                    > `/timeout` Sends a user into timeout, depending on the time selected, the user can no longer write or join voice calls for a certain period of time
                    > `/remove-timeout` Removes a timeout from a user
                    > `/clear` Deletes the amount of messages you specify when running
                    > `/give-role` Adds a role to a user provided it is not a role with permissions
                    > `/remove-role` Removes a role of a user
                    """, color=bot_colour
            ),
            discord.Embed(
                description=f"""## Fun commands explained
                    {Emojis.dot_emoji} There are different fun commands, here is an overview with explanations for the individual commands
                    
                    > `/rps` Play a round of rock, paper, scissors if you choose a user you can challenge them to a duel, but if you choose a bot or no one you play against shrio
                    > `/coinflip` Toss a coin, either heads or tails comes out
                    > `/cocktails` Gives you a random recipe for a cocktail, with the necessary ingredients, preparation and whether it is with alcohol or not, as well as a picture of what it should ideally look like
                    > `/animememe` Send a random anime meme from reddit
                    > `/anime gif (tag)` Send a random anime gif for this you can choose from the following tags `kiss` `hug` `lick` `feed` `idk` `dance` `slap` `fbi` `embarres` `pet`
                    """, color=bot_colour
            ),
            discord.Embed(
                description=f"""## Statistic system explained
                    {Emojis.dot_emoji} The statistics system consists of two leaderboards, one shows the users who have written the most messages and the other shows who has invited the most other users, for both there are fixed intervals

                    ```General commands for the statistic system```
                    {Emojis.dot_emoji} There are also commands that show the current numbers of the server or user

                    > `/show-invites` Shows the number of invited users from specific users
                    > `/userinfo` Displays information about specific users
                    > `/serverinfo` Displays information about the server

                    ```Leaderboard commands```
                    {Emojis.dot_emoji} You can set your own intervals for each leaderboard for the message leaderboard there are the intervals, daily, weekly and monthly, for the invite leaderboard weekly, monthly and quarterly is possible in addition a total overview is always sent
                    
                    > `/set-message-leaderboard` Let you set the leaderboards, including the intervals and the channel to which the leaderboards should be sent
                    > `/show-message-leaderboard-setting` Shows how the leaderboard is set and which channels or intervals have been defined
                    
                    ```Leaderboard roles```
                    {Emojis.dot_emoji} You can set whether you should receive a role when you reach a certain place on a leaderboard, it is also possible to set a separate role for each place or a role that is assigned for each place
                    
                    > `/add-message-leaderboard-role` Adds a role for the message leaderboard, it can be specified whether only a certain place receives the role or everyone
                    > `/remove-message-leaderboard-role` Removes a role from the message leaderboard
                    > `/show-message-leaderboard-roles` Displays all leaderboard roles of the message leaderboard
                    > `/reset-message-leaderboard-roles` Deletes all leaderboard roles of the message leaderboard

                    > `/add-invite-leaderboard-role` Adds a role for the invite leaderboard, it can also be specified whether only a certain place receives the role or everyone who is on the invite leaderboard
                    > `/remove-invite-leaderboard-role` Removes a ROlle from the invite leaderboard
                    > `/show-invite-leaderboard-roles` Shows all roles that are defined for the invite leaderboard
                    > `/reset-invite-leaderboard-roles` Deletes all roles defined for the invite leaderboard
                    """, color=bot_colour
            ),
            discord.Embed(
                description=f"""## Anti-link system explained
                    {Emojis.dot_emoji} The anti-link system prevents users from sending links of any kind or only certain kinds in channels where it is not wanted

                    ```Anti-link commands```
                    {Emojis.dot_emoji} Set the anti-link system, you can delete all discord links or only allow images / videos, it is also possible to allow no links at all

                    > `/set-anti-link` Choose how the anti-link system should behave
                    > `/show-antilink-settings` Shows how the anti-link system is set

                    ```Anti-link whitelist ```
                    {Emojis.dot_emoji} The whitelist is a list for which the anti-link system makes an exception and does not react, channels, users, roles or categories can be listed on it

                    > `/add-antilink-whitelist` Add something to the whitelist
                    > `/remove-antilink-whitelist` Remove something from the whitelist
                    > `/show-antilink-whitelist` Shows you what is listed on the anit-link whitelist
                    > `/reset-antilink-whitelist` Deletes all entries from the whitelist
                    """, color=bot_colour
            ),
            discord.Embed(
                description=f"""## Auto reaction system explained
                    {Emojis.dot_emoji} The auto reaction system adds selected reactions to content, you can choose to react only to text, only to images / videos or also to links or simply to every message
                    
                    > `/set-auto-reaction` Sets the auto-reaction system, you can choose what the system should react to, text, images / videos, links or everything
                    > `/add-auto-reaction` Adds something to the auto-reaction system, channel, user, role or categories can be added
                    > `/remove-auto-reaction` Removes some of the auto-reaction system
                    > `/show-auto-reactions` Shows how the auto-reaction system is set and what it reacts to
                    > `/reset-auto-reactions` Resets the auto-reaction system
                    """, color=bot_colour
            ),
            discord.Embed(
                description=f"""## Message system explained
                    {Emojis.dot_emoji} The message system consists of two components, the sticky message system and the auto message system, the sticky message system ensures that a message is always at the end of a channel, the auto message system always sends a message to a specific channel at a defined interval
                    
                    ```Sticky message```
                    {Emojis.dot_emoji} The sticky message system always sends a message when another user sends a message to a channel, so the bot's message is always the last message read

                    > `/set-sticky-message` Switch the sticky message system on or off
                    > `/add-sticky-message` Create a channel in which the sticky message should be sent and a text that should be sent
                    > `/remove-sticky-message` Removes a sticky message
                    > `/show-sticky-message` Shows you all sticky messages that have been defined for the server, these can be deactivated or deleted individually, and you can also edit them
                    > `/reset-sticky-message` Deletes all sticky messages

                    ```Auto message```
                    {Emojis.dot_emoji} The auto message system always sends a message at a specific interval to a specific channel

                    > `/set-auto-message` Switches the auto message system on or off
                    > `/add-auto-message` Defines a channel and an interval in which the message is then sent, the text of which can be freely selected
                    > `/remove-auto-message` Removes an auto message
                    > `/show-auto-message` Shows you all auto messages that have been defined for the server, these can be deactivated or deleted individually, you can also edit them
                    > `/reset-auto-message` Deletes all auto messages
                    """, color=bot_colour
            ),
            discord.Embed(
                description=f"""## Other systems explained
                    {Emojis.dot_emoji} There are also smaller systems like the ghost ping system and the booster channel system, with the ghost ping system a message is sent when a message is deleted with a ping, with the booster channel system you can set a channel for booster notifications

                    ```Ghost ping system```
                    {Emojis.dot_emoji} The ghost ping system always reacts when someone sends a message with a ping and then deletes it

                    > `/ghost-ping-settings` Sets the ghost ping system by activating or deactivating it
                    
                    ```Booster channel system```
                    {Emojis.dot_emoji} With the booster channel system you can define a channel for booster notifications, the message to be sent can also be freely defined

                    > `/set-booster-channel` Switches the booster channel system on or off
                    > `/add-booster-channel` Defines a channel for the booster messages and lets you freely determine the text
                    > `/remove-booster-channel` Removes the booster channel
                    > `/show-booster-channel` Shows the current booster channel including message, this can also be adjusted immediately

                    ```Ticket system```
                    {Emojis.dot_emoji} The ticket system allows users to create tickets to report problems (To use the ticket system you need to set a ticket message, a channel and at least one layer)
                    
                    > `/set-ticket-system` Sets the ticket system, it is possible to set on / off, temp voice channel can be created from tickets and the message itself can also be freely designed
                    """, color=bot_colour
            )
        ] 
        self.current_page = 0
        self.update_buttons_help()


    def update_buttons_help(self):

        self.children[0].disabled = self.current_page == 0  
        self.children[1].disabled = self.current_page == 0  
        self.children[2].disabled = self.current_page == len(self.pages) - 1 
        self.children[3].disabled = self.current_page == len(self.pages) - 1  


    async def update_message_help(self, interaction):
        self.update_buttons_help()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)


    @discord.ui.button(
        label="To the first page", 
        style=discord.ButtonStyle.blurple,
        custom_id="to_first_page_help"
    )
    
    async def go_to_first_page_help(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            self.current_page = 0
            await self.update_message_help(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="Back", 
        style=discord.ButtonStyle.blurple,
        custom_id="back_help"
    )

    async def back_button_help(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            
            if self.current_page > 0:
                self.current_page -= 1
            await self.update_message_help(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="Next", 
        style=discord.ButtonStyle.blurple,
        custom_id="next_help"
    )

    async def next_button_help(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            if self.current_page < len(self.pages) - 1:
                self.current_page += 1
            await self.update_message_help(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="To the last page", 
        style=discord.ButtonStyle.blurple,
        custom_id="to_last_page_help"
    )

    async def go_to_last_page_help(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            self.current_page = len(self.pages) - 1
            await self.update_message_help(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



bot.add_cog(HelpMenu(bot))




