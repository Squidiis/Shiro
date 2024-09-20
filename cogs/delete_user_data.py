from discord.ext import commands
import discord
from sql_function import DatabaseCheck, DatabaseRemoveDatas, DatabaseSetup
import aiomysql




class DeleteData(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



#########################################  Deletes data when a user or the bot itself leaves the server   ############################################


    '''
    Deletes the database entries when a role or channel is deleted or a user leaves the server

    Parameters:
    ------------
        - table
            From which table the data should be deleted
        - column
            Which column to start from
        - itme
            What is to be deleted (id)

    Info:
        - If the bot itself is kicked from the server, all entries are deleted
    '''
    async def delete_data(table:str, column:str, item):

        db_connect = await DatabaseSetup.db_connector()
        cursor = await db_connect.cursor()

        try:

            delete_datas = f"DELETE FROM {table} WHERE guildId = %s AND {column} = %s" if column != 'guildId' else f'DELETE FROM {table} WHERE guildId = %s'
            delete_datas_values = [item.guild.id, item.id] if column != 'guildId' else [item.id]
            await cursor.execute(delete_datas, delete_datas_values)
            await db_connect.commit() 

        except aiomysql.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            await DatabaseSetup.db_close(cursor=cursor, db_connection=db_connect)



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
            "LeaderboardTacking",
            "BotSettings",
            "LeaderboardSettingsMessage",
            "LeaderboardSettingsInvite",
            "LeaderboardRoles",
            "LeaderboardGivenRoles",
            "LeaderboardInviteTracking"
            ]

        for table in tables:

            await DeleteData.delete_data(table=table, column='guildId', item=guild)


    # Deletes all data when the user leaves the server 
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):

        if not member.bot:

            tables = [
                "LevelSystemBlacklist", 
                "LevelSystemStats",
                "BonusXpList",
                "AntiLinkWhiteList",
                "LeaderboardTacking",
                "LeaderboardInviteTracking",
                "LeaderboardGivenRoles",
                "LeaderboardTacking"
                ]
                
            for table in tables:

                await DeleteData.delete_data(table=table, column='userId', item=member)

        else:

            return


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
            await DeleteData.delete_data(table=table, column=column, item=channel)


    # Deletes the entries of a role when it is deleted
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):

        tables = [
                "LevelSystemBlacklist",
                "BonusXpList",
                "AntiLinkWhiteList",
                "LevelSystemRoles",
                "LeaderboardRoles",
                "LeaderboardGivenRoles"
                ]
        
        for table in tables:

            await DeleteData.delete_data(table=table, column='roleId', item=role)

    
def setup(bot):
    bot.add_cog(DeleteData(bot))