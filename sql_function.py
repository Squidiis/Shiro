import os
import mysql.connector
from utils import *
import discord

#######################  Database connection  #######################

'''
Establishes a connection to the db
All required data must be included in the .env file
'''
class DatabaseSetup():

    def db_connector():

        db_connector = mysql.connector.connect(host=os.getenv('host'), user=os.getenv('user'), password=os.getenv("sql_password"), database=os.getenv('discord_db'), buffered=True)
        return db_connector

    def db_close(cursor, db_connection):

        if db_connection.is_connected():
            
            db_connection.close()
            cursor.close()

        else:
            pass



##################################################  Database Statemants  #####################################

# Contains all check functions of the entire bot
class DatabaseCheck():

#################################################  Checks Level System  ##############################################################

    
    '''
    Checks whether a channel, category, role or user is on the blacklist
    if you specify individual IDs, the system only checks whether they are present, if they are not present, none is returned if they are present, the entire entry is returned 

    Parameters:
    -----------
        - guild_id
            Id of the server
        - channel_id
            Id of the channel to be checked
        - category_id
            Id of the category to be checked
        - role_id 
            Id of the role to be checked
        - user_id
            Id of the user to be checked

    Info:
        - guild_id must be specified
        - If only the `guild_id` is specified, all entries specified for the server are returned
        - Always specify only one id otherwise errors may occur     
    '''
    def check_blacklist(
        guild_id:int, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

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
 
    
    '''
    If you specify a user, the user's statistics are returned; if no user is specified, the statistics of all users on the server are returned

    Parameters:
    -----------
        - guild_id
            Id of the server
        - user_id
            Id of the user

    Info:
        - The guild_id must be specified
        - If only the `guild_id` is specified, all entries specified for the server are returned
    '''
    def check_level_system_stats(guild_id:int, user_id:int = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        if user_id != None:

            levelsys_stats_check = "SELECT * FROM LevelSystemStats WHERE guildId = %s AND userId = %s"
            levelsys_stats_check_values = [guild_id, user_id]

        else:

            levelsys_stats_check = "SELECT * FROM LevelSystemStats WHERE guildId = %s"
            levelsys_stats_check_values = [guild_id]

        cursor.execute(levelsys_stats_check, levelsys_stats_check_values)

        if user_id != None:
            levelsys_stats = cursor.fetchone()
        else:
            levelsys_stats = cursor.fetchall()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return levelsys_stats
    
    
    '''
    Returns all level roles that are available on the server
    if you specify individual IDs, the system only checks whether they are present, if they are not present, none is returned if they are present, the entire entry is returned 

    Parameters:
    ------------
        - guild_id
            Id of the server
        - level_role
            The id of the level role to be returned
        - needed_level
            The level from which the role is assigned
        - status
            - check
                Checks whether the level or role is in the database
            - level_role
                Returns all level roles from level descending

    Info:
        - guild_id must be specified
        - If no status, level or role is specified, all level roles are returned
        - If a level is specified but no status or role, the entry for the level is returned
        - If only one role is specified and no level or status, the entry with the role is returned
        - If no entry exists, None is returned
    '''
    def check_level_system_levelroles(
        guild_id:int, 
        level_role:int = None, 
        needed_level:int = None, 
        status:str = None):

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
    

    '''
    Returns the entries of the bonus-xp-list that are defined for a server, 
    if you specify individual IDs, the system only checks whether they are present, if they are not present, none is returned if they are present, the entire entry is returned 

    Parameters:
    -----------
        - guild_id
            Id of the server
        - channel_id
            Id of the channel to be checked
        - category_id
            Id of the category to be checked
        - role_id 
            Id of the role to be checked
        - user_id
            Id of the user to be checked

    Info:
        - guild_id must be specified
        - If only the `guild_id` is specified, all entries specified for the server are returned
        - Always specify only one id otherwise errors may occur     
    '''
    def check_xp_bonus_list(
        guild_id:int, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

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
    

    '''
    Returns the settings of a server if you enter the guild_id

    Parameters:
    -----------
        - guild_id
            Id of the server

    Info:
        - guild_id must be specified
    '''
    def check_level_settings(guild_id:int):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        level_settings_check = "SELECT * FROM LevelSystemSettings WHERE guildId = %s"
        level_settings_check_values = [guild_id]
        cursor.execute(level_settings_check, level_settings_check_values)
        level_system_settings = cursor.fetchone()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return level_system_settings
    

    '''
    Returns either all entries of the antilink whitelist or only specific ones depending on which item is specified

    Parameters:
    -----------
        - guild_id
            Id of the server
        - channel_id
            Id of the channel to be checked
        - category_id
            Id of the category to be checked
        - role_id
            Id of the role to be checked
        - user_id
            Id of the user to be checked
    
    Info:
        - guild_id must be specified
        - Depending on which item you specify, you will receive the respective entries from the database
        - If you do not specify a channel, category, role or user id, the entire whitelist will be returned
    '''
    def check_antilink_whitelist(
        guild_id:int, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        column_name = ["channelId", "categoryId", "roleId", "userId"]
        
        all_items = [channel_id, category_id, role_id, user_id]
        
        if all(x is None for x in all_items):
            
            check_white_list = f"SELECT * FROM AntiLinkWhiteList WHERE guildId = %s"
            check_white_list_values = [guild_id]

        else:
            
            for count in range(len(all_items)):
                if all_items[count] != None:
                    
                    check_white_list = f"SELECT * FROM AntiLinkWhiteList WHERE guildId = %s AND {column_name[count]} = %s"
                    check_white_list_values = [guild_id, all_items[count]]

        cursor.execute(check_white_list, check_white_list_values)
        
        if all(x is None for x in all_items):
            white_list = cursor.fetchall()
        
        else:
            white_list = cursor.fetchone()
            
        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return white_list


    '''
    Returns the settings of the leadebourd 

    Parameters:
    -----------
        - guild_id
            Id of the server
        
    Info:
        - guild_id must be specified
    '''
    def check_leaderboard_settings(guild_id:int, system:str = None):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        check_settings = f"SELECT * FROM {'LeaderboardSettingsMessage' if system == "message" else 'LeaderboardSettingsInvite'} WHERE guildId = %s"
        check_settings_values = [guild_id]
        cursor.execute(check_settings, check_settings_values)

        leaderboard_settings = cursor.fetchone()

        DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)
        return leaderboard_settings
    

    '''
    Returns either all entries of the leaderboard or only specific ones depending on which item is specified

    Parameters:
    -----------
        - guild_id
            Id of the server
        - user_id
            Id of the user to be checked
        - interval
            The interval in which the leaderboard is updated (distinguishes between message and invite leaderboard)
            - 0 day or week
            - 1 week or month
            - 2  month or quarter
            - 3 whole
            
    Info:
        - guild_id must be specified
        - Depending on which item you specify, you will receive the respective entries from the database
        - If you do not specify a channel, category, role or user id, the entire whitelist will be returned
    '''
    def check_leaderboard(
        guild_id:int,
        system:str, 
        user_id:int = None,
        interval:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        column_name = [
            "dailyCountMessage", "weeklyCountMessage", "monthlyCountMessage", "wholeCountMessage"
            ] if system == "message" else [
            "weeklyCountInvite", "monthlyCountInvite", "quarterlyCountInvite", "wholeCountInvite"]

        if interval != None:

            check_leaderboard_count = f"SELECT * FROM LeaderboardTacking WHERE guildId = %s ORDER BY {column_name[interval]} DESC"
            check_leaderboard_count_values = [guild_id]
        
        else:

            check_leaderboard_count = f"SELECT * FROM LeaderboardTacking WHERE guildId = %s AND userId = %s"
            check_leaderboard_count_values = [guild_id, user_id]

        cursor.execute(check_leaderboard_count, check_leaderboard_count_values)

        if interval != None:
            leaderboard = cursor.fetchall()
        else:
            leaderboard = cursor.fetchone()

        DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        return leaderboard
    

    '''
    Returns all leaderboard roles that are available on the server
    if you specify individual IDs, the system only checks whether they are present, if they are not present, none is returned if they are present, the entire entry is returned 

    Parameters:
    ------------
        - guild_id
            Id of the server
        - system
            Which system is affected
                - message
                - invite
        - role_id
            The id of the leaderboard role to be returned
        - position
            The potition from which the role is assigned
        - interval
            - daily or weekly
                Daily updated leaderboard / weekly
            - weekly or monthly
                Weekly updated leaderboard / monthly
            - monthly or quarterly
                Monthly updating leaderboard / quarterly
            - general
                Leaderboard that is updated daily shows the total activity (only those who have written the most messages)

    Info:
        - guild_id must be specified
        - If no role_id, position or interval is specified, all leadboard roles are returned
        - If a position is specified but no interval or role, the entry for the position is returned
        - If only one role is specified and no interval or position, the entry with the role is returned
        - If no entry exists, None is returned
    '''
    def check_leaderboard_roles(
        guild_id:int,
        system:str,
        role_id:int = None, 
        position:int = None,
        interval:str = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        check = False
        if role_id != None and position != None:

            check_roles = "SELECT * FROM LeaderboardRoles WHERE guildId = %s AND status = %s AND roleId = %s OR rankingPosition = %s"
            check_roles_values = [guild_id, system, role_id, position]

        elif role_id:

            check_roles = "SELECT * FROM LeaderboardRoles WHERE guildId = %s AND roleId = %s AND status = %s"
            check_roles_values = [guild_id, role_id, system]

        elif position:

            check_roles = "SELECT * FROM LeaderboardRoles WHERE guildId = %s AND rankingPosition = %s AND status = %s"
            check_roles_values = [guild_id, position, system]

        elif interval and role_id:

            check = True
            check_roles = "SELECT * FROM LeaderboardRoles WHERE guildId = %s AND roleId = %s AND roleInterval = %s AND status = %s"
            check_roles_values = [guild_id, role_id, interval, system]

        else:
            
            check_roles = f"SELECT * FROM LeaderboardRoles WHERE guildId = %s AND status = %s {'AND roleInterval = %s' if interval != None else ''} ORDER BY rankingPosition DESC"
            check_roles_values = [guild_id, system] if interval == None else [guild_id, system, interval]

        cursor.execute(check_roles, check_roles_values)
        if role_id == None and position == None or check == True:
            leaderboard_roles = cursor.fetchall()
        else:
            leaderboard_roles = cursor.fetchone()
        
        DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)
        return leaderboard_roles
    

    '''
    Returns all assigned leaderboard roles

    Parameters:
    ------------
        - guild_id
            Id of the server
        - interval
            From which interval the assigned roles should be returned
            - daily or weekly
            - weekly or monthly
            - monthly or quarterly
            - general
        - status
            for which system it was given
            - message
            - invite
    
    Info:
        - All variables must always be specified
    '''
    def check_leaderboard_roles_users(guild_id:int, interval:str, status:str):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        check_users = "SELECT * FROM LeaderboardGivenRoles WHERE guildId = %s AND roleInterval = %s AND status = %s"
        check_users_values = [guild_id, interval, status]

        cursor.execute(check_users, check_users_values)
        leaderbaord_user_roles = cursor.fetchall()

        return leaderbaord_user_roles
    

    '''
    Returns all invite codes or only specific ones

    parameters:
    ------------
        - guild_id
            Server id
        - invite_code
            Which invite code should be returned
        - user_id
            User id
        - remove_value
            If this is None, everything is returned
    
    Info:
        - guild_id must be specified
    '''
    def check_invite_codes(
        guild_id:int,
        invite_code:str = None,  
        user_id:int = None,
        remove_value:str = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        if invite_code:

            check_invite = f"SELECT * FROM LeaderboardInviteTracking WHERE guildId = %s AND inviteCode = %s {'AND user_id = %s' if user_id != None else ''}"
            check_invite_values = [guild_id, user_id, invite_code] if user_id != None else [guild_id, invite_code]

        else:

            check_invite = f"SELECT {'*' if remove_value == None else 'inviteCode'} FROM LeaderboardInviteTracking WHERE guildId = %s"
            check_invite_values = [guild_id]
        
        cursor.execute(check_invite, check_invite_values)

        if invite_code:
            invite_code_check = cursor.fetchone()
        else:
            invite_code_check = cursor.fetchall()

        return invite_code_check
    

    '''
    Returns all auto-reactions or only specific ones

    parameters:
    ------------
        - guild_id
            Server id
        - channel_id
            Id of the channel to be scanned
        - category_id
            Id of the category to be checked
        - parameter
            Which parameters to search for
                - links, images and videos
                - text messages
                - any message
        - emoji
            Which emoji mention to search for
    
    Info:
        - guild_id must be specified
        - If no channel or category is specified, all auto-reactions are returned
    '''
    def check_auto_reaction(
        guild_id:int,
        channel_id:int = None,
        category_id:int = None,
        parameter:str = None,
        emoji:str = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        column_name = ["channelId", "categoryId", "parameter", "emoji"]
        column_value = [channel_id, category_id, parameter, emoji]
        
        check = None
        for count in range(len(column_value)):
           
            if (channel_id is not None or category_id is not None) and parameter is not None and emoji is not None:
                check = True
                check_autoreact = f"SELECT * FROM AutoReactions WHERE guildId = %s AND {'channelId' if channel_id != None else 'categoryId'} = %s AND parameter = %s AND emoji = %s"
                check_autoreact_values = [guild_id, channel_id if channel_id != None else category_id, parameter, emoji]

            elif any(value is not None for value in column_value):
                
                for count in range(len(column_value)):

                    if column_value[count] is not None:
                        check_autoreact = f"SELECT * FROM AutoReactions WHERE guildId = %s AND {column_name[count]} = %s"
                        check_autoreact_values = [guild_id, column_value[count]]
                        break
            
            else:

                check_autoreact = f"SELECT * FROM AutoReactions WHERE guildId = %s"
                check_autoreact_values = [guild_id] 

        cursor.execute(check_autoreact, check_autoreact_values)

        if check == True:
            auto_react_settings = cursor.fetchone()
        else:
            auto_react_settings = cursor.fetchall()

        return auto_react_settings



########################################################  Checks the bot settings  ##############################################


    '''
    Returns how the level system is set on the respective servers

    Info:
        - guild_id must be specified
    '''
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

    '''
    Creates entries for a server on which the bot has just joined

    Table Daten: 

        BotSettings:
            guildId BIGINT UNSIGNED NOT NULL
            botColour VARCHAR(20) NULL
            ghostPing BIT DEFAULT 0
            antiLink BIT(4) DEFAULT 3
            antiLinkTimeout INT DEFAULT 0

        LevelSystemSettings:
            guildId BIGINT UNSIGNED NOT NULL,
            xpRate INT UNSIGNED DEFAULT 20,
            levelStatus VARCHAR(50) DEFAULT 'on',
            levelUpChannel BIGINT UNSIGNED NULL,
            levelUpMessage VARCHAR(500) DEFAULT 'Oh nice {user} you have a new level, your newlevel is {level}',
            bonusXpPercentage INT UNSIGNED DEFAULT 10
    '''
    async def _create_bot_settings(guild_id:int):

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


    '''
    Updates the individual settings of the bot

    Parameters:
    -----------
        - guild_id
            The server id of the current server
        - bot_colour
            The color code which color the embeds should have (can also be changed in config.yaml)
        - ghost_ping
            How the ghost_ping system should work
                - 1: switched on
                - 0: switched off
        - antilink
            How the antilink system should behave
                - 0: All messages with a discord invitation link will be deleted
                - 1: Every message with a link will be deleted exept Pictures and Videos
                - 2: All messages with a link will be deleted this also includes pictures and videos
                - 3: Deactivate antilink system! (no messages are deleted)
        - antilink_timeout
            How long someone should receive a timeout if they violate the antilink system
        - back_to_none
            Depending on the value, a system is set back to default settings
                - 0: The bot color is set back to the default value
                - 1: The ghost ping system is switched off
                - 2: The Antilink system is switched off
                - 3: The Antilink timeout is set back to 0 minutes 

    Info:
        - guild_id must be specified
        - all values must have the specified data type
    '''
    async def update_bot_settings(
        guild_id:int, 
        bot_colour:str = None, 
        ghost_ping:int = None, 
        antilink:int = None, 
        antilink_timeout:int = None,
        back_to_none:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["botColour", "ghostPing", "antiLink", "antiLinkTimeout"]
        items = [bot_colour, ghost_ping, antilink]

        try:
            
            if back_to_none == None:

                for count in range(len(items)):
                    
                    if items[count] != None:

                        update_settings = f'UPDATE BotSettings SET {column_name[count]} = %s{f", antiLinkTimeout = {antilink_timeout}" if antilink_timeout != None else ""} WHERE guildId = %s'
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


    '''
    Serves to set the antilink whitelist, can add as well as remove or completely reset things

    Parameters:
    -----------
        - guild_id
            Id of the server
        - operation
            What should be done
                - add: If something is to be added to the whitelist
                - remove: If something is to be removed from the whitelist
                - reset: Resets the whitelist
        - channel_id
            Id of the channel you want to add or remove
        - category_id
            Id of the category you want to add or remove
        - role_id
            Id of the role you want to add or remove
        - user_id
            Id of the user you want to add or remove

    Info:
        - guild_id must be specified
        - An operation must be specified either add, remove or reset
    '''
    async def manage_antilink_whitelist(
        guild_id:int, 
        operation:str, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        column_name = ["channelId", "categoryId", "roleId", "userId"]
        items = [channel_id, category_id, role_id, user_id]
        
        try:
            
            if any(elem is not None for elem in items) and operation != "reset":

                for count in range(len(items)):
                    
                    if items[count] != None:
                        
                        if operation == "add":
                            
                            white_list = f"INSERT INTO AntiLinkWhiteList (guildId, {column_name[count]}) VALUES (%s, %s)"
                            white_list_values = [guild_id, items[count]]
                        
                        elif operation == "remove":
                            
                            white_list = f"DELETE FROM AntiLinkWhiteList WHERE guildId = %s AND {column_name[count]} = %s"
                            white_list_values = [guild_id, items[count]]

                        cursor.execute(white_list, white_list_values)
                        db_connect.commit()

            elif operation == "reset":
                
                white_list = f"DELETE FROM AntiLinkWhiteList WHERE guildId = %s"
                white_list_values = [guild_id]

                cursor.execute(white_list, white_list_values)
                db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)



########################################  Insert into / Update the level System  ##################################################


    '''
    Creates entries for users who are new to the level system 

    Parameters:
    -----------
        - guild_id
            Id of the server
        - user_id
            Id of the user
        - user_name
            Name of the user
        - user_level
            Number of levels the user has (is always 0 at the beginning)
        - user_xp
            Number of XP the user has (is always 0 at the beginning)
        - whole_xp
            Number of XP the user has in total (is always 0 at the beginning)

    Info:
        - guild_id, user_id, user_level must be specified
        - All other values have a default value and do not need to be changed
    '''
    async def insert_user_stats_level(
        guild_id:int, 
        user_id:int, 
        user_name:str, 
        user_level:int = 0, 
        user_xp:int = 0, 
        whole_xp:int = 0
        ):
    
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
    

    '''
    Creates entries for the level roles

    Parameters:
    -----------
        - guild_id
            Id of the server
        - role_id
            Id of the new level role
        - level
            Level from which the level role should be assigned
    
    Info:
        - All values must be specified
    '''
    async def insert_level_roles(
        guild_id:int, 
        role_id:int, 
        level:int
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            insert_level_role = "INSERT INTO LevelSystemRoles (guildId, roleId, roleLevel) VALUES (%s, %s, %s)"
            insert_level_role_values = [guild_id, role_id, level]
            cursor.execute(insert_level_role, insert_level_role_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)
        

    '''
    Serves to set the level system blacklist, can add as well as remove or completely reset things

    Parameters:
    -----------
        - guild_id
            Id of the server
        - operation
            What should be done
                - add: If something is to be added to the blacklist
                - remove: If something is to be removed from the blacklist
                - reset: Resets the blacklist
        - channel_id
            Id of the channel you want to add or remove
        - category_id
            Id of the category you want to add or remove
        - role_id
            Id of the role you want to add or remove
        - user_id
            Id of the user you want to add or remove

    Info:
        - guild_id must be specified
        - An operation must be specified either add, remove or reset
    '''
    async def manage_blacklist(
        guild_id:int, 
        operation:str, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None
        ):

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

    
    '''
    Updates the individual settings of the level system

    Parameters:
    -----------
        - guild_id
            The server id of the current server
        - xp_rate
            Amount of XP awarded per message
        - level_status
            - on
            - off
        - level_up_channel
            Channel in which level up notifications are sent
        - level_up_message
            Level up notification message
        - percentage
            Percentage of how much more XP should be awarded when writing to a channel, category, role or user
        - back_to_none
            Depending on the value, a system is set back to default settings
                - 0: xp rate is set back to 20
                - 1: The level system is set to `on
                - 2: Level up channel is reset so level up notifications are sent back to the channel with the last activity
                - 3: Level up message is set back to `Oh nice {user} you have a new level, your newlevel is {level}`
                - 4: The bonus XP percentage is set back to 10

    Info:
        - guild_id must be specified
        - All values must have the specified data type
    '''
    async def update_level_settings(
        guild_id:int, 
        xp_rate:int = None, 
        level_status:str = None, 
        level_up_channel:int = None, 
        level_up_message:str = None, 
        percentage:int = None, 
        back_to_none:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        column_name = ["xpRate", "levelStatus", "levelUpChannel", "levelUpMessage","bonusXpPercentage"]
        items = [xp_rate, level_status, level_up_channel, level_up_message, percentage]

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


    '''
    Updates the stats of a single user

    Parameters:
    -----------
        - guild_id
            Server id
        - user_id
            Id of the user whose stats are to be changed
        - level
            New level of the user
        - xp
            New amount of XP of the user
        - whole_xp
            Amount of the user's total XP

    Info:
        - guild_id and user_id must be specified as well as either XP and whole_xp or level
        - If you give a user XP without having earned it through activities, it will not be counted towards the whole_xp
    ''' 
    async def update_user_stats_level(
        guild_id:int, 
        user_id:int, 
        level:int = None, 
        xp:int = None, 
        whole_xp:int = None
        ):

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


    '''
    Updates the level-roles

    Parameters:
    -----------
        - guild_id
            Id of the server
        - role_id
            Id of the role to be changed
        - role_level
            Level at which a role is to be redefined
        - status
            Which value is to be overwritten
                - role: The role is given a new level
                - level: The level receives a new role

    Info:
        - guild_id must be specified
        - Status only needs to be specified if you want to overwrite an existing entry 
    '''
    async def update_level_roles(
        guild_id:int, 
        role_id:int = None, 
        role_level:int = None, 
        status:str = None
        ):

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

    
    '''
    Serves to set the bonus xp list, can add as well as remove or completely reset things

    Parameters:
    -----------
        - guild_id
            Id of the server
        - operation
            What should be done
                - add: If something is to be added to the bonus xp list
                - remove: If something is to be removed from the bonus xp list
                - reset: Resets the bonus xp list
        - channel_id
            Id of the channel you want to add or remove
        - category_id
            Id of the category you want to add or remove
        - role_id
            Id of the role you want to add or remove
        - user_id
            Id of the user you want to add or remove

    Info:
        - guild_id must be specified
        - An operation must be specified either add, remove or reset
    '''
    async def manage_xp_bonus(
        guild_id:int, 
        operation:str, 
        channel_id:int = None, 
        category_id:int = None, 
        role_id:int = None, 
        user_id:int = None, 
        bonus:int = None
        ):

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



########################################  Insert into / Update the leaderboard system  ##################################################
            

    '''
    Manages the message leaderboard system

    Parameters:
    -----------
        - guild_id
            Id of the server
        - user_id
            Id of the user who has written a message
        - interval 
            Interval at which the leaderboard should be updated
                - daily: Daily update
                - weekly: Weekly update
                - monthly: Monthly update
                - channel: The channel in which the leaderboards should be sent
                - countMessage: Message value is increased 
        - settings
            Which column should be customized
                - status: Switching the system on/off
                - channel: Channel for the leaderboard
                - daily
                - weekly
                - monthly 
        - message_id 
            The message id of the leaderboard
        - channel_id
            The id of the channel to which the leaderboards are to be sent
        - back_to_none
            What should be set back to the default settings
                - daily
                - weekly
                - monthly
                - channel

    Info:
        - guild_id must be specified
        - An operation must be specified
    '''
    async def manage_leaderboard_message(
        guild_id:int, 
        user_id:int = None,
        interval:str = None,
        settings:str = None,
        message_id:int = None,
        channel_id:int = None,
        back_to_none = None
        ):
    
        column_name_settings = {
            "daily":"bourdMessageIdDay" if settings != "tracking" else "dailyCountMessage", 
            "weekly":"bourdMessageIdWeek" if settings != "tracking" else "weeklyCountMessage", 
            "monthly":"bourdMessageIdMonth" if settings != "tracking" else "monthlyCountMessage",
            "whole":"bourdMessageIdWhole" if settings != "tracking" else "wholeCountMessage",
            "channel":"leaderboardChannel",
            "status":"statusMessage"
        }

        coulmn_values = {
            "daily":message_id,
            "weekly":message_id,
            "monthly":message_id,
            "whole":message_id,
            "channel":channel_id,
            "status":0 if DatabaseCheck.check_leaderboard_settings(guild_id = guild_id, system = "message")[1] == 1 else 1
        }
        
        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        try:
            
            if settings != None and settings != "tracking":
                
                value = coulmn_values[settings]
                settings = f"UPDATE LeaderboardSettingsMessage SET {column_name_settings[settings]} = %s WHERE guildId = %s"
                settings_values = [value, guild_id]
                cursor.execute(settings, settings_values)

            elif interval:
                
                check_user = DatabaseCheck.check_leaderboard(guild_id = guild_id, user_id = user_id, system = "message")

                if check_user and interval == "countMessage":
                    
                    update_stats = f"UPDATE LeaderboardTacking SET dailyCountMessage = %s, weeklyCountMessage = %s, monthlyCountMessage = %s, wholeCountMessage = %s WHERE guildId = %s AND userId = %s"
                    update_stats_values = [check_user[2] + 1, check_user[3] + 1, check_user[4] + 1, check_user[5] + 1, guild_id, user_id]

                else:   
                    
                    update_stats = f"INSERT INTO LeaderboardTacking (guildId, userId) VALUES (%s, %s)"
                    update_stats_values = [guild_id, user_id]
                
                cursor.execute(update_stats, update_stats_values)

            elif back_to_none != None:

                set_back_to_none = f"UPDATE {'LeaderboardTacking' if settings == "tracking" else 'LeaderboardSettingsMessage'} SET {column_name_settings[back_to_none]} = DEFAULT WHERE guildId = %s"
                set_back_to_none_values = [guild_id]
                cursor.execute(set_back_to_none, set_back_to_none_values)
            
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)

    
    '''
    Manages the invite leaderboard system

    Parameters:
    -----------
        - guild_id
            Id of the server
        - user_id
            Id of the user who has invited the user
        - interval 
            Interval at which the leaderboard should be updated
                - weekly: Weekly update
                - monthly: Monthly update
                - quarterly: Quartlerly update
                - channel: The channel in which the leaderboards should be sent
                - countInvite: Invite value is increased 
        - settings
            Which column should be customized
                - status: Switching the system on/off
                - channel: Channel for the leaderboard
                - weekly
                - monthly
                - quarterly 
        - message_id 
            The message id of the leaderboard
        - channel_id
            The id of the channel to which the leaderboards are to be sent
        - back_to_none
            What should be set back to the default settings
                - weekly
                - monthly
                - quarterly
                - channel

    Info:
        - guild_id must be specified
        - An operation must be specified
    '''
    async def manage_leaderboard_invite(
        guild_id:int, 
        user_id:int = None,
        interval:str = None,
        settings:str = None,
        message_id:int = None,
        channel_id:int = None,
        back_to_none = None
        ):

        column_name_settings = {
            "weekly":"invitebourdMessageIdWeek" if settings != "tracking" else "weeklyCountInvite", 
            "monthly":"invitebourdMessageIdMonth" if settings != "tracking" else "monthlyCountInvite", 
            "quarterly":"invitebourdMessageIdQuarter" if settings != "tracking" else "quarterlyCountInvite",
            "whole":"invitebourdMessageIdWhole" if settings != "tracking" else "wholeCountInvite",
            "channel":"leaderboardChannel",
            "status":"statusInvite"
        }

        coulmn_values = {
            "weekly":message_id,
            "monthly":message_id,
            "quarterly":message_id,
            "whole":message_id,
            "channel":channel_id,
            "status":0 if DatabaseCheck.check_leaderboard_settings(guild_id = guild_id, system = "invite")[1] == 1 else 1
        }

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        try:
            
            if settings != None and settings != "tracking":
                
                value = coulmn_values[settings]
                settings = f"UPDATE LeaderboardSettingsInvite SET {column_name_settings[settings]} = %s WHERE guildId = %s"
                settings_values = [value, guild_id]
                cursor.execute(settings, settings_values)

            elif interval:
                
                check_user = DatabaseCheck.check_leaderboard(guild_id = guild_id, user_id = user_id, system = "invite")

                if check_user != None and interval == "countInvite":
                
                    update_stats = f"UPDATE LeaderboardTacking SET weeklyCountInvite = %s, monthlyCountInvite = %s, quarterlyCountInvite = %s, wholeCountInvite = %s WHERE guildId = %s AND userId = %s"
                    update_stats_values = [check_user[6] + 1, check_user[7] + 1, check_user[8] + 1, check_user[9] + 1, guild_id, user_id]

                else:   
                    
                    update_stats = f"INSERT INTO LeaderboardTacking (guildId, userId) VALUES (%s, %s)"
                    update_stats_values = [guild_id, user_id]
                
                cursor.execute(update_stats, update_stats_values)

            elif back_to_none != None:

                set_back_to_none = f"UPDATE {'LeaderboardTacking' if settings == "tracking" else 'LeaderboardSettingsInvite'} SET {column_name_settings[back_to_none]} = DEFAULT WHERE guildId = %s"
                set_back_to_none_values = [guild_id]
                cursor.execute(set_back_to_none, set_back_to_none_values)
            
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    '''
    Creates the setting entry

    Parameter:
    ----------
        - guild_id 
            Server id
        - channel
            Channel for the leaderboard system
        - system
            Which system is affected
                - message
                - invite
    
    Info:
        - guild_id must be specified
        - system must be specified
    '''
    async def create_leaderboard_settings(
        guild_id:int,
        system:str,
        channel_id:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            create_settings = f"INSERT INTO {'LeaderboardSettingsMessage' if system == 'message' else 'LeaderboardSettingsInvite'} (guildId, leaderboardChannel) VALUES (%s, %s)"
            create_settings_values = [guild_id, channel_id]

            cursor.execute(create_settings, create_settings_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    '''
    Edits the list with all invite links that exist on the respective server

    Parameters:
    ----------
        - guild_id
            Id of the server
        - user_id
            Id of the user who created the invitation
        - invite_code
            The code of the invitation
        - uses
            How often the invitation was used

    Info:
        - All variables must always be specified
    '''
    async def manage_leaderboard_invite_list(
        guild_id:int, 
        user_id:int, 
        invite_code:str, 
        uses:int
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            invite_code_check = DatabaseCheck.check_invite_codes(guild_id = guild_id, invite_code = invite_code)

            if invite_code_check:
                
                update_invites = "UPDATE LeaderboardInviteTracking SET usesCount = %s WHERE guildId = %s AND inviteCode = %s"
                update_invites_values = [uses, guild_id, invite_code]

            else:

                update_invites = "INSERT INTO LeaderboardInviteTracking (guildId, userId, inviteCode, usesCount) VALUES (%s, %s, %s, %s)"
                update_invites_values = [guild_id, user_id, invite_code, uses]

            cursor.execute(update_invites, update_invites_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)

    
    '''
    Manage the leaderboard-roles

    Parameters:
    -----------
        - guild_id
            Id of the server
        - role_id
            Id of the role to be changed
        - position
            position at which a role is to be redefined
        - status
            - 0: off 
            - 1: on
        - settings
            This value determines what is to be overwritten
            - position
            - role
            - status
            - interval
        - interval
            Which intervals should be set for the message leaderboard
            - daily
            - weekly
            - monthly
            - general

    Info:
        - guild_id must be specified
        - Status only needs to be specified if you want to overwrite an existing entry
    '''
    async def manage_leaderboard_roles(
        guild_id:int,
        role_id:int = None,
        position:int = None,
        status:str = None,
        settings:str = None,
        interval:str = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        try:

            if settings:

                if settings == "position":

                    update_roles = "UPDATE LeaderboardRoles SET rankingPosition = %s WHERE guildId = %s AND roleId = %s AND roleInterval = %s"
                    update_roles_values = [position, guild_id, role_id, interval]
                    
                elif settings == "role":
                    
                    update_roles = "UPDATE LeaderboardRoles SET roleId = %s WHERE guildId = %s AND rankingPosition = %s AND roleInterval = %s"
                    update_roles_values = [role_id, guild_id, position, interval]

                elif settings == "status":
                    
                    update_roles = "UPDATE LeaderboardRoles SET status = %s WHERE guildId = %s AND roleId = %s AND roleInterval = %s"
                    update_roles_values = [status, guild_id, role_id, interval]

                elif settings == "interval":
                    
                    update_roles = "UPDATE LeaderboardRoles SET roleInterval = %s WHERE guildId = %s AND roleId = %s"
                    update_roles_values = [interval, guild_id, role_id]

            else:

                update_roles = f"INSERT INTO LeaderboardRoles (guildId, roleId, rankingPosition, status, roleInterval) VALUES (%s, %s, %s, %s, %s)"
                update_roles_values = [guild_id, role_id, position, status, interval]

            cursor.execute(update_roles, update_roles_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)

    
    '''
    Manages all roles that are defined for a leaderboard

    Parameters:
    ----------
        - guild_id
            Server id
        - status
            For which leaderboard the setting should apply
                - message: Message Leaderboard
                - invite: Invite Leaderboard
        - operation
            what should be done
                - add: Something is added to the database
                - remove: Something is removed from the database
        - interval
            Which invterval leaderboard is affected (depends on status)
                - daily or weekly
                - weekly or monthly
                - monthly or quarterly
                - general
        - role_id
            role id
        - user_id
            Id of the user who is to receive the role
            
    Info:
    - guild_id and user_id must be specified to add a role
    - The intervals depend on which leaderboard was specified in status
    '''
    async def manage_leaderboard_roles_users(
        guild_id:int, 
        status:str, 
        operation:str, 
        interval:str,
        role_id:int = None, 
        user_id:int = None,
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()
        
        try:

            if operation == "add":
                manage_role = "INSERT INTO LeaderboardGivenRoles (guildId, roleId, userId, roleInterval, status) VALUES (%s, %s, %s, %s, %s)"
                manage_role_values = [guild_id, role_id, user_id, interval, status]

            else:

                manage_role = "DELETE FROM LeaderboardGivenRoles WHERE guildId = %s AND roleInterval = %s AND status = %s"
                manage_role_values = [guild_id, interval, status]

            cursor.execute(manage_role, manage_role_values)
            db_connect.commit()
        
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)


    '''
    Manages the auto-reaction system

    Parameters:
    ----------
        - guild_id 
            Server id
        - emoji
            Mention of the emoji
        - operation
            Which action should be performed
                - add: Adds an auto-reaction
                - remove: Removes an auto-reaction
        - channel_id
            Id of the channel in which the auto-reaction should react
        - category_id
            Id of the category in which the auto-reaction should react
        - parameter
            What the auto-reaction should react to
                - links, images and videos: Only reacts to images, videos or links
                - text messages: Only reacts to text messages
                - any message: Reacts to all messages regardless of whether they are text or links

    Info:
        - guild_id must be specified
        - An operation must be specified
        - At least one channel or category must be specified and an associated parameter
    '''
    async def manage_auto_reaction(
        guild_id:int, 
        emoji:str,
        operation:str,
        channel_id:int = None, 
        category_id:int = None, 
        parameter:str = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            if operation == "add":

                manage_reaction = f"INSERT INTO AutoReactions (guildId, {'channelId' if channel_id != None else 'categoryId'}, parameter, emoji) VALUES (%s, %s, %s, %s)"
                manage_reaction_values = [guild_id, channel_id, parameter, emoji] if channel_id != None else [guild_id, category_id, parameter, emoji]
                
            else:

                manage_reaction = f"DELETE FROM AutoReactions WHERE guildId = %s AND emoji = %s AND {'channelId' if channel_id != None else 'categoryId'}"
                manage_reaction_values = [guild_id, channel_id, parameter, emoji] if channel_id != None else [guild_id, category_id, parameter, emoji]

            cursor.execute(manage_reaction, manage_reaction_values)
            db_connect.commit()
        
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)





class DatabaseRemoveDatas():

###########################################################  Removes values from the level system  #######################################


    '''
    Deletes either the stats of a specific user or those of all users, depending on whether a user is specified

    Info:
        - guild_id must be specified
        - If no user_id is specified, all entries belonging to the server are deleted
    '''
    async def remove_level_system_stats(guild_id:int, user_id:int = None):

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


    '''
    Deletes level roles

    Parameters:
    -----------
        - guild_id
            Id of the server
        - role_id
            Id of the role to be deleted as level role
        - role_level
            Level of a role that is to be deleted as a level role

    Info:
        - guild_id must be specified
        - If no role_id or role_level is specified, all roles are removed as level roles
    '''
    async def remove_level_system_level_roles(guild_id:int, role_id:int = None, role_level:int = None):

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



###########################################  Remove values from the message leaderboard system  #########################################


    '''
    Resets the message leaderboard settings

    Parameters:
    -----------
        - guild_id
            Id of the server
        - system
            Which system is affected
                - message
                - invite

    Info:
        - guild_id must be specified
    '''
    async def remove_leaderboard_settings(guild_id:int, system:str):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            delete_message_id = f"DELETE FROM {'LeaderboardSettingsMessage' if system == 'message' else 'LeaderboardSettingsInvite'} WHERE guildId = %s"
            delete_message_id_values = [guild_id]
            cursor.execute(delete_message_id, delete_message_id_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)


    '''
    Removes individual roles or resets all of them

    Parameters:
    -----------
        - guild_id
            Id of the server
        - system
            Welches system betroffen ist
                - message
                - invite
        - role_id
            Id of the role to be removed
        - poistion
            From which position the role is to be removed
        - interval
            From which interval the role is to be removed

    Info:
        - guild_id must be specified
        - An `interval` must always be specified
        - Position can only be 0 - 15
        - If only `guild_id` is specified, all roles are removed from the leaderboard
    '''
    async def remove_leaderboard_role(
        guild_id:int, 
        system:str,
        role_id:int = None, 
        position:int = None, 
        interval:str = None
        ):
        
        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:
            
            if any(x != None for x in [role_id, position, interval]):

                delete_leaderboard_role = f"DELETE FROM LeaderboardRoles WHERE guildId = %s AND status = %s AND {'roleId = %s' if position == None else 'rankingPosition = %s'} AND roleInterval = %s"
                delete_leaderboard_role_values = [guild_id, system, role_id if position == None else position, interval]

            else:

                delete_leaderboard_role = "DELETE FROM LeaderboardRoles WHERE guildId = %s AND status = %s"
                delete_leaderboard_role_values = [guild_id, system]

            cursor.execute(delete_leaderboard_role, delete_leaderboard_role_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
        
        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)


    '''
    Removes specific invitation codes from the database

    Parameters:
    ----------
        - guild_id 
            Server id
        - invite_code
            Code of the invitation to be removed
        - user_id
            Id of the user who created the invitation

    Info:
        - guild_id must be specified
        - An invitation code must always be specified
    '''
    async def remove_invite_links(
        guild_id:int,
        invite_code:str,
        user_id:int = None
        ):
        
        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            if user_id:

                delete_invite_link = "DELETE FROM LeaderboardInviteTracking WHERE guildId = %s AND inviteCode = %s AND userId = %s"
                delete_invite_link_values = [guild_id, invite_code, user_id]

            else:

                delete_invite_link = "DELETE FROM LeaderboardInviteTracking WHERE guildId = %s AND inviteCode = %s"
                delete_invite_link_values = [guild_id, invite_code]

            cursor.execute(delete_invite_link, delete_invite_link_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
        
        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)



###########################################  Remove values from the auto-reaction system  #########################################


    '''
    Removes certain auto-reactions or resets them all equally

    Parameters:
    ----------
        - guild_id 
            Server id
        - channel_id
            Id of the channel to be removed
        - category_id
            Id of the category to be removed

    Info:
        - guild_id must be specified
        - If no channel and no category are specified, all auto-reactions of a server are reset
    '''
    async def remove_auto_reactions(
        guild_id:int,
        channel_id:int = None,
        category_id:int = None
        ):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        try:

            if channel_id != None or category_id != None:

                delete_auto_reaction = f"DELETE FROM AutoReactions WHERE guildId = %s AND {'channelId' if channel_id != None else 'categoryId'} = %s"
                delete_auto_reaction_values = [guild_id, channel_id if channel_id != None else category_id]
            
            else:

                delete_auto_reaction = "DELETE FROM AutoReactions WHERE guildId = %s"
                delete_auto_reaction_values = [guild_id]

            cursor.execute(delete_auto_reaction, delete_auto_reaction_values)
            db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
        
        finally:

            DatabaseSetup.db_close(db_connection=db_connect, cursor=cursor)