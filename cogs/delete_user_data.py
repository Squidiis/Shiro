import mysql.connector
from discord.ext import commands
import discord
from sql_function import DatabaseCheck, DatabaseRemoveDatas


class UserLeavesServer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


#########################################  Deletes data when a user or the bot itself leaves the server   ############################################


    # Deletes all data when the bot is kicked from the server 
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        guild_id = guild.id

        # Level System checks
        level_system_blacklist = DatabaseCheck.check_level_system_blacklist(guild=guild_id)
        level_system_stats = DatabaseCheck.check_level_system_stats(guild=guild_id)
        level_system_control = DatabaseCheck.check_bot_settings(guild=guild_id)
        level_system_levelroles = DatabaseCheck.check_level_system_levelroles(guild=guild_id)

        try:

            # Delete all values from the Level System!
            if level_system_blacklist:
                DatabaseRemoveDatas._remove_level_system_blacklist(guild=guild_id)

            if level_system_stats:
                DatabaseRemoveDatas._remove_level_system_stats(guild=guild_id)

            if level_system_control:
                DatabaseRemoveDatas._remove_bot_settings(guild=guild_id)

            if level_system_levelroles:
                DatabaseRemoveDatas._remove_level_system_level_roles(guild=guild_id)

        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))

        finally:

            return True
        

    # Deletes all data when the user leaves the server 
    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):

        if not member.bot:

            guild_id = member.guild.id

            # Searches everything for the user 
            check_level_blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, user=member.id)
            check_level_stats = DatabaseCheck.check_level_system_stats(guild=guild_id, user=member.id)
            check_economy_blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, user=member.id)
            check_economy_stats = DatabaseCheck.check_economy_system_stats(guild=guild_id, user=member.id)

            try:

                # Deletes all data from the user
                if check_level_blacklist:
                    DatabaseRemoveDatas._remove_level_system_blacklist(guild_id=member.guild.id, user_id=member.id)
                
                if check_level_stats:
                    DatabaseRemoveDatas._remove_level_system_stats(guild_id=member.guild.id, user_id=member.id)

                if check_economy_blacklist:
                    DatabaseRemoveDatas._remove_economy_system_blacklist(guild_id=member.guild.id, user_id=member.id)

                if check_economy_stats:
                    DatabaseRemoveDatas._remove_economy_system_stats(guild_id=member.guild.id, user_id=member.id)

            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))

            finally:

                return True
            

def setup(bot):
    bot.add_cog(UserLeavesServer(bot))