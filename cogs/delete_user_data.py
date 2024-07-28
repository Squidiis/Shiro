import mysql.connector
from discord.ext import commands
import discord
from sql_function import DatabaseCheck, DatabaseRemoveDatas, DatabaseSetup




class DeleteData(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



#########################################  Deletes data when a user or the bot itself leaves the server   ############################################


    '''
    
    '''
    def delete_data(table:str, column:str, item):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        delete_datas = f"DELETE FROM {table} WHERE guildId = %s AND {column} = %s" if column != 'guildId' else f'DELETE FROM {table} WHERE guildId = %s'
        delete_datas_values = [item.guild.id, item.id] if column != 'guildId' else [item.id]
        cursor.execute(delete_datas, delete_datas_values)
        db_connect.commit() 


    # Deletes all data when the bot is kicked from the server 
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        tables = [
            "LevelSystemStats", 
            "LevelSystemBlacklist", 
            "LevelSystemRoles", 
            "LevelSystemSettings",
            "BonusXpList",
            "AntiLinkWhiteList",
            "LeaderboardSettings",
            "LeaderboardTacking",
            "BotSettings"
            ]

        for table in tables:

            DeleteData.delete_data(table=table, column='guildId', item=guild)


    # Deletes all data when the user leaves the server 
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):

        if not member.bot:

            tables = [
                "LevelSystemBlacklist", 
                "LevelSystemStats",
                "BonusXpList",
                "AntiLinkWhiteList",
                "LeaderboardTacking"
                ]
            
            for table in tables:

                DeleteData.delete_data(table=table, column='userId', item=member)   


    # Deletes the entries of a channel when it is deleted
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        tables = [
            "LevelSystemBlacklist", 
            "AntiLinkWhiteList", 
            "LevelSystemSettings", 
            "BonusXpList",
            "AntiLinkWhiteList"
            ]
        
        for table in tables:
            
            column = "channelId" if table != "LevelSystemSettings" else "levelUpChannel"
            DeleteData.delete_data(table=table, column=column, item=channel)


    # Deletes the entries of a role when it is deleted
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):

        tables = ['LevelSystemBlacklist',
                  'BonusXpList',
                  "AntiLinkWhiteList",
                  'LevelSystemRoles']
        
        for table in tables:

            DeleteData.delete_data(table=table, column='roleId', item=role)

    
def setup(bot):
    bot.add_cog(DeleteData(bot))