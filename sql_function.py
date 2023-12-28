import os
import mysql.connector

import discord
from discord.ext import commands


#######################  Database connection  #######################

class DatabaseSetup():

    def db_connector():

        db_connector = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv("sql_passwort"), database=os.getenv('discord_db'), buffered=True)
        return db_connector

    def db_close(cursor, db_connection):

        if db_connection.is_connected():
            
            db_connection.close()
            cursor.close()

        else:
            pass

        

class DatabaseStatusCheck():

    # Returns True if an element is on the blacklist.
    def _blacklist_check_text(guild_id:int, message_check:discord.Message):

        if isinstance(message_check.channel, discord.TextChannel):

            levelsystem_blacklist = DatabaseCheck.check_blacklist(guild_id=guild_id)

            if levelsystem_blacklist:

                for _, channel_blacklist, category_blacklist, role_blacklist, user_blacklist in levelsystem_blacklist:
                   
                    if user_blacklist == message_check.author.id:
                        return True

                    if role_blacklist != None:
                        
                        blacklist_role = message_check.guild.get_role(role_blacklist)
                        if blacklist_role in message_check.author.roles:
                            return True
                                
                    if message_check.channel.category.id == category_blacklist:
                        return True

                    if message_check.channel.id == channel_blacklist:
                        return True
                        
            else:
                return None
            
    
    # Returns the value True if "on" in the database and False when not
    def _level_system_status(guild_id:int):

        levelsystem_status = DatabaseCheck.check_level_settings(guild_id=guild_id)
        # Anpassen das es auch überprüft ob voice und so an ist!
        if levelsystem_status:

            if levelsystem_status[2] == "on":
                return True
            
            else:
                return False
            
        else:
            return None



##################################################  Database Statemants  #####################################

class DatabaseCheck():

#################################################  Checks Level System  ##############################################################


    # Checks the Blacklist from the level system
    def check_blacklist(guild_id:int, channel_id:int = None, category_id:int = None, role_id:int = None, user_id:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        
        all_items = [channel_id, category_id, role_id, user_id]
        
        if all(x is None for x in all_items):
            
            check_blacklist = f"SELECT * FROM LevelSystemBlacklist WHERE guildId = %s"
            check_blacklist_values = [guild_id]

        else:
            
            for count in range(len(all_items)):
                if all_items[count] != None:
                    
                    check_blacklist = f"SELECT * FROM LevelSystemBlacklist WHERE guildId = %s AND {column_name[count]} = %s"
                    check_blacklist_values = [guild_id, all_items[count]]

        cursor.execute(check_blacklist, check_blacklist_values)
        
        if all(x is None for x in all_items):
            blacklist = cursor.fetchall()
        
        else:
            blacklist = cursor.fetchone()
            
        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return blacklist
 
    
    # Checks the stats from a user in the level system
    def check_level_system_stats(guild_id:int, user:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        if user != None:

            levelsys_stats_check = "SELECT * FROM LevelSystemStats WHERE guildId = %s AND userId = %s"
            levelsys_stats_check_values = [guild_id, user]

        else:

            levelsys_stats_check = "SELECT * FROM LevelSystemStats WHERE guildId = %s"
            levelsys_stats_check_values = [guild_id]

        cursor.execute(levelsys_stats_check, levelsys_stats_check_values)

        if user != None:
            levelsys_stats = cursor.fetchone()
        else:
            levelsys_stats = cursor.fetchall()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return levelsys_stats
    
    
    # Checks the level roles, when you get them or what level you need to get them
    def check_level_system_levelroles(guild_id:int, level_role:int = None, needed_level:int = None, status:str = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        if level_role != None and needed_level != None and status == None:

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s AND roleId = %s AND roleLevel = %s"
            levelsys_levelroles_check_values = [guild_id, level_role, needed_level]
        
        elif level_role != None and needed_level == None and status == None:

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s AND roleId = %s"
            levelsys_levelroles_check_values = [guild_id, level_role]

        elif level_role == None and needed_level != None and status == None:

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s AND roleLevel = %s"
            levelsys_levelroles_check_values = [guild_id, needed_level]

        elif level_role != None and needed_level != None and status == "check":

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s AND roleId = %s OR roleLevel = %s"
            levelsys_levelroles_check_values = [guild_id, level_role, needed_level]

        elif level_role == None and needed_level == None and status == "level_role":
            
            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s ORDER BY roleLevel DESC"
            levelsys_levelroles_check_values = [guild_id]

        else:

            levelsys_levelroles_check = "SELECT * FROM LevelSystemRoles WHERE guildId = %s"
            levelsys_levelroles_check_values = [guild_id]

        cursor.execute(levelsys_levelroles_check, levelsys_levelroles_check_values)

        if level_role == None and needed_level == None:
            levelsys_levelroles = cursor.fetchall()
        else:
            levelsys_levelroles = cursor.fetchone()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return levelsys_levelroles
    

    def check_xp_bonus_list(guild_id:int, channel_id:int = None, category_id:int = None, role_id:int = None, user_id:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        
        all_items = [channel_id, category_id, role_id, user_id]
        
        if all(x is None for x in all_items):
            
            check_xp_bonus_list = f"SELECT * FROM BonusXpList WHERE guildId = %s"
            check_xp_bonus_list_values = [guild_id]

        else:
            
            for count in range(len(all_items)):
                if all_items[count] != None:
                    
                    check_xp_bonus_list = f"SELECT * FROM BonusXpList WHERE guildId = %s AND {column_name[count]} = %s"
                    check_xp_bonus_list_values = [guild_id, all_items[count]]

        cursor.execute(check_xp_bonus_list, check_xp_bonus_list_values)
        
        if all(x is None for x in all_items):
            xp_bonus_list = cursor.fetchall()
        
        else:
            xp_bonus_list = cursor.fetchone()
            
        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return xp_bonus_list
    

    def check_level_settings(guild_id:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        level_settings_check = "SELECT * FROM LevelSystemSettings WHERE guildId = %s"
        level_settings_check_values = [guild_id]
        cursor.execute(level_settings_check, level_settings_check_values)
        level_system_settings = cursor.fetchone()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return level_system_settings



#######################################################  Checks the auto reaction system  ################################################


    # Checks the autoreaction system
    def check_autoreaction(guild:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        autoreaction_check = "SELECT * FROM AutoReactionSetup WHERE guildId = %s"
        autoreaction_check_values = [guild]
        cursor.execute(autoreaction_check, autoreaction_check_values)
        auto_reaction = cursor.fetchall()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return auto_reaction



########################################################  Checks the bot settings  ##############################################


    # Checks the bot settings 
    def check_bot_settings(guild_id:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        bot_settings_check = "SELECT * FROM BotSettings WHERE guildId = %s"
        bot_settings_check_values = [guild_id]
        cursor.execute(bot_settings_check, bot_settings_check_values)
        bot_settings = cursor.fetchone()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return bot_settings



#####################################  Inserting and updating the database  ####################################

class DatabaseUpdates():

###############################################  Bot Settings  ###############################################


    def _create_bot_settings(guild_id:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        sql_tables = ["BotSettings", "LevelSystemSettings"]

        try:

            for table in sql_tables:

                creat_bot_settings = f"INSERT INTO {table} (guildId) VALUES (%s)"
                creat_bot_settings_values = [guild_id]
                cursor.execute(creat_bot_settings, creat_bot_settings_values)
                db_connect.commit()

        except mysql.connector.Error as error:
           print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    def update_bot_settings(guild_id:int, 
                            bot_colour:str = None, 
                            ghost_ping:int = None, 
                            anti_link:int = None, 
                            anti_link_timeout:int = None,
                            back_to_none:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["botColour", "ghostPing", "antiLink"]
        items = [bot_colour, ghost_ping, anti_link]

        try:
            
            if back_to_none == None:

                for count in range(len(items)):
                    
                    if items[count] != None:

                        update_settings = f'UPDATE BotSettings SET {column_name[count]} = %s{f", antiLinkTimeout = {anti_link_timeout}" if anti_link_timeout != None else ""} WHERE guildId = %s'
                        update_settings_values = (items[count], guild_id)
                        cursor.execute(update_settings, update_settings_values)
                        db_connect.commit()

            else:

                update_settings = f'UPDATE BotSettings SET {column_name[back_to_none]} = DEFAULT WHERE guildId = %s'
                update_settings_values = [guild_id]
                cursor.execute(update_settings, update_settings_values)
                db_connect.commit()
            
        except mysql.connector.Error as error:
            print('parameterized query failed {}'.format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)



########################################  Insert into / Update the Level System  ##################################################


    # Inserts all data of the user into the database
    def _insert_user_stats_level(guild_id:int, user_id:int, user_name:str, user_level:int = 0, user_xp:int = 0, whole_xp:int = 0):
    
        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            insert_new_user = "INSERT INTO LevelSystemStats (guildId, userId, userLevel, userXp, userName, wholeXp) VALUES (%s, %s, %s, %s, %s, %s)"        
            insert_new_user_values = [guild_id, user_id, user_level, user_xp, user_name, whole_xp]
            cursor.execute(insert_new_user, insert_new_user_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
    

    # Inserts the infos about the level roles into the database
    def _insert_level_roles(guild_id:int, role_id:int, level:int, guild_name):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            insert_level_role = "INSERT INTO LevelSystemRoles (guildId, roleId, roleLevel, guildName) VALUES (%s, %s, %s, %s)"
            insert_level_role_values = [guild_id, role_id, level, guild_name]
            cursor.execute(insert_level_role, insert_level_role_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        

    # Function that adds all specified data to the blacklist 
    def manage_blacklist(guild_id:int, operation:str, channel_id:int = None, category_id:int = None, role_id:int = None, user_id:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        items = [channel_id, category_id, role_id, user_id]
        
        try:
            
            if any(i is not None for i in items) and operation != "reset":
            
                for count in range(len(items)):
                    
                    if items[count] != None:

                        if operation == "add":
                            
                            level_sys_blacklist = f"INSERT INTO LevelSystemBlacklist (guildId, {column_name[count]}) VALUES (%s, %s)"
                            level_sys_blacklist_values = [guild_id, items[count]]
                        
                        elif operation == "remove":
                            
                            level_sys_blacklist = f"DELETE FROM LevelSystemBlacklist WHERE guildId = %s AND {column_name[count]} = %s"
                            level_sys_blacklist_values = [guild_id, items[count]]

                        cursor.execute(level_sys_blacklist, level_sys_blacklist_values)
                        db_connect.commit()

            elif operation == "reset":
                
                level_sys_blacklist = f"DELETE FROM LevelSystemBlacklist WHERE guildId = %s"
                level_sys_blacklist_values = [guild_id]
        
                cursor.execute(level_sys_blacklist, level_sys_blacklist_values)
                db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)

    
    # Update the level system settings
    def update_level_settings(guild_id:int, xp_rate:int = None, level_status:str = None, levelup_channel:int = None, level_up_message:str = None, percentage:int = None, back_to_none:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        column_name = ["xpRate", "levelStatus", "levelUpChannel", "levelUpMessage","bonusXpPercentage"]
        items = [xp_rate, level_status, levelup_channel, level_up_message, percentage]

        try:
            
            if back_to_none == None:

                for count in range(len(items)):

                    if items[count] != None:

                        update_settings = f"UPDATE LevelSystemSettings SET {column_name[count]} = %s WHERE guildId = %s"
                        update_settings_values = (items[count], guild_id)
                        cursor.execute(update_settings, update_settings_values)
                        db_connect.commit()

            else:

                update_settings = f"UPDATE LevelSystemSettings SET {column_name[back_to_none]} = DEFAULT WHERE guildId = %s"
                update_settings_values = [guild_id]
                cursor.execute(update_settings, update_settings_values)
                db_connect.commit()
            
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    # Update the stats from users in the level system  
    def _update_user_stats_level(guild_id:int, user_id:int, level:int = None, xp:int = None, whole_xp:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            if xp != None and whole_xp != None:

                update_stats = f"UPDATE LevelSystemStats SET userXp = %s, wholeXp = %s WHERE guildId = %s AND userId = %s"
                update_stats_values = [xp, whole_xp, guild_id, user_id]

            elif xp != None and whole_xp == None:

                update_stats = f"UPDATE LevelSystemStats SET userXp = %s WHERE guildId = %s AND userId = %s"
                update_stats_values = [xp, guild_id, user_id]

            elif level != None:

                update_stats = f"UPDATE LevelSystemStats SET userLevel = %s, userXp = %s, wholeXp = %s WHERE guildId = %s AND userId = %s"
                update_stats_values = [level, 0, whole_xp, guild_id, user_id]
            
            cursor.execute(update_stats, update_stats_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    # Update the level roles
    def update_level_roles(guild_id:int, role_id:int = None, role_level:int = None, status:str = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor() 
     
        try:

            if status == "role":
                    
                update_level_roles = "UPDATE LevelSystemRoles SET roleLevel = %s WHERE guildId = %s AND roleId = %s"
                update_level_roles_values = [role_level, guild_id, role_id]
                
            elif status == "level":

                update_level_roles = "UPDATE LevelSystemRoles SET roleId = %s WHERE guildId = %s AND roleLevel = %s"
                update_level_roles_values = [role_id, guild_id, role_level]

            cursor.execute(update_level_roles, update_level_roles_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)

    
    # Updates the bonus xp system
    def manage_xp_bonus(guild_id:int, operation:str, channel_id:int = None, category_id:int = None, role_id:int = None, user_id:int = None, bonus:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        items = [channel_id, category_id, role_id, user_id]
        
        try:
            
            if any(elem is not None for elem in items) and operation != "reset":

                for count in range(len(items)):
                    
                    if items[count] != None:
                        
                        if operation == "add":
                            
                            bonus_list = f"INSERT INTO BonusXpList (guildId, {column_name[count]}) VALUES (%s, %s)" if bonus == None else f"INSERT INTO BonusXpList (guildId, {column_name[count]}, PercentBonusXp) VALUES (%s, %s, %s)"
                            bonus_list_values = [guild_id, items[count]] if bonus == None else [guild_id, items[count], bonus]
                        
                        elif operation == "remove":
                            
                            bonus_list = f"DELETE FROM BonusXpList WHERE guildId = %s AND {column_name[count]} = %s"
                            bonus_list_values = [guild_id, items[count]]

                        cursor.execute(bonus_list, bonus_list_values)
                        db_connect.commit()

            elif operation == "reset":
                
                bonus_list = f"DELETE FROM BonusXpList WHERE guildId = %s"
                bonus_list_values = [guild_id]

                cursor.execute(bonus_list, bonus_list_values)
                db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)



class DatabaseRemoveDatas():

###########################################################  Removes values from the level system  #######################################


    # Removes level system stats
    def _remove_level_system_stats(guild_id:int, user_id:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:
        
            remove_stats = "DELETE FROM LevelSystemStats WHERE guildId = %s AND userId = %s" if user_id != None else "DELETE FROM LevelSystemStats WHERE guildId = %s"
            remove_stats_values = [guild_id, user_id] if user_id != None else [guild_id]
            
            cursor.execute(remove_stats, remove_stats_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)


    # Removes level roles from the level system
    def _remove_level_system_level_roles(guild_id:int, role_id:int = None, role_level:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        if role_id != None and role_level == None:
            column_name, data = "roleId", role_id
        elif role_level != None and role_id == None:
            column_name, data = "roleLevel", role_level

        try:

            if all(x is None for x in [role_id, role_level]):
                remove_level_role = "DELETE FROM LevelSystemRoles WHERE guildId = %s"
                remove_level_role_values = [guild_id]

            else:

                remove_level_role = f"DELETE FROM LevelSystemRoles WHERE guildId = %s AND {column_name} = %s"
                remove_level_role_values = [guild_id, data]

            cursor.execute(remove_level_role, remove_level_role_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)



#############################################################  Removes the bot settings  ############################################


    # Removes the data from the bot settings
    def _remove_bot_settings(guild:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            remove_settings = "DELETE FROM BotSettings WHERE guildId = %s"
            remove_settings_values = [guild]
            cursor.execute(remove_settings, remove_settings_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)