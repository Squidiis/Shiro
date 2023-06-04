
from Import_file import *
from check import check_exists
from typing import Union
from easy_pil import Editor, load_image_async, Font
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from check import *
import re
    
class BlacklistManagerButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Add to Blacklist", style=discord.ButtonStyle.blurple, custom_id="add_blacklist")
    async def add_blacklist_manager_callback_button(self, button, interaction:discord.Interaction):

        view = BlacklistManagerSelectAdd()
        view.add_item(TempBlackklistLevelSaveButton())

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Hier kannst du auswählen was du auf die Blacklist setzen möchtest", 
                description=f"""{dot_emoji} Mit den unteren select menüs kannst du auswählen was du auf die Blacklist setzen möchtest!
                {dot_emoji} Du kannst dabei frei wählen was du möchtest du kannst aber nur maximal 5 elemente pro menü auswählen""", color=shiro_colour)
            await interaction.response.edit_message(embed=emb, view=view)

        else:

            await interaction.send_message(embed=no_permissions_emb, ephemeral=True, view=None)

    @discord.ui.button(label="Remove from blacklist", style=discord.ButtonStyle.blurple, custom_id="remove_blacklist")
    async def remove_blacklist_manager_callback_button(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Hier kannst du auswählen was du von der Blacklist entfernen willst", 
                description=f"""{dot_emoji} Mit den unseren selectmenüs kannst du auswählen was von der Blacklist enfernt werden soll 
                {dot_emoji} Wenn du nicht weißt was auf der Blacklist steht kannst du entweder auf den show blacklist button drücken oder den {show_blacklist_level} command benutzen""")
            await interaction.response.send_message(embed=emb)

class BlacklistManagerChecks():

    def check_items_level(guild_id, channels = None, categories = None, roles = None, users = None):
        
        sorted_list = []
        
        if channels != None:
            item_list = channels
        elif categories != None:
            item_list = categories
        elif roles != None:
            item_list = roles
        elif users != None:
            item_list = users
        
        for item in item_list:
            
            if channels != None:
                blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, channel=item.id)
            if categories != None:
                blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, category=item.id)
            if roles != None:
                blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, role=item.id)
            if users != None:
                blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, user=item.id)
            if blacklist == None or blacklist == []:
                sorted_list.append(str(item.id))
            
        return sorted_list
    
    def check_temp_blacklist_level(guild_id:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        check_temp_blacklist = "SELECT * FROM ManageBlacklistTemp WHERE guildId = %s"
        check_temp_blacklist_values = [guild_id]
        cursor.execute(check_temp_blacklist, check_temp_blacklist_values)
        temp_blacklist = cursor.fetchone()

        return temp_blacklist

    async def configure_temp_blacklist_level(guild_id:int, operation:str, channel_id:int = None, category_id:int = None, role_id:int = None, user_id:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        temp_blacklist = BlacklistManagerChecks.check_temp_blacklist_level(guild_id=guild_id)
        print(role_id)
        if channel_id != None:
            item_list = channel_id
        if category_id != None:
            item_list = category_id
        if role_id != None:
            item_list = role_id
        if user_id != None:
            item_list = user_id
        print(item_list)
        if item_list != None:
            
            sorted_list = ", ".join(item_list)

            if channel_id != None:
                
                if temp_blacklist:
                    
                    temp_blacklist_operation = "UPDATE ManageBlacklistTemp SET channelId = %s, operation = %s WHERE guildId = %s"
                    temp_blacklist_operation_values = [sorted_list, operation, guild_id]

                else:
                    
                    temp_blacklist_operation = "INSERT INTO ManageBlacklistTemp (guildId, channelId, operation) VALUES (%s, %s, %s)"
                    temp_blacklist_operation_values = [guild_id, sorted_list, operation]

            if category_id != None:

                if temp_blacklist:

                    temp_blacklist_operation = "UPDATE ManageBlacklistTemp SET categoryId = %s, operation = %s WHERE guildId = %s"
                    temp_blacklist_operation_values = [sorted_list, operation, guild_id]
                
                else:

                    temp_blacklist_operation = "INSERT INTO ManageBlacklistTemp (guildId, categoryId, operation) VALUES (%s, %s, %s)"
                    temp_blacklist_operation_values = [guild_id, sorted_list, operation]

            if role_id != None:
                print(4)
                if temp_blacklist:
                    print("sollte")
                    temp_blacklist_operation = "UPDATE ManageBlacklistTemp SET roleId = %s, operation = %s WHERE guildId = %s"
                    temp_blacklist_operation_values = [sorted_list, operation, guild_id]

                else:

                    temp_blacklist_operation = "INSERT INTO ManageBlacklistTemp (guildId, roleId, operation) VALUES (%s, %s, %s)"
                    temp_blacklist_operation_values = [guild_id, sorted_list, operation]

            if user_id != None:
                    
                if temp_blacklist:

                    temp_blacklist_operation = "UPDATE ManageBlacklistTemp SET userId = %s, operation = %s WHERE guildId = %s"
                    temp_blacklist_operation_values = [sorted_list, operation, guild_id]

                else:

                    temp_blacklist_operation = "INSERT INTO ManageBlacklistTemp (guildId, userId, operation) VALUES (%s, %s, %s)"
                    temp_blacklist_operation_values = [guild_id, sorted_list, operation]

            cursor.execute(temp_blacklist_operation, temp_blacklist_operation_values)
            db_connect.commit()
            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)

    def delete_temp_blacklist_level(guild_id:int):
        
        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        delete_temp_blacklist = "DELETE FROM ManageBlacklistTemp WHERE guildId = %s"
        delete_temp_blacklist_values = [guild_id]
        cursor.execute(delete_temp_blacklist, delete_temp_blacklist_values)
        db_connect.commit()

class BlacklistManagerSelectAdd(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.channel_select(placeholder="Wähle die channels aus die du auf die Blacklist setzen möchtest!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.text, discord.ChannelType.voice, discord.ChannelType.forum, discord.ChannelType.news], custom_id="add_channel_blacklist_select")
    async def add_blacklist_channel_level_select(self, select, interaction:discord.Interaction):

        channel_list = BlacklistManagerChecks.check_items_level(guild_id=interaction.guild.id, channels=select.values)
        await BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", channel_id=channel_list)


    @discord.ui.channel_select(placeholder="Wähle die Kategorien aus die du auf die Blacklist setzen möchtest!", min_values=1, max_values=5, 
        channel_types=[discord.ChannelType.category], custom_id="add_category_blacklist_select")
    async def add_blacklist_category_level_select(self, select, interaction:discord.Interaction):

        category_list = BlacklistManagerChecks.check_items_level(guild_id=interaction.guild.id, categories=select.values)
        await BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", category_id=category_list)

    @discord.ui.role_select(placeholder="Wähle die rollen aus die du auf die Blacklist setzen möchtes!", min_values=1, max_values=5, custom_id="add_role_blacklist_select")
    async def add_blacklist_role_level_select(self, select, interaction:discord.Interaction):

        role_list = BlacklistManagerChecks.check_items_level(guild_id=interaction.guild.id, roles=select.values)
        print(role_list)
        await BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", role_id=role_list)
        

    @discord.ui.user_select(placeholder="Wähle die User aus die du auf die Blacklist setzen möchtest!", min_values=1, max_values=5, custom_id="add_user_blacklist_select")
    async def add_blacklist_user_level_select(self, select, interaction:discord.Interaction):

        user_list = BlacklistManagerChecks.check_items_level(guild_id=interaction.guild.id, users=select.values)
        await BlacklistManagerChecks.configure_temp_blacklist_level(guild_id=interaction.guild.id, operation="add", user_id=user_list)


class TempBlackklistLevelSaveButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Press me to complete the blacklist configuration",  
            style=discord.enums.ButtonStyle.blurple,  
            custom_id="safe_configuration")
    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            
            await interaction.response.defer()

            temp_blacklist = BlacklistManagerChecks.check_temp_blacklist_level(guild_id=interaction.guild.id)
            print(f"temp blacklist{temp_blacklist}")
            if temp_blacklist:
                channel_list, category_list, role_list, user_list = [], [], [], []
                if temp_blacklist[1] != None:
                    print(5)
                    channel_list = (list(map(int, re.findall('\d+', temp_blacklist[1]))))
                    print(channel_list)
                if temp_blacklist[2] != None: 
                    category_list = (list(map(int, re.findall('\d+', temp_blacklist[2]))))
                if temp_blacklist[4] != None:
                    role_list = (list(map(int, re.findall('\d+', temp_blacklist[4]))))
                if temp_blacklist[3] != None:
                    user_list = (list(map(int, re.findall('\d+', temp_blacklist[3]))))
                operation = temp_blacklist[5]
                
                if channel_list != None:
                    print(6)
                    for channel in channel_list:

                        if operation == "add":
                            print(7)
                            DatabaseUpdates._insert_level_system_blacklist(guild_id=temp_blacklist[0], guild_name=interaction.guild.name, channel_id=channel)

                        else:

                            DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=temp_blacklist[0], channel_id=channel)
                
                if category_list != None:

                    for category in category_list:

                        if operation == "add":

                            DatabaseUpdates._insert_level_system_blacklist(guild_id=temp_blacklist[0], guild_name=interaction.guild.name, category_id=category)
                        
                        else:

                            DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=temp_blacklist[0], category_id=category)

                if role_list != None:

                    for role in role_list:

                        if operation == "add":

                            DatabaseUpdates._insert_level_system_blacklist(guild_id=temp_blacklist[0], guild_name=interaction.guild.name, role_id=role)

                        else:

                            DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=temp_blacklist[0], role_id=role)

                if user_list != None:

                    for user in user_list:

                        if operation == "add":

                            DatabaseUpdates._insert_level_system_blacklist(guild_id=temp_blacklist[0], guild_name=interaction.guild.name, user_id=user)

                        else:

                            DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=temp_blacklist[0], user_id=user)

                BlacklistManagerChecks.delete_temp_blacklist_level(guild_id=temp_blacklist[0])
                emb = discord.Embed(title="Alles wurde auf die blacklist gesetzt")
                await interaction.edit_original_response(embed=emb, view=None)

            else:

                emb = discord.Embed(title="Es wurde nichts ausgewählt")
                await interaction.followup.send(embed=emb, view=None)



#############################################  Level Systen Settings  #############################################


class LevelSystemSettings(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    # Button to set the status of the level system to on
    @discord.ui.button(label="On/Off Level system", style=discord.ButtonStyle.blurple, custom_id="on_off_level_system")
    async def yes_button_callback_settings(self, button, interaction):

        guild_id = interaction.guild.id
        
        check_status = DatabaseCheck.check_bot_settings(guild=guild_id)

        if interaction.user.guild_permissions.administrator:

            if check_status == None:

                emb = discord.Embed(title=f"Es wurde kein eintrag gefunden {fail_emoji}", 
                    description=f"""Es wurde kein eintrag gefunden deshalb wurde einer für dein server erstellt. 
                    {dot_emoji} Das Level system wurde auch gleich automatisch eingeschalten.
                    {dot_emoji} Wenn du es deaktivieren möchtest benutzen sie diesen command einfach noch einmal""", color=error_red)
                await interaction.response.edit_message(embed=emb)

            else:

                if check_status[2] == "on":

                    new_status, status = "Ausgeschalten", "off"
                    opposite_status = "Einschalten"

                elif check_status[2] == "off":

                    new_status, status = "Eingeschalten", "on"
                    opposite_status = "Ausschalten"

                DatabaseUpdates._update_status_level(guild_id=guild_id, status=status)
                        
                emb = discord.Embed(title=f"Das Level system wurde {new_status}", 
                    description=f"""Sie haben das Level system erfolgreich {new_status}.
                    {dot_emoji} Wenn sie das level system wieder {opposite_status} wollen benutzen sie diesen command einfach noch einmal {exclamation_mark_emoji}""", color=shiro_colour)
                await interaction.response.edit_message(embed=emb, view=None)
        
        else:
            await interaction.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



######################################################  Level System level roles button  ##################################################

class LevelRolesButtons(discord.ui.View):
    def __init__(self, role_id:int, role_level:int, status:str):
        self.role_id = role_id
        self.role_level = role_level
        self.status = status
        super().__init__(timeout=None)

    # Button to override the level role 
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.blurple, custom_id="yes_button_level_role")
    async def yes_button_callback_levelroles(self, button, interaction):
        
        guild_id = interaction.guild.id 
    
        if interaction.user.guild_permissions.administrator:

            if self.role_id == None and self.role_level == None and self.status == None:

                emb = discord.Embed(title=f"Die rolle oder das Level konnte nicht überschrieben werden {fail_emoji}", 
                    description=f"""{dot_emoji} Die rolle oder das Level konnte nicht überschrieben werden da der Prozess abgelaufen ist.
                    {dot_emoji} Dies Passiert wenn man zu lange wartet um auf den Button zu reagieren.
                    {dot_emoji} Du kannst den Command einfach erneut ausführen wenn du das level oder die rolle noch immer überschreiben möchtest {exclamation_mark_emoji}""", color=shiro_colour)
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                DatabaseUpdates.update_level_roles(guild_id=guild_id, role_id=self.role_id, role_level=self.role_level, status=self.status)
                            
                emb = discord.Embed(title=f"Erfolgreiche überschreibung der level role {succesfully_emoji}", 
                    description=f"""{dot_emoji} Die level role wurde erfolgreich überschrieben. 
                    {dot_emoji} Die role <@&{self.role_id}> wird ab jetzt bei level {self.role_level} vergeben.""", color=shiro_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:
                
            await interaction.response.send_message(embed=no_permissions_emb, view=None, ephemeral=True)


    # Button to cancel the overwriting of the level role 
    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, custom_id="no_button_level_role")
    async def no_button_callback_levelroles(self, button, interaction:discord.Integration):

        if interaction.user.guild_permissions.administrator:

            check_level_roles = DatabaseCheck.check_level_system_levelroles(guild=interaction.guild.id, level_role=self.role_id, needed_level=self.role_level, status="check")

            if self.role_id == None and self.role_level == None and self.status == None:

                emb = discord.Embed(title=f"Die überschreibung der level role wurde abgebrochen",
                    description=f"""{dot_emoji} Die überschreiben der level role wurde erfolgreich abgebrochen.
                    {dot_emoji} Wenn du alle level rollen sehen möchtest verwende den {show_level_role} command.""")

            else:

                if check_level_roles[1] == self.role_id:

                    emb = discord.Embed(title=f"Die überschreibung der level role wurde abgebrochen", 
                        description=f"""{dot_emoji} Das überschreiben der level role wurde erfolgreich abgebrochen.
                        {dot_emoji} Die role <@&{self.role_id}> wird weiterhin bei errechen von level {check_level_roles[2]} vergeben""", color=shiro_colour)
                    await interaction.response.edit_message(embed=emb, view=None)

                if check_level_roles[2] == self.role_level:

                    emb = discord.Embed(title=f"Die überschreibung der level role wurde abgebrochen", 
                        description=f"""{dot_emoji} Das überschreiben der level role wurde erfolgreich abgebrochen.
                        {dot_emoji} Bei erreichen von level {self.role_level} erhält man weiterhin die rolle {check_level_roles[1]}""", color=shiro_colour)
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
    async def yes_button_callback_levelup(self, button, interaction):
            
        if interaction.user.guild_permissions.administrator:

            if self.channel == None:

                emb = discord.Embed(title=f"Der level up channel konnte nicht überschrieben werden {fail_emoji}", 
                    description=f"""{dot_emoji} Der level up channel konnte nicht überschrieben werden da der Prozess abgelaufen ist.
                    {dot_emoji} Dies Passiert wenn man zu lange wartet um auf den Button zu reagieren.
                    {dot_emoji} Du kannst den Command einfach erneut ausführen wenn du den level up channel noch immer überschreiben möchtest {exclamation_mark_emoji}""")
                await interaction.response.edit_message(embed=emb, view=None)


            else:

                DatabaseUpdates.update_level_up_channel(guild_id=interaction.guild.id, channel_id=self.channel)

                emb = discord.Embed(title=f"Der level up channel wurde erfolgreich überschrieben {succesfully_emoji}", 
                    description=f"""{dot_emoji} Der level up channel wurde erfolgreich überschrieben.
                    {dot_emoji} Ab jetzt ist der channel <#{self.channel}> als level up channel zugewiesen.""", color=shiro_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, view=None, ephemeral=True)


    # Button to cancel the overwriting of the level up channel 
    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="no_button_level_up")
    async def no_button_callback_levelup(self, button, interaction):
        
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
    async def reset_stats_button_level_yes(self, button, interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id
            DatabaseRemoveDatas._remove_level_system_stats(guild_id=guild_id)

            emb = discord.Embed(title=f"Du hast alle stats des level systems zurückgesetzt {succesfully_emoji}", 
                description=f"""{arrow_emoji} Alle user datein wurden gelöscht jeder user ist jetzt wieder level 0 und hat 0 XP.
                Es werden wieder bei aktivitäht neue enträge erstellt, wenn sie das nicht möchten stellen sie das level system aus {exclamation_mark_emoji}""", color=shiro_colour)
            await interaction.response.edit_message(embed=emb, view=None)


        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True)

    
    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="no_button_reset")
    async def reset_stats_button_level_no(self, button, interaction):

        if interaction.user.guild_permissions.administrator:
        
            emb = discord.Embed(title=f"Der vorgang wurde erfolgreich abgebrochen {succesfully_emoji}", 
                description=f"""{dot_emoji} Das resetten der stats wurde erfolgreich abgebrochen.
                Alle user behalten Ihre stats im level system.""", color=shiro_colour)
            await interaction.response.edit_message(embed=emb, view=None)
                    
        else:

            await interaction.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



#######################################  Level system Blacklist buttons  ###########################################


class ResetBlacklistLevelButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.blurple, row=1, custom_id="yes_button_level")
    async def reset_blacklist_button_level_yes(self, button, interaction, ):

        if interaction.user.guild_permissions.administrator:
            guild_id = interaction.guild.id

            DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=guild_id)

            emb = discord.Embed(title=f"Die blacklist wurde geresetet {succesfully_emoji}", 
                description=f"""{arrow_emoji} alle Channel, User, Rollen und Kategorien wurden von der Blacklist entfernt.
                Wenn du wieder Dinge auf die Blacklist setzten möchtest kannst du die Befehle wie zuvor nutzen {exclamation_mark_emoji}""", color=shiro_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)


    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, row=1, custom_id="no_button_level")
    async def reset_blacklist_button_level_no(self, button, interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Der vorgang wurde erfolgreich abgebrochen {succesfully_emoji}", 
                description=f"""{dot_emoji} Das resetten der blacklist wurde erfolgreich abgebrochen.
                Alle Channels, Rollen, Kategorien und User sind weiterhin auf der blacklist gelistet.
                {dot_emoji} Wenn du einzelne elemente von der blacklist steichen möchtest kannst du sie mit den Remove commands streichen lassen {exclamation_mark_emoji}""", color=shiro_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)

            
    @discord.ui.button(label="Shows all elements of the blacklist", style=discord.ButtonStyle.blurple, row=2, custom_id="show_blacklist_button_level")
    async def show_blacklist_button_level(self, button, interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id
            blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)
            
            channel, category, role, user = blacklist[0], blacklist[1], blacklist[2], blacklist[3] 

            emb = discord.Embed(title=f"Hier siehst du alle Elemente die auf der level system Blacklist stehen {exclamation_mark_emoji}", 
                description=f"""Hier sind alle Elemente aufgelistet die auf der level system Blacklist stehen.""", color=shiro_colour)
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

    def get_ratelimit(self, message: discord.Message):
        bucket = self.cd.get_bucket(message)
        return bucket.update_rate_limit()

    def xp_generator(self):
        xp = 20
        return xp

    @commands.Cog.listener()
    async def on_message(self, message):

        connection_db_level = DatabaseSetup.db_connector()
        my_cursor = connection_db_level.cursor()

        if self.get_ratelimit(message):
            return

        if message.content.startswith("?"):
            return

        if message.author.bot:
            return 

        # user infos 
        user_id_insert = message.author.id

        guild_id_insert = message.guild.id
        user_name_insert = message.author.name

        check_levelsystem_control = DatabaseStatusCheck._level_system_status(guild_id=guild_id_insert)
        
        if check_levelsystem_control == False:
            return
        
        if check_levelsystem_control == None:
            DatabaseUpdates._create_bot_settings(guild_id=guild_id_insert)
            return
                
        # Blacklist check
        check_blacklist = DatabaseStatusCheck._blacklist_check_text(guild_id=guild_id_insert, message_check=message)
                        
        if isinstance(message.channel, discord.TextChannel):
                    
            # Check if the blacklist returns None
            if check_blacklist != True:
                
                try:   
                            
                    # Database check for all values 
                    check_if_exists = DatabaseCheck.check_level_system_stats(guild=guild_id_insert, user=user_id_insert)
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
                                DatabaseUpdates._update_user_stats_level(guild_id=guild_id_insert, user_id=user_id_insert, level=new_level)

                                print("Data were changed")

                            except mysql.connector.Error as error:
                                print("parameterized query failed {}".format(error))
                                                                    
                            finally:   

                                level_role_check = DatabaseCheck.check_level_system_levelroles(guild=guild_id_insert, needed_level=new_level)
                                levelup_channel_check = DatabaseCheck.check_bot_settings(guild=guild_id_insert)

                                if level_role_check:

                                    role_id, level_need = level_role_check[1], level_role_check[2]

                                else:

                                    role_id, level_need = None, None

                                if level_role_check != None and levelup_channel_check[3] != None:

                                    levelup_channel = bot.get_channel(levelup_channel_check[3])

                                    level_role = message.guild.get_role(role_id)
                                    await message.author.add_roles(level_role) 

                                    await levelup_channel.send(f"<@{user_id_insert}> du hast die rolle <@&{role_id}> bekommen da du level **{level_need}** ereicht hast")
                                    await levelup_channel.send(f"Oh nice <@{user_id_insert}> you have a new level your newlevel is {new_level}")
                                
                                elif levelup_channel_check[3] == None and level_role_check != None:
                                    
                                    level_role = message.guild.get_role(role_id)
                                    await message.author.add_roles(level_role)

                                    await message.channel.send(f"Oh nice <@{user_id_insert}> you have a new level your newlevel is {new_level}")
                                    await message.channel.send(f"<@{user_id_insert}> du hast die rolle <@&{role_id}> bekommen da du level **{level_need}** ereicht hast")

                                elif levelup_channel_check[3] == None and level_role_check == None:

                                    await message.channel.send(f"Oh nice <@{user_id_insert}> you have a new level your newlevel is {new_level}") 

                                elif levelup_channel_check[3] != None and level_role_check == None:
                                        
                                    levelup_channel = bot.get_channel(levelup_channel_check[3])
                                    await levelup_channel.send(f"Oh nice <@{user_id_insert}> you have a new level your newlevel is {new_level}")
                         
                        else:

                            try:

                                DatabaseUpdates._update_user_stats_level(guild_id=guild_id_insert, user_id=user_id_insert, xp=user_has_xp)                       
                                print("Data were changed")

                            except mysql.connector.Error as error:
                                print("parameterized query failed {}".format(error))

                    else:
                            
                        DatabaseUpdates._insert_user_stats_level(guild_id=guild_id_insert, user_id=user_id_insert, user_name=user_name_insert)

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))
                    
        DatabaseSetup.db_close(cursor=my_cursor, db_connection=connection_db_level)
                


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        
        if not member.bot:

            user_id = member.id
            guild_id = member.guild.id

            check_level_system = DatabaseCheck.check_level_system_stats(guild=guild_id, user=user_id)

            if check_level_system:
                  
                if user_id == check_level_system[1] and guild_id == check_level_system[0]:
                    
                    DatabaseRemoveDatas._remove_level_system_stats(guild_id=guild_id, user_id=user_id)

                else:
                    return

        else:
            return



####################################################  User stats setting  #################################################


    # Command to give a user XP, The XP awarded can only be as high as he needs for a new level!
    @commands.slash_command(name = "give-xp", description = "Give a user a quantity of XP chosen by you!")
    @commands.has_permissions(administrator = True)
    async def give_xp_slash(self, ctx, user:Option(discord.Member, description="Select a user who should receive the xp!"),
        xp:Option(int, description="Specify a quantity of XP to be added!")):

        user_id = user.id
        guild_id = ctx.guild.id
        user_name = user.name

        if user.bot:
            await ctx.respond(embed=user_bot_emb)

        else:

            check_stats = DatabaseCheck.check_level_system_stats(guild=guild_id, user=user_id)

            if check_stats:
                
                user_level, user_xp = check_stats[2], check_stats[3]
                xp_need_next_level = 5 * (user_level ^ 2) + (50 * user_level) + 100 - user_xp

                if xp <= xp_need_next_level:

                    new_xp = user_xp + xp

                    DatabaseUpdates._update_user_stats_level(guild_id=guild_id, user_id=user_id, xp=new_xp)
                        
                    emb = discord.Embed(title=f"You have successfully passed {user_name} to {xp} XP {succesfully_emoji}", 
                        description=f"""{dot_emoji} You have transferred **{user_name}** {xp} XP **{user_name}** has from now on **{new_xp}** XP.
                        {dot_emoji} If you want to remove **{user_name}** XP again use the:\n{remove_xp} command {exclamation_mark_emoji}""", color=shiro_colour)
                    await ctx.respond(embed=emb)

                    if xp >= xp_need_next_level:

                        new_level = user_level + 1
                                            
                        DatabaseUpdates._update_user_stats_level(guild_id=guild_id, user_id=user_id, level=new_level)
                        levelup_channel_check = DatabaseCheck.check_bot_settings(guild=guild_id)

                        if levelup_channel_check != None:

                            await ctx.send(f"Oh nice <@{user_id}> you have a new level, your newlevel is {new_level}")
                            
                        else:
                            
                            levelup_channel = bot.get_channel(levelup_channel_check[3])
                            await levelup_channel.send(f"Oh nice <@{user_id}> you have a new level, your newlevel is {new_level}")
                else:
        
                    emb = discord.Embed(title=f"The XP you want to give {user_name} is too high {fail_emoji}", 
                        description=f"""{dot_emoji} The XP you want to pass to **{user_name}** is too high.
                        {dot_emoji} You can only give **{user_name}** a maximum of **{xp_need_next_level}** XP.""", color=error_red)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=guild_id, user_id=user_id, user_name=user_name)
                
                emb = discord.Embed(title=f"The user was not found {fail_emoji}", 
                    description=f"""{dot_emoji} No entry was found for **{user_name}**, so one was created.
                    {dot_emoji} **{user_name}** now starts at level 0 with 0 xp""", color=error_red)
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
                            
                    emb = discord.Embed(title=f"The XP you want to remove from {user_name} is too high {fail_emoji}", 
                        description=f"""{dot_emoji} The XP you want to remove from **{user_name}** is too high.
                        {dot_emoji} You can remove **{user_name}** only maximum **{user_xp}** XP.""", color=error_red)
                    await ctx.respond(embed=emb)

                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=guild_id, user_id=user_id, xp=new_xp)

                    emb = discord.Embed(title=f"You have successfully removed {user_name} {xp} XP {succesfully_emoji}", 
                        description=f"""{dot_emoji} You have removed **{user_name}** {xp} XP **{user_name}** has **{new_xp}** XP from now on.
                        {dot_emoji} If you want to give **{user_name}** XP again use the:\n{give_xp} command {exclamation_mark_emoji}""", color=shiro_colour)
                    await ctx.respond(embed=emb)

            else:
                    
                DatabaseUpdates._insert_user_stats_level(guild_id=guild_id, user_id=user_id, user_name=user_name)
                    
                emb = discord.Embed(title=f"The user was not found {fail_emoji}", 
                    description=f"""{dot_emoji} No entry was found for **{user_name}**, so one was created.
                    {dot_emoji} **{user_name}** now starts at level 0 with 0 xp""", color=error_red)
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

                    emb = discord.Embed(title=f"The level you want to give {user_name} is too high {fail_emoji}", 
                        description=f"""{dot_emoji} The level you want to give **{user_name}** is too high because the maximum level is **999**.
                        {dot_emoji} You can only give **{user_name}** a maximum {levels_to_maxlevel} level.""", color=error_red)
                    await ctx.respond(embed=emb)

                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=guild_id, user_id=user_id, level=new_level)

                    emb = discord.Embed(title=f"You have successfully added {user_name} {level} level {succesfully_emoji}",
                        description=f"""{dot_emoji} You gave **{user_name}** {level} level **{user_name}** now has **{new_level}** level.
                        {dot_emoji} If you want to remove **{user_name}** level again use the:\n{remove_level} command {exclamation_mark_emoji}""", colour=shiro_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=guild_id, user_id=user_id, user_name=user_name)

                emb = discord.Embed(title=f"The user was not found {fail_emoji}", 
                    description=f"""{dot_emoji} No entry was found for **{user_name}**, so one was created.
                    {dot_emoji} **{user_name}** now starts at level 0 with 0 xp""", color=error_red)
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

                    emb = discord.Embed(title=f"The number of levels you want to remove {user_name} is too high {fail_emoji}", 
                        description=f"""{dot_emoji} The number of levels you want to remove from {user_name} is too high.
                        {dot_emoji} You can remove **{user_name}** only up to **{user_level}** level.""", color=error_red)
                    await ctx.respond(embed=emb)

                
                else:

                    DatabaseUpdates._update_user_stats_level(guild_id=guild_id, user_id=user_id,  level=new_level)

                    emb = discord.Embed(title=f"You have successfully removed {user_name} {level} level {succesfully_emoji}", 
                        description=f"""{dot_emoji} You have removed **{user_name}** {level} level **{user_name}** is now level **{new_level}**
                        {dot_emoji} If you want to give **{user_name}** level again use the:\n{give_level} command {exclamation_mark_emoji}""", color=shiro_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_level(guild_id=guild_id, user_id=user_id, user_name=user_name)
                
                emb = discord.Embed(title=f"The user was not found {fail_emoji}", 
                    description=f"""{dot_emoji} No entry was found for **{user_name}**, so one was created.
                    {dot_emoji} **{user_name}** now starts at level 0 with 0 xp""", color=error_red)
                await ctx.respond(embed=emb)    
    
    
    @commands.slash_command(name = "reset-level", description = "Reset all levels and xp of everyone!")
    @commands.has_permissions(administrator = True)
    async def reset_levels_slash(self, ctx):

        guild_id = ctx.guild.id

        check_stats = DatabaseCheck.check_level_system_stats(guild=guild_id)

        if check_stats:

            emb = discord.Embed(title="Are you sure you want to reset the level system?", 
                description=f"""{help_emoji} With the buttuns you can confirm your decision!
                {dot_emoji} If you press the **Yes button** all user stats will be deleted.
                {dot_emoji} If you press the **No button** the process will be aborted.""", color=shiro_colour)
            await ctx.respond(embed=emb, view=ResetLevelStatsButton())

        else:
            
            emb = discord.Embed(title=f"No data found for this server {fail_emoji}", 
                description=f"""{dot_emoji} No data was found for this server, so nothing could be deleted.
                {help_emoji} Data is created automatically as soon as messages are sent and the level system is switched on.""", color=error_red)
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

            rank_show_infos_level = "SELECT * FROM LevelSystemStats WHERE guildId = %s ORDER BY userLevel DESC"
            rank_show_infos_levels_values = [ctx.guild.id]
            my_cursor.execute(rank_show_infos_level, rank_show_infos_levels_values)
            all_info = my_cursor.fetchall()
          
            for _, user_id_rank, user_level, user_xp, _, _ in all_info:
                    
                if user.id == user_id_rank:
                
                    for rank_count in all_info:

                        count += 1
                                                            
                        if user.id == rank_count[1]:

                            rank = count 
                            print(check_user)
            xp, level = check_user[3], check_user[2]
        
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

            #emb = discord.Embed(title=f"{ctx.user.name} rank!", description=f"All your values in the level system and your rank.", color=discord.Colour.blurple())
            #emb.add_field(name="Name:",
            #    value=f"<@{user_id}>", inline=True)
            #emb.add_field(name="Rank:", value=f"**{count_end}**", inline=False)
            #emb.add_field(name="Level:", value=f"**{user_data[1]}**")
            #emb.add_field(name="XP:", value=f"**{user_data[2]}**")
            #emb.add_field(name="Nedded-XP:", value=f"**{xp_need_next_level}**")
            #emb.set_thumbnail(url=f"{user.display_avatar.url}")
            #await ctx.respond(embed=emb)

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

        level_settings = DatabaseCheck.check_bot_settings(guild=guild_id)

        if level_settings:

            if level_settings[2] == "on":
                active_deactive = "Enabled "
            elif level_settings[2] == "off":
                active_deactive = "Deactivated"

            emb = discord.Embed(title=f"Here you can see all the settings of the level system {help_emoji}", 
                description=f"With the lower button you can set the level system, You can activate or deactivate. At the moment it is: **{active_deactive}**",color=shiro_colour)
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
    async def add_chanels_level_blacklist(self, ctx, channel:Option(Union[discord.VoiceChannel, discord.TextChannel], description="Select a channel that you want to exclude from the level system!")):

        guild_id = ctx.guild.id
        channel_id = channel.id
        guild_name = ctx.guild.name
        
        blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, channel=channel_id)

        if blacklist:

            blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)

            emb = discord.Embed(title=f"This channel is already on the blacklist {fail_emoji}", 
                description=f"""The following channels are on the blacklist:\n
                {blacklist[0]}
                If you want to remove channels from the blacklist execute this command:\n{remove_blacklist_level_channel}""", color=error_red)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates._insert_level_system_blacklist(guild_id=guild_id, guild_name=guild_name, channel_id=channel_id)

            emb = discord.Embed(title=f"This channel was successfully blacklisted {succesfully_emoji}", 
                description=f"""{dot_emoji} The channel: <#{channel_id}> was successfully blacklisted.
                {dot_emoji} If you want to remove it again use this command:\n{remove_blacklist_level_channel}""", color=shiro_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-channel-level-blacklist", description = "Remove a channel from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_channel_blacklist(self, ctx, channel:Option(Union[discord.TextChannel, discord.VoiceChannel], description="Select a channel to remove from the blacklist!")):
        
        guild_id = ctx.guild.id
        channel_id = channel.id

        blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, channel=channel_id)

        if blacklist:
                
            DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=guild_id, channel_id=channel_id)

            emb = discord.Embed(title=f"The channel was removed from the blacklist {succesfully_emoji}", 
                description=f"""{dot_emoji} The channel has been successfully removed from the blacklist if you want to add it again use the: {add_blacklist_level_channel} command.
                {dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} command""", color=shiro_colour)
            await ctx.respond(embed=emb)
        
        else:
            
            blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)

            emb = discord.Embed(title=f"This channel is not on the blacklist {fail_emoji}", 
                description=f"""{dot_emoji} The channel: <#{channel_id}> is not blacklisted.
                The following channels are blacklisted:\n\n{blacklist[0]}""", color=error_red)
            await ctx.respond(embed=emb)
        
    
    @commands.slash_command(name = "add-category-level-blacklist", description = "Exclude categories from the level system and all channels that belong to them!")
    @commands.has_permissions(administrator = True)
    async def add_category_blacklist(self, ctx, category:Option(discord.CategoryChannel, description="Select a category that you want to exclude from the level system!")):

        category_id = category.id
        guild_id = ctx.guild.id
        guild_name = ctx.guild.name

        blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, category=category_id)
        
        if blacklist:
            
            blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)
                
            emb = discord.Embed(title=f"This category is already on the blacklist {fail_emoji}", 
                description=f"""The following categories are on the blacklist:\n
                {blacklist[1]}
                If you want to remove categories from the blacklist execute this command:\n{remove_blacklist_level_category}""", color=error_red)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates._insert_level_system_blacklist(guild_id=guild_id, guild_name=guild_name, category_id=category_id)
            
            emb = discord.Embed(title=f"This category was successfully blacklisted {succesfully_emoji}", 
                description=f"""{dot_emoji} The category: <#{category_id}> was successfully blacklisted.
                {dot_emoji} If you want to remove them again use this command:\n{remove_blacklist_level_category}""", color=shiro_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-category-level-blacklist", description = "Remove categories from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_category_blacklist(self, ctx, category:Option(discord.CategoryChannel, description="Select a category to remove from the blacklist!")):

        guild_id = ctx.guild.id
        category_id = category.id

        blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, category=category_id)

        if blacklist:
            
            DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=guild_id, category_id=category_id)
            
            emb = discord.Embed(title=f"The category was removed from the blacklist {succesfully_emoji}", 
                description=f"""{dot_emoji} The category has been successfully removed from the blacklist if you want to add it again use the: {add_blacklist_level_category} command.
                {dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} comamnd""", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)

            emb = discord.Embed(title=f"This category is not on the blacklist{fail_emoji}", 
                description=f"""{dot_emoji} The category: <#{category_id}> is not on the blacklist.
                The following categories are blacklisted:\n\n{blacklist[1]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "add-role-level-blacklist", description = "Choose a role that you want to exclude from the level system!")
    @commands.has_permissions(administrator = True)
    async def add_role_blacklist(self, ctx, role:Option(discord.Role, description="Select a role that you want to exclude from the level system!")):

        guild_id = ctx.guild.id
        role_id = role.id
        guild_name = ctx.guild.name

        blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, role=role_id)

        if blacklist:
     
            blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)

            emb = discord.Embed(title=f"This role is already on the blacklist {fail_emoji}", 
                description=f"""The following roles are on the blacklist:\n\n{blacklist[2]}
                If you want to remove roles from the blacklist execute this command:\n{remove_blacklist_level_role}""", color=error_red)
            await ctx.respond(embed=emb)
        
        else:
            
            DatabaseUpdates._insert_level_system_blacklist(guild_id=guild_id, guild_name=guild_name, role_id=role_id)
            
            emb = discord.Embed(title=f"This role has been successfully blacklisted {succesfully_emoji}", 
                description=f"""{dot_emoji} The role: <#{role_id}> has been successfully blacklisted.
                {dot_emoji} If you want to remove them again use this command:\n{remove_blacklist_level_role}""", color=shiro_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-role-level-blacklist", description = "Remove a role from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_role_blacklist(self, ctx, role:Option(discord.Role, description="Select a role you want to remove from the blacklist!")):
        
        guild_id = ctx.guild.id
        role_id = role.id

        blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, role=role_id)

        if blacklist:

            DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=guild_id, role_id=role_id)
            
            emb = discord.Embed(title=f"The role was removed from the blacklist {succesfully_emoji}", 
                description=f"""{dot_emoji} The role has been successfully removed from the blacklist if you want to add it again use the: {add_blacklist_level_role} command.
                {dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} comamnd""", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)

            emb = discord.Embed(title=f"This role is not blacklisted {fail_emoji}", 
                description=f"""{dot_emoji} The role: <@&{role_id}> is not blacklisted.
                The following roles are blacklisted:\n\n{blacklist[2]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name= "add-user-level-blacklist", description = "Choose a user that you want to exclude from the level system!")
    @commands.has_permissions(administrator = True)
    async def add_user_level_blacklsit(self, ctx, user:Option(discord.User, description="Select a user that you want to exclude from the level system!")):

        guild_id = ctx.guild.id 
        user_id = user.id 
        guild_name = ctx.guild.name 

        blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, user=user_id)

        if user.bot:
            await ctx.respond(embed=user_bot_emb, view=None)
        
        else:

            if blacklist:

                blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)

                emb = discord.Embed(title=f"This user is already on the blacklist {fail_emoji}", 
                    description=f"""The following users are on the blacklist:\n\n{blacklist[3]}
                    If you want to remove users from the blacklist execute this command:\n{remove_blacklist_level_user}""", color=error_red)
                await ctx.respond(embed=emb)

            else:   

                DatabaseUpdates._insert_level_system_blacklist(guild_id=guild_id, guild_name=guild_name, user_id=user_id)

                emb = discord.Embed(title=f"This user was successfully blacklisted {succesfully_emoji}", 
                    description=f"""{dot_emoji} The user: <@{user_id}> was successfully blacklisted.
                    If you want to remove it again use this command:\n{remove_blacklist_level_user}""", color=shiro_colour)
                await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-user-level-blacklist", description="Remove a user from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_user_level_blacklist(self, ctx, user:Option(discord.User, description="Select a user you want to remove from the blacklist!")):

        guild_id = ctx.guild.id
        user_id = user.id
        
        blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id, user=user_id)

        if blacklist:
            
            DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=guild_id, user_id=user_id)

            emb = discord.Embed(title=f"The user was removed from the blacklist {succesfully_emoji}", 
                description=f"""{dot_emoji} The user has been successfully removed from the blacklist if you want to add him again use the: {add_blacklist_level_user} command.
                {dot_emoji} If you want to see what else is on the blacklist then use that: {show_blacklist_level} comamnd""", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)

            emb = discord.Embed(title=f"This user is not on the blacklist {fail_emoji}", 
                description=f"""The user: <@{user_id}> is not on the blacklist.
                The following users are on the blacklist:\n\n{blacklist[3]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "reset-level-blacklist", description="Reset the blacklist of the level system and remove all entries!")
    @commands.has_permissions(administrator = True)
    async def reset_blacklist(self, ctx):

        guild_id = ctx.guild.id

        blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id)

        if blacklist:

            emb = discord.Embed(title="Are you sure you want to remove everything from the blacklist?", 
                description=f"""{help_emoji} With the buttuns you can confirm your decision!!
                {dot_emoji} If you press the **Yes button** all channels, categories, users and roles will be removed from the blacklist.
                {dot_emoji} If you press the **No button** the process will be aborted.
                {dot_emoji} The **Shows all elements button** shows you what is currently on the blacklist.""", color=shiro_colour)
            await ctx.respond(embed=emb, view=ResetBlacklistLevelButton())
        
        else:

            emb = discord.Embed(title=f"There is nothing on the blacklist {fail_emoji}", 
                description=f"""{dot_emoji} The blacklist could not be reset because nothing is stored on it.
                {dot_emoji} If you want to blacklist something use one of these commands:
                
                {arrow_emoji} {add_blacklist_level_channel}
                {arrow_emoji} {add_blacklist_level_category}
                {arrow_emoji} {add_blacklist_level_role}
                {arrow_emoji} {add_blacklist_level_user}""", color=shiro_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "manage-level-blacklist")
    async def manage_level_blacklist(self, ctx):

        emb = discord.Embed(title=f"Wilkommen im blacklist manager {settings_emoji}", 
            description=f"""{help_emoji} Mit den Beiden Buttons kannst du auswählen ob du etwas auf die Blacklist setzen möchtest oder etwas entfernen möchtest!
            {dot_emoji} Sobalt du etwas ausgewählt hast werden dir select menüs angezeigt.
            {dot_emoji} Mit diesen kannst du auswählen was du auf die blacklist setzen oder entfernen möchtest.""", color=shiro_colour)
        await ctx.respond(embed=emb, view=BlacklistManagerButtons())


   
    @commands.slash_command(name = "show-level-blacklist", description = "Shows you everything that is blacklisted!")
    async def show_blacklist(self, ctx):

        guild_id = ctx.guild.id

        blacklist = ShowBlacklist._show_blacklist_level(guild_id=guild_id)
        channel, category, role, user = blacklist[0], blacklist[1], blacklist[2], blacklist[3] 

        emb = discord.Embed(title=f"Here you can see the complete level system blacklist", 
            description=f"""Here you can see everything that is on the level system blacklist:{exclamation_mark_emoji}
            """, color=shiro_colour)
        emb.add_field(name=f"{arrow_emoji} All Channels on the Blacklist", value=f"{channel}", inline=False)
        emb.add_field(name=f"{arrow_emoji} All Categories on the Blacklist", value=f"{category}", inline=False)
        emb.add_field(name=f"{arrow_emoji} All Roles on the Blacklist", value=f"{role}", inline=False)
        emb.add_field(name=f"{arrow_emoji} All Users on the Blacklist", value=f"{user}", inline=False)
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

        emb_level_0 = discord.Embed(title=f"The level you want to set is 0 {fail_emoji}", 
            description=f"""{dot_emoji} The level to vest a level role must be at least **1**.""", color=error_red)
        emb_higher = discord.Embed(title=f"The level you want to set for the level role is too high {fail_emoji}", 
            description=f"""{dot_emoji} The level you want to set for the level role is too high you can only set a value that is below or equal to **999**.""", color=error_red)

        if level_roles == None:
            
            if level <= 999:
                         
                DatabaseUpdates._insert_level_roles(guild_id=guild_id, role_id=role_id, level=level, guild_name=guild_name)

                emb = discord.Embed(title=f"The role was assigned successfully {succesfully_emoji}", 
                    description=f"""{dot_emoji} The role <@&{role_id}> was successfully assigned to the level {level}.
                    {dot_emoji} As soon as a user reaches {level} he gets the <@&{role_id}> role. {exclamation_mark_emoji}""", color=shiro_colour)
                await ctx.respond(embed=emb)

            await ctx.respond(embed=emb_level_0) if level == 0 else None

            await ctx.respond(embed=emb_higher) if  level > 999 else None 

        else:

            check_same = DatabaseCheck.check_level_system_levelroles(guild=guild_id, level_role=role_id, needed_level=level)
                
            if check_same:

                same_emb = discord.Embed(title=f"This role has already been set at this level {fail_emoji}",
                    description=f"""{dot_emoji} The role <@&{role_id}> is already assigned to the level {level}.
                    {dot_emoji} If you want to change it you can assign this role to another level or another role to this level {exclamation_mark_emoji}""", color=error_red)
                await ctx.respond(embed=same_emb)

            else:
                
                if role_id == level_roles[1]:

                    level_needed = level_roles[2]
        
                    emb = discord.Embed(title=f"This role is already assigned {fail_emoji}", 
                        description=f"""{dot_emoji} Do you want to override the required level for this role? 
                        {dot_emoji} The role <@&{role_id}> is currently assigned at level **{level_needed}**.
                        {dot_emoji} If you want to override the required level for this role select the yes buttons otherwise the no button {exclamation_mark_emoji}""", color=shiro_colour)
                    await ctx.respond(embed=emb, view=LevelRolesButtons(role_id=role_id, role_level=level, status="role"))
    
                elif level == level_roles[2]:
                    
                    level_role = level_roles[1]

                    emb = discord.Embed(title=f"This level is already assigned {fail_emoji}", 
                        description=f"""{dot_emoji} Do you want to overwrite the role for this level?
                        {dot_emoji} For the level {level} the role <@&{level_role}> is currently assigned.
                        {dot_emoji} If you want to override the role for this level select the yes buttons otherwise select the no button {exclamation_mark_emoji}""", color=shiro_colour)
                    await ctx.respond(embed=emb, view=LevelRolesButtons(role_id=role_id, role_level=level, status="level"))   



    @commands.slash_command(name = "remove-level-role", description = "Choose a role that you want to remove as a level role!")
    @commands.has_permissions(administrator = True)
    async def remove_level_role(self, ctx, role:Option(discord.Role, description="Select a level role that you want to remove")):
        
        guild_id = ctx.guild.id
        role_id = role.id

        level_roles = DatabaseCheck.check_level_system_levelroles(guild=guild_id, level_role=role_id)

        if level_roles:
            
            DatabaseRemoveDatas.remove_level_system_level_roles(guild_id=guild_id, role_id=role_id)

            emb = discord.Embed(f"This role has been removed as a level role {succesfully_emoji}", 
                description=f"""{dot_emoji} The role <@&{role_id}> was successfully removed as a level role.
                {dot_emoji} If you want to add them again you can do this with the {add_level_role} command {exclamation_mark_emoji}""", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:

            level_roles = DatabaseCheck.check_level_system_levelroles(guild=guild_id, status="level_role")

            if level_roles:
                
                result_strings = []
                for guild_id, role_id, level, _ in level_roles:
                    result_strings.append(f"{dot_emoji} <@&{role_id}> we assign on level: {level}")

                result = '\n'.join(result_strings)

            else:

                result = f"{dot_emoji} No level roles have been assigned!"

            emb = discord.Embed(title=f"This role is not defined as a level role {fail_emoji}", 
                description=f"""{dot_emoji} This role cannot be removed because it is not set as a level role.
                {dot_emoji} Here you can see all the level rolls.\n\n{result}""", color=error_red)
            await ctx.respond(embed=emb)



    @commands.slash_command(name = "show-all-level-roles", description = "View all rolls that are available with a level!")
    async def show_all_level_roles(self, ctx):

        guild_id = ctx.guild.id

        level_roles = DatabaseCheck.check_level_system_levelroles(guild=guild_id, status="level_role")
        
        if level_roles:
            
            result_strings = []
            for guild_id, role_id, level, _ in level_roles:
                result_strings.append(f"{dot_emoji} <@&{role_id}> you get from level: {level}")

            result = '\n'.join(result_strings)
            
            emb = discord.Embed(title="Here you can find all level roles", 
                description=f"{help_emoji} Here you can see all level rolls sorted by level in descending order:\n\n {result}", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:
            emb = discord.Embed(title=f"No level rolls have been added yet", 
                description=f"{help_emoji} There are no level rolls added yet if you want to add some use the {add_level_role} command", color=shiro_colour)
            await ctx.respond(embed=emb)

       
    
#############################################  Level up channel settings  #################################


    @commands.slash_command(nanme = "set-level-up-channel", description = "Set a channel for the level up notifications!")
    @commands.has_permissions(administrator = True)
    async def set_levelup_channel(self, ctx, channel:Option(discord.TextChannel, description="Select a channel in which the level up message should be sent")):

        guild_id = ctx.guild.id
        channel_id = channel.id

        level_up_channel = DatabaseCheck.check_bot_settings(guild=guild_id)

        if None == level_up_channel[3]:
       
            DatabaseUpdates.update_level_up_channel(guild_id=guild_id, channel_id=channel_id)

            emb = discord.Embed(title=f"The level up channel was set successfully {succesfully_emoji}", 
                description=f"""{dot_emoji} You have successfully set the channel <#{channel_id}> as a level up channel.
                {dot_emoji} From now on all level up notifications will be sent to this channel.""", color=shiro_colour)
            await ctx.respond(embed=emb)

        elif channel_id == level_up_channel[3]:

            emb = discord.Embed(title=f"This channel is already assigned as level up channel {fail_emoji}", 
                description=f"{dot_emoji} This channel is already set as a level up channel if you want to remove it as a level up channel use the:\n{disable_level_up_channel} command {exclamation_mark_emoji}", color=error_red)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(title=f"There is already a level up channel assigned {fail_emoji}", 
                description=f"""{dot_emoji} Currently the channel <#{level_up_channel[3]}> is set as level up channel. 
                {dot_emoji} Do you want to overwrite this one?
                {dot_emoji} If yes select the yes button if not select the no button {exclamation_mark_emoji}""", color=shiro_colour)
            await ctx.respond(embed=emb, view=LevelUpChannelButtons(channel=channel_id))


    @commands.slash_command(name = "disable-level-up-channel", description = "Deactivate the level up channel!")
    @commands.has_permissions(administrator = True)
    async def disable_levelup_channel(self, ctx):

        guild_id = ctx.guild.id

        level_up_channel = DatabaseCheck.check_bot_settings(guild=guild_id)

        if level_up_channel[3] != None:
                
            DatabaseUpdates.update_level_up_channel(guild_id=guild_id, channel_id=None)

            emb = discord.Embed(title=f"The level up channel was successfully removed {succesfully_emoji}", 
                description=f"""{dot_emoji} From now on level up notifications will always be sent after level up.""", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:
            
            emb = discord.Embed(title=f"No level up channel was assigned {fail_emoji}", 
                description=f"{dot_emoji} There was no level up channel assigned so none could be removed.", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "show-level-up-channel", description = "Let them show the current level up channel!")
    async def show_levelup_channel(self, ctx):

        level_up_channel = DatabaseCheck.check_bot_settings(guild=ctx.guild.id)
        
        if None != level_up_channel[3]:
        
            emb = discord.Embed(title=f"Here you can see the current level up channel {help_emoji}", 
                description=f"""{dot_emoji} The current level up channel is <#{level_up_channel[3]}> all level up notifications are sent to this channel.""", color=shiro_colour)
            await ctx.respond(embed=emb)
        
        else:
            
            emb = discord.Embed(title=f"No level up channel has been set {help_emoji}", 
                description=f"""{dot_emoji} No level up channel has been set if you want to set one use that:\n{add_level_up_channel} command""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command()
    async def test(self, ctx, user:Option(discord.Member)):

        level = 999
        rank = 544
        final_xp = 1000
        xp = 400
        user_name = user.name

        # Text fronts
        big_font = ImageFont.FreeTypeFont("assets/rank-card/ABeeZee-Regular.otf", 55)
        medium_font = ImageFont.FreeTypeFont("assets/rank-card/ABeeZee-Regular.otf", 35)
        rank_font = ImageFont.FreeTypeFont("assets/rank-card/ABeeZee-Regular.otf", 25)
        small_font = ImageFont.FreeTypeFont("assets/rank-card/ABeeZee-Regular.otf", 30)
        very_small_fron = ImageFont.FreeTypeFont("assets/rank-card/ABeeZee-Regular.otf", 20)

        img = Image.open("assets/rank-card/card2.png")
        new = Image.new('RGBA', img.size, (255, 255, 255, 0))

        draw = ImageDraw.Draw(new)
        rectangle_width = 850
        rectangle_height = 270
        left = img.width // 2 - rectangle_width // 2
        top = img.height // 2 - rectangle_height // 2
        right = left + rectangle_width
        bottom = top + rectangle_height
        draw.rectangle([(left, top), (right, bottom)], fill=(0, 0, 0, 130))
        out = Image.alpha_composite(img, new)

        pfp = BytesIO(await user.display_avatar.read())
        profile = Image.open(pfp).resize((170, 170))
        bigsize = (profile.size[0] * 3, profile.size[1] * 3)
        mask = Image.new("L", bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0)+ bigsize, 255)
        mask = mask.resize(profile.size, Image.ANTIALIAS)
        profile.putalpha(mask)

        img.paste(out)
        img.paste(profile, (20, 20), mask=mask)

        # Bar
        bar = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(bar)

        bar_offset_x = 210
        bar_offset_y = 230
        bar_offset_x_1 = 820
        bar_offset_y_1 = 270
        circle_size = bar_offset_y_1 - bar_offset_y 
        circle_size = bar_offset_y_1 - bar_offset_y  # Diameter

        # Progress Bar
        draw.rectangle((bar_offset_x, bar_offset_y, bar_offset_x_1, bar_offset_y_1), fill=(0, 0, 0, 160))
        draw.ellipse((bar_offset_x - circle_size // 2, bar_offset_y, bar_offset_x + circle_size // 2, bar_offset_y_1), fill=(0, 0, 0, 160))
        draw.ellipse((bar_offset_x_1 - circle_size // 2, bar_offset_y, bar_offset_x_1 + circle_size // 2, bar_offset_y_1), fill=(0, 0, 0, 160))

        # Filling Bar
        bar_length = bar_offset_x_1 - bar_offset_x
        progress = (final_xp - xp) * 100 / final_xp
        progress = 100 - progress
        progress_bar_length = round(bar_length * progress / 100)
        bar_offset_x_1 = bar_offset_x + progress_bar_length

        # Filling the Progress Bar
        draw.rectangle((bar_offset_x, bar_offset_y, bar_offset_x_1, bar_offset_y_1), fill="#11ebf2")
        draw.ellipse((bar_offset_x - circle_size // 2, bar_offset_y, bar_offset_x + circle_size // 2, bar_offset_y_1), fill="#11ebf2")
        draw.ellipse((bar_offset_x_1 - circle_size // 2, bar_offset_y, bar_offset_x_1 + circle_size // 2, bar_offset_y_1), fill="#11ebf2")

        text_size = draw.textsize(f"/ {final_xp} XP", font=small_font)    
        offset_x = 810 - text_size[0]
        offset_y = bar_offset_y - text_size[1] - 10
        draw.text((offset_x, offset_y), f"/ {final_xp:,} XP", font=small_font, fill="#727175")

        text_size = draw.textsize(f"{xp:,}", font=small_font)
        offset_x -= text_size[0] + 8
        draw.text((offset_x, offset_y), f"{xp:,}", font=small_font, fill="#fff")


        text_size = draw.textsize(f"Rank:", font=rank_font)
        offset_x = 205
        draw.text((offset_x, offset_y + 5), f"Rank:", font=rank_font, fill="#fff")

        text_size = draw.textsize(f"#{rank}", font=medium_font)
        offset_x = 275
        draw.text((offset_x, offset_y - 5), f"#{rank}", font=medium_font, fill="#fff")

        text_size = draw.textsize(str(level), font=big_font)
        if level <= 9:
            offset_x = 205 - text_size[1]
        elif level <= 99:
            offset_x = 174 - text_size[1]
        elif level <= 999:
            offset_x = 141 - text_size[1]
        offset_y = bar_offset_y - 10
        draw.text((offset_x, offset_y), str(level), font=big_font, fill="white")

        text_size = draw.textsize("LVL", font=very_small_fron)
        if level <= 9:
            offset_x = 144
        elif level <= 99:
            offset_x = 128
        elif level <= 999:
            offset_x = 108
        draw.text((offset_x, offset_y - 15), "LVL", font=very_small_fron, fill="white")
        
        # Blitting Name
        text_size = draw.textsize(user_name, font=big_font)
        offset_x = 200
        offset_y = 80
        draw.text((offset_x, offset_y), user_name, font=big_font, fill="#fff")

        bar_out = Image.alpha_composite(img, bar)
        img.paste(bar_out)

        bytes = BytesIO()
        img.save(bytes, format="PNG")
        bytes.seek(0)
        dfile = discord.File(bytes, filename="card.png")
        await ctx.respond(file=dfile)




##################################################  Voice leveling  ####################################################


class VoiceLevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Testen und neu Optimieren
    @commands.Cog.listener()
    async def on_voice_state_update(self, member:discord.Member, before: discord.VoiceState, after:discord.VoiceState):
        
        if member.bot:
            return
        
        guild_id = member.guild.id
        user_id = member.id

        channel_id = before.channel.id
        print(channel_id)
        print(before)

        check_levelsys_control = DatabaseStatusCheck._level_system_status(guild_id=guild_id)
        print(check_levelsys_control)
        if check_levelsys_control == False:
            return
        
        elif check_levelsys_control == None:
            DatabaseUpdates._create_bot_settings(guild_id=guild_id)
        
       

def setup(bot):
    bot.add_cog(LevelSystem(bot))
    bot.add_cog(VoiceLevelSystem(bot))
    