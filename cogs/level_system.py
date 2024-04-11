
from typing import Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import discord
from discord.ext import commands
import re

from discord.interactions import Interaction
from utils import *


# level up message
def level_message(guild_id:int, user_id:int, level:int):

    user = f"<@{user_id}>"
    level_up_message = eval("f'{}'".format(DatabaseCheck.check_level_settings(guild_id=guild_id)[4]))
    return level_up_message


# Check the different parts of the level system and the database
class CheckLevelSystem():
    
    # Function that checks how high the bonus xp percentage rate is
    def check_bonus_xp(guild_id:int, message:discord.Message):

        check_settings = DatabaseCheck.check_level_settings(guild_id=guild_id)
        check_bonus_xp_list = DatabaseCheck.check_xp_bonus_list(guild_id=guild_id)
        
        if check_bonus_xp_list:
            
            for _, channel, category, role, user, percentage in check_bonus_xp_list:

                new_percentage = percentage if percentage != 0 else check_settings[5]

                if user == message.author.id:
                    return new_percentage
                
                check_role = message.guild.get_role(role)
                if check_role in message.author.roles:
                    return new_percentage
                
                if channel == message.channel.id:
                    return new_percentage

                if category == message.channel.category.id:
                    return new_percentage
        
        else:
            return None
    

    def show_level_roles(guild_id:int):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild_id = guild_id, status = "level_role")

        if level_roles:

            final_level_roles = []
            for _, role, lvl, _ in level_roles:

                final_level_roles.append(f"{Emojis.dot_emoji} The role <@&{role}> is assigned at level {lvl}")

            return "\n".join(final_level_roles)

        else:

            return f"{Emojis.dot_emoji} No level roles have been set"
    
    # Returns the blacklist completely formatted 
    def show_blacklist(guild_id:int):

        blacklist = DatabaseCheck.check_blacklist(guild_id = guild_id)

        channel_blacklist, category_blacklist, role_blacklist, user_blacklist = [], [], [], []
        for _, channel, category, role, user in blacklist:
                
            if channel != None:
                channel_blacklist.append(f"> {Emojis.dot_emoji} <#{channel}>\n")

            if category != None:
                category_blacklist.append(f"> {Emojis.dot_emoji} <#{category}>\n")

            if role != None:
                role_blacklist.append(f"> {Emojis.dot_emoji} <@&{role}>\n")

            if user != None:
                user_blacklist.append(f"> {Emojis.dot_emoji} <@{user}>\n")

        if all([channel_blacklist == [], category_blacklist == [], role_blacklist == [], user_blacklist == []]):
            return f"**{Emojis.dot_emoji} Nothing is listed on the blacklist**"
            
        else:

            final_blacklist = []
            for lst, label in [(channel_blacklist, "Channels"), (category_blacklist, "Categories"), (role_blacklist, "Roles"), (user_blacklist, "Users")]:

                if lst != []:
                    final_blacklist.extend([f"**{Emojis.dot_emoji} All {label} on the Blacklist:**\n"] + lst)

            return "".join(final_blacklist)
        

    # Returns the bonus Xp list completely formatted 
    def show_bonus_xp_list(guild_id:int):

        bonus_list = DatabaseCheck.check_xp_bonus_list(guild_id = guild_id)

        if bonus_list:

            final_bonus_xp_list = []
            for _, channel, category, role, user, percentage in bonus_list:

                for lst, percent, text in [
                    (f"<#{channel}>", percentage, "in"), 
                    (f"<#{category}>", percentage, "within the category"), 
                    (f"<@&{role}>", percentage, "of users with the role"), 
                    (f"<@{user}>", percentage, "from")]:

                    if "None" not in lst:
                        final_bonus_xp_list.append(f"{Emojis.dot_emoji} Activities {text} {lst} are rewarded with {percent if percent != None else '10'} % more XP")

            return "\n".join(final_bonus_xp_list)
        
        else:

            return f"{Emojis.dot_emoji} There is nothing listed on the bonus XP list"

  

######################################################  Level System level roles button  ##################################################

class LevelRolesButtons(discord.ui.View):
    def __init__(self, role_id:int, role_level:int, status:str):
        self.role_id = role_id
        self.role_level = role_level
        self.status = status
        super().__init__(timeout=None)

    # Button to override the level role 
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.blurple, custom_id="yes_button_level_role")
    async def yes_button_levelroles(self, button, interaction:discord.Interaction):
    
        if interaction.user.guild_permissions.administrator:

            if self.role_id == None and self.role_level == None and self.status == None:

                emb = discord.Embed(description=f"""## The role or level could not be overwritten
                    {Emojis.dot_emoji} The role or level could not be overwritten because the process has expired
                    {Emojis.dot_emoji} This happens when you wait too long to react to the button
                    {Emojis.dot_emoji} You can simply run the command again if you still want to overwrite the level or role {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                DatabaseUpdates.update_level_roles(guild_id=interaction.guild.id , role_id=self.role_id, role_level=self.role_level, status=self.status)
                            
                emb = discord.Embed(description=f"""## Successful override of the level role
                    {Emojis.dot_emoji} The level role was successfully overwritten
                    {Emojis.dot_emoji} The role <@&{self.role_id}> will be assigned at level **{self.role_level}** from now on""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:
                
            await interaction.response.send_message(embed=no_permissions_emb, view=None, ephemeral=True)


    # Button to cancel the overwriting of the level role 
    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, custom_id="no_button_level_role")
    async def no_button_levelroles(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## The overwriting of the level roles was successfully canceled
                {Emojis.dot_emoji} The overwriting of the level role has been canceled, so it is still available at the level it had before
                {Emojis.help_emoji} If you change your mind, you can re-execute the command at any time""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:
            
            await interaction.response.send_message(embed=no_permissions_emb, view=None, ephemeral=True)



#############################################  Reset Buttons level system  #######################################################


class ResetLevelStatsButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray, custom_id="yes_button_reset")
    async def reset_stats_button_level_yes(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id
            DatabaseRemoveDatas._remove_level_system_stats(guild_id=guild_id)

            emb = discord.Embed(description=f"""## You have reset all the stats of the level system
                {Emojis.dot_emoji} All user files have been deleted every user is now level 0 again and has 0 XP
                {Emojis.help_emoji} New entries will be created again when there is an activity""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)


        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True)

    
    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="no_button_reset")
    async def reset_stats_button_level_no(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
        
            emb = discord.Embed(description=f"""## The operation was successfully canceled
                {Emojis.dot_emoji} Resetting the stats was successfully aborted
                {Emojis.dot_emoji} All users keep their stats in the level system""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)
                    
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



#######################################  Level system Blacklist buttons  ###########################################


class ResetBlacklistLevelButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.blurple, row=1, custom_id="yes_button_level")
    async def reset_blacklist_button_level_yes(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            guild_id = interaction.guild.id

            DatabaseUpdates.manage_blacklist(guild_id=guild_id, operation="reset")

            emb = discord.Embed(description=f"""## The blacklist has been reset
                {Emojis.dot_emoji} All channels, users, roles and categories have been removed from the blacklist
                {Emojis.help_emoji} If you want to blacklist things again you can use the commands as before""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)


    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, row=1, custom_id="no_button_level")
    async def reset_blacklist_button_level_no(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""Resetting the level system blacklist has been canceled 
                {Emojis.dot_emoji} Resetting the blacklist was successfully aborted
                {Emojis.dot_emoji} All channels, roles, categories and users are still listed on the blacklist
                {Emojis.help_emoji} If you want to remove single elements from the blacklist you can remove them with the `/remove-level-blacklist` command""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)



#########################################################  Message Level system  ###################################################

class LevelSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.cd = commands.CooldownMapping.from_cooldown(1, 10.0, commands.BucketType.member)

    def get_ratelimit(self, message:discord.Message):
        bucket = self.cd.get_bucket(message)
        return bucket.update_rate_limit()

    @staticmethod
    def xp_generator(guild_id:int, message:discord.Message = None):

        settings = DatabaseCheck.check_level_settings(guild_id=guild_id) 
        check_bonus_xp_system = CheckLevelSystem.check_bonus_xp(guild_id=guild_id, message=message) if message != None else 0
     
        if check_bonus_xp_system != 0 and check_bonus_xp_system != None:
        
            xp = settings[1] * (1 + (check_bonus_xp_system / 100))    
        else:
            xp = settings[1]
        
        return xp
    
    @staticmethod
    def round_corner_mask(radius, rectangle, fill):
    
        bigsize = (rectangle.size[0] * 3, rectangle.size[1] * 3)
        mask_rectangle = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask_rectangle)
        draw.rounded_rectangle((0, 0)+bigsize, radius=radius, fill=fill, outline=None)
        mask = mask_rectangle.resize(rectangle.size, Image.LANCZOS)
        rectangle.putalpha(mask)
        return (rectangle, mask)
    
    
    # Level system checks who gets XP and how much has a cooldown of 10 seconds
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        
        # If it is a direct message
        if not message.guild:
            return

        # Check if the cool down has already expired if not the message will not be counted
        if self.get_ratelimit(message):
            return

        with open("config.yaml", 'r') as f:
            data = yaml.safe_load(f)

        if message.content.startswith(data["Prefix"]):
            return

        if message.author.bot:
            return 

        # Checks the settings and returns false if the level system is disabled and none if no entry was found 
        check_settings = DatabaseStatusCheck._level_system_status(guild_id=message.guild.id)
        
        if check_settings == None:
            DatabaseUpdates._create_bot_settings(guild_id=message.guild.id)
            return
        
        elif check_settings == False:
            return
                
        # Checks the blacklist and returns true if the channel is on the blacklist
        check_blacklist = DatabaseStatusCheck._blacklist_check_text(message_check=message, guild_id=message.guild.id)
                        
        if isinstance(message.channel, discord.TextChannel):
                    
            if check_blacklist != True:
                
                try:   
                            
                    # Database check for all values 
                    check_if_exists = DatabaseCheck.check_level_system_stats(guild_id=message.guild.id, user=message.author.id)

                    if check_if_exists:
                                     
                        if check_if_exists[2] >= 999:
                            return

                        XP = self.xp_generator(guild_id=message.guild.id, message=message)
                    
                        user_has_xp = check_if_exists[3] + XP 
                        whole_xp = check_if_exists[6] + XP                     
                        xp_need_next_level = 5 * (check_if_exists[2] ^ 2) + (50 * check_if_exists[2]) + 100 - check_if_exists[3]
                        final_xp = xp_need_next_level + check_if_exists[3]
                        
                        if user_has_xp >= final_xp:
                                                                        
                            new_level = check_if_exists[2] + 1    

                            try:
                                
                                # Updates the XP
                                DatabaseUpdates._update_user_stats_level(guild_id=message.guild.id, user_id=message.author.id, level=new_level, whole_xp=whole_xp)

                            except mysql.connector.Error as error:
                                print("parameterized query failed {}".format(error))
                                                                    
                            finally:   

                                # Checks if a level role or a level up channel is defined                                
                                check_level_role = DatabaseCheck.check_level_system_levelroles(guild_id=message.guild.id, needed_level=new_level)
                                check_level_up_channel = DatabaseCheck.check_level_settings(guild_id=message.guild.id)

                                if check_level_up_channel[3]:
                                    
                                    channel = bot.get_channel(check_level_up_channel[3])
                            
                                    await channel.send(level_message(guild_id=message.guild.id, user_id=message.author.id, level=new_level))

                                    if check_level_role:

                                        level_role = message.guild.get_role(check_level_role[1])
                                        await message.author.add_roles(level_role)
                                        await channel.send(f"<@{message.author.id}> you have received the role <@&{check_level_role[1]}> because you have reached level **{check_level_role[2]}**. ")
                                
                                else:

                                    await message.channel.send(level_message(guild_id=message.guild.id, user_id=message.author.id, level=new_level))

                                    if check_level_role:

                                        level_role = message.guild.get_role(check_level_role[1])
                                        await message.author.add_roles(level_role)
                                        await message.channel.send(f"<@{message.author.id}> you have received the role <@&{check_level_role[1]}> because you have reached level **{check_level_role[2]}**. ")
                                                
                        else:

                            try:

                                DatabaseUpdates._update_user_stats_level(guild_id=message.guild.id, user_id=message.author.id, xp=user_has_xp, whole_xp=whole_xp)                       

                            except mysql.connector.Error as error:
                                print("parameterized query failed {}".format(error))

                    else:
                            
                        DatabaseUpdates._insert_user_stats_level(guild_id=message.guild.id, user_id=message.author.id, user_name=message.author.name)

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))
   


    @commands.slash_command(name = "set-level-system", description = "Set the level system the way you want it!")
    @commands.has_permissions(administrator = True)
    async def set_level_system(self, ctx:discord.ApplicationContext):

        emb = discord.Embed(
            description=f"""# {Emojis.settings_emoji} Set the level system
            With the lower select menu you can choose which function of the level system you want to set\n## Individual systems:
            **{Emojis.dot_emoji} Level up channel:** 
            > Set a channel to which all level up notifications and all notifications for new roles are sent

            **{Emojis.dot_emoji} Level up message:** 
            > Set a custom message that is sent when you get level up

            **{Emojis.dot_emoji} Bonus XP rate:** 
            > Set how much XP should be awarded per activity

            **{Emojis.dot_emoji} Bonus XP percentage:** 
            > Set a percentage with which all activities in the channel, categories or by the 
            > users with a role or the users themselves are rewarded with extra XP

            {Emojis.help_emoji} `You can also reset all settings individually`""", color=bot_colour)
        await ctx.response.send_message(embed=emb, view=LevelSystemSetting())



####################################################  User stats setting  #################################################


    @commands.slash_command(name = "give-xp", description = "Give a user a quantity of XP chosen by you!")
    @commands.has_permissions(administrator = True)
    async def give_xp(self, ctx:discord.ApplicationContext, user:Option(discord.Member, description="Select a user who should receive the xp!"),
        xp:Option(int, description="Specify a quantity of XP to be added!")):

        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id, user=user.id)

            if check_stats:
                
                user_level, user_xp = check_stats[2], check_stats[3]
                xp_need_next_level = 5 * (user_level ^ 2) + (50 * user_level) + 100 - user_xp

                if xp <= xp_need_next_level:

                    new_xp = user_xp + xp
                    new_whole_xp = xp + check_stats[6]

                    DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, xp=new_xp, whole_xp=new_whole_xp)
                        
                    emb = discord.Embed(description=f"""## You have successfully given {user.mention} {xp} XP
                    {Emojis.dot_emoji} You have given **{user.mention}** {xp} XP, **{user.mention}** has from now on **{new_xp}** XP
                    {Emojis.help_emoji} If you want to remove {user.mention} XP you can use the `/remove-xp` command or use the `/give-level` command to enter level""", color=bot_colour)
                    await ctx.respond(embed=emb)

                    if xp >= xp_need_next_level:

                        new_level = user_level + 1
                                            
                        DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, level=new_level, whole_xp=new_whole_xp)
                        levelup_channel_check = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

                        if levelup_channel_check[3] == None:

                            await ctx.send(level_message(guild_id=ctx.guild.id, user_id=user.id, level=new_level))
                            
                        else:
                            
                            levelup_channel = bot.get_channel(levelup_channel_check[3])
                            await levelup_channel.send(level_message(guild_id=ctx.guild.id, user_id=user.id, level=new_level))
                else:
        
                    emb = discord.Embed(description=f"""## The XP you want to give is too high
                        {Emojis.dot_emoji} The XP you want to pass to **{user.mention}** is too high
                        {Emojis.dot_emoji} You can only give **{user.mention}** a maximum of **{xp_need_next_level}** XP, as it then reaches a new level""", color=bot_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)
                
                await ctx.respond(embed=GetEmbed.get_embed(embed_index=1, settings=user.name)) 


    @commands.slash_command(name = "remove-xp", description = "Remove a chosen amount of Xp from a user!")
    @commands.has_permissions(administrator = True)
    async def remove_xp(self, ctx:discord.ApplicationContext, user:Option(discord.Member, description="Choose a user from which you want to remove xp!"),
        xp:Option(int, description="Specify a quantity of Xp to be removed!")):
            
        check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id, user=user.id)

        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            if check_stats:
                
                user_xp = check_stats[3]
                new_xp = user_xp - xp 

                if xp > user_xp:
                            
                    emb = discord.Embed(description=f"""## The XP you want to remove from is too high
                        {Emojis.dot_emoji} The XP you want to remove from **{user.mention}** is too high
                        {Emojis.dot_emoji} You can only remove a maximum of **{user_xp}** XP from **{user.mention}**""", color=bot_colour)
                    await ctx.respond(embed=emb)

                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, xp=new_xp)

                    emb = discord.Embed(description=f"""## You have successfully removed the XP
                        {Emojis.dot_emoji} You have removed **{user.mention}** {xp} XP **{user.mention}** has **{new_xp}** XP from now on
                        {Emojis.dot_emoji} If you want to give **{user.mention}** XP again use the /give-xp command""", color=bot_colour)
                    await ctx.respond(embed=emb)

            else:
                    
                DatabaseUpdates._insert_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)
                    
                await ctx.respond(embed=GetEmbed.get_embed(embed_index=1, settings=user.name))  


    @commands.slash_command(name = "give-level", description = "Give a user a selected amount of levels!")
    @commands.has_permissions(administrator = True)
    async def give_level(self, ctx:discord.ApplicationContext, user:Option(discord.Member, description="Choose a user you want to give the levels to!"), 
        level:Option(int, description="Specify a set of levels that you want to assign!")):

        check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id, user=user.id)

        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            if check_stats:
                
                new_level = check_stats[2] + level
                levels_to_maxlevel = 999 - level
                            
                if level > 999 or new_level >= 999:

                    emb = discord.Embed(description=f"""## The level you want to give is too high
                        {Emojis.dot_emoji} The level you want to give **{user.mention}** is too high because the maximum level is **999**
                        {Emojis.dot_emoji} You can only give **{user.mention}** a maximum of {levels_to_maxlevel} levels""", color=bot_colour)
                    await ctx.respond(embed=emb)

                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, level=new_level, whole_xp = check_stats[6])

                    emb = discord.Embed(description=f"""## You have successfully added the levels
                        {Emojis.dot_emoji} You gave **{user.mention}** {level} levels, from now on **{user.mention}** has **{new_level}** level
                        {Emojis.dot_emoji} If you want to remove **{user.mention}** levels again use the /remove-level command""", colour=bot_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)

                await ctx.respond(embed=GetEmbed.get_embed(embed_index=1, settings=user.name)) 
                

    @commands.slash_command(name = "remove-level", description = "Remove a quantity of levels chosen by you!")
    @commands.has_permissions(administrator = True)
    async def remove_level(self, ctx:discord.ApplicationContext, user:Option(discord.Member, description="Select a user from whom you want to remove the level!"), 
        level:Option(int, description="Specify how many levels should be removed!")):

        check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id, user=user.id)
        
        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            if check_stats:
    
                new_level = check_stats[2]  - level 

                if level > check_stats[2] :

                    emb = discord.Embed(description=f"""## The number of levels you want to remove is too high
                        {Emojis.dot_emoji} The number of levels you want to remove from {user.mention} is too high
                        {Emojis.dot_emoji} You can remove from **{user.mention}** only up to **{check_stats[2] }** levels""", color=bot_colour)
                    await ctx.respond(embed=emb)

                
                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id,  level=new_level)

                    emb = discord.Embed(description=f"""## You have successfully removed the levels
                        {Emojis.dot_emoji} You have removed **{user.mention}** {level} levels, **{user.mention}** is now level **{new_level}**
                        {Emojis.dot_emoji} If you want to give **{user.mention}** levels again use the /give-level command""", color=bot_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)
                
                await ctx.respond(embed=GetEmbed.get_embed(embed_index=1, settings=user.name))  
    

    @commands.slash_command(name = "reset-level-system-stats", description = "Reset all levels and xp of everyone!")
    @commands.has_permissions(administrator = True)
    async def reset_level(self, ctx:discord.ApplicationContext):

        check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id)

        if check_stats:

            emb = discord.Embed(description=f"""## Are you sure you want to reset the level system?
                {Emojis.dot_emoji} With the buttons you can confirm your decision
                {Emojis.dot_emoji} If you press the **Yes button** all user stats will be deleted
                {Emojis.dot_emoji} If you press the **No button** the process will be aborted""", color=bot_colour)
            await ctx.respond(embed=emb, view=ResetLevelStatsButton())

        else:
            
            emb = discord.Embed(description=f"""## No data found for this server
                {Emojis.dot_emoji} No data was found for this server, so nothing could be deleted
                {Emojis.dot_emoji} Data is created automatically as soon as messages are sent and the level system is switched on""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "reset-user-stats", description = "Resets all stats of the specified user in the level system!")
    @commands.has_permissions(administrator = True)
    async def reset_user_stats(self, ctx:discord.ApplicationContext, user:Option(discord.Member, description="Choose a user whose stats you want to reset!")):

        check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id, user=user.id)

        if check_stats:

            DatabaseRemoveDatas._remove_level_system_stats(guild_id=ctx.guild.id, user_id=user.id)

            emb = discord.Embed(description=f"""## The user data has been reset
                {Emojis.dot_emoji} The user stats of {user.mention} have been reset
                {Emojis.dot_emoji} {user.mention} is now level 0 again with 0 XP""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(description=f"""## No entry was found
                {Emojis.dot_emoji} No entry was found for {user.mention}
                {Emojis.dot_emoji} Therefore the stats could not be reset""", color=bot_colour)


    @commands.slash_command(name = "rank", description = "Shows you the rank of a user in the level system!")
    async def rank(self, ctx:discord.ApplicationContext, user:Option(discord.Member, description="Look at the rank of others!")):

        count = 0
        rank = 0
        connection_to_db_level = DatabaseSetup.db_connector()
        my_cursor = connection_to_db_level.cursor()

        error_emb = discord.Embed(title=f"{Emojis.help_emoji} The user was not found", 
            description=f"""{Emojis.dot_emoji} The user was not found, it may be that he is not yet participating in the level system.
            {Emojis.dot_emoji} You can only join the level system if you have sent at least one message to a channel that is not blacklisted {Emojis.exclamation_mark_emoji}""", color=bot_colour)

        check_user = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id, user=user.id)
        
        if check_user:

            rank_show_infos_level = "SELECT * FROM LevelSystemStats WHERE guildId = %s ORDER BY userLevel DESC, userXp DESC"
            rank_show_infos_levels_values = [ctx.guild.id]
            my_cursor.execute(rank_show_infos_level, rank_show_infos_levels_values)
            all_info = my_cursor.fetchall()
          
            for _, user_id_rank, _, _, _, _, _ in all_info:
                    
                if user.id == user_id_rank:
                
                    for rank_count in all_info:

                        count = count + 1
                                                            
                        if user.id == rank_count[1]:

                            rank = count 
                            
            xp = check_user[3]
        
            xp_needed = 5 * (check_user[2] ^ 2) + (50 * check_user[2]) + 100 - check_user[3]
            final_xp = xp_needed + xp
            xp_have = check_user[3]

            # Create card
            big_font = ImageFont.FreeTypeFont("assets/rank-card/ABeeZee-Regular.otf", 58)
            small_font = ImageFont.truetype("assets/rank-card/arial.ttf", 24)

            background_color = (8, 120, 151)
            background = Image.new("RGBA", (885, 303), color=background_color)
            new_background = self.round_corner_mask(radius=50, rectangle=background, fill=255)
            background.paste(new_background[0], (0, 0), new_background[1])

            img = Image.open("assets/rank-card/card2.png").resize((867, 285))
            filtered_image = img.filter(ImageFilter.BoxBlur(4))
            new_img = self.round_corner_mask(radius=50, rectangle=filtered_image, fill=255)
            background.paste(new_img[0], (9, 9), mask=new_img[1])

            # Get the profile picture and set it on the background
            pfp = BytesIO(await user.display_avatar.read())
            profile = Image.open(pfp).resize((225, 225))
            bigsize = (profile.size[0] * 3, profile.size[1] * 3)
            mask = Image.new("L", bigsize, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0)+ bigsize, 255)
            mask = mask.resize(profile.size, Image.LANCZOS)
            profile.putalpha(mask)

            background.paste(profile, (47, 39), mask=mask)

            draw = ImageDraw.Draw(background)

            bar_offset_x = 304
            bar_offset_y = 155
        
            bar = Image.new('RGBA', (545, 36), (0, 0, 0))
            bar = self.round_corner_mask(radius=50, rectangle=bar, fill=160)
            background.paste(bar[0], (bar_offset_x, bar_offset_y), bar[1])

            # Filling Bar
            bar_length = 849 - bar_offset_x
            progress = (final_xp - xp_have) * 100 / final_xp
            progress = 100 - progress
            progress_bar_length = round(bar_length * progress / 100)
            bar_offset_x_1 = bar_offset_x + progress_bar_length
           
            # Progress Bar
            if xp != 0:

                progress_bar = Image.new("RGBA", ((bar_offset_x_1 - bar_offset_x), 36), background_color)
                progress_bar = self.round_corner_mask(radius=50, rectangle=progress_bar, fill=255) 
                background.paste(progress_bar[0], (bar_offset_x, bar_offset_y), progress_bar[1])

            xp_display_line = Image.new(mode="RGBA", size=(340, 33), color=(0, 0, 0))
            xp_display_line = self.round_corner_mask(radius=50, rectangle=xp_display_line, fill=160)
            offset_y = 200
            background.paste(xp_display_line[0], (304, offset_y), xp_display_line[1])

            # Displays the level of the user
            data_display = Image.new(mode="RGBA", size=(196, 33), color=(0, 0, 0))
            data_display = self.round_corner_mask(radius=50, rectangle=data_display, fill=160)
            background.paste(data_display[0], (655, offset_y), data_display[1])

            total_xp_display = Image.new(mode="RGBA", size=(547, 33), color=(0, 0, 0))
            total_xp_display = self.round_corner_mask(radius=50, rectangle=total_xp_display, fill=160)
            background.paste(total_xp_display[0], (304, (offset_y + 46)), total_xp_display[1])

            draw.text((304, 75), user.name, font=big_font, fill=(255, 255, 255))
            draw.text((315, (offset_y + 2)), f"{xp_have:,} / {final_xp:,} XP", font=small_font, fill=(255, 255, 255))
            draw.text((665, (offset_y + 1)), f"#{rank} Lvl {check_user[2]}", font=small_font, fill=(255, 255, 255))
            draw.text((315, (offset_y + 48)), f"total: {check_user[6]:,} XP", font=small_font, fill=(255, 255, 255))

            bytes = BytesIO()
            background.save(bytes, format="PNG")
            bytes.seek(0)
            dfile = discord.File(bytes, filename="card.png")
            await ctx.respond(file=dfile)

        else:

            await ctx.respond(embed=error_emb)


    @commands.slash_command(name = "leaderboard-level", description = "Shows the highest ranks in the lavel system!")
    async def leaderboard(self, ctx:discord.ApplicationContext):

        leaderboard_connect = DatabaseSetup.db_connector()
        my_cursor = leaderboard_connect.cursor()

        leaderboard_levels = "SELECT userId, userLevel, userXp FROM LevelSystemStats WHERE guildId = %s ORDER BY userLevel DESC, userXp DESC"
        leaderboard_levels_values = [ctx.guild.id]
        my_cursor.execute(leaderboard_levels, leaderboard_levels_values)

        leaderboard_members =  my_cursor.fetchall()
        c = []
        for i, pos in enumerate(leaderboard_members, start=1):
            member_id, lvl, xp = pos
            
            if i <= 10:

                c.append(f"{i}. `level {lvl: }` `{xp} XP`    <@{member_id}>")
            
        level_roles_mention_end = '\n'.join(c)

        DatabaseSetup.db_close(cursor=my_cursor, db_connection=leaderboard_connect)

        emb = discord.Embed(title="Leaderboard", description=f"{level_roles_mention_end}", color=bot_colour)
        emb.set_footer(icon_url=ctx.guild.icon.url, text="These are the most active users of this server")
        await ctx.respond(embed=emb)

    

#################################################  Level Blacklist settings  ###############################################


    async def config_level_blacklist(
            self, 
            guild_id:int, 
            operation:str, 
            channel = None, 
            category = None, 
            role = None, 
            user = None):

        if [x for x in [channel, category, role, user] if x]:
            
            check_channel = DatabaseCheck.check_blacklist(guild_id=guild_id, channel_id=channel.id) if channel != None else False
            check_category = DatabaseCheck.check_blacklist(guild_id=guild_id, category_id=category.id) if category != None else False
            checK_role = DatabaseCheck.check_blacklist(guild_id=guild_id, role_id=role.id) if role != None else False
            check_user = DatabaseCheck.check_blacklist(guild_id=guild_id, user_id=user.id) if user != None else False

            items = {0:check_channel, 1:check_category, 2:checK_role, 3:check_user}
            items_list = [channel, category, role, user]
            
            if [x for x in items.values() if x is None] and operation == "add" or any(x for x in items.values() if x is not False or None) and operation == "remove":

                res = list({ele for ele in items if items[ele]}) if operation == "add" else list({ele for ele in items if items[ele] is None})
                second_res = list({ele for ele in items if items[ele] is None}) if operation == "add" else list({ele for ele in items if items[ele]})
            
                item = [(f"> {Emojis.dot_emoji} {items_list[i].mention}") for i in res] 
                second_item = [(f"> {Emojis.dot_emoji} {items_list[i].mention}") for i in second_res]
        
                items_dict = {
                    0:channel.id if 0 in second_res else None, 
                    1:category.id if 1 in second_res else None, 
                    2:role.id if 2 in second_res else None,
                    3:user.id if 3 in second_res else None
                }
            
                if operation == "add":
                    
                    formatted_items = "\n".join(item) if item != [] else "\n> None of the items you specified were on the blacklist"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> None of the items you specified could be blacklisted because they are already on the blacklist"
                    
                    DatabaseUpdates.manage_blacklist(guild_id=guild_id, operation="add", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3])    
                        
                    emb = discord.Embed(title=f"{Emojis.help_emoji} The following items have been added to the blacklist or were already there", 
                        description=f"""### {Emojis.dot_emoji} The following were already on the blacklist:
                        {formatted_items}\n### {Emojis.dot_emoji} Newly added:
                        {formatted_add_items}""", color=bot_colour)
                    return emb

                elif operation == "remove":
                
                    formatted_items = "\n".join(item) if item != [] else "> All the items you specified were on the blacklist"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> None of the items you specified could be removed from the blacklist because they are not on the blacklist"

                    DatabaseUpdates.manage_blacklist(guild_id=guild_id, operation="remove", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3])

                    emb = discord.Embed(title=f"{Emojis.help_emoji} The following items have been removed from the blacklist or were not listed", 
                        description=f"""### {Emojis.dot_emoji} The following items were not on the blacklist:
                        {formatted_items}\n### {Emojis.dot_emoji} Was deleted from the blacklist:
                        {formatted_add_items}""", color=bot_colour)
                    return emb
                
            else:

                emb = discord.Embed(title=f"{Emojis.help_emoji} Nothing can be {'blacklisted' if operation == 'add' else 'removed from the blacklist'}", 
                    description=f"""{Emojis.dot_emoji} {"All the things you have specified are already on the blacklist" 
                        if operation == "add" else 
                        "None of the things you mentioned are on the blacklist"}""", color=bot_colour)
                return emb
            
        else:

            emb = discord.Embed(title=f"{Emojis.help_emoji} You have not specified anything!", 
                description=f"""{Emojis.dot_emoji}You have not specified anything {"what should be blacklisted" 
                    if operation == "add" else
                    "What should be removed from the blacklist"}""", color=bot_colour)
            return emb


    @commands.slash_command(name = "add-level-blacklist", description = "Add what you want to the blacklist!")
    @commands.has_permissions(administrator = True)
    async def add_level_blacklist(self, ctx:discord.ApplicationContext, 
        channel:Option(Union[discord.VoiceChannel, discord.TextChannel], required = False, description="Select a channel that you want to exclude from the level system!"),
        category:Option(discord.CategoryChannel, required = False, description="Select a category that you want to exclude from the level system!"),
        role:Option(discord.Role, required = False, description="Select a role that you want to exclude from the level system!"),
        user:Option(discord.User, required = False, description="Select a user that you want to exclude from the level system!")):

        check_blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id)

        filtered_list = []
        if category != None:
            
            for _, channels, _, _, _ in check_blacklist:

                if channels:
                    
                    if bot.get_channel(channels).category.id == category.id:

                        DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", channel_id=channels)
                        filtered_list.append(f"> {Emojis.dot_emoji} <#{channels}>")
        
        if channel != None and any(channel.category.id == x[2] for x in check_blacklist):

            emb = discord.Embed(description=f"""## The channel is already indirectly on the blacklist
                {Emojis.dot_emoji} The channel {channel.mention} that you want to blacklist is already on the blacklist because it is listed under the category {channel.category.mention} and is therefore automatically excluded.""", color=bot_colour)
            await ctx.respond(embed=emb)

        elif category != None and filtered_list != []:
 
            channel_list = "\n".join(filtered_list)
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", category_id=category.id)
                    
            emb = discord.Embed(description=f"""## {Emojis.help_emoji} {'One channel' if len(filtered_list) == 1 else 'Several channels'} in this category {'is' if len(filtered_list) == 1 else 'are'} already blacklisted
                    {Emojis.dot_emoji} The following {'channel is' if len(filtered_list) == 1 else 'channels are'} already blacklisted \n\n{channel_list}
                    {Emojis.arrow_emoji} Therefore {'this' if len(filtered_list) == 1 else 'these'} channel will be removed from the blacklist and the category will be added instead
                   This excludes all channels in the category from the level system""", color=bot_colour)
            await ctx.respond(embed=emb) 

        elif user != None and user.bot:

            emb = discord.Embed(description=f"""## You cannot put a bot on the blacklist
                {Emojis.dot_emoji} All bots are automatically excluded from the level system
                {Emojis.dot_emoji} Bots also do not receive XP and cannot level up""", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:

            emb = await self.config_level_blacklist(guild_id=ctx.guild.id, operation="add", channel=channel, category=category, role=role, user=user)
            await ctx.respond(embed=emb)
    
    
    @commands.slash_command(name = "remove-level-blacklist", description = "Remove what you want from the blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_level_blacklist(self, ctx:discord.ApplicationContext, 
        channel:Option(Union[discord.VoiceChannel, discord.TextChannel], required = False, description="Select a channel you want to remove from the blacklist!"),
        category:Option(discord.CategoryChannel, required = False, description="Select a category you want to remove from the blacklist"),
        role:Option(discord.Role, required = False, description="Select a role you want to remove from the blacklist"),
        user:Option(discord.User, required = False, description="Select a user that you want to remove from the blacklist!")):

        emb = await self.config_level_blacklist(guild_id=ctx.guild.id, operation="remove", channel=channel, category=category, role=role, user=user)
        await ctx.respond(embed=emb)

   
    @commands.slash_command(name = "show-level-blacklist", description = "Shows you everything that is blacklisted!")
    async def show_blacklist(self, ctx:discord.ApplicationContext):

        emb = discord.Embed(description=f"""## Current level system blacklist
            {Emojis.dot_emoji} Everything that is on the blacklist is excluded from the level system so you will not receive any XP when you perform an activity
            Here you can see all items that are on the blacklist:
                
            {CheckLevelSystem.show_blacklist(guild_id = ctx.guild.id)}""", color=bot_colour)
        await ctx.respond(embed=emb)


    @commands.slash_command(name = "reset-level-blacklist", description="Reset the blacklist of the level system and remove all entries!")
    @commands.has_permissions(administrator = True)
    async def reset_blacklist(self, ctx:discord.ApplicationContext):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id)

        if blacklist:

            view = ResetBlacklistLevelButton()

            emb = discord.Embed(description=f"""## Are you sure you want to remove everything from the blacklist?
                {Emojis.help_emoji} With the buttons you can confirm your decisions!
                {Emojis.dot_emoji} If you press the **Yes button** all channels, categories, users and roles will be removed from the blacklist
                {Emojis.dot_emoji} If you press the **No button** the process will be aborted""", color=bot_colour)
            await ctx.respond(embed=emb, view=view)
        
        else:

            emb = discord.Embed(description=f"""## {Emojis.help_emoji} There is nothing on the blacklist
                {Emojis.dot_emoji} No entries have been created yet
                {Emojis.dot_emoji} Therefore nothing can be deleted from the blacklist""", color=bot_colour)
            await ctx.respond(embed=emb)



#############################################  level roles settings  #################################################

    
    @commands.slash_command(name = "add-level-role", description = "Add a role that you get from a certain level!")
    @commands.has_permissions(administrator = True)
    async def add_level_role(self, ctx:discord.ApplicationContext, role:Option(discord.Role, description = "Select a role that you want to assign from a certain level onwards"),
        level:Option(int, description = "Enter a level from which this role should be assigned")):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, level_role=role.id, needed_level=level, status = "check")

        emb_level_0 = discord.Embed(description=f"""## The level you want to set is 0
            {Emojis.dot_emoji} The level to vest a level role must be at least level **1**
            {Emojis.help_emoji} You can simply run the command again to assign this role to a different level""", color=bot_colour)
        
        emb_higher = discord.Embed(description=f"""## The level you want to set is too high
            {Emojis.dot_emoji} The level you want to set for the level role is too high
            {Emojis.dot_emoji} You can only set a value that is below or equal to **999**""", color=bot_colour)
        
        if role.permissions.administrator or role.permissions.moderate_members:

            emb = discord.Embed(description=f"""## This role cannot be assigned as a level role
                {Emojis.dot_emoji} This role has administration or moderation rights and therefore cannot be assigned as a level role
                {Emojis.dot_emoji} In order to protect your server, you should not carelessly assign roles with important authorizations""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            if level_roles == None:
                
                if level <= 999:
                            
                    DatabaseUpdates._insert_level_roles(guild_id=ctx.guild.id, role_id=role.id, level=level, guild_name=ctx.guild.name)

                    emb = discord.Embed(description=f"""## The role was assigned successfully as a level role
                        {Emojis.dot_emoji} The role {role.mention} was successfully assigned to the level {level}
                        {Emojis.dot_emoji} As soon as a user reaches level {level} he gets the {role.mention} role""", color=bot_colour)
                    await ctx.respond(embed=emb)

                await ctx.respond(embed=emb_level_0) if level == 0 else None

                await ctx.respond(embed=emb_higher) if  level > 999 else None 

            else:

                check_same = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, level_role=role.id, needed_level=level)
                    
                if check_same:

                    same_emb = discord.Embed(description=f"""## This role has already been set at this level
                        {Emojis.dot_emoji} The role {role.mention} is already assigned to the level {level}
                        {Emojis.dot_emoji} If you want to change it you can assign this role to another level or another role to this level""", color=bot_colour)
                    await ctx.respond(embed=same_emb)

                else:
                    
                    if role.id == level_roles[1]:
            
                        emb = discord.Embed(description=f"""## This role is already assigned
                            {Emojis.dot_emoji} Do you want to override the required level for this role? 
                            {Emojis.dot_emoji} The role <@&{level_roles[1]}> is currently assigned at level **{level_roles[2]}**
                            {Emojis.dot_emoji} If you want to change the required level for the role {role.mention} to level {level} press the `yes` button if not press the `no` button""", color=bot_colour)
                        await ctx.respond(embed=emb, view=LevelRolesButtons(role_id=role.id, role_level=level, status='role'))

                    elif level == level_roles[2]:

                        emb = discord.Embed(description=f"""## This level is already assigned
                            {Emojis.dot_emoji} Do you want to override the role for this level?
                            {Emojis.dot_emoji} For the level **{level}** the role <@&{level_roles[1]}> is currently assigned
                            {Emojis.dot_emoji} If you want to change the role for level {level} to the role {role.mention} press the `yes` button if not press the `no` button""", color=bot_colour)
                        await ctx.respond(embed=emb, view=LevelRolesButtons(role_id=role.id, role_level=level, status='level'))



    @commands.slash_command(name = "remove-level-role", description = "Choose a role that you want to remove as a level role!")
    @commands.has_permissions(administrator = True)
    async def remove_level_role(self, ctx:discord.ApplicationContext, role:Option(discord.Role, description="Select a level role that you want to remove")):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, level_role=role.id)

        if level_roles:
            
            DatabaseRemoveDatas._remove_level_system_level_roles(guild_id=ctx.guild.id, role_id=role.id)

            emb = discord.Embed(description=f"""## This role has been removed as a level role
                {Emojis.dot_emoji} The role <@&{role.id}> was successfully removed as a level role
                {Emojis.dot_emoji} If you want to add them again you can do this with the /add-level-role command""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, status="level_role")

            emb = discord.Embed(description=f"""## This role is not defined as a level role
                {Emojis.dot_emoji} This role cannot be removed because it is not set as a level role
                {Emojis.dot_emoji} Here you can see all the level roles\n\n{level_roles}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "reset-level-roles", description = "Setze alle level roles zurück!")
    @commands.has_permissions(administrator = True)
    async def reset_level_roles(self, ctx:discord.ApplicationContext):

        check_level_roles = DatabaseCheck.check_level_system_levelroles(guild_id = ctx.guild.id)

        if check_level_roles:
            
            DatabaseRemoveDatas._remove_level_system_level_roles(guild_id = ctx.guild.id)

            emb = discord.Embed(description=f"""## All level roles have been successfully reset
                {Emojis.dot_emoji} All level roles have been removed so no more level roles will be assigned
                {Emojis.dot_emoji} If you want to add some again use the /add-level-role command""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(description=f"""## Level roles could not be reset
                {Emojis.dot_emoji} No entries were found
                {Emojis.dot_emoji} Therefore the level roles could not be reset""", color=bot_colour)


    @commands.slash_command(name = "show-level-roles", description = "View all rolls that are available with a level!")
    async def show_level_roles(self, ctx:discord.ApplicationContext):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, status = "level_role")
        print(level_roles)
        if level_roles:
            
            emb = discord.Embed(description=f"""## Current level roles
                {Emojis.dot_emoji} Level roles are always assigned when the user has reached the required level
                **{Emojis.dot_emoji} Here you can see all currently set level roles:**
                
                {CheckLevelSystem.show_level_roles(guild_id = ctx.guild.id)}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(description=f"""## No level roles have currently been defined
                {Emojis.help_emoji} Currently no level roles have been defined yet if you want to add some you can simply use the `/add-level-role` command for it
                {Emojis.dot_emoji} If you define some you have to specify a role and a level if a user reaches the given level he gets the role""", color=bot_colour)
            await ctx.respond(embed=emb)
       
    

#########################################  Bonus xp system  #############################################

    @staticmethod
    def check_bonus_percentage(guild_id:int, bonus:int = None):

        if bonus != 0 and bonus != None:

            bonus_percentage = bonus

        else:
            
            percentage = DatabaseCheck.check_level_settings(guild_id=guild_id)
            bonus_percentage = percentage[5]
        
        return bonus_percentage
    
    
    async def config_bonus_xp_list(
        self, 
        guild_id:int, 
        operation:str, 
        channel = None, 
        category = None, 
        role = None, 
        user = None, 
        bonus = None):

        if [x for x in [channel, category, role, user] if x]:
            
            check_channel = DatabaseCheck.check_xp_bonus_list(guild_id=guild_id, channel_id=channel.id) if channel != None else False
            check_category = DatabaseCheck.check_xp_bonus_list(guild_id=guild_id, category_id=category.id) if category != None else False
            check_role = DatabaseCheck.check_xp_bonus_list(guild_id=guild_id, role_id=role.id) if role != None else False
            check_user = DatabaseCheck.check_xp_bonus_list(guild_id=guild_id, user_id=user.id) if user != None else False

            items = {0:check_channel, 1:check_category, 2:check_role, 3:check_user}
            items_list = [channel, category, role, user]
            
            if [x for x in items.values() if x is None] and operation == "add" or any(x for x in items.values() if x is not False or None) and operation == "remove":

                res = list({ele for ele in items if items[ele]}) if operation == "add" else list({ele for ele in items if items[ele] is None})
                second_res = list({ele for ele in items if items[ele] is None}) if operation == "add" else list({ele for ele in items if items[ele]})
            
                item = [(f"> {Emojis.dot_emoji} {items_list[i].mention}") for i in res] 
                second_item = [(f"> {Emojis.dot_emoji} {items_list[i].mention}") for i in second_res]
        
                items_dict = {
                    0:channel.id if 0 in second_res else None, 
                    1:category.id if 1 in second_res else None, 
                    2:role.id if 2 in second_res else None,
                    3:user.id if 3 in second_res else None
                }
            
                if operation == "add":
                    
                    formatted_items = "\n".join(item) if item != [] else "\n> None of these items are on the Bonus XP list"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> None of these items can be removed from the Bonus XP list as they are not listed there"
                    
                    DatabaseUpdates.manage_xp_bonus(guild_id=guild_id, operation="add", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3], bonus = bonus)    
                    server_bonus = DatabaseCheck.check_level_settings(guild_id=guild_id)[5]
                    emb = discord.Embed(title=f"{Emojis.help_emoji} The following items have been added to the bonus XP list or were already there", 
                        description=f"""### {Emojis.dot_emoji} The following were already on the XP bonus list:
                        {formatted_items}\n### {Emojis.dot_emoji} Newly added:
                        {formatted_add_items}
                        {Emojis.dot_emoji} Each of the newly added items is rewarded with {f'the bonus you specified this is: {bonus} %' if bonus != None else f'the bonus you have specified for the server, which is: {server_bonus} %'}""", color=bot_colour)
                    return emb

                elif operation == "remove":
                
                    formatted_items = "\n".join(item) if item != [] else "> All the items you specified were on the XP bonus list"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> None of the items you specified could be removed from the XP bonus list because they are not on the blacklist"

                    DatabaseUpdates.manage_xp_bonus(guild_id=guild_id, operation="remove", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3])

                    emb = discord.Embed(title=f"{Emojis.help_emoji} The following items have been removed from the XP bonus list or were not listed", 
                        description=f"""### {Emojis.dot_emoji} The following items were not on the XP bonus list:
                        {formatted_items}\n### {Emojis.dot_emoji} Was deleted from the XP bonus list:
                        {formatted_add_items}""", color=bot_colour)
                    return emb
                
            else:

                emb = discord.Embed(title=f"{Emojis.help_emoji}Nothing can be {'added to the bonus XP list' if operation == 'add' else 'removed from the bonus XP list'}", 
                    description=f"""{Emojis.dot_emoji} {"All the things you have specified are already on the bonus XP list" 
                        if operation == "add" else 
                        "None of the things you mentioned are on the bonus XP list"}""", color=bot_colour)
                return emb
            
        else:

            emb = discord.Embed(title=f"{Emojis.help_emoji} You have not specified anything!", 
                description=f"""{Emojis.dot_emoji}You have not specified anything {"what should be added to the bonus XP list" 
                    if operation == "add" else
                    "what should be removed from the bonus XP list"}""", color=bot_colour)
            return emb

    
    @commands.slash_command(name = "add-bonus-xp-list", description = "Choose what you want to reward with more XP!")
    @commands.has_permissions(administrator = True)
    async def add_bonus_xp_list(self, ctx:discord.ApplicationContext, 
        channel:Option(Union[discord.VoiceChannel, discord.TextChannel], required = False, description="Choose a channel in which messages should be rewarded with more XP"),
        category:Option(discord.CategoryChannel, required = False, description="Choose a category in which messages should be rewarded with more XP"),
        role:Option(discord.Role, required = False, description="Choose a role where the one who owns it gets more XP when writing messages"),
        user:Option(discord.User, required = False, description="Select a user who should receive more XP per message"),
        bonus:Option(int, required = False, description="Choose how much more xp to give in percent (if nothing is specified the default value is used)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])):

        if user.bot:

            emb = discord.Embed(description=f"""## You cannot put a bot on the bonus XP list
                {Emojis.dot_emoji} Bots are excluded from the level system from the start
                {Emojis.dot_emoji} Thus they do not receive XP and cannot be set to this level""", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:

            emb = await self.config_bonus_xp_list(guild_id=ctx.guild.id, operation="add", channel=channel, category=category, role=role, user=user, bonus=bonus)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-bonus-xp-list", description = "Choose what you want to remove from the bonus XP list!")
    @commands.has_permissions(administrator = True)
    async def remove_bonus_xp_list(self, ctx:discord.ApplicationContext, 
        channel:Option(Union[discord.VoiceChannel, discord.TextChannel], required = False, description="Select a channel you want to remove from the bonus XP list"),
        category:Option(discord.CategoryChannel, required = False, description="Select a category you want to remove from the bonus XP list"),
        role:Option(discord.Role, required = False, description="Select a role you want to remove from the bonus XP list"),
        user:Option(discord.User, required = False, description="Select a user that you want to remove from the bonus XP list")):

        emb = await self.config_bonus_xp_list(guild_id=ctx.guild.id, operation="remove", channel=channel, category=category, role=role, user=user)
        await ctx.respond(embed=emb)
    

    @commands.slash_command(name = "show-bonus-xp-list", description = "Display everything that is on the bonus xp list!")
    async def show_bonus_xp_list(self, ctx:discord.ApplicationContext):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)

        if check_list:

            emb = discord.Embed(description=f"""## Current bonus XP list
                {Emojis.dot_emoji} All things that are listed on the bonus XP list are rewarded with a percentage of extra XP when activities take place there this can be divided for each item individually
                **Here you can see everything on the bonus XP list:**
                
                {CheckLevelSystem.show_bonus_xp_list(guild_id = ctx.guild.id)}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            all_bonus_xp_items = f"{Emojis.dot_emoji} No channel, category, role or user has been given an XP bonus!"

        emb = discord.Embed(title=f"{Emojis.help_emoji} Here you can see everything that is on the bonus XP list", 
            description=f"""{Emojis.dot_emoji} Here you can see all channels, categories, roles and users that get bonus XP and their XP bonus:\n\n{all_bonus_xp_items}""", color=bot_colour)
        await ctx.respond(embed=emb)


    @commands.slash_command(name = "reset-bonus-xp-list", description = "Reset the bonus XP list!")
    @commands.has_permissions(administrator = True)
    async def reset_bonus_xp_list(self, ctx:discord.ApplicationContext):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove")

            emb = discord.Embed(description=f"""## The bonus xp list was reset
                {Emojis.dot_emoji} All channels, users, roles and categories have been deleted from the xp bonus list
                {Emojis.dot_emoji} So every activity will be rewarded with {self.xp_generator(guild_id=ctx.guild.id, message=None)} XP""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(description=f"""## The bonus XP list cannot be reset
                {Emojis.dot_emoji} No entries were found
                {Emojis.dot_emoji} Therefore the list cannot be reset either""", color=bot_colour)
            await ctx.respond(embed=emb)




class LevelSystemSetting(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelSetLevelSystem())
        self.add_item(LevelSystemOnOffSwitch())
        self.add_item(ShowLevelSettings())

    @discord.ui.select( 
        placeholder = "Choose the system you want to set!",
        min_values = 1,
        max_values = 1,
        custom_id="set_level_system_select",
        options = [
            discord.SelectOption(
                label="Level up channel",
                description="Set a level up channel",
                value="level_up_channel"
            ),
            discord.SelectOption(
                label="Level up message",
                description="Set a level up message",
                value="level_up_message"
            ),
            discord.SelectOption(
                label="Set XP rate",
                description="Set an XP value, this is then distributed as XP per activity",
                value="set_xp_rate"
            ),
            discord.SelectOption(
                label="Set bonus xp percentage",
                description="Set a default percentage for the bonus XP system (this is set to 10 % by default)",
                value="set_bonus_xp_percentage"
            ),
            discord.SelectOption(
                label="Set all level settings on default",
                description="Resets all level system settings to default",
                value="set_level_system_default"
            )
        ]
    )

    async def select_callback(self, select, interaction:discord.Interaction):
        
        check_settings = DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)

        view = View(timeout=None)
        view.add_item(CancelSetLevelSystem())
        default_message = 'Oh nice {user} you have a new level, your newlevel is {level}'

        if interaction.user.guild_permissions.administrator:

            if "level_up_channel" == select.values[0]:

                view.add_item(SetLevelUpChannelButton())

                emb = discord.Embed(description=f"""## {'Set the level up channel' if check_settings[3] == None else 'Overwrite the current level up channel'}
                    {Emojis.dot_emoji} {'No level up channel has been defined yet' if check_settings[3] == None else f'The current level up channel is <#{check_settings[3]}>'}
                    {Emojis.dot_emoji} Use the lower button to set a level up channel""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=view, ephemeral=True)

            elif "level_up_message" == select.values[0]:

                view.add_item(LevelUpMessageButton())
                
                emb = discord.Embed(description=f"""## {'Set the level up message' if check_settings[4] == default_message else 'overwrite the current level up message'}
                    {Emojis.dot_emoji} A level up message is always sent when a user get a level up and is then either sent to a level up channel (if available) or simply directly after the last message.
                    {Emojis.dot_emoji} The current level up message is:\n`{check_settings[4]}` 
                    {Emojis.dot_emoji} The name of the user is inserted in the parameter **{'{user}'}** and the new level of the user is set in the place of **{'{level}'}**
                    {Emojis.dot_emoji} Press the button below to set a level up message""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=view, ephemeral=True)

            elif "set_bonus_xp_percentage" == select.values[0]:

                view.add_item(SetBonusXpPercentageButton())
                
                emb = discord.Embed(description=f"""## Set a {'new' if check_settings[5] == 10 else ''} bonus XP percentage
                    {Emojis.dot_emoji} Currently the bonus XP percentage is **{check_settings[5]}** {', by default the bonus XP percentage is **10 %**' if check_settings[5] != 10 else ', this is also the default value'}
                    {Emojis.dot_emoji} Each time an activity is performed by a user, in a channel, a category or by users with a certain role on the Bonus XP list or a user himself who is on the list, it will be rewarded according to the Bonus XP percentage you have set.
                    {Emojis.dot_emoji} The bonus XP percentage is always added to the XP received
                    {Emojis.dot_emoji} Press the button below to set the percentage to be used.""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=view, ephemeral=True)

            elif "set_xp_rate" == select.values[0]:
             
                emb = discord.Embed(description=f"""## Set a {'new' if check_settings[1] == 20 else ''} default XP value
                    {Emojis.dot_emoji} The XP value is the amount of XP you receive per activity, currently you get **{check_settings[1]} XP** per activity {', by default, the amount of XP is 20.' if check_settings[1] != 20 else ', this is also the standard quantity that is set from the start.'}
                    {Emojis.dot_emoji} You can use the select menu to choose one that is suggested to you
                    {Emojis.dot_emoji} By default, the XP value per message is 20 XP""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=SetXpRate(), ephemeral=True)

            elif "set_level_system_default" == select.values[0]:
                
                settings = [
                    '' if check_settings[1] == 20 else f'{Emojis.dot_emoji} Currently, the amount of XP you receive per message is {check_settings[1]} XP per message\n',
                    '' if check_settings[3] == None else f'{Emojis.dot_emoji} <#{check_settings[3]}> is currently set as level up channel means all level up messages and all role notifications are sent to this channel\n',
                    '' if check_settings[4] == default_message else f'{Emojis.dot_emoji} Currently is this the level up message `{check_settings[4]}`\n',
                    '' if check_settings[5] == 10 else f'{Emojis.dot_emoji} The bonus XP percentage rate is currently {check_settings[5]} %\n',
                    f'{Emojis.dot_emoji} All your settings are already at the default value' if check_settings[1] == None and check_settings[3] == None and check_settings[4] == default_message and check_settings[5] == 10 else ''
                ]

                emb = discord.Embed(description=f"""## Reset settings?
                    {Emojis.dot_emoji} With the lower button you can reset all settings, if you only want to reset individual settings, you can select them from the lower selct menu 
                    
                    **{Emojis.help_emoji} Here you can see a list of the settings that are not set to the default settings and what they are set to**

                    {"".join(settings)}
                    """, color=bot_colour)
                await interaction.response.send_message(embed=emb, view=LevelSystemDefault(), ephemeral=True)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



################################################  on / off Button  #############################################


class LevelSystemOnOffSwitch(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label = "Switching the level system on / off",
            style = discord.ButtonStyle.blurple,
            custom_id = "on_off_switch"
        )

    async def callback(self, interaction:Interaction):
        
        if interaction.user.guild_permissions.administrator:
            
            settings = DatabaseCheck.check_level_settings(guild_id=interaction.guild.id)[2]

            DatabaseUpdates.update_level_settings(guild_id=interaction.guild.id, level_status='on' if settings == 'off' else 'on')
                        
            emb = discord.Embed(description=f"""## The level system was switched {' off' if settings == 'on' else 'on'}
                {Emojis.dot_emoji} {'From now on, XP will no longer be given as a reward.' if settings == 'on' else 'From now on all activities will be rewarded with XP, you can adjust the amount manually using the **/set-level-system** command'}
                {Emojis.help_emoji} If you want to {'turn on' if settings == 'on' else 'switch off'} the level system, just use this command again""", color=bot_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



################################################  Level up message  ##############################################


class LevelUpMessageButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label = "Set a level up message",
            style = discord.ButtonStyle.blurple,
            custom_id = "set_level_up_message"
        )

    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            await interaction.response.send_modal(LevelUpMessageModal())
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class LevelUpMessageModal(discord.ui.Modal):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title="Set a level-up message for your server!")
        self.add_item(discord.ui.InputText(label="Insert here the text for the level-up message", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):

        user = interaction.user.mention
        level = 1
        level_up_message = eval("f'{}'".format(self.children[0].value))

        DatabaseUpdates.update_level_settings(guild_id=interaction.guild.id, level_up_message=self.children[0].value)

        embed = discord.Embed(description=f"""## The level-up message was successfully set
            {Emojis.dot_emoji} The level-up message was set to:\n{Emojis.arrow_emoji} `{level_up_message}`
            {Emojis.dot_emoji} When someone receives a level-up this message is sent""", color=bot_colour)
        await interaction.response.edit_message(embeds=[embed], view=None)



#######################################  Level up channel  ############################################


class SetLevelUpChannelButton(discord.ui.Button):
        
    def __init__(self):
        super().__init__(
            label = "Set the level up channel",
            style = discord.ButtonStyle.blurple,
            custom_id = "set_level_up_channel_button"
        )

    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Set a level up channel
                {Emojis.dot_emoji} With the lower select menu you can choose which channel should become the level up channel.
                {Emojis.dot_emoji} All level up messages and all notifications for the level roles are then sent to this folder.""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=SetLevelUpChannelSelect())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class SetLevelUpChannelSelect(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelSetLevelSystem())
        
    @discord.ui.channel_select(
        placeholder = "Choose a channel that you want to set as a level up channel!",
        min_values = 1,
        max_values = 1,
        custom_id = "level_up_channel_select",
        channel_types = [
            discord.ChannelType.text, 
            discord.ChannelType.forum, 
            discord.ChannelType.news
        ]
    )
    
    async def callback(self, select, interaction:discord.Interaction):
        
        settings = DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)

        if interaction.user.guild_permissions.administrator:

            if settings[3] != select.values[0].id:

                DatabaseUpdates.update_level_settings(guild_id = interaction.guild.id, level_up_channel = select.values[0].id)
                    
                emb = discord.Embed(
                    description=f"""## Level up channel has been {f"set " if DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[3] == None else "overwritten"}
                    {Emojis.dot_emoji} You have set <#{select.values[0].id}> as the {"new" if DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[3] == None else ""} level up channel.
                    {Emojis.dot_emoji} All level up messages and all notifications for the level roles will be sent to this channel from now on.""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)
            
            else:

                emb = discord.Embed(description=f"""## {Emojis.help_emoji} This channel is already set as a level up channel 
                    {Emojis.dot_emoji} <#{select.values[0].id}> is already defined as the level up channel""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



################################################  Bonus XP Percentage  ################################################


class SetBonusXpPercentageButton(discord.ui.Button):

    def __init__(self, ):
        super().__init__(
            label = "Set the bonus XP percentage",
            style = discord.ButtonStyle.blurple,
            custom_id = "set_xp_percentage_button"
        )

    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Set an individual bonus XP percentage 
                {Emojis.dot_emoji} With the dropdown menu below you can enter a bonus XP percentage that will be added to the total XP amount.
                {Emojis.dot_emoji} If you don't like any of the suggested percentages, you can also use the button below to enter your own, but remember that it must not exceed 100 %!
                {Emojis.help_emoji} Your self-entered bonus XP percentage must be an integer, i.e. no commas or other characters, only numbers such as: 1, 2, 3, and so on""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=BonusXpPercentage())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class BonusXpPercentage(discord.ui.View):
    
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SendXpBonusModal())
        self.add_item(CancelSetLevelSystem())

    @discord.ui.string_select(
        placeholder = "Select a percentage",
        min_values = 1,
        max_values = 1,
        custom_id="set_bonus_xp_percentage_select",
        options = [
            discord.SelectOption(label = "5"),
            discord.SelectOption(label = "10"),
            discord.SelectOption(label = "20"),
            discord.SelectOption(label = "30"),
            discord.SelectOption(label = "40"),
            discord.SelectOption(label = "50"),
            discord.SelectOption(label = "60"),
            discord.SelectOption(label = "70"),
            discord.SelectOption(label = "80"),
            discord.SelectOption(label = "90"),
            discord.SelectOption(label = "100")
        ]
    )

    async def callback(self, select, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            check_settings = DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[5]

            if check_settings == select.values[0]:

                emb = GetEmbed.get_embed(settings=check_settings, embed_index=0)
                await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

            else:
            
                DatabaseUpdates.update_level_settings(guild_id=interaction.guild.id, percentage=int(select.values[0]))

                emb = discord.Embed(description=f"""## A new bonus XP percentage rate has been set
                    {Emojis.dot_emoji} The newly set bonus percentage rate is now **{select.values[0]}**
                    {Emojis.dot_emoji} From now on, all activities in a channel, category or by a user, user with a role that is on the Bonus XP list will be rewarded with extra XP\n### {Emojis.dot_emoji} Here you can also see an overview of the entire bonus XP list:\n
                    {CheckLevelSystem.bonus_xp_list(guild_id = interaction.guild.id)}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class SendXpBonusModal(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label = "Set individual XP bonus percentage",
            style = discord.ButtonStyle.blurple,
            custom_id = "set_individual_percentage"
        )
    
    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            await interaction.response.send_modal(BonusXpPercentageModal())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class BonusXpPercentageModal(discord.ui.Modal):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title="Enter your own bonus XP percentage!")
        self.add_item(discord.ui.InputText(label="Enter your bonus percentage as a number here", style=discord.InputTextStyle.short))

    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            
            check_settings = DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[5]

            if check_settings == self.children[0].value:

                emb = GetEmbed.get_embed(settings=check_settings, embed_index=0)
                await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

            else:

                try:
                    
                    if int(self.children[0].value) <= 100:

                        DatabaseUpdates.update_level_settings(guild_id=interaction.guild.id, percentage=self.children[0].value)

                        embed = discord.Embed(description=f"""## Your bonus XP percentage has been set
                            {Emojis.dot_emoji} The bonus XP percentage was set to **{self.children[0].value}** %
                            {Emojis.dot_emoji} Here you can also see an overview of what the new bonus XP percentage applies to, as well as a list of those that have their own percentage value
                            {CheckLevelSystem.bonus_xp_list(guild_id=interaction.guild.id)}""", color=bot_colour)
                        await interaction.response.edit_message(embeds=[embed], view=None)

                    else:
                        raise Exception('Exception message')

                except:

                    emb = discord.Embed(description=f"""## Your input is invalid
                        {Emojis.dot_emoji} Your input is either greater than 100 or contains letters, special characters or a comma
                        {Emojis.dot_emoji} You can enter a new value by pressing the button again or you can cancel the setting by pressing the red button.""", color=bot_colour)
                    await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



#######################################  Set XP rate  #########################################
            

class SetXpRate(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelSetLevelSystem())

    @discord.ui.select(
        max_values = 1,
        min_values = 1,
        placeholder = "Choose how much XP you want to receive per activity and how difficult the level up should be!",
        options=[
            discord.SelectOption(label="5 XP", value="5"),
            discord.SelectOption(label="10 XP", value="10"),
            discord.SelectOption(label="15 XP", value="15"),
            discord.SelectOption(label="20 XP", value="20"),
            discord.SelectOption(label="30 XP", value="30"),
            discord.SelectOption(label="40 XP", value="40"),
            discord.SelectOption(label="50 XP", value="50"),
            discord.SelectOption(label="60 XP", value="60")
        ],
        custom_id="set_xp_rate"
    )
    async def set_xp_rate_selct(self, select, interaction:discord.Interaction):
        
        check_xp_rate = DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[1]

        if interaction.user.guild_permissions.administrator:

            if select.values[0] == check_xp_rate:

                emb = discord.Embed(description=f"""## {Emojis.help_emoji} This value is already set as the bonus XP value
                    {Emojis.dot_emoji} The bonus XP value is already set to {check_xp_rate} XP per message""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            else:

                DatabaseUpdates.update_level_settings(guild_id = interaction.guild.id, xp_rate = int(select.values[0]))

                emb = discord.Embed(description=f"""## The XP bonus value has been set
                    {Emojis.dot_emoji} You have set the new XP bonus value to **{select.values[0]}** XP
                    {Emojis.dot_emoji} After each activity, this XP value is awarded as a reward""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



#########################################################  Set on Default  ##################################################


class LevelSystemDefault(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelSetLevelSystem())

    @discord.ui.select(
        max_values = 4,
        min_values = 1,
        placeholder = "Select which components you want to reset to default settings!",
        options=[
            discord.SelectOption(label="Level up channel", description="Reset the level up channel", value="level_up_channel"),
            discord.SelectOption(label="Level up message", description="Resets the level up message", value="level_up_message"),
            discord.SelectOption(label="Bonus XP percentage", description="Resets the bonus XP percentage", value="bonus_xp_percentage"),
            discord.SelectOption(label="XP rate", description="Reset the amount of XP you get per message", value="xp_rate")
        ],
        custom_id="level_default_select"
    )

    async def level_system_default_select(self, select, interaction:discord.Interaction):

        settings_dict = {
            "xp_rate":1,
            "level_up_channel":2,
            "level_up_message":3,
            "bonus_xp_percentage":4
        }

        settings = DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)
        default_message = 'Oh nice {user} you have a new level, your newlevel is {level}'

        settings_list = {"reset":{
            "xp_rate":'' if settings[1] == 20 else f'{Emojis.dot_emoji} XP rate',
            "level_up_channel":'' if settings[3] == None else f'{Emojis.dot_emoji} Level up channel',
            "level_up_message":'' if settings[4] == default_message else f'{Emojis.dot_emoji} Level up message',
            "bonus_xp_percentage":'' if settings[5] == 10 else f'{Emojis.dot_emoji} Bonus XP percentage'
        },
        "default":{
            "xp_rate":f'{Emojis.dot_emoji} XP rate' if settings[1] == 20 else '',
            "level_up_channel":f'{Emojis.dot_emoji} Level up channel' if settings[3] == None else '',
            "level_up_message":f'{Emojis.dot_emoji} Level up message' if settings[4] == default_message else '',
            "bonus_xp_percentage":f'{Emojis.dot_emoji} Bonus XP percentage' if settings[5] == 10 else ''
        }}

        reset_list, default_list = [], []
        for i in select.values:
            reset_list.append(settings_list['reset'][i])

        for i in select.values:
            default_list.append(settings_list['default'][i])
    
        reset_list = list(filter(None, reset_list))
        default_list = list(filter(None, default_list))
        reset_new_list = "\n".join(reset_list)
        default_new_list = "\n".join(default_list)
  
        for i in select.values:
            DatabaseUpdates.update_level_settings(guild_id = interaction.guild.id, back_to_none = settings_dict[i])

        emb = discord.Embed(description=f"""## Reset settings                
            **{Emojis.arrow_emoji} The following level system settings have been reset:**

            {reset_new_list if any(x for x in reset_list if x != '') else f'{Emojis.dot_emoji} No settings can be reset as they are already all set to default settings'}
            
            **{Emojis.arrow_emoji} The following settings were already set to default:**
            
            {default_new_list if any(x for x in default_list if x != '') else f'{Emojis.dot_emoji} No settings were set to default settings'}
            """, color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)


    @discord.ui.button(
        label = "Reset all settings to default values",
        style = discord.ButtonStyle.blurple,
        custom_id = "set_all_settings_default"
    )
    async def level_system_all_dafault(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            for i in [0, 2, 3, 4]:
                DatabaseUpdates.update_level_settings(guild_id = interaction.guild.id, back_to_none = i)

            emb = discord.Embed(description=f"""## All data has been reset to default
                {Emojis.dot_emoji} You have successfully set all level system settings back to default
                {Emojis.dot_emoji} You can change these again at any time""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



#########################################  Cancel Button  ########################################


class CancelSetLevelSystem(discord.ui.Button):
    
    def __init__(self):
        super().__init__(
            label = "Cancel setting",
            style = discord.ButtonStyle.danger,
            custom_id = "cancel_level_set"
        )

    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Setting canceled
                {Emojis.dot_emoji} The setting of the level system was canceled.
                {Emojis.dot_emoji} If you change your mind, you can always execute the command again.""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



class ShowLevelSettings(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label = "Show all Level system settings",
            style = discord.ButtonStyle.blurple,
            custom_id = "show_level_settings",
            row=3
        )
    
    async def callback(self, interaction: discord.Interaction):

        emb = discord.Embed(description=f"""## Select which settings you want to see
            {Emojis.help_emoji} Here you have a small overview of what the individual systems can do and what they are currently set to:
                            
            **{Emojis.dot_emoji} Level up Channel**
            > All level up notifications as well as the notifications for receiving a level role are sent to a channel specified by you

            **{Emojis.dot_emoji} Level up Message**
            > A custom message that is sent after a level up

            **{Emojis.dot_emoji} Level system Blacklist**
            > Channels, categories, roles or users that are excluded from the level system

            **{Emojis.dot_emoji} Level Roles**
            > Roles that are assigned when you reach a specified level

            **{Emojis.dot_emoji} XP rate**
            > Indicates how much XP you get per activity can be customized and can be influenced by items on the Bonus XP list

            **{Emojis.dot_emoji} Bonus XP perventage**
            > A percentage value that is added to the individual items of the Bonus XP list if no own items are specified

            **{Emojis.dot_emoji} Bonus XP list**
            > Channel, category, role and user can be added to this list and rewarded either 
            > with an individual percentage of bonus XP per activity or with
            > the bonus XP percentage as a bonus.           
            
            **{Emojis.dot_emoji} Level System status**
            > Shows whether the level system is switched on or off""", color=bot_colour)
        await interaction.response.send_message(embed=emb, ephemeral=True, view=ShowLevelSettingsSelect())


# Fertig machen 
class ShowLevelSettingsSelect(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelSetLevelSystem())

    @discord.ui.select(
        max_values = 1,
        min_values = 1,
        placeholder = "Select the system from which you want to see the settings",
        options=[
            discord.SelectOption(label="Level up channel", description="Shows you the current Levl up channel", value="show_level_up_channel"),
            discord.SelectOption(label="Level up message", description="Shows you the current level up message", value="show_level_up_message"),
            discord.SelectOption(label="XP rate", description="Shows you how much XP you get per activity", value="show_xp_rate"),
            discord.SelectOption(label="Bonus XP percentage", description="Shows you the current bonus XP percentage", value="show_bonus_xp_percentage"),
            discord.SelectOption(label="Level System status", description="Shows you whether the level system is switched on or off", value="show_level_status"),
        ],
        custom_id="show_level_settigs_select")
        
    async def show_level_settings(self, select, interaction: discord.Interaction):

        if select.values[0] == "show_level_up_channel":

            level_up_channel = DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[3]

            emb = discord.Embed(description=f"""## Current level up channel
                {Emojis.dot_emoji} {f'The current level up channel is {level_up_channel}' if level_up_channel != None else 'No level up channel has been set yet'}
                {Emojis.dot_emoji} If a level up channel is set, all level up notifications are sent to this channel as well as all notifications for receiving a level role
                {Emojis.dot_emoji} If no level up channel is set, all notifications are sent to the channel where the last activity took place""", color=bot_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

        elif select.values[0] == "show_level_up_message":

            level_up_message = DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[4]

            emb = discord.Embed(description=f"""## Current level up message
                {Emojis.dot_emoji} Currently is:\n{f'`{level_up_message}`' if level_up_message != default_message else f'`{default_message}`'} the level up message.
                {Emojis.dot_emoji} The level up message is always sent when someone gets a level up
                {Emojis.help_emoji} You also have several parameters to customize them exactly in the curly brackets you can either use the parameter user or level""", color=bot_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

        elif select.values[0] == "show_xp_rate":

            emb = discord.Embed(description=f"""## Current XP rate
                {Emojis.dot_emoji} The XP rate is the amount of XP you receive as a reward per activity
                {Emojis.dot_emoji} The current XP rate is {DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[1]} XP per activity
                {Emojis.help_emoji} The XP rate can be influenced by the entries on the bonus XP list if activities take place in a channel, category, role or user that is on this list, extra XP will be awarded""", color=bot_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

        elif select.values[0] == "show_bonus_xp_percentage":

            emb = discord.Embed(description=f"""## Current bonus XP percentage 
                {Emojis.dot_emoji} The bonus percentage is the default value of the bonus XP list and is always taken into account if no own is specified
                {Emojis.dot_emoji} Currently the bonus XP percentage is {DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[5]} % more XP per activity as long as the channel, category, role or user is on the bonus XP list""", color=bot_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

        elif select.values[0] == "show_level_status":

            emb = discord.Embed(description=f"""## Current status of the level system
                {Emojis.dot_emoji} The level system is currently {'switched on' if DatabaseCheck.check_level_settings(guild_id = interaction.guild.id)[2] == 'on' else 'switched off'}
                {Emojis.dot_emoji} All activities are rewarded with XP unless the channel, category, role or user is on the blacklist""", color=bot_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True, view=None)




def setup(bot):
    bot.add_cog(LevelSystem(bot))
    