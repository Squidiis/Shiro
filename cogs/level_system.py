
from Import_file import *
from typing import Union
from easy_pil import Editor, load_image_async, Font
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from check import *
import re


class CheckLevelSystem():

    def show_blacklist_level(guild_id:int):

        blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id, table="level")
        
        if blacklist:

            all_channels, all_categories, all_roles, all_users = [], [], [], []
            for _, blacklist_channel, blacklist_category, blacklist_role, blacklist_user in blacklist:

                None if None == blacklist_channel else all_channels.append(f"{Emojis.dot_emoji} <#{blacklist_channel}>\n")

                None if None == blacklist_category else all_categories.append(f"{Emojis.dot_emoji} <#{blacklist_category}>\n")

                None if None == blacklist_role else all_roles.append(f"{Emojis.dot_emoji} <@&{blacklist_role}>\n")

                None if None == blacklist_user else all_users.append(f"{Emojis.dot_emoji} <@{blacklist_user}>\n")
                
            if all_channels == []:
                channels_mention = f"{Emojis.dot_emoji} There are no channels on the blacklist"
            else:
                channels_mention = "".join(all_channels)
                
            if all_categories == []:
                categories_mention = f"{Emojis.dot_emoji} There are no categories on the blacklist"
            else:
                categories_mention = "".join(all_categories)
                
            if all_roles == []:
                roles_mention = f"{Emojis.dot_emoji} There are no roles on the blacklist"
            else:
                roles_mention = "".join(all_roles)
                
            if all_users == []:
                users_mention = f"{Emojis.dot_emoji} There are no users on the blacklist"
            else:
                users_mention = "".join(all_users)
        
        else:

            channels_mention = f"{Emojis.dot_emoji} There are no channels on the blacklist"
            categories_mention = f"{Emojis.dot_emoji} There are no categories on the blacklist"
            roles_mention = f"{Emojis.dot_emoji} There are no roles on the blacklist"
            users_mention = f"{Emojis.dot_emoji} There are no users on the blacklist"

        return [channels_mention, categories_mention, roles_mention, users_mention]




##############################################  Blacklist manager  ##############################################


class BlacklistManagerButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Button for adding items to the Blacklist Manager
    @discord.ui.button(label="add to blacklist", style=discord.ButtonStyle.blurple, custom_id="add_blacklist")
    async def add_blacklist_manager_button(self, button, interaction:discord.Interaction):

        view = BlacklistManagerSelectAdd()
        view.add_item(TempBlackklistLevelSaveButton())
        view.add_item(ShowBlacklistLevelSystemButton())

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Here you can select what you want to blacklist", 
                description=f"""{Emojis.dot_emoji} With the lower select menus you can choose what you want to put on the blacklist!
                {Emojis.dot_emoji} You can freely choose what you want, but you can only select a maximum of 5 items per menu.
                {Emojis.dot_emoji} When you have selected everything you want, confirm your selection by pressing the safe configuration button.
                {Emojis.dot_emoji} If you want to see already everything on the blacklist use the show blacklist button.
                {Emojis.help_emoji} If you select something that is already on the blacklist it will be automatically sorted out. {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=view)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    # Button for removing items from the Blacklist Manager
    @discord.ui.button(label="remove from blacklist", style=discord.ButtonStyle.blurple, custom_id="remove_blacklist")
    async def remove_blacklist_manager_button(self, button, interaction:discord.Interaction):
        
        view = BlacklistManagerSelectRemove()
        view.add_item(TempBlackklistLevelSaveButton())
        view.add_item(ShowBlacklistLevelSystemButton())

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Here you can select what you want to remove from the blacklist {Emojis.help_emoji}", 
                description=f"""{Emojis.dot_emoji} With our selectmenus you can choose what to remove from the blacklist.
                {Emojis.dot_emoji} When you have selected everything you want, confirm your selection by pressing the Safe configuaration button.
                {Emojis.dot_emoji} If you don't know what is on the blacklist you can either press the show blacklist button or use the {show_blacklist_level} command.
                {Emojis.help_emoji} If you select something that is not on the blacklist it will be sorted out automatically.  {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=view)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)

# All functions for the blacklist manager
class BlacklistManagerChecks():

    # Checks each entry to see if any of them are blacklisted.
    def check_items_blacklist_manager(guild_id:str, table:str, channels = None, categories = None, roles = None, users = None, operation = None):
        
        sorted_list = []
        item_list = channels or categories or roles or users
        
        for item in item_list:
                
            if channels != None:
                blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id, channel_id=item.id, table=table)
            if categories != None:
                blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id, category_id=item.id, table=table)
            if roles != None:
                blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id, role_id=item.id, table=table)
            if users != None:
                blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id, user_id=item.id, table=table)

            if operation == "add":

                if blacklist == None or blacklist == []:
                    sorted_list.append(str(item.id))
            
            else:
                
                if blacklist != None and blacklist != []:
                    sorted_list.append(str(item.id))
            
        return sorted_list
    

    # Checks the temp blacklist 
    def check_temp_blacklist_level(guild_id:int, system:str):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        if system == "level":
          
            check_temp_blacklist = f"SELECT * FROM ManageBlacklistTemp WHERE guildId = %s AND systemStatus = %s"
            check_temp_blacklist_values = [guild_id, system]

        cursor.execute(check_temp_blacklist, check_temp_blacklist_values)
        temp_blacklist = cursor.fetchone()
    
        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return temp_blacklist


    # Update or insert elements into the temporary black list 
    def configure_temp_blacklist_level(guild_id:int, operation:str, channel_id:int = None, category_id:int = None, role_id:int = None, user_id:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        temp_blacklist = BlacklistManagerChecks.check_temp_blacklist_level(guild_id=guild_id, system="level")

        item = channel_id or category_id or role_id or user_id
        count = 0

        if channel_id != None and channel_id != [] or category_id != None and category_id != [] or role_id != None and role_id != [] or user_id != None and user_id != []:

            for item in channel_id, category_id, role_id, user_id:
        
                column_name = ["channelId", "categoryId", "roleId", "userId"]
                
                if item != None:
                    sorted_list = ", ".join(item)
                    if temp_blacklist:
                                
                        temp_blacklist_operation = f"UPDATE ManageBlacklistTemp SET {column_name[count]} = %s, operation = %s WHERE guildId = %s AND systemStatus = %s"
                        temp_blacklist_operation_values = [sorted_list, operation, guild_id, 'level']

                    else:
                                
                        temp_blacklist_operation = f"INSERT INTO ManageBlacklistTemp (guildId, {column_name[count]}, operation, systemStatus) VALUES (%s, %s, %s, %s)"
                        temp_blacklist_operation_values = [guild_id, sorted_list, operation, 'level']   
                count = count + 1 
            cursor.execute(temp_blacklist_operation, temp_blacklist_operation_values)
            db_connect.commit()
        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    # Deletes the entire temporary blacklist after the transfer is complete
    def delete_temp_blacklist_level(guild_id:int):
        
        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        delete_temp_blacklist = "DELETE FROM ManageBlacklistTemp WHERE guildId = %s"
        delete_temp_blacklist_values = [guild_id]
        cursor.execute(delete_temp_blacklist, delete_temp_blacklist_values)
        db_connect.commit()


class BlacklistManagerSelectAdd(discord.ui.View):
    def __init__(self):
        self.table = "level"
        super().__init__(timeout=None)

    @discord.ui.channel_select(placeholder="Select the channels you want to blacklist!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.text, discord.ChannelType.voice, discord.ChannelType.forum, discord.ChannelType.news], custom_id="add_channel_blacklist_select")
    async def add_blacklist_channel_level_select(self, select, interaction:discord.Interaction):

        channel_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, channels=select.values, operation="add", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", channel_id=channel_list)
        await interaction.response.defer()

    @discord.ui.channel_select(placeholder="Select the categories you want to blacklist!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.category], custom_id="add_category_blacklist_select")
    async def add_blacklist_category_level_select(self, select, interaction:discord.Interaction):

        category_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, categories=select.values, operation="add", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", category_id=category_list)
        await interaction.response.defer()

    @discord.ui.role_select(placeholder="Select the roles you want to blacklist!", min_values=1, max_values=5, custom_id="add_role_blacklist_select")
    async def add_blacklist_role_level_select(self, select, interaction:discord.Interaction):

        role_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, roles=select.values, operation="add", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", role_id=role_list)
        await interaction.response.defer()
        
    @discord.ui.user_select(placeholder="Select the users you want to blacklist!", min_values=1, max_values=5, custom_id="add_user_blacklist_select")
    async def add_blacklist_user_level_select(self, select, interaction:discord.Interaction):

        user_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, users=select.values, operation="add", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", user_id=user_list)
        await interaction.response.defer()


class BlacklistManagerSelectRemove(discord.ui.View):
    def __init__(self):
        self.table = "level"
        super().__init__(timeout=None)

    @discord.ui.channel_select(placeholder="Select the channels you want to remove from the blacklist!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.text, discord.ChannelType.voice, discord.ChannelType.forum, discord.ChannelType.news], custom_id="remove_channel_blacklist_select")
    async def add_blacklist_channel_level_select(self, select, interaction:discord.Interaction):

        channel_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, channels=select.values, operation="remove", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="remove", channel_id=channel_list)
        await interaction.response.defer()

    @discord.ui.channel_select(placeholder="Select the categories you want to remove from the blacklist!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.category], custom_id="remove_category_blacklist_select")
    async def add_blacklist_category_level_select(self, select, interaction:discord.Interaction):

        category_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, categories=select.values, operation="remove", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="remove", category_id=category_list)
        await interaction.response.defer()

    @discord.ui.role_select(placeholder="Select the roles you want to remove from the blacklist!", min_values=1, max_values=5, custom_id="remove_role_blacklist_select")
    async def add_blacklist_role_level_select(self, select, interaction:discord.Interaction):
        
        role_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, roles=select.values, operation="remove", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="remove", role_id=role_list)
        await interaction.response.defer()
        
    @discord.ui.user_select(placeholder="Select the users you want to remove from the blacklist!", min_values=1, max_values=5, custom_id="remove_user_blacklist_select")
    async def add_blacklist_user_level_select(self, select, interaction:discord.Interaction):

        user_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, users=select.values, operation="remove", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="remove", user_id=user_list)
        await interaction.response.defer()


class TempBlackklistLevelSaveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Safe all configurations", style=discord.enums.ButtonStyle.blurple,custom_id="safe_configuration")
    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            
            await interaction.response.defer()
            temp_blacklist = BlacklistManagerChecks.check_temp_blacklist_level(guild_id=interaction.guild.id, system="level")
            
            operation = "add" if temp_blacklist[5] == "add" else "remove"

            if temp_blacklist:
                    
                mention = []
                    
                if temp_blacklist[1]:
                    
                    channel_list = (list(map(int, re.findall('\d+', temp_blacklist[1]))))
                    
                    for channel in channel_list:
                            
                        mention.append(f"{Emojis.dot_emoji} <#{channel}>")
                        
                        DatabaseUpdates.manage_blacklist(guild_id=temp_blacklist[0], operation=operation, channel_id=channel, table="level")

                if temp_blacklist[2]: 

                    category_list = (list(map(int, re.findall('\d+', temp_blacklist[2]))))
                    for category in category_list:

                        mention.append(f"{Emojis.dot_emoji} <#{category}>")

                        DatabaseUpdates.manage_blacklist(guild_id=temp_blacklist[0], operation=operation, category_id=category, table="level")
                      
                if temp_blacklist[3]:
                        
                    role_list = (list(map(int, re.findall('\d+', temp_blacklist[3]))))
                    for role in role_list:
                            
                        mention.append(f"{Emojis.dot_emoji} <@&{role}>")
                        
                        DatabaseUpdates.manage_blacklist(guild_id=temp_blacklist[0], operation=operation, role_id=role, table="level")
                                
                if temp_blacklist[4]:
                        
                    user_list = (list(map(int, re.findall('\d+', temp_blacklist[4]))))
                    for user in user_list:

                        mention.append(f"{Emojis.dot_emoji} <@{user}>")
                        
                        DatabaseUpdates.manage_blacklist(guild_id=temp_blacklist[0], operation=operation, user_id=user, table="level")

                BlacklistManagerChecks.delete_temp_blacklist_level(guild_id=temp_blacklist[0])
                    
                mentions = "\n".join(mention)

                if temp_blacklist[5] == "add":

                    emb = discord.Embed(title=f"The selected elements were set on the blacklist {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} Everything you selected was blacklisted.
                        {Emojis.dot_emoji} Here you can see again everything that was added:\n\n{mentions}\n
                        {Emojis.help_emoji} If something is not listed it is already on the blacklist {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await interaction.edit_original_response(embed=emb, view=None)

                if temp_blacklist[5] == "remove":

                    emb = discord.Embed(title=f"The selected elements have been removed from the blacklist {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} Everything you selected was removed from the blacklist.
                        {Emojis.dot_emoji} Here you can see again everything that was removed:\n\n{mentions}\n
                        {Emojis.help_emoji} If something is not listed it is not on the blacklist {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await interaction.edit_original_response(embed=emb, view=None)

            else:

                emb = discord.Embed(title=f"Nothing was selected {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} Nothing has been selected to be blacklisted or removed.
                    {Emojis.dot_emoji} If you want to blacklist or remove items from the blacklist you can simply use this command again.""", color=bot_colour)
                await interaction.edit_original_response(embed=emb, view=None)





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

                emb = discord.Embed(title=f"No entry was found {Emojis.fail_emoji}", 
                    description=f"""No entry was found so one was created for your server. 
                    {Emojis.dot_emoji} The level system was also switched on automatically.
                    {Emojis.dot_emoji} If you want to disable it just use this command again""", color=error_red)
                await interaction.response.edit_message(embed=emb)

            else:

                if check_status[2] == "on":

                    new_status, status = "Switched off", "off"
                    opposite_status = "Switch on"

                elif check_status[2] == "off":

                    new_status, status = "Switch on", "on"
                    opposite_status = "Switched off"

                DatabaseUpdates.update_level_settings(guild_id=guild_id, level_status=status)
                        
                emb = discord.Embed(title=f"The level system has been {new_status}", 
                    description=f"""{Emojis.dot_emoji} If you want to {opposite_status} the level system just use this command again {Emojis.exclamation_mark_emoji}""", color=bot_colour)
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

                emb = discord.Embed(title=f"The role or level could not be overwritten {Emojis.fail_emoji}", 
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

                emb = discord.Embed(title=f"The level up channel could not be overwritten {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} The level up channel could not be overwritten because the process has expired.
                    {Emojis.dot_emoji} This happens when you wait too long to react to the button.
                    {Emojis.dot_emoji} You can simply run the command again if you still want to overwrite the level up channel {Emojis.exclamation_mark_emoji}""", color=error_red)
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
                description=f"{Emojis.dot_emoji} You have successfully canceled the overwriting of the level up channel",color = bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)
        
        else:
            
            await interaction.response.send_message(embed=no_permissions_emb ,view=None, ephemeral=True)



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

            DatabaseUpdates.manage_blacklist(guild_id=guild_id, operation="remove", table="level")

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
            
            channel, category, role, user = blacklist[0], blacklist[1], blacklist[2], blacklist[3] 

            emb = discord.Embed(title=f"Here you can see all the elements that are on the blacklist of the level system {Emojis.exclamation_mark_emoji}", 
                description=f"""Here are listed all the elements that are on the level system blacklist.""", color=bot_colour)
            emb.add_field(name="Channels:", value=f"{channel}", inline=False)
            emb.add_field(name="Categories:", value=f"{category}", inline=False)
            emb.add_field(name="Roles", value=f"{role}", inline=False)
            emb.add_field(name="Users", value=f"{user}", inline=False)
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
    def xp_generator(guild_id:int):

        settings = DatabaseCheck.check_level_settings(guild_id=guild_id)
        return settings[1]
    
    @staticmethod
    def xp_generator_global():
        xp = 20
        return xp
    
    @staticmethod
    def round_corner_mask(radius, rectangle, fill):
    
        bigsize = (rectangle.size[0] * 3, rectangle.size[1] * 3)
        mask_rectangle = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask_rectangle)
        draw.rounded_rectangle((0, 0)+bigsize, radius=radius, fill=fill, outline=None)
        mask = mask_rectangle.resize(rectangle.size, Image.ANTIALIAS)
        rectangle.putalpha(mask)
        return (rectangle, mask)

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

                        XP = self.xp_generator(guild_id=message.guild.id)
                        
                        xp_global = self.xp_generator_global()
                        user_xp_global = xp_global + check_if_exists[6]
                        user_has_xp = check_if_exists[3] + XP 
                                                                    
                        xp_need_next_level = 5 * (check_if_exists[2] ^ 2) + (50 * check_if_exists[2]) + 100 - check_if_exists[3]
                        final_xp = xp_need_next_level + check_if_exists[3]
                        
                        if user_has_xp >= final_xp:
                                                                        
                            new_level = check_if_exists[2] + 1    

                            try:
                                
                                # Updates the XP
                                DatabaseUpdates._update_user_stats_level(guild_id=message.guild.id, user_id=message.author.id, level=new_level)

                            except mysql.connector.Error as error:
                                print("parameterized query failed {}".format(error))
                                                                    
                            finally:   

                                # Checks if a level role or a level up channel is defined                                
                                level_role_check = DatabaseCheck.check_level_system_levelroles(guild_id=message.guild.id, needed_level=new_level)
                                levelup_channel_check = DatabaseCheck.check_level_settings(guild_id=message.guild.id)

                                if level_role_check:

                                    role_id, level_need = level_role_check[1], level_role_check[2]

                                else:

                                    role_id, level_need = None, None

                                if level_role_check != None and levelup_channel_check[3] != None:

                                    levelup_channel = bot.get_channel(levelup_channel_check[3])

                                    level_role = message.guild.get_role(role_id)
                                    await message.author.add_roles(level_role) 

                                    await levelup_channel.send(f"<@{message.author.id}> du hast die rolle <@&{role_id}> bekommen da du level **{level_need}** ereicht hast")
                                    await levelup_channel.send(f"Oh nice <@{message.author.id}> you have a new level your newlevel is {new_level}")
                                
                                elif levelup_channel_check[3] == None and level_role_check != None:
                                    
                                    level_role = message.guild.get_role(role_id)
                                    await message.author.add_roles(level_role)

                                    await message.channel.send(f"Oh nice <@{message.author.id}> you have a new level your newlevel is {new_level}")
                                    await message.channel.send(f"<@{message.author.id}> du hast die rolle <@&{role_id}> bekommen da du level **{level_need}** ereicht hast")

                                elif levelup_channel_check[3] == None and level_role_check == None:

                                    await message.channel.send(f"Oh nice <@{message.author.id}> you have a new level your newlevel is {new_level}") 

                                elif levelup_channel_check[3] != None and level_role_check == None:
                                        
                                    levelup_channel = bot.get_channel(levelup_channel_check[3])
                                    await levelup_channel.send(f"Oh nice <@{message.author.id}> you have a new level your newlevel is {new_level}")
                         
                        else:

                            try:

                                DatabaseUpdates._update_user_stats_level(guild_id=message.guild.id, user_id=message.author.id, xp=user_has_xp, whole_xp=user_xp_global)                       
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
    async def give_xp_slash(self, ctx:commands.Context, user:Option(discord.Member, description="Select a user who should receive the xp!"),
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

                    DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, xp=new_xp)
                        
                    emb = discord.Embed(title=f"You have successfully passed {user.name} to {xp} XP {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} You have transferred **{user.name}** {xp} XP **{user.names}** has from now on **{new_xp}** XP.
                        {Emojis.dot_emoji} If you want to remove **{user.name}** XP again use the:\n{remove_xp} command {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb)

                    if xp >= xp_need_next_level:

                        new_level = user_level + 1
                                            
                        DatabaseUpdates._update_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, level=new_level)
                        levelup_channel_check = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

                        if levelup_channel_check != None:

                            await ctx.send(f"Oh nice <@{user.id}> you have a new level, your newlevel is {new_level}")
                            
                        else:
                            
                            levelup_channel = bot.get_channel(levelup_channel_check[3])
                            await levelup_channel.send(f"Oh nice <@{user.id}> you have a new level, your newlevel is {new_level}")
                else:
        
                    emb = discord.Embed(title=f"The XP you want to give {user.name} is too high {Emojis.fail_emoji}", 
                        description=f"""{Emojis.dot_emoji} The XP you want to pass to **{user.name}** is too high.
                        {Emojis.dot_emoji} You can only give **{user.name}** a maximum of **{xp_need_next_level}** XP.""", color=error_red)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)
                
                emb = discord.Embed(title=f"The user was not found {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} No entry was found for **{user.name}**, so one was created.
                    {Emojis.dot_emoji} **{user.name}** now starts at level 0 with 0 xp""", color=error_red)
                await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-xp", description = "Remove a chosen amount of Xp from a user!")
    @commands.has_permissions(administrator = True)
    async def remove_xp_slash(self, ctx:commands.Context, user:Option(discord.Member, description="Choose a user from which you want to remove xp!"),
        xp:Option(int, description="Specify a quantity of Xp to be removed!")):

        user_id = user.id
        guild_id = ctx.guild.id
        user_name = user.name
            
        check_stats = DatabaseCheck.check_level_system_stats(guild_id=guild_id, user=user_id)

        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            if check_stats:
                
                user_xp = check_stats[3]
                new_xp = user_xp - xp 

                if xp > user_xp:
                            
                    emb = discord.Embed(title=f"The XP you want to remove from {user_name} is too high {Emojis.fail_emoji}", 
                        description=f"""{Emojis.dot_emoji} The XP you want to remove from **{user_name}** is too high.
                        {Emojis.dot_emoji} You can remove **{user_name}** only maximum **{user_xp}** XP.""", color=error_red)
                    await ctx.respond(embed=emb)

                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=guild_id, user_id=user_id, xp=new_xp)

                    emb = discord.Embed(title=f"You have successfully removed {user_name} {xp} XP {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} You have removed **{user_name}** {xp} XP **{user_name}** has **{new_xp}** XP from now on.
                        {Emojis.dot_emoji} If you want to give **{user_name}** XP again use the:\n{give_xp} command {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb)

            else:
                    
                DatabaseUpdates._insert_user_stats_level(guild_id=guild_id, user_id=user_id, user_name=user_name)
                    
                emb = discord.Embed(title=f"The user was not found {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} No entry was found for **{user_name}**, so one was created.
                    {Emojis.dot_emoji} **{user_name}** now starts at level 0 with 0 xp""", color=error_red)
                await ctx.respond(embed=emb)  


    @commands.slash_command(name = "give-levels", description = "Give a user a selected amount of levels!")
    @commands.has_permissions(administrator = True)
    async def give_level_slash(self, ctx:commands.Context, user:Option(discord.Member, description="Choose a user you want to give the levels to!"), 
        level:Option(int, description="Specify a set of levels that you want to assign!")):

        user_id = user.id
        guild_id = ctx.guild.id
        user_name = user.name

        check_stats = DatabaseCheck.check_level_system_stats(guild=guild_id, user=user_id)

        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            if check_stats:
                
                user_level = check_stats[2]
                new_level = user_level + level
                levels_to_maxlevel = 999 - level
                            
                if level > 999 or new_level >= 999:

                    emb = discord.Embed(title=f"The level you want to give {user_name} is too high {Emojis.fail_emoji}", 
                        description=f"""{Emojis.dot_emoji} The level you want to give **{user_name}** is too high because the maximum level is **999**.
                        {Emojis.dot_emoji} You can only give **{user_name}** a maximum {levels_to_maxlevel} level.""", color=error_red)
                    await ctx.respond(embed=emb)

                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=guild_id, user_id=user_id, level=new_level)

                    emb = discord.Embed(title=f"You have successfully added {user_name} {level} level {Emojis.succesfully_emoji}",
                        description=f"""{Emojis.dot_emoji} You gave **{user_name}** {level} level **{user_name}** now has **{new_level}** level.
                        {Emojis.dot_emoji} If you want to remove **{user_name}** level again use the:\n{remove_level} command {Emojis.exclamation_mark_emoji}""", colour=bot_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=guild_id, user_id=user_id, user_name=user_name)

                emb = discord.Embed(title=f"The user was not found {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} No entry was found for **{user_name}**, so one was created.
                    {Emojis.dot_emoji} **{user_name}** now starts at level 0 with 0 xp""", color=error_red)
                await ctx.respond(embed=emb)
                

    @commands.slash_command(name = "remove-level", description = "Remove a quantity of levels chosen by you!")
    @commands.has_permissions(administrator = True)
    async def remove_level_slash(self, ctx:commands.Context, user:Option(discord.Member, description="Select a user from whom you want to remove the level!"), 
        level:Option(int, description="Specify how many levels should be removed!")):

        user_id = user.id
        guild_id = ctx.guild.id
        user_name = user.name

        check_stats = DatabaseCheck.check_level_system_stats(guild_id=guild_id, user=user_id)
        
        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            if check_stats:

                user_level = check_stats[2]     
                new_level = user_level - level 

                if level > user_level:

                    emb = discord.Embed(title=f"The number of levels you want to remove {user_name} is too high {Emojis.fail_emoji}", 
                        description=f"""{Emojis.dot_emoji} The number of levels you want to remove from {user_name} is too high.
                        {Emojis.dot_emoji} You can remove **{user_name}** only up to **{user_level}** level.""", color=error_red)
                    await ctx.respond(embed=emb)

                
                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=guild_id, user_id=user_id,  level=new_level)

                    emb = discord.Embed(title=f"You have successfully removed {user_name} {level} level {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} You have removed **{user_name}** {level} level **{user_name}** is now level **{new_level}**
                        {Emojis.dot_emoji} If you want to give **{user_name}** level again use the:\n{give_level} command {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=guild_id, user_id=user_id, user_name=user_name)
                
                emb = discord.Embed(title=f"The user was not found {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} No entry was found for **{user_name}**, so one was created.
                    {Emojis.dot_emoji} **{user_name}** now starts at level 0 with 0 xp""", color=error_red)
                await ctx.respond(embed=emb)    
    

    @commands.slash_command(name = "reset-level-system", description = "Reset all levels and xp of everyone!")
    @commands.has_permissions(administrator = True)
    async def reset_levels_slash(self, ctx:commands.Context):

        guild_id = ctx.guild.id

        check_stats = DatabaseCheck.check_level_system_stats(guild_id=guild_id)

        if check_stats:

            emb = discord.Embed(title="Are you sure you want to reset the level system?", 
                description=f"""{Emojis.help_emoji} With the buttuns you can confirm your decision!
                {Emojis.dot_emoji} If you press the **Yes button** all user stats will be deleted.
                {Emojis.dot_emoji} If you press the **No button** the process will be aborted.""", color=bot_colour)
            await ctx.respond(embed=emb, view=ResetLevelStatsButton())

        else:
            
            emb = discord.Embed(title=f"No data found for this server {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} No data was found for this server, so nothing could be deleted.
                {Emojis.help_emoji} Data is created automatically as soon as messages are sent and the level system is switched on.""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "rank", description = "Shows you the rank of a user in the level system!")
    async def rank_slash(self, ctx:commands.Context, user:Option(discord.Member, description="Look at the rank of others!")):

        count = 0
        rank = 0
        connection_to_db_level = DatabaseSetup.db_connector()
        my_cursor = connection_to_db_level.cursor()

        error_emb = discord.Embed(title=f"The user was not found {Emojis.fail_emoji}", 
            description=f"""{Emojis.dot_emoji} Der User wurde nich gefunden es kann sein das er noch nicht am level system teilimmt.
            {Emojis.help_emoji} Man nimmt erst am level system teil wemm man mindestens eine Nachricht in einen Channel gesendet hat der auf keiner Blacklist steht {Emojis.exclamation_mark_emoji}""", color=error_red)

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
            mask = mask.resize(profile.size, Image.ANTIALIAS)
            profile.putalpha(mask)

            background.paste(profile, (47, 39), mask=mask)

            draw = ImageDraw.Draw(background)

            bar_offset_x = 304
            bar_offset_y = 179
        
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
            progress_bar = Image.new("RGBA", ((bar_offset_x_1 - bar_offset_x), 36), background_color)
            progress_bar = self.round_corner_mask(radius=50, rectangle=progress_bar, fill=255)
            background.paste(progress_bar[0], (bar_offset_x, bar_offset_y), progress_bar[1])

            xp_display_line = Image.new(mode="RGBA", size=(340, 33), color=(0, 0, 0))
            xp_display_line = self.round_corner_mask(radius=50, rectangle=xp_display_line, fill=160)
            offset_y = 247
            background.paste(xp_display_line[0], (304, offset_y), xp_display_line[1])

            # Displays the level of the user
            data_display = Image.new(mode="RGBA", size=(200, 33), color=(0, 0, 0))
            data_display = self.round_corner_mask(radius=50, rectangle=data_display, fill=160)
            background.paste(data_display[0], (655, offset_y), data_display[1])

            draw.text((304, 97), user.name, font=big_font, fill=(255, 255, 255))
            draw.text((315, 249), f"{xp_have:,} / {final_xp:,} XP", font=small_font, fill=(255, 255, 255))
            draw.text((665, offset_y), f"#{rank} Lvl {check_user[2]}", font=small_font, fill=(255, 255, 255))

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

        guild_id = ctx.guild.id

        leaderboard_levels = "SELECT userId, userLevel, userXp FROM LevelSystemStats WHERE guildId = %s ORDER BY userLevel DESC, userXp DESC"
        leaderboard_levels_values = [guild_id]
        my_cursor.execute(leaderboard_levels, leaderboard_levels_values)

        leaderboard_members =  my_cursor.fetchall()
        c = []
        for i, pos in enumerate(leaderboard_members, start=1):
            member_id, lvl, xp = pos
            
            if i <= 10:

                c.append(f"{i}. <@{member_id}>, level: {lvl}, XP: {xp}")
            
        level_roles_mention_end = '\n'.join(c)

        DatabaseSetup.db_close(cursor=my_cursor, db_connection=leaderboard_connect)

        emb = discord.Embed(title="leaderboard", description=f"leaderboard participants:\n\n{level_roles_mention_end}", color=discord.Colour.random())
        emb.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.respond(embed=emb)

               

#############################################  Level system Settings  #####################################################    


    @commands.slash_command(name = "level-system-settings", description = "Set the level system freely!")
    @commands.has_permissions(administrator = True)
    async def level_system_settings(self, ctx:commands.Context):

        guild_id = ctx.guild.id

        level_settings = DatabaseCheck.check_level_settings(guild_id=guild_id)

        if level_settings:

            if level_settings[2] == "on":
                active_deactive = "Enabled "
            elif level_settings[2] == "off":
                active_deactive = "Deactivated"

            emb = discord.Embed(title=f"Here you can see all the settings of the level system {Emojis.help_emoji}", 
                description=f"With the lower button you can set the level system, You can activate or deactivate. At the moment it is: **{active_deactive}**",color=bot_colour)
            await ctx.respond(embed=emb, view=LevelSystemSettings())

        else:

            DatabaseUpdates._create_bot_settings(guild_id=guild_id)

            emb = discord.Embed(title="No entry found", 
                description="No entry was found so one was created the level system was also activated immediately", color=error_red)
            await ctx.respond(embed=emb)

    

#################################################  Level Blacklist settings  ###############################################


    @commands.slash_command(name = "add-channel-level-blacklist", description = "Exclude channels from the level system!")
    @commands.has_permissions(administrator = True)
    async def add_chanels_level_blacklist(self, ctx:commands.Context, channel:Option(Union[discord.VoiceChannel, discord.TextChannel], description="Select a channel that you want to exclude from the level system!")):
        
        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, channel_id=channel.id, table="level")
        check_blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, table="level")
        show_blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)

        check_channel = [f"{Emojis.help_emoji} Die Kategorie von diesen Channel ist bereits auf der Blacklist" if bot.get_channel(i).category.id == i[2] else None for i in check_blacklist]

        if check_channel != None:

            emb = discord.Embed(title=check_channel, 
                description=f"""{Emojis.dot_emoji} Der channel {channel.mention} ist in einer Kategorie gelistet die auf der Blacklist steht.
                {Emojis.dot_emoji} Daher ist er bereits vom Level system ausgeschlossen.
                {Emojis.dot_emoji} Hier shist du auch welche Kategorien schon auf der Blacklist stehen:\n\n{show_blacklist[1]}""")
            await ctx.respond(embed=emb)
            return
        
        if blacklist:

            emb = discord.Embed(title=f"{Emojis.help_emoji} This channel is already on the blacklist", 
                description=f"""The following channels are on the blacklist:\n\n{show_blacklist[0]}
                If you want to remove channels from the blacklist execute this command:\n{remove_blacklist_level_channel}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", channel_id=channel.id, table="level")

            emb = discord.Embed(title=f"This channel was successfully blacklisted {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The channel <#{channel.id}> was successfully blacklisted.
                {Emojis.dot_emoji} If you want to remove it again use this command:\n{remove_blacklist_level_channel}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-channel-level-blacklist", description = "Remove a channel from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_channel_blacklist(self, ctx:commands.Context, channel:Option(Union[discord.TextChannel, discord.VoiceChannel], description="Select a channel to remove from the blacklist!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, channel_id=channel.id, table="level")

        if blacklist:
                
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", channel_id=channel.id, table="level")

            emb = discord.Embed(title=f"The channel was removed from the blacklist {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The channel <#{channel.id}> has been successfully removed from the blacklist if you want to add it again use the: {add_blacklist_level_channel} command.
                {Emojis.dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} command""", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:
            
            blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"{Emojis.help_emoji} This channel is not on the blacklist", 
                description=f"""{Emojis.dot_emoji} The channel <#{channel.id}> is not blacklisted.
                The following channels are blacklisted:\n\n{blacklist[0]}""", color=bot_colour)
            await ctx.respond(embed=emb)
        
    
    @commands.slash_command(name = "add-category-level-blacklist", description = "Exclude categories from the level system and all channels that belong to them!")
    @commands.has_permissions(administrator = True)
    async def add_category_blacklist(self, ctx:commands.Context, category:Option(discord.CategoryChannel, description="Select a category that you want to exclude from the level system!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, category_id=category.id, table="level")
        check_blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, table="level")

        if blacklist:
            
            blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)
                
            emb = discord.Embed(title=f"{Emojis.help_emoji} This category is already on the blacklist", 
                description=f"""The following categories are on the blacklist:\n\n{blacklist[1]}
                If you want to remove categories from the blacklist execute this command:\n{remove_blacklist_level_category}""", color=bot_colour)
            await ctx.respond(embed=emb)
            return

        filtered_list = []
        for _, channel, _, _, _ in check_blacklist:

            if channel:

                if bot.get_channel(channel).category.id == category.id:

                    DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", channel_id=channel, table="level")
                    filtered_list.append(f"{Emojis.dot_emoji} <#{channel}>\n")

        if filtered_list != []:  
            
            channel_list = "\n".join(filtered_list)
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", category_id=category.id, table="level")
                
            emb = discord.Embed(title=f"{Emojis.help_emoji} {'One channel' if len(filtered_list) == 1 else 'Several channels'} in this category is already blacklisted", 
                description=f"""{Emojis.dot_emoji} The following {'channel is' if len(filtered_list) == 1 else 'channels are'} already blacklisted \n\n{channel_list}
                    {Emojis.arrow_emoji} Therefore {'this' if len(filtered_list) == 1 else 'these'} channel will be removed from the blacklist and the category will be added instead.
                    This excludes all channels in the category from the level system.""", color=bot_colour)
            await ctx.respond(embed=emb) 

        else:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", category_id=category.id, table="level")
            
            emb = discord.Embed(title=f"This category was successfully blacklisted {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The category <#{category.id}> was successfully blacklisted.
                {Emojis.dot_emoji} If you want to remove them again use this command:\n{remove_blacklist_level_category}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-category-level-blacklist", description = "Remove categories from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_category_blacklist(self, ctx:commands.Context, category:Option(discord.CategoryChannel, description="Select a category to remove from the blacklist!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, category_id=category.id, table="level")

        if blacklist:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", category_id=category.id, table="level")
            
            emb = discord.Embed(title=f"The category was removed from the blacklist {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The category <#{category.id}> has been successfully removed from the blacklist if you want to add it again use the: {add_blacklist_level_category} command.
                {Emojis.dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} comamnd""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"{Emojis.help_emoji} This category is not on the blacklist", 
                description=f"""{Emojis.dot_emoji} The category <#{category.id}> is not on the blacklist.
                The following categories are blacklisted:\n\n{blacklist[1]}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "add-role-level-blacklist", description = "Choose a role that you want to exclude from the level system!")
    @commands.has_permissions(administrator = True)
    async def add_role_blacklist(self, ctx:commands.Context, role:Option(discord.Role, description="Select a role that you want to exclude from the level system!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, role_id=role.id, table="level")

        if blacklist:
     
            blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"{Emojis.help_emoji} This role is already on the blacklist", 
                description=f"""The following roles are on the blacklist:\n\n{blacklist[2]}
                If you want to remove roles from the blacklist execute this command:\n{remove_blacklist_level_role}""", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", role_id=role.id, table="level")
            
            emb = discord.Embed(title=f"This role has been successfully blacklisted {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The role <@&{role.id}> has been successfully blacklisted.
                {Emojis.dot_emoji} If you want to remove them again use this command:\n{remove_blacklist_level_role}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-role-level-blacklist", description = "Remove a role from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_role_blacklist(self, ctx:commands.Context, role:Option(discord.Role, description="Select a role you want to remove from the blacklist!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, role_id=role.id, table="level")

        if blacklist:

            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", role_id=role.id, table="level")
            
            emb = discord.Embed(title=f"The role was removed from the blacklist {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The role <@&{role.id}> has been successfully removed from the blacklist if you want to add it again use the: {add_blacklist_level_role} command.
                {Emojis.dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} comamnd""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"{Emojis.help_emoji} This role is not on the blacklist", 
                description=f"""{Emojis.dot_emoji} The role <@&{role.id}> is not blacklisted.
                The following roles are blacklisted:\n\n{blacklist[2]}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name= "add-user-level-blacklist", description = "Choose a user that you want to exclude from the level system!")
    @commands.has_permissions(administrator = True)
    async def add_user_level_blacklsit(self, ctx:commands.Context, user:Option(discord.User, description="Select a user that you want to exclude from the level system!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, user_id=user.id, table="level")

        if user.bot:
            await ctx.respond(embed=user_bot_emb, view=None)
        
        else:

            if blacklist:

                blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)

                emb = discord.Embed(title=f"{Emojis.help_emoji} This user is already on the blacklist", 
                    description=f"""The following users are on the blacklist:\n\n{blacklist[3]}
                    If you want to remove users from the blacklist execute this command:\n{remove_blacklist_level_user}""", color=bot_colour)
                await ctx.respond(embed=emb)

            else:   

                DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", user_id=user.id, table="level")

                emb = discord.Embed(title=f"This user was successfully blacklisted {Emojis.succesfully_emoji}", 
                    description=f"""{Emojis.dot_emoji} The user <@{user.id}> was successfully blacklisted.
                    If you want to remove it again use this command:\n{remove_blacklist_level_user}""", color=bot_colour)
                await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-user-level-blacklist", description="Remove a user from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_user_level_blacklist(self, ctx:commands.Context, user:Option(discord.User, description="Select a user you want to remove from the blacklist!")):
        
        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, user_id=user.id, table="level")

        if blacklist:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", user_id=user.id, table="level")

            emb = discord.Embed(title=f"The user was removed from the blacklist {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The user <@{user.id}> has been successfully removed from the blacklist if you want to add him again use the: {add_blacklist_level_user} command.
                {Emojis.dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} comamnd""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"{Emojis.help_emoji} This user is not on the blacklist.",
                description=f"""The user <@{user.id}> is not on the blacklist.
                The following users are on the blacklist:\n\n{blacklist[3]}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "reset-level-blacklist", description="Reset the blacklist of the level system and remove all entries!")
    @commands.has_permissions(administrator = True)
    async def reset_blacklist(self, ctx:commands.Context):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, table="level")

        if blacklist:

            view = ResetBlacklistLevelButton()
            view.add_item(ShowBlacklistLevelSystemButton())

            emb = discord.Embed(title="Are you sure you want to remove everything from the blacklist?", 
                description=f"""{Emojis.help_emoji} With the buttuns you can confirm your decision!!
                {Emojis.dot_emoji} If you press the **Yes button** all channels, categories, users and roles will be removed from the blacklist.
                {Emojis.dot_emoji} If you press the **No button** the process will be aborted.
                {Emojis.dot_emoji} The **Shows all elements button** shows you what is currently on the blacklist.""", color=bot_colour)
            await ctx.respond(embed=emb, view=view)
        
        else:

            emb = discord.Embed(title=f"There is nothing on the blacklist {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} The blacklist could not be reset because nothing is stored on it.
                {Emojis.dot_emoji} If you want to blacklist something use one of these commands:
                
                {Emojis.arrow_emoji} {add_blacklist_level_channel}
                {Emojis.arrow_emoji} {add_blacklist_level_category}
                {Emojis.arrow_emoji} {add_blacklist_level_role}
                {Emojis.arrow_emoji} {add_blacklist_level_user}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "manage-level-blacklist", description = "Add or remove anything you want from the blacklist!")
    async def manage_level_blacklist(self, ctx:commands.Context):

        emb = discord.Embed(title=f"Welcome to the blacklist manager for the level system {Emojis.settings_emoji}", 
            description=f"""{Emojis.help_emoji} With the two buttons you can select whether you want to put something on the blacklist or remove something!
            {Emojis.dot_emoji} As soon as you have selected something, select menus are displayed.
            {Emojis.dot_emoji} With these you can select what you want to blacklist or remove.""", color=bot_colour)
        await ctx.respond(embed=emb, view=BlacklistManagerButtons())


   
    @commands.slash_command(name = "show-level-blacklist", description = "Shows you everything that is blacklisted!")
    async def show_blacklist(self, ctx:commands.Context):

        blacklist = CheckLevelSystem.show_blacklist_level(guild_id=ctx.guild.id)
        channel, category, role, user = blacklist[0], blacklist[1], blacklist[2], blacklist[3] 

        emb = discord.Embed(title=f"Here you can see the complete level system blacklist", 
            description=f"""Here you can see everything that is on the level system blacklist:{Emojis.exclamation_mark_emoji}
            """, color=bot_colour)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Channels on the Blacklist", value=f"{channel}", inline=False)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Categories on the Blacklist", value=f"{category}", inline=False)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Roles on the Blacklist", value=f"{role}", inline=False)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Users on the Blacklist", value=f"{user}", inline=False)
        await ctx.respond(embed=emb)



#############################################  level roles settings  #################################################

    
    @commands.slash_command(name = "add-level-role", description = "Add a role that you get from a certain level!")
    @commands.has_permissions(administrator = True)
    async def add_level_role(self, ctx:commands.Context, role:Option(discord.Role, description = "Select a role that you want to assign from a certain level onwards"),
        level:Option(int, description = "Enter a level from which this role should be assigned")):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, level_role=role.id, needed_level=level, status="check")

        emb_level_0 = discord.Embed(title=f"The level you want to set is 0 {Emojis.fail_emoji}", 
            description=f"""{Emojis.dot_emoji} The level to vest a level role must be at least **1**.""", color=error_red)
        emb_higher = discord.Embed(title=f"The level you want to set for the level role is too high {Emojis.fail_emoji}", 
            description=f"""{Emojis.dot_emoji} The level you want to set for the level role is too high you can only set a value that is below or equal to **999**.""", color=error_red)

        if role.permissions.administrator:

            emb = discord.Embed(title=f"This role cannot be assigned as a level role {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} This role has administations rule therefore it cannot be assigned as a level role {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            if level_roles == None:
                
                if level <= 999:
                            
                    DatabaseUpdates._insert_level_roles(guild_id=ctx.guild.id, role_id=role.id, level=level, guild_name=ctx.guild.name)

                    emb = discord.Embed(title=f"The role was assigned successfully {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} The role {role.mention} was successfully assigned to the level {level}.
                        {Emojis.dot_emoji} As soon as a user reaches {level} he gets the <@&{role.mention}> role. {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb)

                await ctx.respond(embed=emb_level_0) if level == 0 else None

                await ctx.respond(embed=emb_higher) if  level > 999 else None 

            else:

                check_same = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, level_role=role.id, needed_level=level)
                    
                if check_same:

                    same_emb = discord.Embed(title=f"This role has already been set at this level {Emojis.fail_emoji}",
                        description=f"""{Emojis.dot_emoji} The role {role.mention} is already assigned to the level {level}.
                        {Emojis.dot_emoji} If you want to change it you can assign this role to another level or another role to this level {Emojis.exclamation_mark_emoji}""", color=error_red)
                    await ctx.respond(embed=same_emb)

                else:
                    
                    if role.id == level_roles[1]:

                        level_needed = level_roles[2]
            
                        emb = discord.Embed(title=f"This role is already assigned {Emojis.fail_emoji}", 
                            description=f"""{Emojis.dot_emoji} Do you want to override the required level for this role? 
                            {Emojis.dot_emoji} The role {role.mention} is currently assigned at level **{level_needed}**.
                            {Emojis.dot_emoji} If you want to override the required level for this role select the yes buttons otherwise the no button {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                        await ctx.respond(embed=emb, view=LevelRolesButtons(role_id=role.id, role_level=level, status="role"))
        
                    elif level == level_roles[2]:
                        
                        level_role = level_roles[1]

                        emb = discord.Embed(title=f"This level is already assigned {Emojis.fail_emoji}", 
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

            emb = discord.Embed(title=f"This role is not defined as a level role {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} This role cannot be removed because it is not set as a level role.
                {Emojis.dot_emoji} Here you can see all the level rolls.\n\n{result}""", color=error_red)
            await ctx.respond(embed=emb)



    @commands.slash_command(name = "show-all-level-roles", description = "View all rolls that are available with a level!")
    async def show_all_level_roles(self, ctx:commands.Context):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild_id=ctx.guild.id, status="level_role")
        
        if level_roles:
            
            result_strings = [f"{Emojis.dot_emoji} <@&{i[1]}> you get from level: {i[2]}" for i in level_roles]
            result = '\n'.join(result_strings)
            
            emb = discord.Embed(title="Here you can find all level roles", 
                description=f"{Emojis.help_emoji} Here you can see all level rolls sorted by level in descending order:\n\n {result}", color=bot_colour)
            await ctx.respond(embed=emb)

        else:
            emb = discord.Embed(title=f"No level rolls have been added yet", 
                description=f"{Emojis.help_emoji} There are no level rolls added yet if you want to add some use the {add_level_role} command", color=bot_colour)
            await ctx.respond(embed=emb)

       
    
#############################################  Level up channel settings  #################################


    @commands.slash_command(nanme = "set-level-up-channel", description = "Set a channel for the level up notifications!")
    @commands.has_permissions(administrator = True)
    async def set_levelup_channel(self, ctx:commands.Context, channel:Option(discord.TextChannel, description="Select a channel in which the level up message should be sent")):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settings[3]:
       
            if channel.id == check_settings[3]:

                emb = discord.Embed(title=f"This channel is already assigned as level up channel {Emojis.fail_emoji}", 
                    description=f"{Emojis.dot_emoji} This channel is already set as a level up channel if you want to remove it as a level up channel use the:\n{disable_level_up_channel} command {Emojis.exclamation_mark_emoji}", color=error_red)
                await ctx.respond(embed=emb)

            else:

                emb = discord.Embed(title=f"There is already a level up channel assigned {Emojis.fail_emoji}", 
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
            
            emb = discord.Embed(title=f"No level up channel was assigned {Emojis.help_emoji}", 
                description=f"{Emojis.dot_emoji} There was no level up channel assigned so none could be removed.", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "show-level-up-channel", description = "Let them show the current level up channel!")
    async def show_levelup_channel(self, ctx:commands.Context):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)
        
        if check_settings[3]:
        
            emb = discord.Embed(title=f"Here you can see the current level up channel {Emojis.help_emoji}", 
                description=f"""{Emojis.dot_emoji} The current level up channel is <#{check_settings[3]}> all level up notifications are sent to this channel.""", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:
            
            emb = discord.Embed(title=f"No level up channel has been set {Emojis.help_emoji}", 
                description=f"""{Emojis.dot_emoji} No level up channel has been set if you want to set one use that:\n{add_level_up_channel} command""", color=bot_colour)
            await ctx.respond(embed=emb)



##########################################  Set xp rate system  ###################################


    @commands.slash_command(name = "set-xp-rate", description = "Set how much XP will be awarded per message!")
    @commands.has_permissions(administrator = True)
    async def set_xp_rate(self, ctx:commands.Context, xp:Option(int, description="Set a base value how much XP you earn per message!")):

        if xp <= 0:

            emb = discord.Embed(title=f"The xp amount you want to set is too low {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} The XP amount you get per message as a reward is too low it must be at least 1!""", color=error_red)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, xp_rate=xp)

            emb = discord.Embed(title=f"You have successfully set the xp to be assigned per message {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The xp to be assigned per message has been set to **{xp}**. 
                {Emojis.help_emoji} From now on every message will be rewarded with **{xp}** XP {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "set-xp-rate-back-to-default", description = "Set the XP you get per message back to default settings!")
    @commands.has_permissions(administrator = True)
    async def set_xp_rate_default(self, ctx:commands.Context):
        
        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settings[1] == 20:

            emb = discord.Embed(title=f"The xp quantity is already set to the default settings {Emojis.help_emoji}", 
                description=f"{Emojis.dot_emoji} The xp amount assigned for each message is already at the default value of **20**.", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, back_to_none=0)

            emb = discord.Embed(title=f"The XP quantity for messages was successfully reset {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The XP assigned for each message has been set back to **20**.""", color=bot_colour)
            await ctx.respond(embed=emb)
        
       
    @commands.slash_command(name = "show-xp-rate", description = "Let us show you how much xp you currently get per message!")
    @commands.has_permissions(administrator = True)
    async def show_xp_rate(self, ctx:commands.Context):
        
        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        emb = discord.Embed(title=f"Here you can see how much XP you get per message {Emojis.help_emoji}",
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
            bonus_percentage = percentage[4]
        
        return bonus_percentage
    

    @commands.slash_command(name = "add-bonus-xp-channel")
    @commands.has_permissions(administrator = True)
    async def add_bonus_xp_channel(self, ctx:commands.Context, 
        channel:Option(Union[discord.TextChannel, discord.VoiceChannel], description="Choose a channel that is rewarded with extra xp!"), 
        bonus:Option(int, description="Choose how much more XP to give in percent (if nothing is specified the default value is used!)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) = None):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, channel_id=channel.id)

        if check_list: 

            emb = discord.Embed(title=f"Dieser Channel wurde bereits als XP bonus channel festgelegt {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} Der channel <#{channel.id}> wurde bereits als XP bonus channel festgelegt deshalb werden alle aktivitäten in diesen channel mit extra XP belohnt""", color=error_red)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="add", channel_id=channel.id, bonus=bonus)

            emb = discord.Embed(title=f"Der bonus xp channel wurde erfolgreich festgelegt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Der channel <#{channel.id}> wurde als XP bonus channel festgelegt.
                {Emojis.dot_emoji} Nachrichten oder aktivitäten in diesen Channel werden mit **{self.check_bonus_percentage(bonus=bonus, guild_id=ctx.guild.id)} %** mehr XP belohnt""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-bonus-xp-channel")
    @commands.has_permissions(administrator = True)
    async def remove_bonus_xp_channel(self, ctx:commands.Context, channel:Option(Union[discord.TextChannel, discord.VoiceChannel], description="Wähle einen channel den du als XP bonus channel entfenren willst!")):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, channel_id=channel.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove", channel_id=channel.id)

            emb = discord.Embed(title=f"Der channel wurde erfolgreich als bonus xp channel entfernt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Der channel <#{channel.id}> wurde als XP bonus channel entfernt.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            bonus_xp_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
            
            bonus_xp_channels = [f"{Emojis.dot_emoji} {i}" for i in bonus_xp_list[1]] if bonus_xp_list else ["Es wurde kein channel als bonus XP channel festgelegt"]
            bonus_channels = "\n".join(bonus_xp_channels)

            emb = discord.Embed(title=f"{Emojis.help_emoji} Dieser channel wurde nicht als bonus XP channel festgelegt.", 
                description=f"""{Emojis.dot_emoji} Der channel <#{channel.id}> wurde nicht als bonus XP channel festgelegt und kann daher nicht entfernt werden.
                Hier sihst du alle channel die als bonus XP channel festgelegt wurden:\n\n{bonus_channels}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "add-bonus-xp-category")
    @commands.has_permissions(administrator = True)
    async def add_bonus_xp_category(self, ctx:commands.Context, 
        category:Option(discord.CategoryChannel, description="Wähle eine Kategorie in der alle aktivitäten in allen channel mit extra xp belohnt werden!"),
        bonus:Option(int, description="Choose how much more XP to give in percent (if nothing is specified the default value is used!)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) = None):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, category_id=category.id)

        if check_list: 

            emb = discord.Embed(title=f"{Emojis.help_emoji} Diese Category wurde bereits als XP bonus Category festgelegt.", 
                description=f"""{Emojis.dot_emoji} Die Category <#{category.id}> ist als XP bonus Category festgelegt deshalb werden alle aktivitäten in allen channeln der Category mit extra XP belohnt.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="add", category_id=category.id, bonus=bonus)

            emb = discord.Embed(title=f"Die bonus xp Category wurde erfolgreich festgelegt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Die Category <#{category.id}> wurde als XP bonus Category festgelegt.
                {Emojis.dot_emoji} Nachrichten oder aktivitäten in dieser Category werden mit **{self.check_bonus_percentage(bonus=bonus, guild_id=ctx.guild.id)} %** mehr XP belohnt.""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-bonus-xp-category")
    @commands.has_permissions(administrator = True)
    async def remove_bonus_xp_category(self, ctx:commands.Context, category:Option(discord.CategoryChannel, description="Wähle eine category die du als XP bonus category entfenren willst!")):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, category_id=category.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove", category_id=category.id)

            emb = discord.Embed(title=f"Die category wurde erfolgreich als bonus xp category entfernt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Die category <#{category.id}> wurde als XP bonus category entfernt.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            bonus_xp_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
            
            bonus_xp_categories = [f"{Emojis.dot_emoji} {i}" for i in bonus_xp_list[2]] if bonus_xp_list else ["Es wurde keine category als bonus XP category festgelegt"]
            bonus_categories = "\n".join(bonus_xp_categories)

            emb = discord.Embed(title=f"{Emojis.help_emoji} Diese category wurde nicht als bonus XP category festgelegt.", 
                description=f"""{Emojis.dot_emoji} Die category <#{category.id}> wurde nicht als bonus XP category festgelegt und kann daher nicht entfernt werden.
                Hier sihst du alle category die als bonus XP categorien festgelegt wurden:\n\n{bonus_categories}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "add-bonus-xp-role", description = "Füge eine rolle als bonus XP rolle hinzu und lege deren XP bonus fest!")
    @commands.has_permissions(administrator = True)
    async def add_bonus_xp_role(self, ctx:commands.Context, 
        role:Option(discord.Role, description="Wähle eine rolle das jeder der diese rolle hat extra xp erhählt!"),
        bonus:Option(int, description="Choose how much more XP to give in percent (if nothing is specified the default value is used!)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) = None):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, role_id=role.id)

        if check_list: 

            emb = discord.Embed(title=f"{Emojis.help_emoji} Diese rolle wurde bereits als XP bonus rolle festgelegt.", 
                description=f"""{Emojis.dot_emoji} Die rolle <@&{role.id}> ist als XP bonus rolle festgelegt deshalb werden alle aktivitäten von benutzern mit dieser rolle mit extra XP belohnt.""", color=bot_colour)
            await ctx.respond(embed=emb)
            
        else:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="add", role_id=role.id, bonus=bonus)

            emb = discord.Embed(title=f"Die bonus xp rolle wurde erfolgreich festgelegt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Die rolle <@&{role.id}> wurde als XP bonus rolle festgelegt.
                {Emojis.dot_emoji} Nachrichten oder aktivitäten von nutzern mit dieser Rolle werden mit **{self.check_bonus_percentage(bonus=bonus, guild_id=ctx.guild.id)} %** mehr XP belohnt""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-bonus-xp-role", description = "Entferne eine rolle als bonus XP rolle!")
    @commands.has_permissions(administrator = True)
    async def remove_bonus_xp_role(self, ctx:commands.Context, role:Option(discord.Role, description="Wähle eine rolle den du als XP bonus rolle entfenren willst!")):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, role_id=role.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove", role_id=role.id)

            emb = discord.Embed(title=f"Die role wurde erfolgreich als bonus xp role entfernt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Die role <@&{role.id}> wurde als XP bonus role entfernt.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            bonus_xp_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
            
            bonus_xp_roles = [f"{Emojis.dot_emoji} {i}" for i in bonus_xp_list[3]] if bonus_xp_list else ["Es wurde keine role als bonus XP role festgelegt"]
            bonus_roles = "\n".join(bonus_xp_roles)

            emb = discord.Embed(title=f"{Emojis.help_emoji} Diese role wurde nicht als bonus XP role festgelegt.", 
                description=f"""{Emojis.dot_emoji} Die role <@&{role.id}> wurde nicht als bonus XP role festgelegt und kann daher nicht entfernt werden.
                Hier sihst du alle rollen die als bonus XP role festgelegt wurden:\n\n{bonus_roles}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "add-bonus-xp-user", description = "Füge einen user als bonus XP user hinzu und lege dessen XP bonus fest!")
    @commands.has_permissions(administrator = True)
    async def add_bonus_xp_user(self, ctx:commands.Context, 
        user:Option(discord.User, description="Wähle einen user der für jede nachricht oder aktivität extra XP erhählt!"),
        bonus:Option(int, description="Choose how much more XP to give in percent (if nothing is specified the default value is used!)", max_value = 100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) = None):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, user_id=user.id)

        if check_list: 

            emb = discord.Embed(title=f"{Emojis.help_emoji} Dieser user wurde bereits als XP bonus user festgelegt.", 
                description=f"""{Emojis.dot_emoji} Der user <@{user.id}> ist als XP bonus user festgelegt deshalb werden alle aktivitäten von <@{user.id}> mit extra XP belohnt.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="add", user_id=user.id, bonus=bonus)

            emb = discord.Embed(title=f"Der bonus xp user wurde erfolgreich festgelegt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Der user <@{user.id}> wurde als XP bonus user festgelegt.
                {Emojis.dot_emoji} Nachrichten oder aktivitäten von <@{user.id}> werden mit **{self.check_bonus_percentage(bonus=bonus, guild_id=ctx.guild.id)} %** mehr XP belohnt""", color=bot_colour)
            await ctx.respond(embed=emb)

        
    @commands.slash_command(name = "remove-bonus-xp-user", description = "Entferne einen user als bonus XP user!")
    @commands.has_permissions(administrator = True)
    async def remove_bonus_xp_user(self, ctx:commands.Context, user:Option(discord.User, description="Wähle einen user den du als XP bonus user entfenren willst!")):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id, user_id=user.id)

        if check_list:

            DatabaseUpdates.manage_xp_bonus(guild_id=ctx.guild.id, operation="remove", user_id=user.id)

            emb = discord.Embed(title=f"Der user {user.name} wurde erfolgreich als bonus xp user entfernt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Der user <@{user.id}> wurde als XP bonus user entfernt.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            bonus_xp_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
            
            bonus_xp_user = [f"{Emojis.dot_emoji} {i}" for i in bonus_xp_list[4]] if bonus_xp_list else ["Es wurde kein user als bonus XP user festgelegt"]
            bonus_user = "\n".join(bonus_xp_user)

            emb = discord.Embed(title=f"{Emojis.help_emoji} Der user {user.name} wurde nicht als bonus XP user festgelegt.", 
                description=f"""{Emojis.dot_emoji} Der user <@{user.id}> wurde nicht als bonus XP user festgelegt und kann daher nicht entfernt werden.
                Hier sihst du alle user die als bonus XP user festgelegt wurden:\n\n{bonus_user}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "show-bonus-xp-list", description = "Lass dir alles anzeigen was auf der bonus xp list steht!")
    @commands.has_permissions(administrator = True)
    async def show_bonus_xp_list(self, ctx:commands.Context):

        check_list = DatabaseCheck.check_xp_bonus_list(guild_id=ctx.guild.id)
        check_bonus = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)
        bonus = check_bonus[4]

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


    @commands.slash_command(name = "set-bonus-xp-percentage", description = "Set a default percentage for the bonus XP system (this is set to 10% by default)!")
    async def set_bonus_xp_percentage(self, ctx:commands.Context, percentage:Option(int, description="Specify a percentage to be used as the default percentage for the bonus XP system!",max_value=100, choices = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settings[4] == percentage:

            emb = discord.Embed(title=f"{Emojis.help_emoji} Der aktuelle Prozentwert ist gleich mit den den du gerade hinzufügen möchtest", 
                description=f"""{Emojis.dot_emoji} Der aktulle Prozentwert für das bonus XP system liegt bei **{check_settings[4]} %**""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, percentage=percentage)

            emb = discord.Embed(title=f"Der standart Prozentsatz für das bonus XP system wurde erfolgteich zugewiesen {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Der stnadart Prozentsatz für das bonus XP system wurde auf **{percentage} %** gesetzt!
                {Emojis.help_emoji} Dieser Prozentsatz gilt jetzt für alle channel, kategorien, rollen und user die teil des bonus XP systems sind.
                Dieser Prozentsatz wird nun immer zu den erhaltenen XP dazugerechnet {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "set-bonus-xp-percentage-default", description = "Set the percentage value for the bonus XP system back to the default value!")
    async def set_bonus_xp_percentage_default(self, ctx:commands.Context):
        
        check_settigns = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if check_settigns[4] == 10:

            emb = discord.Embed(title=f"{Emojis.help_emoji} Der stanfart Prozentwert für das bonus XP system ist bereits auf den standart wert", 
                description=f"""{Emojis.dot_emoji} Der standart Prozentwert für das bonus XP system ligt bereits bei **{check_settigns[4]} %**""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, back_to_none=3)

            emb = discord.Embed(title=f"Der standart Prozentwert für das bonus XP system wurde erfolgreich zurückgesetzt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Der standart Prozentwert für das bonus XP system wurde zurück auf **10 %** gesetzt.
                {Emojis.dot_emoji} Alle aktivitäten von oder in allen channel, Kategorien, Rollen oder usern die teil des bonus XP systems sind werden mit **10 %** mehr XP belohnt.""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "show-bonus-xp-percentage", description = "Lass die anzeigen wo der standart Prozent wert für das bonus XP system liegt!")
    async def show_bonus_xp_percentage(self, ctx:commands.Context):

        check_settings = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        emb = discord.Embed(title=f"{Emojis.help_emoji} Hier sihst du wie viel Prozent mehr XP man beim Bonus XP system erhält", 
            description=f"""{Emojis.dot_emoji} Man erhählt aktuell **{check_settings[4]} %** mehr XP für aktivitäten in Kanälen oder Kategorien die teil des bonus XP systems sind.
            Ebenso erhält man auch diesen Bonus wenn man eine rolle besitzt die auf der liste für das bonus XP system steht oder wenn man ein user ist der auf der bonus XP liste gelistet ist""", color=bot_colour)
        await ctx.respond(embed=emb)


def setup(bot):
    bot.add_cog(LevelSystem(bot))
    