
from Import_file import *
from check import check_exists
from typing import Union
from easy_pil import Editor, load_image_async, Font
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from check import *
import re


##############################################  Black list manager  ##############################################


class BlacklistManagerButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Button for adding items to the Blacklist Manager
    @discord.ui.button(label="Add to Blacklist", style=discord.ButtonStyle.blurple, custom_id="add_blacklist")
    async def add_blacklist_manager_button(self, button, interaction:discord.Interaction):

        view = BlacklistManagerSelectAdd()
        view.add_item(TempBlackklistLevelSaveButton())
        view.add_item(ShowBlacklistLevelSystemButton())

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Hier kannst du auswählen was du auf die Blacklist setzen möchtest", 
                description=f"""{Emojis.dot_emoji} Mit den unteren select menüs kannst du auswählen was du auf die Blacklist setzen möchtest!
                {Emojis.dot_emoji} Du kannst dabei frei wählen was du möchtest du kannst aber nur maximal 5 elemente pro menü auswählen
                {Emojis.dot_emoji} Wenn du alles ausgewählt hast was du möchtest bestätige deine auswähl indem du auf den Safe configuaration button drückst
                {Emojis.dot_emoji} Wenn du sehen möchtest schon alles auf der blacklist ist benutzen den Show blacklist button.
                {Emojis.help_emoji} Falls du etwas auswählen solltest was bereits auf der blacklist ist wird es automatisch aussortiert {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=view)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    # Button for removing items from the Blacklist Manager
    @discord.ui.button(label="Remove from blacklist", style=discord.ButtonStyle.blurple, custom_id="remove_blacklist")
    async def remove_blacklist_manager_button(self, button, interaction:discord.Interaction):
        
        view = BlacklistManagerSelectRemove()
        view.add_item(TempBlackklistLevelSaveButton())
        view.add_item(ShowBlacklistLevelSystemButton())

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Hier kannst du auswählen was du von der Blacklist entfernen willst", 
                description=f"""{Emojis.dot_emoji} Mit den unseren selectmenüs kannst du auswählen was von der Blacklist enfernt werden soll
                {Emojis.dot_emoji} Wenn du alles ausgewählt hast was du möchtest bestätige deine auswähl indem du auf den Safe configuaration button drückst 
                {Emojis.dot_emoji} Wenn du nicht weißt was auf der Blacklist steht kannst du entweder auf den show blacklist button drücken oder den {show_blacklist_level} command benutzen
                {Emojis.help_emoji} Falls du etwas auswählen solltest nicht auf der blacklist ist wird es automatisch aussortiert {Emojis.exclamation_mark_emoji}""", color=bot_colour)
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

    @discord.ui.channel_select(placeholder="Wähle die channels aus die du auf die Blacklist setzen möchtest!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.text, discord.ChannelType.voice, discord.ChannelType.forum, discord.ChannelType.news], custom_id="add_channel_blacklist_select")
    async def add_blacklist_channel_level_select(self, select, interaction:discord.Interaction):

        channel_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, channels=select.values, operation="add", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", channel_id=channel_list)
        await interaction.response.defer()

    @discord.ui.channel_select(placeholder="Wähle die Kategorien aus die du auf die Blacklist setzen möchtest!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.category], custom_id="add_category_blacklist_select")
    async def add_blacklist_category_level_select(self, select, interaction:discord.Interaction):

        category_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, categories=select.values, operation="add", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", category_id=category_list)
        await interaction.response.defer()

    @discord.ui.role_select(placeholder="Wähle die rollen aus die du auf die Blacklist setzen möchtes!", min_values=1, max_values=5, custom_id="add_role_blacklist_select")
    async def add_blacklist_role_level_select(self, select, interaction:discord.Interaction):

        role_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, roles=select.values, operation="add", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", role_id=role_list)
        await interaction.response.defer()
        
    @discord.ui.user_select(placeholder="Wähle die User aus die du auf die Blacklist setzen möchtest!", min_values=1, max_values=5, custom_id="add_user_blacklist_select")
    async def add_blacklist_user_level_select(self, select, interaction:discord.Interaction):

        user_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, users=select.values, operation="add", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", user_id=user_list)
        await interaction.response.defer()


class BlacklistManagerSelectRemove(discord.ui.View):
    def __init__(self):
        self.table = "level"
        super().__init__(timeout=None)

    @discord.ui.channel_select(placeholder="Wähle die channels aus die du von der Blacklist entfernen möchtest!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.text, discord.ChannelType.voice, discord.ChannelType.forum, discord.ChannelType.news], custom_id="remove_channel_blacklist_select")
    async def add_blacklist_channel_level_select(self, select, interaction:discord.Interaction):

        channel_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, channels=select.values, operation="remove", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="remove", channel_id=channel_list)
        await interaction.response.defer()

    @discord.ui.channel_select(placeholder="Wähle die Kategorien aus die du von der Blacklist entfernen möchtest!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.category], custom_id="remove_category_blacklist_select")
    async def add_blacklist_category_level_select(self, select, interaction:discord.Interaction):

        category_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, categories=select.values, operation="remove", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="remove", category_id=category_list)
        await interaction.response.defer()

    @discord.ui.role_select(placeholder="Wähle die rollen aus die du von der Blacklist entfernen möchtes!", min_values=1, max_values=5, custom_id="remove_role_blacklist_select")
    async def add_blacklist_role_level_select(self, select, interaction:discord.Interaction):
        
        role_list = BlacklistManagerChecks.check_items_blacklist_manager(guild_id=interaction.guild.id, roles=select.values, operation="remove", table=self.table)
        BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="remove", role_id=role_list)
        await interaction.response.defer()
        
    @discord.ui.user_select(placeholder="Wähle die User aus die du von der Blacklist entfernen möchtest!", min_values=1, max_values=5, custom_id="remove_user_blacklist_select")
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
                        
                        DatabaseUpdates.manage_blacklist(guild_id=temp_blacklist[0], operation=operation, guild_name=interaction.guild.name, channel_id=channel, table="level")

                if temp_blacklist[2]: 

                    category_list = (list(map(int, re.findall('\d+', temp_blacklist[2]))))
                    for category in category_list:

                        mention.append(f"{Emojis.dot_emoji} <#{category}>")

                        DatabaseUpdates.manage_blacklist(guild_id=temp_blacklist[0], operation=operation, guild_name=interaction.guild.name, category_id=category, table="level")
                      
                if temp_blacklist[3]:
                        
                    role_list = (list(map(int, re.findall('\d+', temp_blacklist[3]))))
                    for role in role_list:
                            
                        mention.append(f"{Emojis.dot_emoji} <@&{role}>")
                        
                        DatabaseUpdates.manage_blacklist(guild_id=temp_blacklist[0], operation=operation, guild_name=interaction.guild.name, role_id=role, table="level")
                                
                if temp_blacklist[4]:
                        
                    user_list = (list(map(int, re.findall('\d+', temp_blacklist[4]))))
                    for user in user_list:

                        mention.append(f"{Emojis.dot_emoji} <@{user}>")
                        
                        DatabaseUpdates.manage_blacklist(guild_id=temp_blacklist[0], operation=operation, guild_name=interaction.guild.name, user_id=user, table="level")

                BlacklistManagerChecks.delete_temp_blacklist_level(guild_id=temp_blacklist[0])
                    
                mentions = "\n".join(mention)

                if temp_blacklist[5] == "add":

                    emb = discord.Embed(title=f"Die ausgwählten elemente wurden auf die blacklist gesetzt {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} Es wurde alles auf die Blacklist gesetzt was du ausgewählt hattest.
                        {Emojis.dot_emoji} Hier sihst du noch mal alles was hinzugefügt wurde:\n\n{mentions}\n
                        {Emojis.help_emoji} Wenn etwas nicht aufgelistet ist befindet es sich bereits auf der Blacklist {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await interaction.edit_original_response(embed=emb, view=None)

                if temp_blacklist[5] == "remove":

                    emb = discord.Embed(title=f"Die ausgewählten elemente wurden von der blacklist entfernt {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} Es wurde alles von der Blacklist entfernt was du ausgewählt hattest.
                        {Emojis.dot_emoji} Hier sihst du nochmal alles was entfernt wurde: \n\n{mentions}\n
                        {Emojis.help_emoji} Wenn etwas nicht aufgelistet ist befindet es sich nicht auf der Blacklist {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await interaction.edit_original_response(embed=emb, view=None)

            else:

                emb = discord.Embed(title=f"Es wurde nichts ausgewählt {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} Es wurde nichta ausgewählt was auf die Blacklist gesetzt oder entfernt werden soll.
                    {Emojis.dot_emoji} Wenn du elemente auf die blacklist setzen oder von ihr entfernen möchtest kanns du diesen Command einfach erneut nutzen.""", color=bot_colour)
                await interaction.edit_original_response(embed=emb, view=None)





#############################################  Level Systen Settings  #############################################


class LevelSystemSettings(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    # Button to set the status of the level system to on
    @discord.ui.button(label="On/Off Level system", style=discord.ButtonStyle.blurple, custom_id="on_off_level_system")
    async def yes_button_settings(self, button, interaction:discord.Interaction):

        guild_id = interaction.guild.id
        
        check_status = DatabaseCheck.check_level_settings(guild_id=guild_id)

        if interaction.user.guild_permissions.administrator:

            if check_status == None:

                emb = discord.Embed(title=f"Es wurde kein eintrag gefunden {Emojis.fail_emoji}", 
                    description=f"""Es wurde kein eintrag gefunden deshalb wurde einer für dein server erstellt. 
                    {Emojis.dot_emoji} Das Level system wurde auch gleich automatisch eingeschalten.
                    {Emojis.dot_emoji} Wenn du es deaktivieren möchtest benutzen sie diesen command einfach noch einmal""", color=error_red)
                await interaction.response.edit_message(embed=emb)

            else:

                if check_status[2] == "on":

                    new_status, status = "Ausgeschalten", "off"
                    opposite_status = "Einschalten"

                elif check_status[2] == "off":

                    new_status, status = "Eingeschalten", "on"
                    opposite_status = "Ausschalten"

                DatabaseUpdates.update_level_settings(guild_id=guild_id, level_status=status)
                        
                emb = discord.Embed(title=f"Das Level system wurde {new_status}", 
                    description=f"""Sie haben das Level system erfolgreich {new_status}.
                    {Emojis.dot_emoji} Wenn sie das level system wieder {opposite_status} wollen benutzen sie diesen command einfach noch einmal {Emojis.exclamation_mark_emoji}""", color=bot_colour)
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
        
        guild_id = interaction.guild.id 
    
        if interaction.user.guild_permissions.administrator:

            if self.role_id == None and self.role_level == None and self.status == None:

                emb = discord.Embed(title=f"Die rolle oder das Level konnte nicht überschrieben werden {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} Die rolle oder das Level konnte nicht überschrieben werden da der Prozess abgelaufen ist.
                    {Emojis.dot_emoji} Dies Passiert wenn man zu lange wartet um auf den Button zu reagieren.
                    {Emojis.dot_emoji} Du kannst den Command einfach erneut ausführen wenn du das level oder die rolle noch immer überschreiben möchtest {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                DatabaseUpdates.update_level_roles(guild_id=guild_id, role_id=self.role_id, role_level=self.role_level, status=self.status)
                            
                emb = discord.Embed(title=f"Erfolgreiche überschreibung der level role {Emojis.succesfully_emoji}", 
                    description=f"""{Emojis.dot_emoji} Die level role wurde erfolgreich überschrieben. 
                    {Emojis.dot_emoji} Die role <@&{self.role_id}> wird ab jetzt bei level {self.role_level} vergeben.""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:
                
            await interaction.response.send_message(embed=no_permissions_emb, view=None, ephemeral=True)


    # Button to cancel the overwriting of the level role 
    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, custom_id="no_button_level_role")
    async def no_button_levelroles(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            check_level_roles = DatabaseCheck.check_level_system_levelroles(guild=interaction.guild.id, level_role=self.role_id, needed_level=self.role_level, status="check")

            if self.role_id == None and self.role_level == None and self.status == None:

                emb = discord.Embed(title=f"Die überschreibung der level role wurde abgebrochen",
                    description=f"""{Emojis.dot_emoji} Die überschreiben der level role wurde erfolgreich abgebrochen.
                    {Emojis.dot_emoji} Wenn du alle level rollen sehen möchtest verwende den {show_level_role} command.""")

            else:

                if check_level_roles[1] == self.role_id:

                    emb = discord.Embed(title=f"Die überschreibung der level role wurde abgebrochen", 
                        description=f"""{Emojis.dot_emoji} Das überschreiben der level role wurde erfolgreich abgebrochen.
                        {Emojis.dot_emoji} Die role <@&{self.role_id}> wird weiterhin bei errechen von level {check_level_roles[2]} vergeben""", color=bot_colour)
                    await interaction.response.edit_message(embed=emb, view=None)

                if check_level_roles[2] == self.role_level:

                    emb = discord.Embed(title=f"Die überschreibung der level role wurde abgebrochen", 
                        description=f"""{Emojis.dot_emoji} Das überschreiben der level role wurde erfolgreich abgebrochen.
                        {Emojis.dot_emoji} Bei erreichen von level {self.role_level} erhält man weiterhin die rolle {check_level_roles[1]}""", color=bot_colour)
                    await interaction.response.edit_message(embed=emb, view=None)

        else:
            
            await interaction.response.send_message(embed=no_permissions_emb ,view=None, ephemeral=True)



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

                emb = discord.Embed(title=f"Der level up channel konnte nicht überschrieben werden {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} Der level up channel konnte nicht überschrieben werden da der Prozess abgelaufen ist.
                    {Emojis.dot_emoji} Dies Passiert wenn man zu lange wartet um auf den Button zu reagieren.
                    {Emojis.dot_emoji} Du kannst den Command einfach erneut ausführen wenn du den level up channel noch immer überschreiben möchtest {Emojis.exclamation_mark_emoji}""")
                await interaction.response.edit_message(embed=emb, view=None)


            else:

                DatabaseUpdates.update_level_settings(guild_id=interaction.guild.id, levelup_channel=self.channel)

                emb = discord.Embed(title=f"Der level up channel wurde erfolgreich überschrieben {Emojis.succesfully_emoji}", 
                    description=f"""{Emojis.dot_emoji} Der level up channel wurde erfolgreich überschrieben.
                    {Emojis.dot_emoji} Ab jetzt ist der channel <#{self.channel}> als level up channel zugewiesen.""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, view=None, ephemeral=True)


    # Button to cancel the overwriting of the level up channel 
    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="no_button_level_up")
    async def no_button_levelup(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title="Erfolgreich abgebrochen", 
                description=f"Du hast erfolgreich die Überschreibung des level up channels abgebrochen",color = discord.Colour.brand_green())
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

            emb = discord.Embed(title=f"Du hast alle stats des level systems zurückgesetzt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.arrow_emoji} Alle user datein wurden gelöscht jeder user ist jetzt wieder level 0 und hat 0 XP.
                Es werden wieder bei aktivitäht neue enträge erstellt, wenn sie das nicht möchten stellen sie das level system aus {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)


        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True)

    
    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="no_button_reset")
    async def reset_stats_button_level_no(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
        
            emb = discord.Embed(title=f"Der vorgang wurde erfolgreich abgebrochen {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Das resetten der stats wurde erfolgreich abgebrochen.
                Alle user behalten Ihre stats im level system.""", color=bot_colour)
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

            emb = discord.Embed(title=f"Die blacklist wurde geresetet {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.arrow_emoji} alle Channel, User, Rollen und Kategorien wurden von der Blacklist entfernt.
                Wenn du wieder Dinge auf die Blacklist setzten möchtest kannst du die Befehle wie zuvor nutzen {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)


    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, row=1, custom_id="no_button_level")
    async def reset_blacklist_button_level_no(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Der vorgang wurde erfolgreich abgebrochen {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Das resetten der blacklist wurde erfolgreich abgebrochen.
                Alle Channels, Rollen, Kategorien und User sind weiterhin auf der blacklist gelistet.
                {Emojis.dot_emoji} Wenn du einzelne elemente von der blacklist steichen möchtest kannst du sie mit den Remove commands streichen lassen {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)

            
class ShowBlacklistLevelSystemButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Show all items on the blacklist", style=discord.ButtonStyle.blurple, custom_id="show_blacklist_button_level")
    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id
            blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)
            
            channel, category, role, user = blacklist[0], blacklist[1], blacklist[2], blacklist[3] 

            emb = discord.Embed(title=f"Hier siehst du alle Elemente die auf der Blacklist des level systems stehen {Emojis.exclamation_mark_emoji}", 
                description=f"""Hier sind alle Elemente aufgelistet die auf der level system Blacklist stehen.""", color=bot_colour)
            emb.add_field(name="Channels:", value=f"{channel}", inline=False)
            emb.add_field(name="Categories:", value=f"{category}", inline=False)
            emb.add_field(name="Rolles", value=f"{role}", inline=False)
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

    def xp_generator(self):
        xp = 20
        return xp

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        connection_db_level = DatabaseSetup.db_connector()
        my_cursor = connection_db_level.cursor()

        if self.get_ratelimit(message):
            return

        if message.content.startswith("?"):
            return

        if message.author.bot:
            return 

        check_settings = DatabaseStatusCheck._level_system_status(guild_id=message.guild.id)
        
        if check_settings == None:
            DatabaseUpdates._create_bot_settings(guild_id=message.guild.id)
            return
        
        elif check_settings == False:
            return
                
        # Blacklist check
        check_blacklist = DatabaseStatusCheck._blacklist_check_text(message_check=message, guild_id=message.guild.id)
                        
        if isinstance(message.channel, discord.TextChannel):
                    
            # Check if the blacklist returns None
            if check_blacklist != True:
                
                try:   
                            
                    # Database check for all values 
                    check_if_exists = DatabaseCheck.check_level_system_stats(guild_id=message.guild.id, user=message.author.id)
                    if check_if_exists:

                        # All user stats                   
                        user_level, user_xp = check_if_exists[2], check_if_exists[3]
                        if check_if_exists[2] >= 999:
                            return

                        XP = self.xp_generator()
                        user_has_xp = user_xp + XP 
                                                                    
                        xp_need_next_level = 5 * (user_level ^ 2) + (50 * user_level) + 100 - user_xp
                        final_xp = xp_need_next_level + user_xp
                        
                        if user_has_xp >= final_xp:
                                                                        
                            new_level = user_level + 1    

                            try:
                                
                                # Updates the XP
                                DatabaseUpdates._update_user_stats_level(guild_id=message.guild.id, user_id=message.author.id, level=new_level)

                                print("Data were changed")

                            except mysql.connector.Error as error:
                                print("parameterized query failed {}".format(error))
                                                                    
                            finally:   

                                level_role_check = DatabaseCheck.check_level_system_levelroles(guild=message.guild.id, needed_level=new_level)
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

                                DatabaseUpdates._update_user_stats_level(guild_id=message.guild.id, user_id=message.author.id, xp=user_has_xp)                       
                                print("Data were changed")

                            except mysql.connector.Error as error:
                                print("parameterized query failed {}".format(error))

                    else:
                            
                        DatabaseUpdates._insert_user_stats_level(guild_id=message.guild.id, user_id=message.author.id, user_name=message.author.name)

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))
                    
        DatabaseSetup.db_close(cursor=my_cursor, db_connection=connection_db_level)
   




####################################################  User stats setting  #################################################


    # Command to give a user XP, The XP awarded can only be as high as he needs for a new level!
    @commands.slash_command(name = "give-xp", description = "Give a user a quantity of XP chosen by you!")
    @commands.has_permissions(administrator = True)
    async def give_xp_slash(self, ctx:commands.Context, user:Option(discord.Member, description="Select a user who should receive the xp!"),
        xp:Option(int, description="Specify a quantity of XP to be added!")):

        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            check_stats = DatabaseCheck.check_level_system_stats(guild=ctx.guild.id, user=user.id)

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


    # Command to removing XP from a user, The XP what should be removed can only be as high as the user owns 
    @commands.slash_command(name = "remove-xp", description = "Remove a chosen amount of Xp from a user!")
    @commands.has_permissions(administrator = True)
    async def remove_xp_slash(self, ctx, user:Option(discord.Member, description="Choose a user from which you want to remove xp!"),
        xp:Option(int, description="Specify a quantity of Xp to be removed!")):

        user_id = user.id
        guild_id = ctx.guild.id
        user_name = user.name
            
        check_stats = DatabaseCheck.check_level_system_stats(guild=guild_id, user=user_id)

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


    # Command to give a user Level
    @commands.slash_command(name = "give-levels", description = "Give a user a selected amount of levels!")
    @commands.has_permissions(administrator = True)
    async def give_level_slash(self, ctx, user:Option(discord.Member, description="Choose a user you want to give the levels to!"), 
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
                

    # command to removing levels from a user 
    @commands.slash_command(name = "remove-level", description = "Remove a quantity of levels chosen by you!")
    @commands.has_permissions(administrator = True)
    async def remove_level_slash(self, ctx, user:Option(discord.Member, description="Select a user from whom you want to remove the level!"), 
        level:Option(int, description="Specify how many levels should be removed!")):

        user_id = user.id
        guild_id = ctx.guild.id
        user_name = user.name

        check_stats = DatabaseCheck.check_level_system_stats(guild=guild_id, user=user_id)
        
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
    
    
    @commands.slash_command(name = "reset-level", description = "Reset all levels and xp of everyone!")
    @commands.has_permissions(administrator = True)
    async def reset_levels_slash(self, ctx):

        guild_id = ctx.guild.id

        check_stats = DatabaseCheck.check_level_system_stats(guild=guild_id)

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
    async def rank_slash(self, ctx, user:Option(discord.Member, description="Let others show you the rank!")):

        count = 0
        rank = 0
        connection_to_db_level = DatabaseSetup.db_connector()
        my_cursor = connection_to_db_level.cursor()

        error_emb = discord.Embed(title="The user was not found", 
            description="The user either does not exist or he has not yet shown that he exists.", color=error_red)

        check_user = DatabaseCheck.check_level_system_stats(guild=ctx.guild.id, user=user.id)
        
        if check_user:

            rank_show_infos_level = "SELECT * FROM LevelSystemStats WHERE guildId = %s ORDER BY userLevel DESC, userXp DESC"
            rank_show_infos_levels_values = [ctx.guild.id]
            my_cursor.execute(rank_show_infos_level, rank_show_infos_levels_values)
            all_info = my_cursor.fetchall()
          
            for _, user_id_rank, _, _, _, _ in all_info:
                    
                if user.id == user_id_rank:
                
                    for rank_count in all_info:

                        count = count + 1
                                                            
                        if user.id == rank_count[1]:

                            rank = count 
                            print(check_user)
            xp = check_user[3]
        
            xp_needed = 5 * (check_user[2] ^ 2) + (50 * check_user[2]) + 100 - check_user[3]
            final_xp = xp_needed + xp
            xp_have = check_user[3]

            percentage = int(((xp_have * 100)/ final_xp))

            poppins = Font.poppins(size=70)
            poppins_small = Font.poppins(size=30)

            background = Editor(("assets/rank-card/card1.png"))
            profile = await load_image_async(user.display_avatar.url)
            circle_avatar = Editor(profile).resize((200, 200)).circle_image()

            imag = Editor("assets/rank-card/zBLACK.png")
            
            background.blend(image=imag, alpha=.5, on_top=True)
            background.ellipse((15, 15), width=210, height=210, outline="#1b67e0", stroke_width=10)
            background.rectangle((40, 250), width=720, height=40, fill="#484b4e", radius=15)
            
            background.paste(circle_avatar, (20, 20))
            background.rectangle((250, 180), width=650, height=40, fill="#fff", radius=15)
            background.bar((250, 180), max_width=650, height=40, percentage=percentage, fill="#1b67e0", radius=15)

            background.text((260, 50), text=user.name, font=poppins, color="white")
            background.text((260, 135), text=f"Level : {check_user[2]}", font=poppins_small, color="white")
            background.text((680, 135), text=f"XP : {xp} / {final_xp}", font=poppins_small, color="white")
            background.text((920, 187), text=f"# {rank}", font=poppins_small, color="white")

                
            rank_card = discord.File(fp=background.image_bytes, filename="rank.png")
            await ctx.respond(file=rank_card)

        else:
                            
            await ctx.respond(embed=error_emb)

        DatabaseSetup.db_close(cursor=my_cursor, db_connection=connection_to_db_level)



    @commands.slash_command(name = "leaderboard-level", description = "Shows the highest ranks in the lavel system!")
    async def leaderboard(self, ctx):

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


    @commands.slash_command(name = "level-system-settings", description = "Stelle das level system frei ein!")
    @commands.has_permissions(administrator = True)
    async def level_system_settings(self, ctx):

        guild_id = ctx.guild.id
        
        level_sytem_conrtol_db = DatabaseSetup.db_connector()
        my_curser_control = level_sytem_conrtol_db.cursor()

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

        DatabaseSetup.db_close(cursor=my_curser_control, db_connection=level_sytem_conrtol_db)

    

#################################################  Level Blacklist settings  ###############################################


    @commands.slash_command(name = "add-channel-level-blacklist", description = "Exclude channels from the level system!")
    @commands.has_permissions(administrator = True)
    async def add_chanels_level_blacklist(self, ctx:commands.Context, channel:Option(Union[discord.VoiceChannel, discord.TextChannel], description="Select a channel that you want to exclude from the level system!")):
        
        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, channel_id=channel.id, table="level")

        if blacklist:

            blacklist = ShowBlacklist._show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"This channel is already on the blacklist {Emojis.fail_emoji}", 
                description=f"""The following channels are on the blacklist:\n
                {blacklist[0]}
                If you want to remove channels from the blacklist execute this command:\n{remove_blacklist_level_channel}""", color=error_red)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", guild_name=ctx.guild.name, channel_id=channel.id, table="level")

            emb = discord.Embed(title=f"This channel was successfully blacklisted {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The channel: <#{channel.id}> was successfully blacklisted.
                {Emojis.dot_emoji} If you want to remove it again use this command:\n{remove_blacklist_level_channel}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-channel-level-blacklist", description = "Remove a channel from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_channel_blacklist(self, ctx:commands.Context, channel:Option(Union[discord.TextChannel, discord.VoiceChannel], description="Select a channel to remove from the blacklist!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, channel_id=channel.id, table="level")

        if blacklist:
                
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", channel_id=channel.id, table="level")

            emb = discord.Embed(title=f"The channel was removed from the blacklist {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The channel has been successfully removed from the blacklist if you want to add it again use the: {add_blacklist_level_channel} command.
                {Emojis.dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} command""", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:
            
            blacklist = ShowBlacklist._show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"This channel is not on the blacklist {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} The channel: <#{channel.id}> is not blacklisted.
                The following channels are blacklisted:\n\n{blacklist[0]}""", color=error_red)
            await ctx.respond(embed=emb)
        
    
    @commands.slash_command(name = "add-category-level-blacklist", description = "Exclude categories from the level system and all channels that belong to them!")
    @commands.has_permissions(administrator = True)
    async def add_category_blacklist(self, ctx:commands.Context, category:Option(discord.CategoryChannel, description="Select a category that you want to exclude from the level system!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, category_id=category.id, table="level")
        
        if blacklist:
            
            blacklist = ShowBlacklist._show_blacklist_level(guild_id=ctx.guild.id)
                
            emb = discord.Embed(title=f"This category is already on the blacklist {Emojis.fail_emoji}", 
                description=f"""The following categories are on the blacklist:\n
                {blacklist[1]}
                If you want to remove categories from the blacklist execute this command:\n{remove_blacklist_level_category}""", color=error_red)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", guild_name=ctx.guild.name, category_id=category.id, table="level")
            
            emb = discord.Embed(title=f"This category was successfully blacklisted {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The category: <#{category.id}> was successfully blacklisted.
                {Emojis.dot_emoji} If you want to remove them again use this command:\n{remove_blacklist_level_category}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-category-level-blacklist", description = "Remove categories from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_category_blacklist(self, ctx:commands.Context, category:Option(discord.CategoryChannel, description="Select a category to remove from the blacklist!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, category_id=category.id, table="level")

        if blacklist:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", category_id=category.id, table="level")
            
            emb = discord.Embed(title=f"The category was removed from the blacklist {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The category has been successfully removed from the blacklist if you want to add it again use the: {add_blacklist_level_category} command.
                {Emojis.dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} comamnd""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"This category is not on the blacklist{Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} The category: <#{category.id}> is not on the blacklist.
                The following categories are blacklisted:\n\n{blacklist[1]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "add-role-level-blacklist", description = "Choose a role that you want to exclude from the level system!")
    @commands.has_permissions(administrator = True)
    async def add_role_blacklist(self, ctx:commands.Context, role:Option(discord.Role, description="Select a role that you want to exclude from the level system!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, role_id=role.id, table="level")

        if blacklist:
     
            blacklist = ShowBlacklist._show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"This role is already on the blacklist {Emojis.fail_emoji}", 
                description=f"""The following roles are on the blacklist:\n\n{blacklist[2]}
                If you want to remove roles from the blacklist execute this command:\n{remove_blacklist_level_role}""", color=error_red)
            await ctx.respond(embed=emb)
        
        else:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", guild_name=ctx.guild.name, role_id=role.id, table="level")
            
            emb = discord.Embed(title=f"This role has been successfully blacklisted {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The role: <#{role.id}> has been successfully blacklisted.
                {Emojis.dot_emoji} If you want to remove them again use this command:\n{remove_blacklist_level_role}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-role-level-blacklist", description = "Remove a role from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_role_blacklist(self, ctx:commands.Context, role:Option(discord.Role, description="Select a role you want to remove from the blacklist!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, role_id=role.id, table="level")

        if blacklist:

            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", role_id=role.id, table="level")
            
            emb = discord.Embed(title=f"The role was removed from the blacklist {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The role has been successfully removed from the blacklist if you want to add it again use the: {add_blacklist_level_role} command.
                {Emojis.dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} comamnd""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"This role is not blacklisted {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} The role: <@&{role.id}> is not blacklisted.
                The following roles are blacklisted:\n\n{blacklist[2]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name= "add-user-level-blacklist", description = "Choose a user that you want to exclude from the level system!")
    @commands.has_permissions(administrator = True)
    async def add_user_level_blacklsit(self, ctx:commands.Context, user:Option(discord.User, description="Select a user that you want to exclude from the level system!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, user_id=user.id, table="level")

        if user.bot:
            await ctx.respond(embed=user_bot_emb, view=None)
        
        else:

            if blacklist:

                blacklist = ShowBlacklist._show_blacklist_level(guild_id=ctx.guild.id)

                emb = discord.Embed(title=f"This user is already on the blacklist {Emojis.fail_emoji}", 
                    description=f"""The following users are on the blacklist:\n\n{blacklist[3]}
                    If you want to remove users from the blacklist execute this command:\n{remove_blacklist_level_user}""", color=error_red)
                await ctx.respond(embed=emb)

            else:   

                DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", guild_name=ctx.guild.name, user_id=user.id, table="level")

                emb = discord.Embed(title=f"This user was successfully blacklisted {Emojis.succesfully_emoji}", 
                    description=f"""{Emojis.dot_emoji} The user: <@{user.id}> was successfully blacklisted.
                    If you want to remove it again use this command:\n{remove_blacklist_level_user}""", color=bot_colour)
                await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-user-level-blacklist", description="Remove a user from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_user_level_blacklist(self, ctx:commands.Context, user:Option(discord.User, description="Select a user you want to remove from the blacklist!")):
        
        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, user_id=user.id, table="level")

        if blacklist:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", user_id=user.id, table="level")

            emb = discord.Embed(title=f"The user was removed from the blacklist {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The user has been successfully removed from the blacklist if you want to add him again use the: {add_blacklist_level_user} command.
                {Emojis.dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} comamnd""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_level(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"This user is not on the blacklist {Emojis.fail_emoji}", 
                description=f"""The user: <@{user.id}> is not on the blacklist.
                The following users are on the blacklist:\n\n{blacklist[3]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "reset-level-blacklist", description="Reset the blacklist of the level system and remove all entries!")
    @commands.has_permissions(administrator = True)
    async def reset_blacklist(self, ctx):

        guild_id = ctx.guild.id

        blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id, table="level")

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


    @commands.slash_command(name = "manage-level-blacklist")
    async def manage_level_blacklist(self, ctx):

        emb = discord.Embed(title=f"Wilkommen im blacklist manager {Emojis.settings_emoji}", 
            description=f"""{Emojis.help_emoji} Mit den Beiden Buttons kannst du auswählen ob du etwas auf die Blacklist setzen möchtest oder etwas entfernen möchtest!
            {Emojis.dot_emoji} Sobalt du etwas ausgewählt hast werden dir select menüs angezeigt.
            {Emojis.dot_emoji} Mit diesen kannst du auswählen was du auf die blacklist setzen oder entfernen möchtest.""", color=bot_colour)
        await ctx.respond(embed=emb, view=BlacklistManagerButtons())


   
    @commands.slash_command(name = "show-level-blacklist", description = "Shows you everything that is blacklisted!")
    async def show_blacklist(self, ctx):

        guild_id = ctx.guild.id

        blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)
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
    async def add_level_role(self, ctx, role:Option(discord.Role, description = "Select a role that you want to assign from a certain level onwards"),
        level:Option(int, description = "Enter a level from which this role should be assigned")):
        
        guild_id = ctx.guild.id
        guild_name = ctx.guild.name
        role_id = role.id

        level_roles = DatabaseCheck.check_level_system_levelroles(guild=guild_id, level_role=role_id, needed_level=level, status="check")

        emb_level_0 = discord.Embed(title=f"The level you want to set is 0 {Emojis.fail_emoji}", 
            description=f"""{Emojis.dot_emoji} The level to vest a level role must be at least **1**.""", color=error_red)
        emb_higher = discord.Embed(title=f"The level you want to set for the level role is too high {Emojis.fail_emoji}", 
            description=f"""{Emojis.dot_emoji} The level you want to set for the level role is too high you can only set a value that is below or equal to **999**.""", color=error_red)

        if level_roles == None:
            
            if level <= 999:
                         
                DatabaseUpdates._insert_level_roles(guild_id=guild_id, role_id=role_id, level=level, guild_name=guild_name)

                emb = discord.Embed(title=f"The role was assigned successfully {Emojis.succesfully_emoji}", 
                    description=f"""{Emojis.dot_emoji} The role <@&{role_id}> was successfully assigned to the level {level}.
                    {Emojis.dot_emoji} As soon as a user reaches {level} he gets the <@&{role_id}> role. {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                await ctx.respond(embed=emb)

            await ctx.respond(embed=emb_level_0) if level == 0 else None

            await ctx.respond(embed=emb_higher) if  level > 999 else None 

        else:

            check_same = DatabaseCheck.check_level_system_levelroles(guild=guild_id, level_role=role_id, needed_level=level)
                
            if check_same:

                same_emb = discord.Embed(title=f"This role has already been set at this level {Emojis.fail_emoji}",
                    description=f"""{Emojis.dot_emoji} The role <@&{role_id}> is already assigned to the level {level}.
                    {Emojis.dot_emoji} If you want to change it you can assign this role to another level or another role to this level {Emojis.exclamation_mark_emoji}""", color=error_red)
                await ctx.respond(embed=same_emb)

            else:
                
                if role_id == level_roles[1]:

                    level_needed = level_roles[2]
        
                    emb = discord.Embed(title=f"This role is already assigned {Emojis.fail_emoji}", 
                        description=f"""{Emojis.dot_emoji} Do you want to override the required level for this role? 
                        {Emojis.dot_emoji} The role <@&{role_id}> is currently assigned at level **{level_needed}**.
                        {Emojis.dot_emoji} If you want to override the required level for this role select the yes buttons otherwise the no button {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb, view=LevelRolesButtons(role_id=role_id, role_level=level, status="role"))
    
                elif level == level_roles[2]:
                    
                    level_role = level_roles[1]

                    emb = discord.Embed(title=f"This level is already assigned {Emojis.fail_emoji}", 
                        description=f"""{Emojis.dot_emoji} Do you want to overwrite the role for this level?
                        {Emojis.dot_emoji} For the level {level} the role <@&{level_role}> is currently assigned.
                        {Emojis.dot_emoji} If you want to override the role for this level select the yes buttons otherwise select the no button {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb, view=LevelRolesButtons(role_id=role_id, role_level=level, status="level"))   



    @commands.slash_command(name = "remove-level-role", description = "Choose a role that you want to remove as a level role!")
    @commands.has_permissions(administrator = True)
    async def remove_level_role(self, ctx, role:Option(discord.Role, description="Select a level role that you want to remove")):
        
        guild_id = ctx.guild.id
        role_id = role.id

        level_roles = DatabaseCheck.check_level_system_levelroles(guild=guild_id, level_role=role_id)

        if level_roles:
            
            DatabaseRemoveDatas._remove_level_system_level_roles(guild_id=guild_id, role_id=role_id)

            emb = discord.Embed(f"This role has been removed as a level role {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} The role <@&{role_id}> was successfully removed as a level role.
                {Emojis.dot_emoji} If you want to add them again you can do this with the {add_level_role} command {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            level_roles = DatabaseCheck.check_level_system_levelroles(guild=guild_id, status="level_role")

            if level_roles:
                
                result_strings = []
                for guild_id, role_id, level, _ in level_roles:
                    result_strings.append(f"{Emojis.dot_emoji} <@&{role_id}> we assign on level: {level}")

                result = '\n'.join(result_strings)

            else:

                result = f"{Emojis.dot_emoji} No level roles have been assigned!"

            emb = discord.Embed(title=f"This role is not defined as a level role {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} This role cannot be removed because it is not set as a level role.
                {Emojis.dot_emoji} Here you can see all the level rolls.\n\n{result}""", color=error_red)
            await ctx.respond(embed=emb)



    @commands.slash_command(name = "show-all-level-roles", description = "View all rolls that are available with a level!")
    async def show_all_level_roles(self, ctx:commands.Context):

        level_roles = DatabaseCheck.check_level_system_levelroles(guild=ctx.guild.id, status="level_role")
        
        if level_roles:
            
            result_strings = []
            for _, role_id, level, _ in level_roles:
                result_strings.append(f"{Emojis.dot_emoji} <@&{role_id}> you get from level: {level}")

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

        level_up_channel = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if level_up_channel[3]:
       
            if channel.id == level_up_channel[3]:

                emb = discord.Embed(title=f"This channel is already assigned as level up channel {Emojis.fail_emoji}", 
                    description=f"{Emojis.dot_emoji} This channel is already set as a level up channel if you want to remove it as a level up channel use the:\n{disable_level_up_channel} command {Emojis.exclamation_mark_emoji}", color=error_red)
                await ctx.respond(embed=emb)

            else:

                DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, levelup_channel=channel.id)

                emb = discord.Embed(title=f"The level up channel was set successfully {Emojis.succesfully_emoji}", 
                    description=f"""{Emojis.dot_emoji} You have successfully set the channel <#{channel.id}> as a level up channel.
                    {Emojis.dot_emoji} From now on all level up notifications will be sent to this channel.""", color=bot_colour)
                await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(title=f"There is already a level up channel assigned {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} Currently the channel <#{level_up_channel[3]}> is set as level up channel. 
                {Emojis.dot_emoji} Do you want to overwrite this one?
                {Emojis.dot_emoji} If yes select the yes button if not select the no button {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb, view=LevelUpChannelButtons(channel=channel.id))


    @commands.slash_command(name = "disable-level-up-channel", description = "Deactivate the level up channel!")
    @commands.has_permissions(administrator = True)
    async def disable_levelup_channel(self, ctx:commands.Context):

        level_up_channel = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)

        if level_up_channel[3]:
                
            DatabaseUpdates.update_level_settings(guild_id=ctx.guild.id, levelup_channel=None)

            emb = discord.Embed(title=f"The level up channel was successfully removed {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} From now on level up notifications will always be sent after level up.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:
            
            emb = discord.Embed(title=f"No level up channel was assigned {Emojis.fail_emoji}", 
                description=f"{Emojis.dot_emoji} There was no level up channel assigned so none could be removed.", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "show-level-up-channel", description = "Let them show the current level up channel!")
    async def show_levelup_channel(self, ctx:commands.Context):

        level_up_channel = DatabaseCheck.check_level_settings(guild_id=ctx.guild.id)
        
        if level_up_channel[3]:
        
            emb = discord.Embed(title=f"Here you can see the current level up channel {Emojis.help_emoji}", 
                description=f"""{Emojis.dot_emoji} The current level up channel is <#{level_up_channel[3]}> all level up notifications are sent to this channel.""", color=bot_colour)
            await ctx.respond(embed=emb)
        
        else:
            
            emb = discord.Embed(title=f"No level up channel has been set {Emojis.help_emoji}", 
                description=f"""{Emojis.dot_emoji} No level up channel has been set if you want to set one use that:\n{add_level_up_channel} command""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.command()
    async def test2(self, ctx, user:discord.User):
        
        background_color = (8, 120, 151)
        user_name = user.name
        final_xp = 5000000
        xp = 4000000
        rank = 100
        level = 100

        big_font = ImageFont.FreeTypeFont("assets/rank-card/ABeeZee-Regular.otf", 58)
        small_font = ImageFont.truetype("arial.ttf", 24)

        background = Image.new("RGBA", (885, 303), color=background_color)
        new_background = round_corner_mask(radius=50, rectangle=background, fill=255)
        background.paste(new_background[0], (0, 0), new_background[1])

        img = Image.open("assets/rank-card/card2.png").resize((867, 285))
        filtered_image = img.filter(ImageFilter.BoxBlur(4))
        new_img = round_corner_mask(radius=50, rectangle=filtered_image, fill=255)
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

        bar = Image.new('RGBA', background.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(bar)

        bar_offset_x = 304
        bar_offset_y = 179
        bar_offset_x_1 = 849
        bar_offset_y_1 = 214

        # Progress Bar
        draw.rounded_rectangle((bar_offset_x, bar_offset_y, bar_offset_x_1, bar_offset_y_1), radius=13 ,fill=(0, 0, 0, 160))

        # Filling Bar
        bar_length = bar_offset_x_1 - bar_offset_x
        progress = (final_xp - xp) * 100 / final_xp
        progress = 100 - progress
        progress_bar_length = round(bar_length * progress / 100)
        bar_offset_x_1 = bar_offset_x + progress_bar_length

        # Filling the Progress Bar
        draw.rounded_rectangle((bar_offset_x, bar_offset_y, bar_offset_x_1, bar_offset_y_1), radius=13, fill=background_color)

        xp_display_line = Image.new(mode="RGBA", size=(340, 33), color=(0, 0, 0))
        xp_display_line = round_corner_mask(radius=50, rectangle=xp_display_line, fill=160)
        offset_y = bar_offset_y_1 + 33
        background.paste(xp_display_line[0], (304, offset_y), xp_display_line[1])

        data_display = Image.new(mode="RGBA", size=(200, 33), color=(0, 0, 0))
        data_display = round_corner_mask(radius=50, rectangle=data_display, fill=160)
        background.paste(data_display[0], (655, offset_y), data_display[1])

        # Blitting Name
        draw.text((304, 97), user_name, font=big_font, fill=(255, 255, 255))

        offset_x = 315
        offset_y = offset_y + 2
        draw.text((offset_x, offset_y), f"{xp:,} / {final_xp:,} XP", font=small_font, fill=(255, 255, 255))

        offset_x = 665
        draw.text((offset_x, offset_y), f"#{rank} Lvl {level}", font=small_font, fill=(255, 255, 255))

        bar_out = Image.alpha_composite(background, bar)
        background.paste(bar_out)

        bytes = BytesIO()
        background.save(bytes, format="PNG")
        bytes.seek(0)
        dfile = discord.File(bytes, filename="card.png")
        await ctx.send(file=dfile)


def round_corner_mask(radius, rectangle, fill):
    
    bigsize = (rectangle.size[0] * 3, rectangle.size[1] * 3)
    mask_rectangle = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask_rectangle)
    draw.rounded_rectangle((0, 0)+bigsize, radius=radius, fill=fill, outline=None)
    mask = mask_rectangle.resize(rectangle.size, Image.ANTIALIAS)
    rectangle.putalpha(mask)
    return (rectangle, mask)





##################################################  Voice leveling  ####################################################


class VoiceLevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Testen und neu Optimieren
    @commands.Cog.listener()
    async def on_voice_state_update(self, member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
        
        
        if member.bot:
            return
        
        guild_id = member.guild.id
        user_id = member.id

        check_settings = DatabaseStatusCheck._level_system_status(guild_id=guild_id)
        
        
       

def setup(bot):
    bot.add_cog(LevelSystem(bot))
    bot.add_cog(VoiceLevelSystem(bot))
    