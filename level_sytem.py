

import mysql.connector

from Import_file import *


class level_system_db():
    def levelconnect():

        level_connector = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv("sql_passwort"), database=os.getenv('database_level'))
        return level_connector

    def db_close(cursor, db_connection):

        if db_connection.is_connected:
            
            db_connection.close()
            cursor.close()

        else:
            pass


class level_system_control_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Aktivieren", style=discord.ButtonStyle.blurple, custom_id="yes_button_control")
    async def yes_button_callback_control(self, button, interaction):

        guild_id = str(interaction.guild.id)
        level_control_setup = "on"

        levelsystem_button_connect = level_system_db.levelconnect()
        my_cursor = levelsystem_button_connect.cursor()

        if interaction.user.guild_permissions.administrator:
                
            if all_infos_setup_level_control[1] == "on":

                emb_already_active = discord.Embed(title="Already active", 
                    description="The level system is already active if you want to disable it execute this command again and press the disable button", color=error_red)
                await interaction.response.edit_message(embed=emb_already_active, view=None)

            else:

                try: 

                    yes_level_control = f"UPDATE level_control SET control = %s WHERE guild_ID = %s"
                    yes_level_control_values = (level_control_setup, guild_id)
                    my_cursor.execute(yes_level_control, yes_level_control_values)
                    levelsystem_button_connect.commit()

                except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))

                finally:

                    level_system_db.db_close(cursor=my_cursor, db_connection=levelsystem_button_connect)
                    
                emb_yes = discord.Embed(title="Aktiviert", 
                    description="The level system has been successfully activated now all messages are rewarded with XP", color=discord.Colour.brand_green())
                await interaction.response.edit_message(embed=emb_yes, view=None)


    @discord.ui.button(label="Deaktivieren", style=discord.ButtonStyle.blurple, custom_id="no_button_control")
    async def  no_button_callback_control(self, button, interaction):
        
        guild_id = str(interaction.guild.id)
        level_control_setup = "off"
        
        levelsystem_button_connect = level_system_db.levelconnect()
        my_cursor = levelsystem_button_connect.cursor()

        if all_infos_setup_level_control[1] == "off":
    
            emb_already_deactivated = discord.Embed(title="Already deactivated", 
                description="The level system is already disabled if you want to enable it run this command again and press the enable button", color=error_red)
            await interaction.response.edit_message(embed=emb_already_deactivated, view=None)

        else:

            try: 
                        
                no_level_control = f"UPDATE level_control SET control = %s WHERE guild_ID = %s"
                no_level_control_values = (level_control_setup, guild_id)

                my_cursor.execute(no_level_control, no_level_control_values)

                levelsystem_button_connect.commit()

            except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))

            finally:

                level_system_db.db_close(cursor=my_cursor, db_connection=levelsystem_button_connect)

            emb_no = discord.Embed(title="You have successfully disabled the level system", 
                description="""The level system has been successfully deactivated now no more XP will be awarded all data will be preserved. 
                When the level system is reactivated, everyone will have their earned XP and level back.""", color=discord.Colour.brand_green())
            await interaction.response.edit_message(embed=emb_no, view=None)



class level_roles_buttons_role(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray, custom_id="yes_button_role")
    async def yes_button_callback(self, button, interaction):
        
        guild_id = str(interaction.guild.id)

        set_level_roles_connect_button = level_system_db.levelconnect()
        my_cursor = set_level_roles_connect_button.cursor()
        
        if interaction.custom_id == "yes_button_role":

            if interaction.user.guild_permissions.administrator:

                try:

                    overwritten_role_level = f"UPDATE level_roles SET role_level = %s WHERE guild_ID = %s AND role_id = %s"
                    overwritten_role_level_values = [global_new_level_role, guild_id, global_level_roles_id]

                    my_cursor.execute(overwritten_role_level, overwritten_role_level_values)
                    set_level_roles_connect_button.commit()

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))

                finally:

                    level_system_db.db_close(cursor=my_cursor, db_connection=set_level_roles_connect_button)
                        
                emb_yes_role = discord.Embed(title="Erfolgreich überschrieben",
                    description=f"Das benötigte level für diese rolle wurde erfolgreich überschrieben, die rolle <@&{global_level_roles_id}> ist bei dem level {global_new_level_role} erhältlich", color=discord.Colour.brand_green())
                await interaction.response.edit_message(embed = emb_yes_role, view = None)

            else:
                
                await interaction.response.send_message(embed=no_author_emb ,view=None, ephemeral=True)

    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="no_button_role")
    async def no_button_callback(self, button, interaction):

        if interaction.user.guild_permissions.administrator:
        
            emb_no = discord.Embed(title="Die Überschreibung wurde abgebrochen", description="Das überschreiben des benötigten levels dieser rolle wurde erfolgreich abgebrochen", color=discord.Colour.green())
            await interaction.response.edit_message(embed = emb_no, view = None)

        else:
                
            await interaction.response.send_message(embed=no_author_emb ,view=None, ephemeral=True)



class level_roles_buttons_level(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray, custom_id="yes_button_level")
    async def yes_button_callback(self, button, interaction):
        
        guild_id = str(interaction.guild.id)

        set_level_roles_connect_button = level_system_db.levelconnect()
        my_cursor = set_level_roles_connect_button.cursor()
        
        if interaction.user.guild_permissions.administrator:

            try:

                overwritten_role_level = f"UPDATE level_roles SET role_id = %s WHERE guild_ID = %s AND role_level = %s"
                overwritten_role_level_values = [global_level_roles_id, guild_id, global_new_level_role]

                my_cursor.execute(overwritten_role_level, overwritten_role_level_values)
                set_level_roles_connect_button.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:

                level_system_db.db_close(cursor=my_cursor, db_connection=set_level_roles_connect_button)
                        
            emb_yes_level = discord.Embed(title="Erfolgreich überschrieben", 
                description=f"Die Rolle für dieses Level wurde erfolgreich überschrieben, die rolle <@&{global_level_roles_id}> ist bei dem level {global_new_level_role} erhältlich", color=discord.Colour.brand_green())
            await interaction.response.edit_message(embed = emb_yes_level, view = None)

        else:
                
            await interaction.response.send_message(embed=no_author_emb ,view=None, ephemeral=True)

    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="No_button_level")
    async def no_button_callback(self, button, interaction):

        if interaction.user.guild_permissions.administrator:

            emb_no = discord.Embed(title="Die Überschreibung wurde abgebrochen", description="Das überschreiben des benötigten levels dieser rolle wurde erfolgreich abgebrochen", color=discord.Colour.green())
            await interaction.response.edit_message(embed = emb_no, view = None)

        else:
            
            await interaction.response.send_message(embed=no_author_emb ,view=None, ephemeral=True)



class levelup_channel_buttons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray, custom_id="Yes_button_levelup_channel")
    async def yes_button_callback_levelup(self, button, interaction):
        	
        levelup_button_connect = level_system_db.levelconnect()
        my_cursor = levelup_button_connect.cursor()

        channel_id = levelup_channel_id
        guild_id = str(interaction.guild.id)

        if interaction.custom_id == "Yes_button_levelup_channel":
            
            if interaction.user.guild_permissions.administrator:

                try:

                    update_levelup_channel = "UPDATE level_control SET levelup_channel = %s WHERE guild_ID = %s"
                    update_levelup_channel_values = [channel_id, guild_id]
                    my_cursor.execute(update_levelup_channel, update_levelup_channel_values)

                    levelup_button_connect.commit()

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))

                finally:

                    level_system_db.db_close(cursor=my_cursor, db_connection=levelup_button_connect)

                yes_button_emb = discord.Embed(title="Du hast erfolgreich den level up channel überschrieben", 
                    description=f"Der aktuelle level up channel ist <#{channel_id}> alle nachrichten das man ein level aufgestiegen ist werden in diesen Channel gesendet", color=discord.Colour.brand_green())
                await interaction.response.edit_message(embed = yes_button_emb, view=None)

            else:

                await interaction.response.send_message(embed=no_author_emb ,view=None, ephemeral=True)


    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="No_button_levelup_channel")
    async def no_button_callback_levelup(self, button, interaction):
        
        if interaction.user.guild_permissions.administrator:

            no_button_emb = discord.Embed(title="Erfolgreich abgebrochen", 
                description=f"Du hast erfolgreich die Überschreibung des level up channels abgebrochen",color = discord.Colour.brand_green())
            await interaction.response.edit_message(embed = no_button_emb, view=None)
        
        else:
            
            await interaction.response.send_message(embed=no_author_emb ,view=None, ephemeral=True)



class reset_level_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray, custom_id="yes_button_reset")
    async def yes_button_callback_levelreset(self, button, interaction):

        if interaction.user.guild_permissions.administrator:
            
            reset_button_connect = level_system_db.levelconnect()
            my_cursor = reset_button_connect.cursor()
            
            if interaction.user.id == global_author_id_resetlevel:

                try:
                        
                    reset_guild = "DELETE FROM levelsystem_info WHERE guild_ID = %s"
                    reset_guild_values = [global_guild_id_reset_level]

                    my_cursor.execute(reset_guild, reset_guild_values)

                    reset_button_connect.commit()

                    successful_emb = discord.Embed(title="You have successfully reset all levels and XP", 
                        description="All levels and xp are now reset and can now also no longer be made!", color=funpark_colour)
                    await interaction.response.edit_message(embed=successful_emb, view=None)

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))

                finally:

                    level_system_db.db_close(cursor=my_cursor, db_connection=reset_button_connect)

        else:

            emb = discord.Embed(title="You are not authorized!", description="You are not the person who carried out this order", color=error_red)
            await interaction.response.send_message(embed=emb, ephemeral=True)

    
    @discord.ui.button(label="No", style=discord.ButtonStyle.gray, custom_id="no_button_reset")
    async def no_button_callback_levelreset(self, button, interaction):

        if interaction.user.guild_permissions.administrator:
            
        
            not_sure_emb = discord.Embed(title="The command was successfully aborted", 
                description="If you are sure you can execute the command again at any time!", color=discord.Colour.brand_green())
            await interaction.response.edit_message(embed=not_sure_emb, view=None)
                    
        else:

            await interaction.send_message(embed=no_author_emb, ephemeral=True, view=None)





class level_system_check():

    def blacklist_check(guild_id, guild_check_message):

        if isinstance(guild_check_message.channel, discord.TextChannel):

            levelsystem_blacklist_connect = level_system_db.levelconnect()
            my_cursor = levelsystem_blacklist_connect.cursor()

            check_blacklist = "SELECT * FROM blacklist_level_setup WHERE guild_id = %s"
            check_blacklist_values = [guild_id]
            my_cursor.execute(check_blacklist, check_blacklist_values)
            levelsystem_blacklist = my_cursor.fetchall()

            channel_blacklist_first, category_blacklist_first, blacklist_role = [], [], []

            for blacklist_items in levelsystem_blacklist:

                channel_blacklist = blacklist_items[0]
                category_blacklist = blacklist_items[1]
                role_blacklist = blacklist_items[4]

                channel_blacklist_first.append(channel_blacklist), category_blacklist_first.append(category_blacklist), blacklist_role.append(role_blacklist)

            blacklist = (channel_blacklist_first, category_blacklist_first, blacklist_role)
            if guild_check_message.channel.category is not None:
                                    
                if str(guild_check_message.channel.category.id) in blacklist[1]:
                    return True

                if str(guild_check_message.channel.id) in blacklist[0]:
                    return True

                for blacklisted_roles in blacklist[2]:
                    if blacklisted_roles == None:
                        pass
                    else:
                        blacklist_role = guild_check_message.guild.get_role(int(blacklisted_roles))
                        if blacklist_role in guild_check_message.author.roles:
                            return True
            




class level_system(commands.Cog):
    
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
    async def on_guild_remove(self, guild):

        setup_level = level_system_db.levelconnect()
        my_cursor = setup_level.cursor()

        guild_id_level = str(guild.id)

        check_level_blacklist = "SELECT guild_id FROM blacklist_level_setup WHERE guild_id = %s" 
        check_level_blacklist_values = [guild_id_level]
        my_cursor.execute(check_level_blacklist, check_level_blacklist_values)

        blacklist_items = my_cursor.fetchall()
        blacklist_items_formatted = [t[0] for t in blacklist_items]


        check_levelsystem = "SELECT guild_ID FROM levelsystem_info WHERE guild_ID = %s"
        check_levelsystem_values = [guild_id_level]
        my_cursor.execute(check_levelsystem, check_levelsystem_values)

        level_system_infos_items = my_cursor.fetchall()
        level_system_infos_items_formatted = [t[0] for t in level_system_infos_items]


        check_level_control = "SELECT guild_ID FROM level_control WHERE guild_ID = %s"
        check_level_control_values = [guild_id_level]
        my_cursor.execute(check_level_control, check_level_control_values)

        level_control_items = my_cursor.fetchall()
        level_control_items_formatted = [t[0] for t in level_control_items]


        check_level_roles = "SELECT guild_id FROM level_roles WHERE guild_id = %s"
        check_level_roles_values = [guild_id_level]
        my_cursor.execute(check_level_roles, check_level_roles_values)

        level_roles_items = my_cursor.fetchall()
        level_roles_items_formatted = [t[0] for t in level_roles_items]


        try:

            if blacklist_items_formatted:

                if guild_id_level in blacklist_items_formatted:

                    try:

                        delete_blacklist = "DELETE FROM blacklist_level_setup WHERE guild_id = %s"
                        delete_blacklist_values = [guild_id_level]

                        my_cursor.execute(delete_blacklist, delete_blacklist_values)
                        
                        setup_level.commit()

                    except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))
                
                else:
                    pass

            else:
                pass

            if level_system_infos_items_formatted:
                
                if guild_id_level in level_system_infos_items_formatted:

                    try:

                        delete_levelsystem = "DELETE FROM levelsystem_info WHERE guild_ID = %s"
                        delete_levelsystem_values = [guild_id_level]

                        my_cursor.execute(delete_levelsystem, delete_levelsystem_values)
                        
                        setup_level.commit()

                    except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))
                
                else:
                    pass
            
            else:
                pass

            if level_control_items_formatted:
        
                if guild_id_level in level_control_items_formatted:

                    try:

                        delete_level_contol = "DELETE FROM level_control WHERE guild_ID = %s"
                        delete_level_contol_values = [guild_id_level]

                        my_cursor.execute(delete_level_contol, delete_level_contol_values)
                        
                        setup_level.commit()

                    except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))
                
                else:
                    pass

            else:
                pass

            if level_roles_items_formatted:
    
                if guild_id_level in level_roles_items_formatted:

                    try:

                        delete_level_roles = "DELETE FROM level_roles WHERE guild_id = %s"
                        delete_level_roles_values = [guild_id_level]

                        my_cursor.execute(delete_level_roles, delete_level_roles_values)
                        
                        setup_level.commit()

                    except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))
                
                else:
                    pass

            else:
                pass

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            level_system_db.db_close(cursor=my_cursor, db_connection=setup_level)



    @commands.Cog.listener()
    async def on_message(self ,message):

        connection_to_db_level = level_system_db.levelconnect()
        my_cursor = connection_to_db_level.cursor()

        if self.get_ratelimit(message):
            return

        if message.content.startswith("?"):
            return

        if message.author.bot:
            return

        # Insert stats    
        user_level_insert = 0
        user_xp_insert = 0

        # user infos 
        user_ID_insert = str(message.author.id)

        guild_ID_insert = str(message.guild.id)
        user_name_insert = str(message.author.name)

        level_control = "SELECT * FROM level_control WHERE guild_ID = %s"
        level_control_values = [guild_ID_insert]
        my_cursor.execute(level_control, level_control_values)
        all_infos_setup = my_cursor.fetchone()

        if all_infos_setup:
            
            if "off" in all_infos_setup[1] and guild_ID_insert in all_infos_setup[0]:
                return

            else:
                
                # Blacklist check
                check_blacklist = level_system_check.blacklist_check(guild_id=guild_ID_insert, guild_check_message=message)
                            
                if isinstance(message.channel, discord.TextChannel):
                    
                    # Variables that enter the data of new users
                    sql_insert_query_level = "INSERT INTO levelsystem_info (guild_ID, user_ID, user_level, user_XP, user_name) VALUES (%s, %s, %s, %s, %s)"        
                    level_values = [guild_ID_insert, user_ID_insert, user_level_insert, user_xp_insert, user_name_insert]
                    
                    # Check if the blacklist returns None
                    if check_blacklist is not True:

                        try:   

                            check_if_exists =  f"SELECT * FROM levelsystem_info WHERE guild_ID = %s AND user_ID = %s"
                            values_check_if_exists = [guild_ID_insert, user_ID_insert]
                            my_cursor.execute(check_if_exists, values_check_if_exists)
                            check_ID = my_cursor.fetchone()

                            if check_ID:
                                                        
                                user_level, xp_from_user, guild_user, user_id = check_ID[2], check_ID[3], check_ID[0], check_ID[1]
                                if check_ID[2] >= 999:
                                    return

                                if user_ID_insert == user_id and guild_ID_insert == guild_user:

                                    XP = self.xp_generator()
                                    user_has_xp = xp_from_user + XP 
                                                                    
                                    xp_need_next_level = 5 * (user_level ^ 2) + (50 * user_level) + 100 - xp_from_user
                                                                    
                                    if xp_from_user >= xp_need_next_level:
                                                                        
                                        new_level = user_level + 1
                                        xp_user = 0        

                                        try:

                                            level_up_edit = f"UPDATE levelsystem_info SET user_level = %s ,user_XP = %s WHERE guild_ID = %s AND user_ID = %s"
                                            level_up_edit_values = [new_level, xp_user, guild_ID_insert, user_ID_insert]
                                            my_cursor.execute(level_up_edit, level_up_edit_values)
                                            connection_to_db_level.commit()

                                            print("Data were changed")

                                        except mysql.connector.Error as error:
                                            print("parameterized query failed {}".format(error))
                                                                    
                                        finally:
                                                                    
                                            check_levelup_channel = "SELECT * FROM level_control WHERE guild_ID = %s"
                                            check_levelup_channel_values = [guild_ID_insert]
                                            my_cursor.execute(check_levelup_channel, check_levelup_channel_values)
                                            all_levelup_channels = my_cursor.fetchone()

                                            if None not in all_levelup_channels:
                                                           
                                                levelup_channel = bot.get_channel(int(all_levelup_channels[2]))
                                                await levelup_channel.send(f"Oh nice <@{user_ID_insert}> you have a new level your newlevel is {new_level}")
                                                        
                                            else:

                                                await message.channel.send(f"Oh nice <@{user_ID_insert}> you have a new level your newlevel is {new_level}")
                                                                        
                                                check_level_role = "SELECT * FROM level_roles WHERE guild_id = %s AND role_level = %s"
                                                check_level_role_values = [guild_ID_insert, new_level]  
                                                my_cursor.execute(check_level_role, check_level_role_values)
                                                all_level_roles = my_cursor.fetchone()
                                                                    
                                                if all_level_roles:
                                                                                
                                                    if new_level == all_level_roles[2]:

                                                        role_id, level_need = all_level_roles[1], all_level_roles[2]
                                                        print(f"{role_id} {level_need}")

                                                        level_role = message.guild.get_role(int(role_id))
                                                        print(level_role)

                                                        await message.author.add_roles(level_role)    
                                                        await message.channel.send(f"<@{user_ID_insert}> du hast die rolle <@&{role_id}> bekommen da du level **{level_need}**")
                                                                            
                                                    else:     
                                                        pass

                                                else:
                                                    pass        
                                                

                                                level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)
                                    else:

                                        try:
                                                                            
                                            xp_edit = f"UPDATE levelsystem_info SET user_XP = %s WHERE user_ID = %s AND guild_ID = %s"
                                            xp_edit_values = [user_has_xp, user_ID_insert, guild_ID_insert]
                                            my_cursor.execute(xp_edit, xp_edit_values)
                                            connection_to_db_level.commit()

                                            print("Data were changed")

                                        except mysql.connector.Error as error:
                                            print("parameterized query failed {}".format(error))

                                        finally:

                                            level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)

                                else:     

                                    try:

                                        my_cursor.execute(sql_insert_query_level, level_values)
                                        connection_to_db_level.commit()

                                        print("Data was successfully inserted")


                                    except mysql.connector.Error as error:
                                        print("parameterized query failed {}".format(error))

                                    finally:
                                                            
                                        level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)
                                            
                            else:

                                try: 
  
                                    my_cursor.execute(sql_insert_query_level, level_values)
                                    connection_to_db_level.commit()

                                except mysql.connector.Error as error:
                                    print("parameterized query failed {}".format(error))
                                                        
                                finally:

                                   level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)

                        except mysql.connector.Error as error:
                            print("parameterized query failed {}".format(error))

                        finally:

                            level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)
                    
        else:

            insert_setup_guild = f"""INSERT INTO level_control (guild_ID, control) VALUES (%s, %s)"""
            setup_guild_values = (guild_ID_insert, "on")
            my_cursor.execute(insert_setup_guild, setup_guild_values)
            connection_to_db_level.commit()

        level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)
                


    @commands.Cog.listener()
    async def on_member_remove(self ,member):
        
        if not member.bot:
            
            connection_to_db_level = level_system_db.levelconnect()
            my_cursor = connection_to_db_level.cursor()

            user_ID_remove = str(member.id)
            guild_ID_remove = str(member.guild.id)

            check_if_remove_member = f"SELECT * FROM levelsystem_info WHERE user_ID = %s AND guild_ID = %s"
            check_if_remove_member_values = (user_ID_remove, guild_ID_remove)
            my_cursor.execute(check_if_remove_member, check_if_remove_member_values)
            remove_member = my_cursor.fetchone()

            if remove_member:
                  
                if user_ID_remove in remove_member[1] and guild_ID_remove in remove_member[0]:
                                
                    try:

                        delete_row_member = f"DELETE FROM levelsystem_info WHERE user_ID = %s AND guild_ID = %s"
                        delete_row_member_values = [user_ID_remove, guild_ID_remove]
                        my_cursor.execute(delete_row_member, delete_row_member_values)
                        connection_to_db_level.commit()

                    except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))
                        
                else:
                    return

        else:
            return

        level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)



    @commands.slash_command(name = "give-xp", description = "Give a user xp!")
    @commands.has_permissions(administrator = True)
    async def give_xp_slash(self, ctx, user:Option(discord.Member, description="Select a user who should receive the xp!"),
        xp:Option(int, description="Choose a quantity of xp that the user should get but do not exaggerate!")):

        connection_to_db_level = level_system_db.levelconnect()
        my_cursor = connection_to_db_level.cursor()

        user_ID = str(user.id)
        guild_ID = str(ctx.guild.id)

        check_if_exists =  f"SELECT * FROM levelsystem_info WHERE guild_ID = %s AND user_ID = %s"
        check_if_exists_value = (guild_ID, user_ID)

        my_cursor.execute(check_if_exists, check_if_exists_value)

        check_all = my_cursor.fetchone()

        emb_error = discord.Embed(title=f"This user either does not exist or has not yet shown that he exists", 
            description="Life signs are given in the form of messages! Just say 'Hello!'", color=error_red)

        if check_all:
                
            user_level, user_xp = check_all[2], check_all[3]

            xp_need_next_level = 5 * (user_level ^ 2) + (50 * user_level) + 100 - user_xp

            if xp == 0:

                emb = discord.Embed(title="Das xp was du vergegeben willst ist 0", description=f"Das zu vergebende Xp muss mindestens 1 sein oder höher", color=error_red)
                await ctx.respond(embed=emb)

            if xp <= xp_need_next_level:

                user_xp_edit = user_xp + xp

                try:
                                
                    xp_give = f"UPDATE levelsystem_info SET user_XP = %s WHERE guild_ID = %s  AND user_ID = %s"
                    xp_give_values = (user_xp_edit, guild_ID, user_ID)
                    my_cursor.execute(xp_give, xp_give_values)
                    connection_to_db_level.commit()

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))

                finally: 
                                    
                    emb = discord.Embed(title=f"Successfully transferred: {xp} xp", 
                        description=f"User: <@{user_ID}> was successfully transferred **{xp}** xp, current xp: **{user_xp_edit}**", color=discord.Colour.brand_green())
                    await ctx.respond(embed=emb)

                if xp >= xp_need_next_level:

                    new_level = user_level + 1
                    xp_user_edit = 0
                                        
                    try:

                        level_up_xp_give = f"UPDATE levelsystem_info SET user_level = %s ,user_XP = %s WHERE guild_ID = %s AND user_ID = %s"
                        level_up_xp_give_values = (new_level, xp_user_edit, guild_ID, user_ID)
                        my_cursor.execute(level_up_xp_give, level_up_xp_give_values)
                        connection_to_db_level.commit()

                    except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))
                                            
                    finally:
                                                
                        await ctx.send(f"Oh nice <@{user_ID}> you have a new level your newlevel is {new_level}")

            else:
    
                    emb = discord.Embed(title=f"The xp you want to give is too high", description=f"You can transfer a maximum of **{xp_need_next_level}** xp this user.", color=error_red)
                    await ctx.respond(embed=emb)

        else:

            await ctx.respond(embed=emb_error)

        level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)


    
    @commands.slash_command(name = "remove-level", description = "Remove levels of a user!")
    @commands.has_permissions(administrator = True)
    async def remove_level_slash(self, ctx, user:Option(discord.Member, description="Select a user from whose level you want to remove!"), 
        levels:Option(int, description="Choose a set of levels that you want to remove!")):

        user_ID_remove = str(user.id)
        guild_ID_remove = str(ctx.guild.id)

        connection_to_db_level = level_system_db.levelconnect()
        my_cursor = connection_to_db_level.cursor()

        check_user_level = f"SELECT * FROM levelsystem_info WHERE guild_ID = %s ANd user_ID = %s"
        check_user_level_values = [guild_ID_remove, user_ID_remove]
        my_cursor.execute(check_user_level, check_user_level_values)
        user_level_info = my_cursor.fetchone()

        user_xp = 0

        no_user_emb = discord.Embed(title=f"This user either does not exist or has not yet shown that he exists", 
            description="Life signs are given in the form of messages! Just say 'Hello!'", color=error_red)
            
        if user_level_info:

            user_level = user_level_info[2]      

            if user_level >= 1 and user_level >= levels:

                try:

                    new_level_edit = user_level - levels

                    remove_level = f"UPDATE levelsystem_info SET user_level = %s, user_XP = %s WHERE guild_ID = %s AND user_ID = %s"
                    remove_level_values = [new_level_edit, user_xp, guild_ID_remove, user_ID_remove]
                    my_cursor.execute(remove_level, remove_level_values)
                    connection_to_db_level.commit()

                    successfully_emb = discord.Embed(title=f"The specified levels were successfully removed", 
                        description=f"You have successfully removed the user <@{user_ID_remove}> {levels} level. The current level is: **{new_level_edit}**", colour=discord.Colour.brand_green())
                    await ctx.respond(embed=successfully_emb)

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))

            else:

                zero_level_emb = discord.Embed(title=f"You can not remove this user level!", 
                    description=f"The level of the user is either 0 or your selected number is too high. User level: **{user_level}**", colour=error_red)
                await ctx.respond(embed=zero_level_emb)

        else:

            await ctx.respond(embed=no_user_emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)


 
    @commands.slash_command(name = "give-levels", description = "Give a user levels!")
    @commands.has_permissions(administrator = True)
    async def give_level_slash(self, ctx, user:Option(discord.Member, description="Choose a user to whom you want to pass the level!"), 
        levels:Option(int, description="Choose a worth how many levels you want to pass!")):

        user_ID_get = str(user.id)
        guild_ID_get = str(ctx.guild.id)

        connection_to_db_level = level_system_db.levelconnect()
        my_cursor = connection_to_db_level.cursor()

        check_level_give = "SELECT * FROM levelsystem_info WHERE user_ID = %s AND guild_ID = %s"
        check_level_give_values = [user_ID_get, guild_ID_get]
        my_cursor.execute(check_level_give, check_level_give_values)
        user_givelevel_info = my_cursor.fetchone()

        if user_givelevel_info:
            
            user_level = user_givelevel_info[2]
            set_new_level = user_level + levels
                           
            if levels > 999 or set_new_level >= 999:

                level_too_high_emb = discord.Embed(title="The level you want to transfer is too high!", 
                    description="The maximum level a user can have is 999", color=error_red)
                await ctx.respond(embed=level_too_high_emb)

            else:

                try:

                    set_level = f"UPDATE levelsystem_info SET user_level = %s WHERE guild_ID = %s AND user_ID = %s"
                    set_level_values = [set_new_level, guild_ID_get, user_ID_get]
                    my_cursor.execute(set_level, set_level_values)
                    connection_to_db_level.commit()

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))

                finally:

                    successfully_emb = discord.Embed(title="The specified levels were successfully transferred",
                        description=f"You have successfully added the user <@{user_ID_get}> {levels} level. The current level is **{set_new_level}**.", colour=discord.Colour.brand_green())
                    await ctx.respond(embed=successfully_emb)

        else:

            error_emb = discord.Embed(title="This user either does not exist or has not yet shown that he exists", 
                description="Life signs are given in the form of messages! Just say 'Hello!", color=error_red)
            await ctx.respond(embed=error_emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)



    @commands.slash_command(name = "remove-xp", description = "Remove xp from a user!")
    @commands.has_permissions(administrator = True)
    async def remove_xp_slash(self, ctx, user:Option(discord.Member, description="Choose a quantity of XP you want to remove!"),
        xp:Option(int, description="Choose a quantity of XP you want to remove!")):

        user_ID_remove_xp = str(ctx.user.id)
        guld_ID_remove_xp = str(ctx.guild.id)
            
        connection_to_db_level = level_system_db.levelconnect()
        my_cursor = connection_to_db_level.cursor()

        check_remove_xp = "SELECT * FROM levelsystem_info WHERE user_ID = %s AND guild_ID = %s"
        check_remove_xp_values = [user_ID_remove_xp, guld_ID_remove_xp]
        my_cursor.execute(check_remove_xp, check_remove_xp_values)
        user_remove_xp_info = my_cursor.fetchone()

        emb_error = discord.Embed(title="This user either does not exist or has not yet shown that he exists", 
            description="Life signs are given in the form of messages! Just say 'Hello!", color=error_red)

        if user_remove_xp_info:
            
            user_xp = user_remove_xp_info[3]
            set_new_xp = user_xp - xp 

            if xp == 0:
                emb = discord.Embed(title=f"The XP you want to remove is 0", description=f"The XP to be removed must be at least 1", color=error_red)
                await ctx.respond(embed=emb)

            if xp > user_xp:
                        
                xp_too_high_emb = discord.Embed(title="The specified xp you want to remove is too high", 
                    description=f"The XP of this user is either 0 or your value is higher than the xp he removes the user has {user_xp} XP", color=error_red)
                await ctx.respond(embed=xp_too_high_emb)

            else:

                if user_ID_remove_xp == user_remove_xp_info[2] and guld_ID_remove_xp == user_remove_xp_info[0]:

                    try:
                                
                        remove_xp = f"UPDATE levelsystem_info SET user_XP = %s WHERE guild_ID = %s AND user_ID = %s"
                        remove_xp_values = [set_new_xp, guld_ID_remove_xp, user_ID_remove_xp]
                        my_cursor.execute(remove_xp, remove_xp_values)
                        connection_to_db_level.commit()

                    except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))

                    finally:

                        successfully_removexp_emb = discord.Embed(title="You have successfully removed the specified XP!", 
                            description=f"You have successfully {xp} removed the user: <@{user_ID_remove_xp}>. Current XP: {set_new_xp}", color=discord.Colour.brand_green())
                        await ctx.respond(embed=successfully_removexp_emb)

                else:

                    await ctx.respond(embed=emb_error)

        else:

            await ctx.respond(embed=emb_error)

        level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)            
    

    
    @commands.slash_command(name = "reset-level", description = "Reset all levels and xp of everyone!")
    @commands.has_permissions(administrator = True)
    async def reset_levels_slash(self, ctx):

        global global_guild_id_reset_level
        global_guild_id_reset_level = str(ctx.guild.id)

        global global_author_id_resetlevel
        global_author_id_resetlevel = ctx.author.id

        connection_to_db_level = level_system_db.levelconnect()
        my_cursor = connection_to_db_level.cursor()

        reset_level = "SELECT guild_ID = %s FROM levelsystem_info"
        reset_level_values = [global_guild_id_reset_level]

        my_cursor.execute(reset_level, reset_level_values)

        check_all = my_cursor.fetchall()

        if check_all:

            emb_sure = discord.Embed(title="Are you sure?", 
                description="If you press the yes button all levels and XP will be deleted. Are you sure you want to do this? If not press the no button", color=funpark_colour)
            await ctx.respond(embed=emb_sure, view = reset_level_button())

        else:
            
            emb = discord.Embed(title="There is no data about this server", 
                description="You can not delete the data because there is none the prerequisite for gaining level is to exchange messages", color=error_red)
            await ctx.respond(embed=emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)


    
    @commands.slash_command(name = "rank", description = "Shows you the rank of a user in the level system!")
    async def rank_slash(self, ctx, user:Option(discord.Member, description="Let others show you the rank!")):

        guild_ID_user = str(ctx.guild.id)
        user_id = str(user.id)

        count = 0
        count_end = 0

        connection_to_db_level = level_system_db.levelconnect()
        my_cursor = connection_to_db_level.cursor()

        rank_show_infos_level = "SELECT * FROM levelsystem_info WHERE guild_ID = %s ORDER BY user_level DESC"
        rank_show_infos_levels_values = [guild_ID_user]
        my_cursor.execute(rank_show_infos_level, rank_show_infos_levels_values)
        all_info = my_cursor.fetchall()

        user_id_rank_first, guild_user_rank_first, user_xp_rank_first, user_level_rank_first = "0", "0", 0, 0

        error_emb = discord.Embed(title="The user was not found", 
            description="The user either does not exist or he has not yet shown that he exists.", color=error_red)

        if all_info:

            for all_infos in all_info:

                user_xp_rank = all_infos[3]
                user_level_rank = all_infos[2]
                user_id_rank = all_infos[1]
                guild_user_rank = all_infos[0]

                if user_id in user_id_rank:
                    
                    user_id_rank_first, guild_user_rank_first, user_xp_rank_first, user_level_rank_first = user_id_rank, guild_user_rank, user_xp_rank, user_level_rank

            if user_id in user_id_rank_first and guild_ID_user in guild_user_rank_first:
    
                for rank_count in all_info:
                
                    count += 1
                                                    
                    if user_id in str(rank_count[1]):

                        count_end = count

                xp_need_next_level = 5 * (user_level_rank_first ^ 2) + (50 * user_level_rank_first) + 100 - user_xp_rank_first

                emb = discord.Embed(title=f"{ctx.user.name} rank!", description=f"All your values in the level system and your rank.", color=discord.Colour.blurple())
                emb.add_field(name="Name:",
                    value=f"`{user} (Bot)`" if user.bot else f"<@{user_id}>",
                    inline=True)
                emb.add_field(name="Rank:", value=f"**{count_end}**", inline=False)
                emb.add_field(name="Level:", value=f"**{user_level_rank_first}**")
                emb.add_field(name="XP:", value=f"**{user_xp_rank_first}**")
                emb.add_field(name="Nedded-XP:", value=f"**{xp_need_next_level}**")
                emb.set_thumbnail(url=f"{user.display_avatar.url}")
            
                await ctx.respond(embed=emb)

            else:
                            
                await ctx.respond(embed=error_emb)

        else:
                            
            await ctx.respond(embed=error_emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=connection_to_db_level)



    @commands.slash_command(name = "leaderboard-level", description = "Shows the highest ranks in the lavel system!")
    async def leaderboard(self, ctx):

        leaderboard_connect = level_system_db.levelconnect()
        my_cursor = leaderboard_connect.cursor()

        guild_id = str(ctx.guild.id)

        leaderboard_levels = "SELECT user_ID, user_level, user_XP FROM levelsystem_info WHERE guild_ID = %s ORDER BY user_level DESC, user_XP DESC"
        leaderboard_levels_values = [guild_id]
        my_cursor.execute(leaderboard_levels, leaderboard_levels_values)

        leaderboard_members =  my_cursor.fetchall()
        c = []
        for i, pos in enumerate(leaderboard_members, start=1):
            member_id, lvl, xp = pos
            
            if i <= 10:

                c.append(f"{i}. <@{member_id}>, level: {lvl}, XP: {xp}")
            
        level_roles_mention_end = '\n'.join(c)

        level_system_db.db_close(cursor=my_cursor, db_connection=leaderboard_connect)

        emb = discord.Embed(title="leaderboard", description=f"leaderboard participants:\n\n{level_roles_mention_end}")
        emb.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.respond(embed=emb)

               

    
    @commands.slash_command(name = "level-system-control", description = "Activate or deactivate the level system!")
    @commands.has_permissions(administrator = True)
    async def level_system_control(self, ctx):

        guild_Id_control = str(ctx.guild.id)
        
        level_sytem_conrtol_db = level_system_db.levelconnect()
        my_curser_control = level_sytem_conrtol_db.cursor()

        level_control = "SELECT * FROM level_control WHERE guild_ID = %s"
        level_control_values = [guild_Id_control]
        my_curser_control.execute(level_control, level_control_values)

        global all_infos_setup_level_control
        all_infos_setup_level_control = my_curser_control.fetchone()

        if all_infos_setup_level_control:
            
            active_deactive = "0"

            if all_infos_setup_level_control[1] == "on":
                active_deactive = "Activated"
            elif all_infos_setup_level_control[1] == "off":
                active_deactive = "Deactivated"

            emb = discord.Embed(title="Level system settings", 
                description=f"With the lower button you can set the level system, You can activate or deactivate. At the moment it is: **{active_deactive}**",color=discord.Colour.random())
            await ctx.respond(embed=emb, view=level_system_control_button())

        else:

            try:

                insert_setup_guild = """ INSERT INTO level_control (guild_ID, control) VALUES (%s, %s)"""
                setup_guild_values = (guild_Id_control, "on")

                my_curser_control.execute(insert_setup_guild, setup_guild_values)
                level_sytem_conrtol_db.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:

                emb = discord.Embed(title="No entry found", 
                    description="No entry was found so one was created the level system was also activated immediately", color=error_red)
                await ctx.respond(embed=emb)

        level_system_db.db_close(cursor=my_curser_control, db_connection=level_sytem_conrtol_db)

    

    @commands.slash_command(name = "add-text-channel-level-blacklist", description = "Exclude text channels from the level system!")
    @commands.has_permissions(administrator = True)
    async def set_textchanels_level_blacklist(self, ctx, channel: Option(discord.TextChannel, description="Select a text channel you want to exclude from the level system")):

        level_connection_blacklist = level_system_db.levelconnect()
        my_cursor = level_connection_blacklist.cursor()

        guild_ID_blacklist = str(ctx.guild.id)
        guild_name = ctx.guild.name
        channel_id = str(channel.id)

        check_blacklist_chanels = "SELECT * FROM blacklist_level_setup WHERE guild_id = %s AND channel_id = %s"
        check_blacklist_chanels_values = [guild_ID_blacklist, channel_id]
        my_cursor.execute(check_blacklist_chanels, check_blacklist_chanels_values)
        blacklist_items = my_cursor.fetchone()

        if blacklist_items:
    
            emb = discord.Embed(title=f"Channel is blacklisted",                     
                description=f"The channel <#{channel_id}> is already on the blacklist and therefore excluded from the level system.", color=error_red)
            await ctx.respond(embed=emb)

        else:
          
            try:

                insert_channel_blacklist = "INSERT INTO blacklist_level_setup (channel_id, guild_id, guild_name) VALUES (%s, %s, %s)"
                insert_channel_blacklist_values = [channel_id, guild_ID_blacklist, guild_name]
                my_cursor.execute(insert_channel_blacklist, insert_channel_blacklist_values)

                level_connection_blacklist.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:
            
                emb = discord.Embed(title="You have successfully blacklisted this channel", 
                    description=f"You have successfully excluded the channel <#{channel_id}> from the levelsystem", color=discord.Colour.brand_green())
                await ctx.respond(embed=emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=level_connection_blacklist)


    
    @commands.slash_command(name = "remove-channel-level-blacklist", description = "remove a channel from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_channel_blacklit(self, ctx, channel:Option(discord.TextChannel, 
        description="remove a channel from the blacklist and allow it back into the level system!")):
        
        guild_id_blacklist_level = str(ctx.guild.id)
        channel_id = str(channel.id)

        remove_channel_blacklist = level_system_db.levelconnect()
        my_cursor = remove_channel_blacklist.cursor()

        check_blacklist = "SELECT * FROM blacklist_level_setup WHERE guild_id = %s AND channel_id = %s"
        check_blacklist_vaules = [guild_id_blacklist_level, channel_id]
        my_cursor.execute(check_blacklist, check_blacklist_vaules)
        check_blacklist_result = my_cursor.fetchone()

        if check_blacklist_result:
                
            try:

                remove_blacklist_channel = "DELETE FROM blacklist_level_setup WHERE guild_ID = %s AND channel_id = %s"
                remove_blacklist_channel_values = [guild_id_blacklist_level, channel_id]

                my_cursor.execute(remove_blacklist_channel, remove_blacklist_channel_values)
                remove_channel_blacklist.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:
            
                emb = discord.Embed(title="You have successfully removed this channel from the balcklist", 
                    description=f"You have successfully removed the channel <#{channel_id}> from the blacklist this channel is now part of the level system again", color=discord.Colour.brand_green())
                await ctx.respond(embed=emb)
        
        else:
            
            emb_error = discord.Embed(title="This channel is not blacklisted",
                description=f"This channel is not on the blacklist if you want to see what all is on the blacklist use:\n<show-level-blacklist:1051935206799577179>", colour=error_red)
            await ctx.respond(embed=emb_error) 
        
        level_system_db.db_close(cursor=my_cursor, db_connection=remove_channel_blacklist)


    
    @commands.slash_command(name = "add-category-level-blacklist", description = "Exclude categories from the level system and all channels that belong to them!")
    @commands.has_permissions(administrator = True)
    async def add_category_blacklist(self, ctx, category:Option(discord.CategoryChannel, description="Add a category to the blacklist!")):
        
        blacklist_connector = level_system_db.levelconnect()
        my_cursor = blacklist_connector.cursor()

        category_id = str(category.id)
        guild_id_blacklist = str(ctx.guild.id)
        guild_name_blacklist = str(ctx.guild.name)

        check_blacklist = "SELECT * FROM blacklist_level_setup WHERE guild_id = %s AND category_id = %s"
        check_blacklist_values = [guild_id_blacklist, category_id]
        my_cursor.execute(check_blacklist, check_blacklist_values)
        all_blacklist_items = my_cursor.fetchone()
        
        if all_blacklist_items:
            
            emb = discord.Embed(title="Diese Kategorie ist bereits auf der Blacklist", 
                description="The category is already blacklisted and therefore also excluded from the level system all channels in the category are also excluded", color=error_red)
            await ctx.respond(embed=emb)

        else:
                
            try:

                add_category_blacklist = "INSERT INTO blacklist_level_setup (category_id, guild_id, guild_name) VALUES (%s, %s, %s)"
                add_category_blacklist_values = [category_id, guild_id_blacklist, guild_name_blacklist]
                my_cursor.execute(add_category_blacklist, add_category_blacklist_values)
                blacklist_connector.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:
            
                emb = discord.Embed(title="You have successfully added this category", 
                    description=f"You have successfully excluded the <#{category_id}> category from the levelsystem", color=discord.Colour.brand_green())
                await ctx.respond(embed=emb)  

        level_system_db.db_close(cursor=my_cursor, db_connection=blacklist_connector)



    @commands.slash_command(name="remove-category-level-blacklist", description="Remove categories from the level blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_category_blacklist(self, ctx, category:Option(discord.CategoryChannel, description="Choose a category you want to remove from the blacklist!")):

        blacklist_connector = level_system_db.levelconnect()
        my_cursor = blacklist_connector.cursor()

        guild_id_blacklist = str(ctx.guild.id)
        category_id = str(category.id)

        check_blacklist = "SELECT * FROM blacklist_level_setup WHERE guild_id = %s AND category_id = %s"
        check_blacklist_values = [guild_id_blacklist, category_id]

        my_cursor.execute(check_blacklist, check_blacklist_values)
        all_blacklist_items = my_cursor.fetchone()

        if all_blacklist_items:

            try:

                remove_category_blacklist = "DELETE FROM blacklist_level_setup WHERE guild_id = %s AND category_id = %s"
                remove_category_blacklist_values = [guild_id_blacklist, category_id]

                my_cursor.execute(remove_category_blacklist, remove_category_blacklist_values)
                blacklist_connector.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:

                emb = discord.Embed(title="You have successfully removed this category from the balcklist", 
                    description=f"The category <#{category_id}> was successfully removed from the blacklist if you want to see what else is on the blacklist use the command:\n<show-level-blacklist:1051935206799577179>", color=error_red)
                await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(title="This category is not on the blacklist", 
                description=f"The category <#{category_id}> is not on the blacklist if you want to see what all is on the blacklist use:\n</show-level-blacklist:1051935206799577179>", color=error_red)
            await ctx.respond(embed=emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=blacklist_connector)



    @commands.slash_command(name = "add-role-level-blacklist", description = "Close rolls from the level system and all who have them!")
    @commands.has_permissions(administrator = True)
    async def add_role_blacklist(self, ctx, role:Option(discord.Role, description="Select a role to be added to the blacklist!")):

        guild_id = str(ctx.guild.id)
        role_id = str(role.id)
        guild_name = ctx.guild.name

        blacklist_connector = level_system_db.levelconnect()
        my_cursor = blacklist_connector.cursor()

        check_blacklist = "SELECT * FROM blacklist_level_setup WHERE guild_id = %s AND role_id = %s"
        check_blacklist_values = [guild_id, role_id]
        my_cursor.execute(check_blacklist, check_blacklist_values)
        blacklist_items = my_cursor.fetchall()

        if blacklist_items:
     
            emb = discord.Embed(title="This role is already blacklisted", 
                description=f"The role <@&{role_id}> is already blacklisted. If you want to remove a role from the blacklist use the command:\n<remove-role-level-blacklist:1043539941545758810>", color=error_red)
            await ctx.respond(embed=emb)
        
        else:

            try:

                insert_role_blacklist = "INSERT INTO blacklist_level_setup (role_id, guild_id, guild_name) VALUES (%s, %s, %s)"
                insert_role_blacklist_values = [role_id, guild_id, guild_name]
                my_cursor.execute(insert_role_blacklist, insert_role_blacklist_values)
                blacklist_connector.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:
            
                emb = discord.Embed(title="Successfully blacklisted", 
                    description=f"The role <@&{role_id}> has been successfully added to the blacklist. If you want to remove it again use:\n</remove-role-level-blacklist:1043539941545758810>", colour=discord.Colour.brand_green())
                await ctx.respond(embed=emb)
             
        level_system_db.db_close(cursor=my_cursor, db_connection=blacklist_connector)



    @commands.slash_command(name = "remove-role-level-blacklist", description = "Remove a role from the level system blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_role_blacklist(self, ctx, role:Option(discord.Role, description="Select a role you want to remove from the blacklist!")):

        connect_blacklist = level_system_db.levelconnect()
        my_cursor = connect_blacklist.cursor()
        
        guild_id = str(ctx.guild.id)
        role_id = str(role.id)

        check_blacklist = "SELECT * FROM blacklist_level_setup WHERE guild_id = %s AND role_id = %s"
        check_blacklist_values = [guild_id, role_id]
        my_cursor.execute(check_blacklist, check_blacklist_values)
        all_blacklist_items = my_cursor.fetchone()

        if all_blacklist_items:

            try:

                delete_role = "DELETE FROM blacklist_level_setup WHERE guild_id = %s AND role_id = %s"
                delete_role_values = [guild_id, role_id]
                my_cursor.execute(delete_role, delete_role_values)
                connect_blacklist.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:
            
                emb = discord.Embed(title="You have successfully removed the role from the blacklist", 
                    description=f"The role <@&{role_id}> was successfully removed from the blacklist, if you want to see what is still on the blacklist use the command:\n</show-level-blacklist:1051935206799577179>", color=error_red)
                await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(title="This role has not been blacklisted", 
                description=f"If you want to see what is on the blacklist use:\n</show-level-blacklist:1051935206799577179>", color=error_red)
            await ctx.respond(embed=emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=connect_blacklist)



    @commands.slash_command(name = "reset-level-blacklist", description="Reset the blacklist of the level system and remove all entries!")
    @commands.has_permissions(administrator = True)
    async def reset_blacklist(self, ctx):

        blacklist_connect = level_system_db.levelconnect()
        my_cursor = blacklist_connect.cursor()

        guild_id_blacklist = str(ctx.guild.id)

        check_blacklist = "SELECT * FROM blacklist_level_setup WHERE guild_id = %s"
        check_blacklist_values = [guild_id_blacklist]
        my_cursor.execute(check_blacklist, check_blacklist_values)
        all_blacklist_items = my_cursor.fetchall()

        if all_blacklist_items:
            
            try:

                reset_blacklist_all = "DELETE FROM blacklist_level_setup WHERE guild_id = %s"
                reset_blacklist_all_values = [guild_id_blacklist]
                my_cursor.execute(reset_blacklist_all, reset_blacklist_all_values)
                blacklist_connect.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:

                emb = discord.Embed(title="You have successfully reset the blacklist", 
                    description=f"You have successfully reset the blacklist and deleted all entries from the list.", color=discord.Colour.brand_green())
                await ctx.respond(embed=emb)
        
        else:

            emb = discord.Embed(title="There is nothing on the blacklist", description=f"You had not put anything on the blacklist therefore nothing could be removed", color=error_red)
            await ctx.respond(embed=emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=blacklist_connect)


   
    @commands.slash_command(name = "show-level-blacklist", description = "Shows you everything that is blacklisted!")
    async def show_blacklist(self, ctx):

        blacklist_connect = level_system_db.levelconnect()
        my_cursor = blacklist_connect.cursor()

        guild_id_blacklist = str(ctx.guild.id)

        check_blacklist = "SELECT * FROM blacklist_level_setup WHERE guild_id = %s"
        check_blacklist_values = [guild_id_blacklist]
        my_cursor.execute(check_blacklist, check_blacklist_values)
        blacklist_items = my_cursor.fetchall()
        
        channel_ids_first, category_ids_first, guild_ids_first, roles_blacklist_first = [], [], [], []

        if blacklist_items:

            for blacklist_ids in blacklist_items:

                channel_ids = blacklist_ids[0]
                guild_ids = blacklist_ids[2]
                category_ids = blacklist_ids[1]
                blacklist_roles = blacklist_ids[4]

                channel_ids_first.append(channel_ids), category_ids_first.append(category_ids), guild_ids_first.append(guild_ids), roles_blacklist_first.append(blacklist_roles)

        if len(channel_ids_first) == 0:

            channel_mention_end = "There are no channels on the blacklist"

        else:
            
            new_list_channel = list(filter(lambda x: x is not None, channel_ids_first))
            channel_mention = [f'<#{i}>' for i in new_list_channel]
            channel_mention_end = '\n'.join(channel_mention)

        if len(category_ids_first) == 0:

            category_mention_end = "There are no categories on the blacklist"

        else:

            new_list_category = list(filter(lambda x: x is not None, category_ids_first))
            category_mention = [f'<#{i}>' for i in new_list_category] 
            category_mention_end = '\n'.join(category_mention)

        if len(roles_blacklist_first) == 0:

            roles_mention_end = f"There are no roles on the blacklist"

        else:

            new_list_roles = list(filter(lambda x: x is not None, roles_blacklist_first))
            roles_mention = [f"<@&{i}>" for i in new_list_roles]
            roles_mention_end = '\n'.join(roles_mention)

        level_system_db.db_close(cursor=my_cursor, db_connection=blacklist_connect)

        emb = discord.Embed(title=f"Blacklist", color=discord.Colour.blurple())
        emb.add_field(name="Blacklist channel", value=f"Here you can see all channels that are on the blacklist: \n\n{channel_mention_end}", inline=False)
        emb.add_field(name="Blacklist categories", value=f"Here you can see all categories that are blacklisted: \n\n{category_mention_end}", inline=False)
        emb.add_field(name="Blacklist roles", value=f"Here you can see all roles that are blacklisted: \n\n {roles_mention_end}", inline=False)
        await ctx.respond(embed=emb)


    
    @commands.slash_command(name = "set-level-role", description = "Add a role that you get from a certain level!")
    @commands.has_permissions(administrator = True)
    async def set_level_role(self, ctx, role:Option(discord.Role, description = "Select a role that you want to assign from a certain level onwards"),
        level:Option(int, description = "Enter a level from which this role should be assigned")):
        
        guild_ID = str(ctx.guild.id)
        guild_name = ctx.guild.name
        role_id = str(role.id)
        
        set_level_role_connect = level_system_db.levelconnect()
        my_cursor = set_level_role_connect.cursor()

        check_level_role = "SELECT * FROM level_roles WHERE guild_id = %s AND role_id = %s OR role_level = %s"
        check_level_role_values = [guild_ID, role_id, level]
        my_cursor.execute(check_level_role, check_level_role_values)
        all_level_role_items = my_cursor.fetchone()

        insert_level_role = "INSERT INTO level_roles (guild_id, role_id, role_level, guild_name) VALUES (%s, %s, %s, %s)"
        insert_level_role_values = [guild_ID, role_id, level, guild_name]

        emb_level_0 = discord.Embed(title="The level is zero", description=f"The level you choose is **0** the level must be at least **1**.", color=error_red)
        emb_higher = discord.Embed(title="The level is too high", description=f"The level you have chosen is higher than **999** but the level can only be a maximum of **999**.", color=error_red)

        global global_level_roles_id
        global global_new_level_role
        global_level_roles_id, global_new_level_role = role_id, level

        if all_level_role_items == None:
            
            if level <= 999:
                    
                try: 
                        
                    my_cursor.execute(insert_level_role, insert_level_role_values)
                    set_level_role_connect.commit()

                except mysql.connector.Error as error:
                    print("parameterized query failed {}".format(error))

                finally:

                    emb = discord.Embed(title="Role was added", description=f"The role <@&{role_id}> has been successfully added as a level role!", color=discord.Colour.brand_green())
                    await ctx.respond(embed=emb)

            if level == 0:

                await ctx.respond(embed=emb_level_0)

            if  level > 999:

                await ctx.respond(embed=emb_higher)

        else:

            check_role_level_info = "SELECT * FROM level_roles WHERE guild_id = %s AND role_id = %s AND role_level = %s"
            check_role_level_info_values = [guild_ID, role_id, level]
            my_cursor.execute(check_role_level_info, check_role_level_info_values)
            check_same = my_cursor.fetchone()
                
            if check_same:

                same_emb = discord.Embed(title="These values are already set",
                    description=f"The role <@&{role_id}> is already assigned to the level {level}.", color=error_red)
                await ctx.respond(embed=same_emb)

            else:

                if role_id in all_level_role_items[1]:

                    check_role_level_info = "SELECT * FROM level_roles WHERE guild_id = %s AND role_id = %s"
                    check_role_level_info_values = [guild_ID, role_id]
                    my_cursor.execute(check_role_level_info, check_role_level_info_values)
                    check_result = my_cursor.fetchone()

                    level_needed = str(check_result[2])
                        
                    emb_role = discord.Embed(title="This level is already assigned!", 
                        description=f"""Do you want to override the required level of this role?
                        The role <@&{role_id}> is currently available at level **{level_needed}**.""", color=funpark_colour)
                    await ctx.respond(embed = emb_role, view = level_roles_buttons_role())

                if str(level) in str(all_level_role_items[2]):
                                
                    check_role_level_info = "SELECT * FROM level_roles WHERE guild_id = %s AND role_level = %s"
                    check_role_level_info_values = [guild_ID, level]
                    my_cursor.execute(check_role_level_info, check_role_level_info_values)
                    check_result = my_cursor.fetchone()
                                
                    level_role = all_level_role_items[1]
                    emb_role = discord.Embed(title="This role is already assigned!", 
                        description=f"""Do you want to overwrite the role for this level?
                        The role <@&{level_role}> is just available at level **{level}**.""", color=funpark_colour)
                    await ctx.respond(embed = emb_role, view = level_roles_buttons_level())   

        level_system_db.db_close(cursor=my_cursor, db_connection=set_level_role_connect)



    @commands.slash_command(name = "remove-level-role", description = "Choose a role you want to remove from the blacklist!")
    @commands.has_permissions(administrator = True)
    async def remove_level_role(self, ctx, role:Option(discord.Role, description="Select a level role that you want to remove")):
        
        guild_id = str(ctx.guild.id)
        role_id = str(role.id)

        remove_level_role_connect = level_system_db.levelconnect()
        my_cursor = remove_level_role_connect.cursor()

        check_level_role = "SELECT * FROM level_roles WHERE guild_id = %s AND role_id = %s"
        check_level_role_values = [guild_id, role_id]
        my_cursor.execute(check_level_role, check_level_role_values)
        remove_level_role = my_cursor.fetchone()

        if remove_level_role:

            try:

                delete_level_role = "DELETE FROM level_roles WHERE guild_id = %s AND role_id = %s"
                delete_level_role_values = [guild_id, role_id]

                my_cursor.execute(delete_level_role, delete_level_role_values)

                remove_level_role_connect.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:
                
                emb = discord.Embed(title="Level role successfully removed", description=f"The role <@&{role_id}> was successfully removed as a level role", color=discord.Colour.brand_green())
                await ctx.respond(embed = emb)

        else:

            emb_error = discord.Embed(title="This role has not been discontinued", 
                description=f"This role has not been set as a level role if you want to see all the roles that have been set then use:\n</show-all-level-roles:1043539941545758811>", color=error_red)
            await ctx.respond(embed = emb_error)

        level_system_db.db_close(cursor=my_cursor, db_connection=remove_level_role_connect)



    @commands.slash_command(name = "show-all-level-roles", description = "View all rolls that are available with a level!")
    async def show_all_level_roles(self, ctx):

        guild_id = str(ctx.guild.id)

        show_level_role_connect = level_system_db.levelconnect()
        my_cursor = show_level_role_connect.cursor()

        check_level_role = "SELECT * FROM level_roles WHERE guild_id = %s ORDER BY role_level DESC"
        check_level_role_values = [guild_id]
        my_cursor.execute(check_level_role, check_level_role_values)
        all_items_level_role = my_cursor.fetchall()

        role_id_first, guild_ids_first, role_level_first = [], [], []
        
        level_roles_mentio = "**There would be no level rolls assigned**"
        emb_error = discord.Embed(title="level roles", description=f"The following roles are assigned at the respective levels:\n\n{level_roles_mentio}", color=discord.Colour.nitro_pink())
        
        if all_items_level_role:

            for level_roles_list in all_items_level_role:

                role_id = level_roles_list[1]
                guild_ids = level_roles_list[0]
                role_level = level_roles_list[2]

                role_id_first.append(role_id), role_level_first.append(str(role_level)), guild_ids_first.append(guild_ids)

            if len(role_id_first or str(role_level_first)) == 0:

                await ctx.respond(embed=emb_error)
            
            else:
                
                new_list_level_roles = list(filter(lambda x: x is not None, role_id_first))
                level_roles_mention = [f'<@&{i}> bei level: ' for i in new_list_level_roles]
                list3 = [item for sublist in zip(level_roles_mention, role_level_first) for item in sublist]
                result = [item_1 + item_2 for item_1, item_2 in zip(list3[::2], list3[1::2])]
                level_roles_mention_end = '\n'.join(result)

                emb = discord.Embed(title="level roles", description=f"The following roles are assigned at the respective levels:\n\n{level_roles_mention_end}", color=discord.Colour.nitro_pink())
                await ctx.respond(embed=emb)

        else:

            await ctx.respond(embed=emb_error)

        level_system_db.db_close(cursor=my_cursor, db_connection=show_level_role_connect)

       
    
    @commands.slash_command(nanme = "set-level-up-channel", description = "Set a channel for the level up notifications!")
    @commands.has_permissions(administrator = True)
    async def set_levelup_channel(self, ctx, channel:Option(discord.TextChannel, description="Select a channel in which the level up message should be sent")):

        levelup_channel_connect = level_system_db.levelconnect()
        my_cursor = levelup_channel_connect.cursor()

        guild_id = str(ctx.guild.id)
        channel_id = str(channel.id)
        author_id = str(ctx.author.id)

        check_levelup_channel = "SELECT levelup_channel FROM level_control WHERE guild_ID = %s"
        check_levelup_channel_values = [guild_id]
        my_cursor.execute(check_levelup_channel, check_levelup_channel_values)
        levelup_infos = my_cursor.fetchone()

        if None in levelup_infos:
       
            try:

                update_levelup_channel = "UPDATE level_control SET levelup_channel = %s WHERE guild_ID = %s"
                update_levelup_channel_values = [channel_id, guild_id]
                my_cursor.execute(update_levelup_channel, update_levelup_channel_values)
                levelup_channel_connect.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:

                emb = discord.Embed(title="Successfully level up channel assigned", 
                    description=f"The channel <#{channel_id}> was successfully selected as the level up message channel.", color=discord.Colour.brand_green())
                await ctx.respond(embed=emb)

        if channel_id in levelup_infos:

            emb = discord.Embed(title="This channel is already set", description="You have already set this channel as level up channel", color=error_red)
            await ctx.respond(embed=emb)

        else:

            if None not in levelup_infos:
                channel_mention = levelup_infos[0]
                global levelup_channel_author_id
                levelup_channel_author_id = author_id
                global levelup_channel_id
                levelup_channel_id = channel_id

                emb = discord.Embed(title="Do you want to overwrite the level up channel?", 
                    description=f"A channel has already been set do you want to overwrite the level up channel? Current channel <#{channel_mention}>", color=funpark_colour)
                await ctx.respond(embed=emb, view = levelup_channel_buttons())

        level_system_db.db_close(cursor=my_cursor, db_connection=levelup_channel_connect)



    @commands.slash_command(name = "disable-level-up-channel", description = "Deactivate the level up channel!")
    @commands.has_permissions(administrator = True)
    async def disable_levelup_channel(self, ctx):

        levelup_connect = level_system_db.levelconnect()
        my_cursor = levelup_connect.cursor()

        guild_id = str(ctx.guild.id) 

        check_levelup_channel = "SELECT * FROM level_control WHERE guild_ID = %s"
        check_levelup_channel_values = [guild_id]

        my_cursor.execute(check_levelup_channel, check_levelup_channel_values)

        levelup_channel = my_cursor.fetchone()

        res = any(map(lambda x: x is None, levelup_channel))

        error_emb = discord.Embed(title="You have not set a level up channel", 
            description="There is no level up channel assigned for this server use the command:\n</set-level-up-channel:1046773446291488818>", color=error_red)

        if res == False:
                
            try: 

                disable_levelup_channel_check = "UPDATE level_control SET levelup_channel = %s WHERE guild_ID = %s"
                disable_levelup_channel_check_values = [None, guild_id]
                my_cursor.execute(disable_levelup_channel_check, disable_levelup_channel_check_values)
                levelup_connect.commit()

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))
                    
            emb = discord.Embed(title="You have removed the level up channel", 
                description=f"You have successfully reset the level up channel the level up messages are now posted to each channel", color=funpark_colour)
            await ctx.respond(embed=emb)

        else:
            
            await ctx.respond(embed=error_emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=levelup_connect)



    @commands.slash_command(name = "show-level-up-channel", description = "Lass die den akktuellen level up channel zeigen!")
    async def show_levelup_channel(self, ctx):

        levelsystem_connect = level_system_db.levelconnect()
        my_cursor = levelsystem_connect.cursor()

        guild_id = str(ctx.guild.id)

        check_levelup_channel = "SELECT * FROM level_control WHERE guild_ID = %s"
        check_levelup_channel_values = [guild_id]
        my_cursor.execute(check_levelup_channel, check_levelup_channel_values)
        levelup_channel = my_cursor.fetchone()
        
        levelup_channel_id = levelup_channel[2]
        levelup_channel_mention = f"<#{levelup_channel_id}>"
    
        if levelup_channel and None != levelup_channel[2]:
        
            emb = discord.Embed(title="Das ist der aktuelle level up channel", description=f"Der aktuelle level up channel ist: {levelup_channel_mention}", color=funpark_colour)
            await ctx.respond(embed=emb)
        
        else:
            
            emb = discord.Embed(title="Es wurde kein level up channel verstgelgt", description="Es wurde keine level up channel festgelgt wenn du einen festlegen möchtest benutze:\n", color=error_red)
            await ctx.respond(embed=emb)

        level_system_db.db_close(cursor=my_cursor, db_connection=levelsystem_connect)

    
    # Testen und neu Optimieren
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        print(f"before = {before}, after = {after}")
        
        level_connect = level_system_db.levelconnect()
        my_cursor = level_connect.cursor()

        guild_id = str(member.guild.id)
        user_id = str(member.id)

        check_levelsystem_info = "SELECT * FROM levelsystem_info WHERE guild_ID = %s AND user_ID = %s"
        check_levelsystem_info_values = [guild_id, user_id]
        my_cursor.execute(check_levelsystem_info, check_levelsystem_info_values)
        
        voice_levelsystem_check = my_cursor.fetchone()

        if voice_levelsystem_check:

            if voice_levelsystem_check[2] >= 999:
                return
        
        
        level_system_db.db_close(cursor=my_cursor, db_connection=level_connect)
        
        print(member, before, after)

bot.add_cog(level_system(bot))




