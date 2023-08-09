import mysql.connector
from discord.ext import commands
import discord
from sql_function import DatabaseCheck, DatabaseRemoveDatas, DatabaseSetup


class UserLeavesServer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


#########################################  Deletes data when a user or the bot itself leaves the server   ############################################


    # Deletes all data when the bot is kicked from the server 
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        tables = ["LevelSystemStats", 
                  "LevelSystemBlacklist", 
                  "LevelSystemRoles", 
                  "LevelSystemSettings",  
                  "BotSettings", 
                  "AutoReactionSetup", 
                  "AutoReactionSettings", 
                  "EconomySystemStats", 
                  "EconomySystemBlacklist", 
                  "EconomySystemShop",
                  "EconomySystemSettings"]

        try:

            for table in tables:

                delete_datas = f"DELETE FROM {table} WHERE guildId = %s"
                delete_datas_values = [guild.id]

                cursor.execute(delete_datas, delete_datas_values)
                db_connect.commit()

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            return True
        

    # Deletes all data when the user leaves the server 
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):

        if not member.bot:

            db_connect = DatabaseSetup.db_connector()
            cursor = db_connect.cursor()

            tables = ["EconomySystemBlacklist", 
                      "EconomySystemStats", 
                      "LevelSystemBlacklist", 
                      "LevelSystemStats"]
            
            try:

                for table in tables:

                    delete_user_datas = f"DELETE {table} WHERE guildId = %s AND userId = %s"
                    delete_user_datas_values = [member.guild.id, member.id]
                    cursor.execute(delete_user_datas, delete_user_datas_values)
                    db_connect.commit()
            
            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:

                return True


class DeleteData(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def delete_data(self, table:str, column:str, item:str):

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        delete_datas = f"DELETE {table} WHERE guildId = %s AND {column} = %s"
        delete_datas_values = [table, item.guild.id, item.id]
        cursor.execute(delete_datas, delete_datas_values)
        db_connect.commit()


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        tables = ["LevelSystemBlacklist", "ManageBlacklistTemp", "AutoReactionSetup", "LevelSystemSettings", "EconomySystemBlacklist", "EconomySystemSettings"]
        for table in tables:

            DeleteData.delete_data(table=table, column="channelId", item=channel)

    
    
        


def setup(bot):
    bot.add_cog(DeleteData(bot))
    bot.add_cog(UserLeavesServer(bot))