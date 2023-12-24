
from import_file import *
from typing import Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import re


class CheckLevelSystem():

    # Function that returns all items of the blacklist 
    def show_blacklist_level(guild_id:int):

        blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id)
    
        check_channel = [i for _, i, _, _, _ in blacklist if i is not None]; checked_channel = [f"> {Emojis.dot_emoji} There are no channels on the blacklist"] if check_channel == [] else [f"> {Emojis.dot_emoji} <#{i}>" for i in check_channel]
        check_category = [i for _, _, i, _, _ in blacklist if i is not None]; checked_category = [f"> {Emojis.dot_emoji} There are no categories on the blacklist"] if check_category == [] else [f"> {Emojis.dot_emoji} <#{i}>" for i in check_category]
        check_role = [i for _, _, _, i, _ in blacklist if i is not None]; checked_role = [f"> {Emojis.dot_emoji} There are no roles on the blacklist"] if check_role == [] else [f"> {Emojis.dot_emoji} <@&{i}>" for i in check_role]
        check_user = [i for _, _, _, _, i in blacklist if i is not None]; checked_user = [f"> {Emojis.dot_emoji} There are no users on the blacklist"] if check_user == [] else [f"> {Emojis.dot_emoji} <@{i}>" for i in check_user]
        
        return ["\n".join(checked_channel), "\n".join(checked_category), "\n".join(checked_role), "\n".join(checked_user)]
    

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
            


#############################################  Level Systen Settings  #############################################


class LevelSystemSettings(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    # Button to set the status of the level system to on
    @discord.ui.button(label="On/Off Level system", style=discord.ButtonStyle.blurple, custom_id="on_off_level_system")
    async def level_system_settings(self, button, interaction:discord.Interaction):

        guild_id = interaction.guild.id
        
        check_status = DatabaseCheck.check_level_settings(guild_id=guild_id)

        if interaction.user.guild_permissions.administrator:

            if check_status == None:

                emb = discord.Embed(title=f"{Emojis.help_emoji} No entry was found", 
                    description=f"""No entry was found so one was created for your server. 
                    {Emojis.dot_emoji} The level system was also switched on automatically.
                    {Emojis.dot_emoji} If you want to disable it just use this command again""", color=bot_colour)
                await interaction.response.edit_message(embed=emb)

            else:

                if check_status[2] == "on":

                    new_status, status = "switched off", "off"
                    opposite_status = "turn on"

                elif check_status[2] == "off":

                    new_status, status = "switched on", "on"
                    opposite_status = "switch off"

                DatabaseUpdates.update_level_settings(guild_id=guild_id, level_status=status)
                        
                emb = discord.Embed(title=f"The level system was {new_status}", 
                    description=f"""{Emojis.dot_emoji} If you want to {opposite_status} the level system, just use this command again {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



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

                emb = discord.Embed(title=f"{Emojis.help_emoji} The role or level could not be overwritten", 
                    description=f"""{Emojis.dot_emoji} The role or level could not be overwritten because the process has expired.
                    {Emojis.dot_emoji} This happens when you wait too long to react to the button.
                    {Emojis.dot_emoji} You can simply run the command again if you still want to overwrite the level or role {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                DatabaseUpdates.update_level_roles(guild_id=interaction.guild.id , role_id=self.role_id, role_level=self.role_level, status=self.status)
                            
                emb = discord.Embed(title=f"Successful override of the level role {Emojis.succesfully_emoji}", 
                    description=f"""{Emojis.dot_emoji} The level role was successfully overwritten.
                    {Emojis.dot_emoji} The role <@&{self.role_id}> will be assigned at level {self.role_level} from now on.""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:
                
            await interaction.response.send_message(embed=no_permissions_emb, view=None, ephemeral=True)


    # Button to cancel the overwriting of the level role 
    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, custom_id="no_button_level_role")
    async def no_button_levelroles(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            title = "The overwriting of the level role was canceled"
            check_level_roles = DatabaseCheck.check_level_system_levelroles(guild=interaction.guild.id, level_role=self.role_id, needed_level=self.role_level, status="check")

            if self.role_id == None and self.role_level == None and self.status == None:

                emb = discord.Embed(title=title,
                    description=f"""{Emojis.dot_emoji} If you want to see all level roles use the {show_level_role} command.""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                if check_level_roles[1] == self.role_id:

                    emb = discord.Embed(title=title, 
                        description=f"""{Emojis.dot_emoji} The role <@&{self.role_id}> will still be assigned when level {check_level_roles[2]} is reached""", color=bot_colour)
                    await interaction.response.edit_message(embed=emb, view=None)

                if check_level_roles[2] == self.role_level:

                    emb = discord.Embed(title=title, 
                        description=f"""{Emojis.dot_emoji} When reaching level {self.role_level} you still get the role {check_level_roles[1]}""", color=bot_colour)
                    await interaction.response.edit_message(embed=emb, view=None)

        else:
            
            await interaction.response.send_message(embed=no_permissions_emb, view=None, ephemeral=True)



#############################################  Level up Channel button  ###########################################


class LevelUpChannelButtons(discord.ui.View):
    def __init__(self, channel:int = None):
        self.channel = channel
        super().__init__(timeout=None)

    # Button to change a level up channel
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray, custom_id="yes_button_level_up")
    async def yes_button_levelup(self, button, interaction:discord.Interaction):
            
        if interaction.user.guild_permissions.administrator:

            if self.channel == None:

                emb = discord.Embed(title=f"{Emojis.help_emoji} The level up channel could not be overwritten", 
                    description=f"""{Emojis.dot_emoji} The level up channel could not be overwritten because the process has expired.
                    {Emojis.dot_emoji} This happens when you wait too long to react to the button.
                    {Emojis.dot_emoji} You can simply run the command again if you still want to overwrite the level up channel {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)


            else:

                DatabaseUpdates.update_level_settings(guild_id=interaction.guild.id, levelup_channel=self.channel)

                emb = discord.Embed(title=f"The level up channel was successfully overwritten {Emojis.succesfully_emoji}", 
                    description=f"""{Emojis.dot_emoji} From now on the channel <#{self.channel}> is assigned as level up channel.""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, view=None, ephemeral=True)


    # Button to cancel the overwriting of the level up channel 
    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="no_button_level_up")
    async def no_button_levelup(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Successfully canceled {Emojis.succesfully_emoji}", 
                description=f"{Emojis.dot_emoji} You have successfully canceled the overwriting of the level up channel", color=bot_colour)
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

            emb = discord.Embed(title=f"You have reset all the stats of the level system {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.arrow_emoji} All user files have been deleted every user is now level 0 again and has 0 XP.
                New entries will be created again when there is activity, if you do not want this, turn off the level system. {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)


        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True)

    
    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="no_button_reset")
    async def reset_stats_button_level_no(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
        
            emb = discord.Embed(title=f"The operation was successfully canceled {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Resetting the stats was successfully aborted.
                {Emojis.dot_emoji} All users keep their stats in the level system.""", color=bot_colour)
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

            emb = discord.Embed(title=f"The blacklist has been reset {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.arrow_emoji} All channels, users, roles and categories have been removed from the blacklist.
                {Emojis.dot_emoji} If you want to blacklist things again you can use the commands as before {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)


    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, row=1, custom_id="no_button_level")
    async def reset_blacklist_button_level_no(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"The operation was successfully canceled {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Resetting the blacklist was successfully aborted.
                {Emojis.dot_emoji} All channels, roles, categories and users are still listed on the blacklist.
                {Emojis.dot_emoji} If you want to remove single elements from the blacklist you can remove them with the Remove commands {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)

            
class ShowBlacklistLevelSystemButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Show all items on the blacklist", style=discord.ButtonStyle.blurple, custom_id="show_blacklist_button_level")
    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id
            blacklist = CheckLevelSystem.show_blacklist_level(guild_id=guild_id) 

            emb = discord.Embed(title=f"Here you can see all the elements that are on the blacklist of the level system {Emojis.exclamation_mark_emoji}", 
                description=f"""Here are listed all the elements that are on the level system blacklist.""", color=bot_colour)
            emb.add_field(name="Channels:", value=f"{blacklist[0]}", inline=False)
            emb.add_field(name="Categories:", value=f"{blacklist[1]}", inline=False)
            emb.add_field(name="Roles", value=f"{blacklist[2]}", inline=False)
            emb.add_field(name="Users", value=f"{blacklist[3]}", inline=False)
            emb.set_footer(icon_url=bot.user.avatar ,text="This message is only visible to you")
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

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
                                print("Data were changed")

                            except mysql.connector.Error as error:
                                print("parameterized query failed {}".format(error))

                    else:
                            
                        DatabaseUpdates._insert_user_stats_level(guild_id=message.guild.id, user_id=message.author.id, user_name=message.author.name)

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))
   


####################################################  User stats setting  #################################################


    @commands.slash_command(name = "give-xp", description = "Give a user a quantity of XP chosen by you!")
    @commands.has_permissions(administrator = True)
    async def give_xp(self, ctx:commands.Context, user:Option(discord.Member, description="Select a user who should receive the xp!"),
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
                        
                    emb = discord.Embed(title=f"You have successfully given {user.name} {xp} XP {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} You have transferred **{user.name}** {xp} XP **{user.name}** has from now on **{new_xp}** XP.
                        {Emojis.dot_emoji} If you want to remove **{user.name}** XP again use the:\n{remove_xp} command {Emojis.exclamation_mark_emoji}""", color=bot_colour)
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
        
                    emb = discord.Embed(title=f"{Emojis.help_emoji} The XP you want to give {user.name} is too high", 
                        description=f"""{Emojis.dot_emoji} The XP you want to pass to **{user.name}** is too high.
                        {Emojis.dot_emoji} You can only give **{user.name}** a maximum of **{xp_need_next_level}** XP.""", color=bot_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)
                
                emb = discord.Embed(title=f"{Emojis.help_emoji} The user was not found", 
                    description=f"""{Emojis.dot_emoji} No entry was found for **{user.name}**, so one was created.
                    {Emojis.dot_emoji} **{user.name}** now starts at level 0 with 0 xp.""", color=bot_colour)
                await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-xp", description = "Remove a chosen amount of Xp from a user!")
    @commands.has_permissions(administrator = True)
    async def remove_xp(self, ctx:commands.Context, user:Option(discord.Member, description="Choose a user from which you want to remove xp!"),
        xp:Option(int, description="Specify a quantity of Xp to be removed!")):
            
        check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id, user=user.id)

        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            if check_stats:
                
                user_xp = check_stats[3]
                new_xp = user_xp - xp 

                if xp > user_xp:
                            
                    emb = discord.Embed(title=f"{Emojis.help_emoji} The XP you want to remove from {user.name} is too high", 
                        description=f"""{Emojis.dot_emoji} The XP you want to remove from **{user.name}** is too high.
                        {Emojis.dot_emoji} You can remove **{user.name}** only maximum **{user_xp}** XP.""", color=bot_colour)
                    await ctx.respond(embed=emb)

                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, xp=new_xp)

                    emb = discord.Embed(title=f"You have successfully removed {user.name} {xp} XP {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} You have removed **{user.name}** {xp} XP **{user.name}** has **{new_xp}** XP from now on.
                        {Emojis.dot_emoji} If you want to give **{user.name}** XP again use the:\n{give_xp} command {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb)

            else:
                    
                DatabaseUpdates._insert_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)
                    
                emb = discord.Embed(title=f"{Emojis.help_emoji} The user was not found", 
                    description=f"""{Emojis.dot_emoji} No entry was found for **{user.name}**, so one was created.
                    {Emojis.dot_emoji} **{user.name}** now starts at level 0 with 0 xp.""", color=bot_colour)
                await ctx.respond(embed=emb)  


    @commands.slash_command(name = "give-level", description = "Give a user a selected amount of levels!")
    @commands.has_permissions(administrator = True)
    async def give_level(self, ctx:commands.Context, user:Option(discord.Member, description="Choose a user you want to give the levels to!"), 
        level:Option(int, description="Specify a set of levels that you want to assign!")):

        check_stats = DatabaseCheck.check_level_system_stats(guild=ctx.guild.id, user=user.id)

        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            if check_stats:
                
                new_level = check_stats[2] + level
                levels_to_maxlevel = 999 - level
                            
                if level > 999 or new_level >= 999:

                    emb = discord.Embed(title=f"{Emojis.help_emoji} The level you want to give {user.name} is too high", 
                        description=f"""{Emojis.dot_emoji} The level you want to give **{user.name}** is too high because the maximum level is **999**.
                        {Emojis.dot_emoji} You can only give **{user.name}** a maximum {levels_to_maxlevel} level.""", color=bot_colour)
                    await ctx.respond(embed=emb)

                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, level=new_level)

                    emb = discord.Embed(title=f"You have successfully added {user.name} {level} level {Emojis.succesfully_emoji}",
                        description=f"""{Emojis.dot_emoji} You gave **{user.name}** {level} level **{user.name}** now has **{new_level}** level.
                        {Emojis.dot_emoji} If you want to remove **{user.name}** level again use the:\n{remove_level} command {Emojis.exclamation_mark_emoji}""", colour=bot_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)

                emb = discord.Embed(title=f"{Emojis.help_emoji} The user was not found", 
                    description=f"""{Emojis.dot_emoji} No entry was found for **{user.name}**, so one was created.
                    {Emojis.dot_emoji} **{user.name}** now starts at level 0 with 0 xp.""", color=bot_colour)
                await ctx.respond(embed=emb)
                

    @commands.slash_command(name = "remove-level", description = "Remove a quantity of levels chosen by you!")
    @commands.has_permissions(administrator = True)
    async def remove_level(self, ctx:commands.Context, user:Option(discord.Member, description="Select a user from whom you want to remove the level!"), 
        level:Option(int, description="Specify how many levels should be removed!")):

        check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id, user=user.id)
        
        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            if check_stats:
    
                new_level = check_stats[2]  - level 

                if level > check_stats[2] :

                    emb = discord.Embed(title=f"{Emojis.help_emoji} The number of levels you want to remove from {user.name} is too high", 
                        description=f"""{Emojis.dot_emoji} The number of levels you want to remove from {user.name} is too high.
                        {Emojis.dot_emoji} You can remove **{user.name}** only up to **{check_stats[2] }** level.""", color=bot_colour)
                    await ctx.respond(embed=emb)

                
                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id,  level=new_level)

                    emb = discord.Embed(title=f"You have successfully removed {user.name} {level} level {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} You have removed **{user.name}** {level} level **{user.name}** is now level **{new_level}**
                        {Emojis.dot_emoji} If you want to give **{user.name}** level again use the:\n{give_level} command {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)
                
                emb = discord.Embed(title=f"{Emojis.help_emoji} The user was not found", 
                    description=f"""{Emojis.dot_emoji} No entry was found for **{user.name}**, so one was created.
                    {Emojis.dot_emoji} **{user.name}** now starts at level 0 with 0 xp""", color=bot_colour)
                await ctx.respond(embed=emb)    
    

    @commands.slash_command(name = "reset-level-system-stats", description = "Reset all levels and xp of everyone!")
    @commands.has_permissions(administrator = True)
    async def reset_level(self, ctx:commands.Context):

        check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id)

        if check_stats:

            emb = discord.Embed(title="Are you sure you want to reset the level system?", 
                description=f"""{Emojis.help_emoji} With the buttuns you can confirm your decision!
                {Emojis.dot_emoji} If you press the **Yes button** all user stats will be deleted.
                {Emojis.dot_emoji} If you press the **No button** the process will be aborted.""", color=bot_colour)
            await ctx.respond(embed=emb, view=ResetLevelStatsButton())

        else:
            
            emb = discord.Embed(title=f"{Emojis.help_emoji} No data found for this server", 
                description=f"""{Emojis.dot_emoji} No data was found for this server, so nothing could be deleted.
                {Emojis.dot_emoji} Data is created automatically as soon as messages are sent and the level system is switched on.""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "reset-user-stats", description = "Resets all stats of the specified user in the level system!")
    @commands.has_permissions(administrator = True)
    async def reset_user_stats(self, ctx:commands.Context, user:Option(discord.Member, description="Choose a user whose stats you want to reset!")):

        check_stats = DatabaseCheck.check_level_system_stats(guild_id=ctx.guild.id, user=user.id)

        if check_stats:

            DatabaseRemoveDatas._remove_level_system_stats(guild_id=ctx.guild.id, user_id=user.id)

            emb = discord.Embed(title=f"The user data of {user.name} has been reset {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} {user.mention} is now level 0 again with 0 XP.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(title=f"{Emojis.help_emoji} This user has not yet collected XP", 
                description=f"""{Emojis.dot_emoji} This user has not yet collected XP, so his data cannot be reset.""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "rank", description = "Shows you the rank of a user in the level system!")
    async def rank_slash(self, ctx:commands.Context, user:Option(discord.Member, description="Look at the rank of others!")):

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
            small_font = ImageFont.truetype("arial.ttf", 24)

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
    async def leaderboard(self, ctx:commands.Context):

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

                c.append(f"{i}. <@{member_id}>, level: {lvl}, XP: {xp}")
            
        level_roles_mention_end = '\n'.join(c)

        DatabaseSetup.db_close(cursor=my_cursor, db_connection=leaderboard_connect)

        emb = discord.Embed(title="leaderboard", description=f"leaderboard participants:\n\n{level_roles_mention_end}", color=bot_colour)
        emb.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.respond(embed=emb)

               

#############################################  Level system Settings  #####################################################    


    @commands.slash_command(name = "level-system-settings", description = "Set the level system freely!")
    @commands.has_permissions(administrator = True)
    async def level_system_settings(self, ctx:commands.Context):

        level_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if level_settings:

            if level_settings[2] == "on":
                active_deactive = "enabled "
            elif level_settings[2] == "off":
                active_deactive = "disabled"

            emb = discord.Embed(title=f"{Emojis.help_emoji} Here you can see all the settings of the level system", 
                description=f"{Emojis.dot_emoji} With the lower button you can set the level system, you can enable or disable it. At the moment it is: **{active_deactive}**",color=bot_colour)
            await ctx.respond(embed=emb, view=LevelSystemSettings())

        else:

            DatabaseUpdates._create_bot_settings(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"{Emojis.help_emoji} No entry found", 
                description=f"{Emojis.dot_emoji} No entry was found so one was created the level system was also activated immediately.", color=bot_colour)
            await ctx.respond(embed=emb)

    

#################################################  Level Blacklist settings  ###############################################


    @commands.slash_command(name = "reset-level-blacklist", description="Reset the blacklist of the level system and remove all entries!")
    @commands.has_permissions(administrator = True)
    async def reset_blacklist(self, ctx:commands.Context):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id)

        if blacklist:

            view = ResetBlacklistLevelButton()
            view.add_item(ShowBlacklistLevelSystemButton())

            emb = discord.Embed(title="Are you sure you want to remove everything from the blacklist?", 
                description=f"""{Emojis.help_emoji} With the buttons you can confirm your decisions!
                {Emojis.dot_emoji} If you press the **Yes button** all channels, categories, users and roles will be removed from the blacklist.
                {Emojis.dot_emoji} If you press the **No button** the process will be aborted.
                {Emojis.dot_emoji} The **Shows all elements button** shows you what is currently on the blacklist.""", color=bot_colour)
            await ctx.respond(embed=emb, view=view)
        
        else:

            emb = discord.Embed(title=f"{Emojis.help_emoji} There is nothing on the blacklist", 
                description=f"""{Emojis.dot_emoji} The blacklist could not be reset because nothing is stored on it.""", color=bot_colour)
            await ctx.respond(embed=emb)


    async def config_level_blacklist(self, guild_id:int, operation:str, channel = None, category = None, role = None, user = None):

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

                emb = discord.Embed(title=f"{Emojis.help_emoji}Nothing can be {'blacklisted' if operation == 'add' else 'removed from the blacklist'}", 
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

            emb = discord.Embed(title=f"{Emojis.help_emoji} The channel is already indirectly on the blacklist", 
                description=f"""{Emojis.dot_emoji} The channel {channel.mention} that you want to blacklist is already on the blacklist because it is listed under the category {channel.category.mention} and is therefore automatically excluded.""", color=bot_colour)
            await ctx.respond(embed=emb)

        elif category != None and filtered_list != []:
 
            channel_list = "\n".join(filtered_list)
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", category_id=category.id)
                    
            emb = discord.Embed(title=f"{Emojis.help_emoji} {'One channel' if len(filtered_list) == 1 else 'Several channels'} in this category is already blacklisted", 
                description=f"""{Emojis.dot_emoji} The following {'channel is' if len(filtered_list) == 1 else 'channels are'} already blacklisted \n\n{channel_list}
                    {Emojis.arrow_emoji} Therefore {'this' if len(filtered_list) == 1 else 'these'} channel will be removed from the blacklist and the category will be added instead.
                   This excludes all channels in the category from the level system.""", color=bot_colour)
            await ctx.respond(embed=emb) 

        elif user != None and user.bot:

            emb = discord.Embed(title=f"{Emojis.help_emoji} You cannot put a bot on the blacklist", 
                description=f"{Emojis.dot_emoji} All bots are automatically excluded from the level system.", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:

            emb = await self.config_level_blacklist(guild_id=ctx.guild.id, operation="add", channel=channel, category=category, role=role, user=user)
            await ctx.respond(embed=emb)
    
    
    @commands.slash_command(name = "remove-level-blacklist", description = "Remove what you want from the blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_level_blacklist(self, ctx:discord.ApplicationContext, 
        channel:Option(Union[discord.VoiceChannel, discord.TextChannel], required = False, description="Select a channel you want to remove from the blacklist!"),
        category:Option(discord.CategoryChannel, required = False, description="Select a category you want to remove from the blacklist "),
        role:Option(discord.Role, required = False, description="Select a role you want to remove from the blacklist "),
        user:Option(discord.User, required = False, description="Select a user that you want to remove from the blacklist!")):

        emb = await self.config_level_blacklist(guild_id=ctx.guild.id, operation="remove", channel=channel, category=category, role=role, user=user)
        await ctx.respond(embed=emb)

   
    @commands.slash_command(name = "show-level-blacklist", description = "Shows you everything that is blacklisted!")
    async def show_blacklist(self, ctx:commands.Context):

        blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)

        emb = discord.Embed(title=f"{Emojis.help_emoji} Here you can see the complete level system blacklist", 
            description=f"""Here you can see everything that is on the level system blacklist:""", color=bot_colour)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Channels on the Blacklist", value=f" {blacklist[0]}", inline=False)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Categories on the Blacklist", value=f" {blacklist[1]}", inline=False)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Roles on the Blacklist", value=f" {blacklist[2]}", inline=False)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Users on the Blacklist", value=f" {blacklist[3]}", inline=False)
        emb.set_footer(icon_url=ctx.guild.icon, text=f"Blacklist from {ctx.guild.name}")
        await ctx.respond(embed=emb)



#############################################  level roles settings  #################################################

    
    @commands.slash_command(name = "add-level-role", description = "Add a role that you get from a certain level!")
    @commands.has_permissions(administrator = True)
    async def add_level_role(self, ctx:commands.Context, role:Option(discord.Role, description = "Select a role that you want to assign from a certain level onwards"),
        level:Option(int, description = "Enter a level from which this role should be assigned")):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, level_role=role.id, needed_level=level, status="check")

        emb_level_0 = discord.Embed(title=f"{Emojis.help_emoji} The level you want to set is 0", 
            description=f"""{Emojis.dot_emoji} The level to vest a level role must be at least **1**.""", color=bot_colour)
        emb_higher = discord.Embed(title=f"{Emojis.help_emoji} The level you want to set for the level role is too high", 
            description=f"""{Emojis.dot_emoji} The level you want to set for the level role is too high you can only set a value that is below or equal to **999**.""", color=bot_colour)
        
        if role.permissions.administrator or role.permissions.moderate_members:

            emb = discord.Embed(title=f"{Emojis.help_emoji} This role cannot be assigned as a level role", 
                description=f"""{Emojis.dot_emoji} This role has administration rights and therefore cannot be assigned as a level role. {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            if level_roles == None:
                
                if level <= 999:
                            
                    DatabaseUpdates._insert_level_roles(guild_id=ctx.guild.id, role_id=role.id, level=level, guild_name=ctx.guild.name)

                    emb = discord.Embed(title=f"The role was assigned successfully {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} The role {role.mention} was successfully assigned to the level {level}.
                        {Emojis.dot_emoji} As soon as a user reaches {level} he gets the {role.mention} role {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb)

                await ctx.respond(embed=emb_level_0) if level == 0 else None

                await ctx.respond(embed=emb_higher) if  level > 999 else None 

            else:

                check_same = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, level_role=role.id, needed_level=level)
                    
                if check_same:

                    same_emb = discord.Embed(title=f"{Emojis.help_emoji} This role has already been set at this level",
                        description=f"""{Emojis.dot_emoji} The role {role.mention} is already assigned to the level {level}.
                        {Emojis.dot_emoji} If you want to change it you can assign this role to another level or another role to this level {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=same_emb)

                else:
                    
                    if role.id == level_roles[1]:

                        level_needed = level_roles[2]
            
                        emb = discord.Embed(title=f"{Emojis.help_emoji} This role is already assigned", 
                            description=f"""{Emojis.dot_emoji} Do you want to override the required level for this role? 
                            {Emojis.dot_emoji} The role {role.mention} is currently assigned at level **{level_needed}**.
                            {Emojis.dot_emoji} If you want to override the required level for this role select the yes buttons otherwise the no button {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                        await ctx.respond(embed=emb, view=LevelRolesButtons(role_id=role.id, role_level=level, status="role"))
        
                    elif level == level_roles[2]:
                        
                        level_role = level_roles[1]

                        emb = discord.Embed(title=f"{Emojis.help_emoji} This level is already assigned", 
                            description=f"""{Emojis.dot_emoji} Do you want to overwrite the role for this level?
                            {Emojis.dot_emoji} For the level {level} the role <@&{level_role}> is currently assigned.
                            {Emojis.dot_emoji} If you want to override the role for this level select the yes buttons otherwise select the no button {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                        await ctx.respond(embed=emb, view=LevelRolesButtons(role_id=role.id, role_level=level, status="level"))   


    @commands.slash_command(name = "remove-level-role", description = "Choose a role that you want to remove as a level role!")
    @commands.has_permissions(administrator = True)
    async def remove_level_role(self, ctx:commands.Context, role:Option(discord.Role, description="Select a level role that you want to remove")):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, level_role=role.id)

        if level_roles:
            
            DatabaseRemoveDatas._remove_level_system_level_roles(guild_id=ctx.guild.id, role_id=role.id)

            emb = discord.Embed(f"This role has been removed as a level role {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The role <@&{role.id}> was successfully removed as a level role.
                {Emojis.dot_emoji} If you want to add them again you can do this with the {add_level_role} command {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, status="level_role")

            if level_roles:
                
                result_strings = [f"{Emojis.dot_emoji} <@&{i[1]}> you get from level: {i[2]}" for i in level_roles]
                result = '\n'.join(result_strings)

            else:

                result = f"{Emojis.dot_emoji} No level roles have been assigned!"

            emb = discord.Embed(title=f"{Emojis.help_emoji} This role is not defined as a level role", 
                description=f"""{Emojis.dot_emoji} This role cannot be removed because it is not set as a level role.
                {Emojis.dot_emoji} Here you can see all the level rolls.\n\n{result}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "show-level-roles", description = "View all rolls that are available with a level!")
    async def show_level_roles(self, ctx:commands.Context):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, status="level_role")
        
        if level_roles:
            
            result_strings = [f"{Emojis.dot_emoji} <@&{i[1]}> you get from level: {i[2]}" for i in level_roles]
            result = '\n'.join(result_strings)
            
            emb = discord.Embed(title="Here you can find all level roles", 
                description=f"{Emojis.help_emoji} Here you can see all level rolls sorted by level in descending order:\n\n {result}", color=bot_colour)
            await ctx.respond(embed=emb)

        else:
            emb = discord.Embed(title=f"No level rolls have been added yet", 
                description=f"{Emojis.help_emoji} There are no level rolls added yet if you want to add some use the {add_level_role} command.", color=bot_colour)
            await ctx.respond(embed=emb)
       
    
    
#############################################  Level up channel settings  #################################


    @commands.slash_command(nanme = "set-level-up-channel", description = "Set a channel for the level up notifications!")
    @commands.has_permissions(administrator = True)
    async def set_levelup_channel(self, ctx:commands.Context, channel:Option(discord.TextChannel, description="Select a channel in which the level up message should be sent")):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settings[3]:
       
            if channel.id == check_settings[3]:

                emb = discord.Embed(title=f"{Emojis.help_emoji} This channel is already assigned as level up channel", 
                    description=f"{Emojis.dot_emoji} This channel is already set as a level up channel if you want to remove it as a level up channel use the:\n{disable_level_up_channel} command {Emojis.exclamation_mark_emoji}", color=bot_colour)
                await ctx.respond(embed=emb)

            else:

                emb = discord.Embed(title=f"{Emojis.help_emoji} There is already a level up channel assigned", 
                    description=f"""{Emojis.dot_emoji} Currently the channel <#{check_settings[3]}> is set as level up channel. 
                    {Emojis.dot_emoji} Do you want to overwrite this one?
                    {Emojis.dot_emoji} If yes select the yes button if not select the no button {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                await ctx.respond(embed=emb, view=LevelUpChannelButtons(channel=channel.id))

        else:

            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, levelup_channel=channel.id)

            emb = discord.Embed(title=f"The level up channel was set successfully {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} You have successfully set the channel <#{channel.id}> as a level up channel.
                {Emojis.dot_emoji} From now on all level up notifications will be sent to this channel.""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "disable-level-up-channel", description = "Deactivate the level up channel!")
    @commands.has_permissions(administrator = True)
    async def disable_levelup_channel(self, ctx:commands.Context):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settings[3]:
                
            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, back_to_none=2)

            emb = discord.Embed(title=f"The level up channel was successfully removed {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} From now on level up notifications will always be sent after level up.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:
            
            emb = discord.Embed(title=f"{Emojis.help_emoji} No level up channel was assigned", 
                description=f"{Emojis.dot_emoji} There was no level up channel assigned so none could be removed.", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "show-level-up-channel", description = "Let them show the current level up channel!")
    async def show_levelup_channel(self, ctx:commands.Context):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)
        
        if check_settings[3]:
        
            emb = discord.Embed(title=f"{Emojis.help_emoji} Here you can see the current level up channel", 
                description=f"""{Emojis.dot_emoji} The current level up channel is <#{check_settings[3]}> all level up notifications are sent to this channel.""", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:
            
            emb = discord.Embed(title=f"{Emojis.help_emoji} No level up channel has been set", 
                description=f"""{Emojis.dot_emoji} No level up channel has been set if you want to set one use that:\n{add_level_up_channel} command.""", color=bot_colour)
            await ctx.respond(embed=emb)



##########################################  Set xp rate system  ###################################


    @commands.slash_command(name = "set-xp-rate", description = "Set how much XP will be awarded per message!")
    @commands.has_permissions(administrator = True)
    async def set_xp_rate(self, ctx:commands.Context, xp:Option(int, description="Set a base value how much XP you earn per message!")):

        if xp <= 0:

            emb = discord.Embed(title=f"{Emojis.help_emoji} The xp amount you want to set is too low", 
                description=f"""{Emojis.dot_emoji} The XP amount you get per message as a reward is too low it must be at least 1!""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, xp_rate=xp)

            emb = discord.Embed(title=f"You have successfully set the xp to be assigned per message {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The xp to be assigned per message has been set to **{xp}**. 
                {Emojis.help_emoji} From now on every message will be rewarded with **{xp}** XP {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "default-xp-rate", description = "Set the XP you get per message back to default settings!")
    @commands.has_permissions(administrator = True)
    async def default_xp_rate(self, ctx:commands.Context):
        
        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settings[1] == 20:

            emb = discord.Embed(title=f"{Emojis.help_emoji} The xp quantity is already set to the default settings", 
                description=f"{Emojis.dot_emoji} The xp amount assigned for each message is already at the default value of **20**.", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, back_to_none=0)

            emb = discord.Embed(title=f"The XP quantity for messages was successfully reset {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The XP assigned for each message has been set back to **20**.""", color=bot_colour)
            await ctx.respond(embed=emb)
        
       
    @commands.slash_command(name = "show-xp-rate", description = "Let us show you how much xp you currently get per message!")
    async def show_xp_rate(self, ctx:commands.Context):
        
        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        emb = discord.Embed(title=f"{Emojis.help_emoji} Here you can see how much XP you get per message",
            description=f"""{Emojis.dot_emoji} Per message you get {check_settings[1]} XP.
            {Emojis.dot_emoji} We recommend that you do not set this value too high if you adjust it, otherwise the level system will lose much of its meaning {Emojis.exclamation_mark_emoji}""")
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
    
    
    async def config_bonus_xp_list(self, guild_id:int, operation:str, channel = None, category = None, role = None, user = None):

        if [x for x in [channel, category, role, user] if x]:
            
            check_channel = DatabaseCheck.check_xp_bonus_list(guild_id=guild_id, channel_id=channel.id) if channel != None else False
            check_category = DatabaseCheck.check_xp_bonus_list(guild_id=guild_id, category_id=category.id) if category != None else False
            checK_role = DatabaseCheck.check_xp_bonus_list(guild_id=guild_id, role_id=role.id) if role != None else False
            check_user = DatabaseCheck.check_xp_bonus_list(guild_id=guild_id, user_id=user.id) if user != None else False

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
                    
                    formatted_items = "\n".join(item) if item != [] else "\n> Keines dieser Items ist auf der Bonus XP list"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> Keines dieser Items kann von der Bonus XP list entfernt werden da sie dort nicht gelistet sind"
                    
                    DatabaseUpdates.manage_blacklist(guild_id=guild_id, operation="add", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3])    
                        
                    emb = discord.Embed(title=f"{Emojis.help_emoji} The following items have been added to the bonus XP list or were already there", 
                        description=f"""### {Emojis.dot_emoji} The following were already on the XP bonus list:
                        {formatted_items}\n### {Emojis.dot_emoji} Newly added:
                        {formatted_add_items}""", color=bot_colour)
                    return emb

                elif operation == "remove":
                
                    formatted_items = "\n".join(item) if item != [] else "> All the items you specified were on the XP bonus list"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> None of the items you specified could be removed from the XP bonus list because they are not on the blacklist"

                    DatabaseUpdates.manage_blacklist(guild_id=guild_id, operation="remove", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3])

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

    
    @commands.slash_command(name = "add-bonus-xp-list", description = "Add what you want to the bonus XP list!")
    @commands.has_permissions(administrator = True)
    async def add_level_blacklist(self, ctx:discord.ApplicationContext, 
        channel:Option(Union[discord.VoiceChannel, discord.TextChannel], required = False, description="Wähle einen channel aus in den nachrichten mit mehr XP belohnen werden sollen!"),
        category:Option(discord.CategoryChannel, required = False, description="Wähle eine Kategorie aus in der nachrichten mit mehr XP belohnen werden sollen!"),
        role:Option(discord.Role, required = False, description="Wähle eine Rolle aus wo der jenige der sie besitzt mehr XP erhält wenn er nachrichten schreibt!"),
        user:Option(discord.User, required = False, description="Wähle einen user aus der mehr XP pro Nachricht erhalten soll!"),
        bonus:Option(int, required = False, description="Choose how much more xp to give in percent (if nothing is specified the default value is used!)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])):

        check_blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id)

        filtered_list = []
        if category != None:
            
            for _, channels, _, _, _ in check_blacklist:

                if channels:

                    if bot.get_channel(channels).category.id == category.id:

                        DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", channel_id=channels)
                        filtered_list.append(f"> {Emojis.dot_emoji} <#{channels}>")
        
        if channel != None and any(channel.category.id == x[2] for x in check_blacklist):

            emb = discord.Embed(title=f"{Emojis.help_emoji} The channel is already indirectly on the XP bonus list", 
                description=f"""{Emojis.dot_emoji} Der channe {channel.mention} ist bereits auf der bonus XP list und wir somit schon mit """, color=bot_colour)
            await ctx.respond(embed=emb)

        elif category != None and filtered_list != []:
 
            channel_list = "\n".join(filtered_list)
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", category_id=category.id)
                    
            emb = discord.Embed(title=f"{Emojis.help_emoji} {'One channel' if len(filtered_list) == 1 else 'Several channels'} in this category is already blacklisted", 
                description=f"""{Emojis.dot_emoji} The following {'channel is' if len(filtered_list) == 1 else 'channels are'} already blacklisted \n\n{channel_list}
                    {Emojis.arrow_emoji} Therefore {'this' if len(filtered_list) == 1 else 'these'} channel will be removed from the blacklist and the category will be added instead.
                   This excludes all channels in the category from the level system.""", color=bot_colour)
            await ctx.respond(embed=emb) 

        elif user != None and user.bot:

            emb = discord.Embed(title=f"{Emojis.help_emoji} You cannot put a bot on the blacklist", 
                description=f"{Emojis.dot_emoji} All bots are automatically excluded from the level system.", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:

            emb = await self.check_level_blacklist(guild_id=ctx.guild.id, operation="add", channel=channel, category=category, role=role, user=user)
            await ctx.respond(embed=emb)



    @commands.slash_command(name = "add-bonus-xp-channel")
    @commands.has_permissions(administrator = True)
    async def add_bonus_xp_channel(self, ctx:commands.Context, 
        channel:Option(Union[discord.TextChannel, discord.VoiceChannel], description="Choose a channel that is rewarded with extra xp!"), 
        bonus:Option(int, description="Choose how much more xp to give in percent (if nothing is specified the default value is used!)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) = None):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, channel_id=channel.id)

        if check_list: 

            emb = discord.Embed(title=f"{Emojis.help_emoji} This channel has already been set as XP bonus channel", 
                description=f"""{Emojis.dot_emoji} The channel <#{channel.id}> has already been set as XP bonus channel therefore all activities in this channel will be rewarded with extra XP.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="add", channel_id=channel.id, bonus=bonus)

            emb = discord.Embed(title=f"The bonus xp channel was successfully set {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The channel <#{channel.id}> was set as XP bonus channel.
                {Emojis.dot_emoji} Messages or activities in this channel will be rewarded with **{self.check_bonus_percentage(bonus=bonus, guild_id=ctx.guild.id)} %** more XP.""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-bonus-xp-channel")
    @commands.has_permissions(administrator = True)
    async def remove_bonus_xp_channel(self, ctx:commands.Context, channel:Option(Union[discord.TextChannel, discord.VoiceChannel], description="Choose a channel that you want to use as xp bonus channel!")):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, channel_id=channel.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove", channel_id=channel.id)

            emb = discord.Embed(title=f"The channel was successfully removed as bonus xp channel {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The channel <#{channel.id}> was removed as XP bonus channel.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            bonus_xp_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
            
            bonus_xp_channels = [f"{Emojis.dot_emoji} {i}" for i in bonus_xp_list[1]] if bonus_xp_list else ["No channel has been set as a bonus XP channel"]
            bonus_channels = "\n".join(bonus_xp_channels)

            emb = discord.Embed(title=f"{Emojis.help_emoji} This channel was not set as a bonus XP channel.", 
                description=f"""{Emojis.dot_emoji} The channel <#{channel.id}> was not set as a bonus XP channel and therefore cannot be removed.
                {Emojis.dot_emoji} Here you can see all the channels that have been set as bonus XP channels:\n\n{bonus_channels}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "add-bonus-xp-category")
    @commands.has_permissions(administrator = True)
    async def add_bonus_xp_category(self, ctx:commands.Context, 
        category:Option(discord.CategoryChannel, description="Choose  a category in which all activities in all channels are rewarded with extra xp!"),
        bonus:Option(int, description="Choose how much more XP to give in percent (if nothing is specified the default value is used!)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) = None):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, category_id=category.id)

        if check_list: 

            emb = discord.Embed(title=f"{Emojis.help_emoji} This category has already been set as XP bonus category.", 
                description=f"""{Emojis.dot_emoji} The category <#{category.id}> is already set as XP bonus category therefore all activities in all channels of the category will be rewarded with extra XP.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="add", category_id=category.id, bonus=bonus)

            emb = discord.Embed(title=f"The bonus xp category was successfully set {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The category <#{category.id}> was set as XP bonus category.
                {Emojis.dot_emoji} Messages or activities in this category will be rewarded with **{self.check_bonus_percentage(bonus=bonus, guild_id=ctx.guild.id)} %** more XP.""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-bonus-xp-category")
    @commands.has_permissions(administrator = True)
    async def remove_bonus_xp_category(self, ctx:commands.Context, category:Option(discord.CategoryChannel, description="Choose a category that you want to remove as XP bonus category!")):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, category_id=category.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove", category_id=category.id)

            emb = discord.Embed(title=f"The category was successfully removed as bonus XP category {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The category <#{category.id}> was removed as XP bonus category.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            bonus_xp_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
            
            bonus_xp_categories = [f"{Emojis.dot_emoji} {i}" for i in bonus_xp_list[2]] if bonus_xp_list else ["No category was set as bonus XP category"]
            bonus_categories = "\n".join(bonus_xp_categories)

            emb = discord.Embed(title=f"{Emojis.help_emoji} This category was not set as a bonus XP category.", 
                description=f"""{Emojis.dot_emoji} The category <#{category.id}> was not set as bonus XP category and therefore cannot be removed.
                {Emojis.dot_emoji} Here you can see all the categories that have been set as bonus XP categories:\n\n{bonus_categories}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "add-bonus-xp-role", description = "Add a role as a bonus XP role and set its XP bonus!")
    @commands.has_permissions(administrator = True)
    async def add_bonus_xp_role(self, ctx:commands.Context, 
        role:Option(discord.Role, description="Choose a role that everyone who has this role gets extra xp!"),
        bonus:Option(int, description="Choose how much more XP to give in percent (if nothing is specified the default value is used!)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) = None):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, role_id=role.id)

        if check_list: 

            emb = discord.Embed(title=f"{Emojis.help_emoji} This role has already been set as XP bonus role.", 
                description=f"""{Emojis.dot_emoji} The role <@&{role.id}> is already set as XP bonus role therefore all activities of users with this role will be rewarded with extra XP.""", color=bot_colour)
            await ctx.respond(embed=emb)
            
        else:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="add", role_id=role.id, bonus=bonus)

            emb = discord.Embed(title=f"The bonus xp role was successfully set {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The role <@&{role.id}> was set as XP bonus role.
                {Emojis.dot_emoji} Messages or activities from users with this role are rewarded with **{self.check_bonus_percentage(bonus=bonus, guild_id=ctx.guild.id)} %** more XP.""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-bonus-xp-role", description = "Remove a role as a bonus XP role!")
    @commands.has_permissions(administrator = True)
    async def remove_bonus_xp_role(self, ctx:commands.Context, role:Option(discord.Role, description="Choose a role that you want to remove as XP bonus role!")):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, role_id=role.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove", role_id=role.id)

            emb = discord.Embed(title=f"The role was successfully removed as bonus XP role {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The role <@&{role.id}> was removed as XP bonus role.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            bonus_xp_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
            
            bonus_xp_roles = [f"{Emojis.dot_emoji} {i}" for i in bonus_xp_list[3]] if bonus_xp_list else ["No role was set as a bonus XP role"]
            bonus_roles = "\n".join(bonus_xp_roles)

            emb = discord.Embed(title=f"{Emojis.help_emoji} This role was not set as a bonus XP role.", 
                description=f"""{Emojis.dot_emoji} The role <@&{role.id}> has not been set as a bonus XP role and therefore cannot be removed.
                {Emojis.dot_emoji} Here you can see all the roles that have been set as bonus XP roles:\n\n{bonus_roles}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "add-bonus-xp-user", description = "Add a user as bonus XP user and set his XP bonus!")
    @commands.has_permissions(administrator = True)
    async def add_bonus_xp_user(self, ctx:commands.Context, 
        user:Option(discord.User, description="Choose a user who gets extra xp for each message or activity!"),
        bonus:Option(int, description="Choose how much more XP to give in percent (if nothing is specified the default value is used!)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) = None):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, user_id=user.id)

        if check_list: 

            emb = discord.Embed(title=f"{Emojis.help_emoji} This user has already been set as XP bonus user.", 
                description=f"""{Emojis.dot_emoji} The user <@{user.id}> is set as XP bonus user therefore all activities of <@{user.id}> will be rewarded with extra XP.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="add", user_id=user.id, bonus=bonus)

            emb = discord.Embed(title=f"The bonus xp user was successfully set {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The user <@{user.id}> was set as XP bonus user.
                {Emojis.dot_emoji} Messages or activities from <@{user.id}> are rewarded with **{self.check_bonus_percentage(bonus=bonus, guild_id=ctx.guild.id)} %** more XP.""", color=bot_colour)
            await ctx.respond(embed=emb)

        
    @commands.slash_command(name = "remove-bonus-xp-user", description = "Remove a user as bonus XP user!")
    @commands.has_permissions(administrator = True)
    async def remove_bonus_xp_user(self, ctx:commands.Context, user:Option(discord.User, description="Choose a user you want to remove as XP bonus user!")):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, user_id=user.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove", user_id=user.id)

            emb = discord.Embed(title=f"The user {user.name} was successfully removed as bonus XP user {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The user <@{user.id}> was removed as XP bonus user.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            bonus_xp_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
            
            bonus_xp_user = [f"{Emojis.dot_emoji} {i}" for i in bonus_xp_list[4]] if bonus_xp_list else ["No user has been set as bonus XP user"]
            bonus_user = "\n".join(bonus_xp_user)

            emb = discord.Embed(title=f"{Emojis.help_emoji} The user {user.name} was not set as bonus XP user.", 
                description=f"""{Emojis.dot_emoji} The user <@{user.id}> was not set as a bonus XP user and therefore cannot be removed.
                {Emojis.dot_emoji} Here you can see all the users that have been set as bonus XP users:\n\n{bonus_user}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "show-bonus-xp-list", description = "Display everything that is on the bonus xp list!")
    async def show_bonus_xp_list(self, ctx:commands.Context):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
        check_bonus = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)
        bonus = check_bonus[5]

        if check_list:

            bonus_xp_list = [f"{Emojis.dot_emoji} <#{i[1]}> activities in this channel are rewarded with **{i[5] if i[5] else bonus} %** more XP" if i[1] else None for i in check_list] + [
                f"{Emojis.dot_emoji} <#{i[2]}> activities of this category are rewarded with **{i[5] if i[5] else bonus} %** more XP" if i[2] != None else None for i in check_list] + [
                f"{Emojis.dot_emoji} <@&{i[3]}> activities of users with this role are rewarded with **{i[5] if i[5] else bonus} %** more XP" if i[3] != None else None for i in check_list] + [
                f"{Emojis.dot_emoji} <@{i[4]}> activities of this user will be rewarded with **{i[5] if i[5] else bonus} %** more XP" if i[4] != None else None for i in check_list]
            filtered_list = [x for x in bonus_xp_list if x is not None]
            all_bonus_xp_items = "\n".join(filtered_list)

        else:

            all_bonus_xp_items = f"{Emojis.dot_emoji} No channel, category, role or user has been given an XP bonus!"

        emb = discord.Embed(title=f"{Emojis.help_emoji} Here you can see everything that is on the bonus XP list", 
            description=f"""{Emojis.dot_emoji} Here you can see all channels, categories, roles and users that get bonus XP and their XP bonus!\n\n{all_bonus_xp_items}""", color=bot_colour)
        await ctx.respond(embed=emb)


    @commands.slash_command(name = "reset-bonus-xp-list", description = "Reset the bonus XP list!")
    @commands.has_permissions(administrator = True)
    async def reset_bonus_xp_list(self, ctx:commands.Context):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove")
            emb = discord.Embed(title=f"The bonus xp list was reset {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} All channels, users, roles and categories have been deleted from the xp bonus list.
                {Emojis.dot_emoji} So every activity will be rewarded with {self.xp_generator(guild_id=ctx.guild.id, message=None)} XP.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(title=f"{Emojis.help_emoji} The bonus XP list cannot be reset", 
                description=f"""{Emojis.dot_emoji} The bonus XP list cannot be reset because it does not contain any entries.""", color=bot_colour)
            await ctx.respond(embed=emb)



#################################################  Bonus XP percentage  ###########################################


    @commands.slash_command(name = "set-bonus-xp-percentage", description = "Set a default percentage for the bonus XP system (this is set to 10 % by default)!")
    @commands.has_permissions(administrator = True)
    async def set_bonus_xp_percentage(self, ctx:commands.Context, percentage:Option(int, description="Specify a percentage to be used as the default percentage for the bonus XP system!",max_value=100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settings[5] == percentage:

            emb = discord.Embed(title=f"{Emojis.help_emoji} The current percentage value is equal to the one you are about to add", 
                description=f"""{Emojis.dot_emoji} The current percentage value for the bonus XP system is **{check_settings[5]} %**""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, percentage=percentage)

            emb = discord.Embed(title=f"The default percentage for the bonus XP system has been assigned to {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The default percentage for the bonus XP system was set to **{percentage} %**!
                {Emojis.help_emoji} This percentage now applies to all channels, categories, roles and users that are part of the bonus XP system.
                This percentage is now always added to the XP received {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "default-bonus-xp-percentage", description = "Set the percentage value for the bonus XP system back to the default value!")
    @commands.has_permissions(administrator = True)
    async def default_bonus_xp_percentage(self, ctx:commands.Context):
        
        check_settigns = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settigns[5] == 10:

            emb = discord.Embed(title=f"{Emojis.help_emoji} The default percentage value for the bonus XP system is already set to the default value", 
                description=f"""{Emojis.dot_emoji} The default percentage value for the bonus XP system is already at **{check_settigns[5]} %**""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, back_to_none=4)

            emb = discord.Embed(title=f"The default percentage value for the bonus XP system was successfully reset {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The default percentage value for the bonus XP system was set back to **10 %**.
                {Emojis.dot_emoji} All activities of or in all channels, categories, roles or users that are part of the bonus XP system will be rewarded with **10 %** more XP.""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "show-bonus-xp-percentage", description = "Let the display where the default percentage value for the bonus XP system is!")
    async def show_bonus_xp_percentage(self, ctx:commands.Context):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        emb = discord.Embed(title=f"{Emojis.help_emoji} Here you can see how many percent more XP you get with the Bonus XP system", 
            description=f"""{Emojis.dot_emoji} You currently get **{check_settings[5]} %** more XP for activities in channels or categories that are part of the bonus XP system.
            You also get this bonus if you have a role that is on the list for the bonus XP system or if you are a user that is listed on the bonus XP list.""", color=bot_colour)
        await ctx.respond(embed=emb)



##########################################  Custom level up message  ########################################


    @commands.slash_command(name = "set-level-up-message", description = "Set a custom level up message for your server!")
    @commands.has_permissions(administrator = True)
    async def set_level_up_message(self, ctx:discord.ApplicationContext):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settings:

            mark_stings = ["{user}", "{level}"]

            emb = discord.Embed(title=f"{Emojis.help_emoji} Set an individual level-up message now", 
                description=f"""{Emojis.dot_emoji} If you want to set the level up message, you have two default arguments `{mark_stings[0]}` and `{mark_stings[1]}`.
                {Emojis.dot_emoji} Where you insert `{mark_stings[0]}`, the user is marked
                {Emojis.dot_emoji} Where you insert `{mark_stings[1]}`, the current level of the user is inserted
                Here you have a small example:

                {Emojis.arrow_emoji} `Oh nice {mark_stings[0]} you have a new level, your newlevel is {mark_stings[1]}`

                {Emojis.dot_emoji} If you want to set the custom message for your server, press the button located just below this message.""", color=bot_colour)
            await ctx.respond(embed=emb, view=ModalButtonLevelUpMessage())
        
        else:

            DatabaseUpdates._create_bot_settings(guild_id=ctx.guild.id)
            await ctx.respond(embed=no_entry_emb)

    
    @commands.slash_command(name = "default-level-up-message", description = "Reset the level-up message to the default message!")
    @commands.has_permissions(administrator = True)
    async def default_level_up_message(self, ctx:commands.Context):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settings:

            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, back_to_none=3)
            level_up_message = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"The level-up message was set back to default settings {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The level-up message for this server was reset to default.
                {Emojis.dot_emoji} Here you can see the current level-up message: `{level_up_message[4]}`.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates._create_bot_settings(guild_id=ctx.guild.id)
            await ctx.respond(embed=no_entry_emb)

        
    @commands.slash_command(name = "show-level-up-message", description = "Shows the current level-up message from your server")
    async def show_level_up_message(self, ctx:commands.Context):

        level_up_message = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if level_up_message:

            emb = discord.Embed(title=f"{Emojis.help_emoji} Here you can see the current level-up message", 
                description=f"""{Emojis.dot_emoji} The current level-up message is:\n\n{Emojis.arrow_emoji} {level_up_message[4]}\n
                {Emojis.dot_emoji} This message is always sent when a user receives a level-up.
                {Emojis.exclamation_mark_emoji} If you set a level-up channel, this message will only be sent to this selected channel.""", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:

            DatabaseUpdates._create_bot_settings(guild_id=ctx.guild.id)
            await ctx.respond(embed=no_entry_emb)


class ModalButtonLevelUpMessage(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Level up message now set", style=discord.ButtonStyle.blurple, custom_id="add_level_up_message")
    async def add_level_up_message(self, button, interaction:discord.Interaction):

        await interaction.response.send_modal(LevelUpMessageModal(title="Set a level-up message for your server!"))


class LevelUpMessageModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Insert here the text for the level-up message", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user.mention
        level = 1
        level_up_message = eval("f'{}'".format(self.children[0].value))

        DatabaseUpdates.update_level_settings(guild_id=interaction.guild.id, level_up_message=self.children[0].value)

        embed = discord.Embed(title=f"The level-up message was successfully set {Emojis.succesfully_emoji}", 
            description=f"""{Emojis.dot_emoji} The level-up message was set to:\n{Emojis.arrow_emoji} `{level_up_message}` {Emojis.exclamation_mark_emoji}
            {Emojis.dot_emoji} When someone receives a level-up this message is sent""", color=bot_colour)
        await interaction.response.edit_message(embeds=[embed], view=None)



def setup(bot):
    bot.add_cog(LevelSystem(bot))
    