from utils import *
from sql_function import *
from discord.ext import tasks

class InviteTrackerSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name = "set-invite-leaderboard", description = "Stelle das invite leaderboard system ein!")
    async def set_invite_leaderboard(self, ctx:discord.ApplicationContext):

        settings = DatabaseCheck.check_leaderboard_settings_message(guild_id = ctx.guild_id)

        emb = discord.Embed(description=f"""## Set the message leaderboard
            {Emojis.dot_emoji} With the lower select menu you can define a channel in which the leaderboard should be sent
            {Emojis.dot_emoji} Then you can also set an interval at which time intervals the leaderboard should be updated
            {Emojis.dot_emoji} You can also switch the system off or on currently it is {'switched off' if settings[0] else 'switched on'}. (as soon as it is switched off, no more messages are counted and when it is switched on, the leaderboard is reset)
            {Emojis.help_emoji} The leaderboard is edited when you update it, so you should make sure that no one else can write in the channel you specified
            {Emojis.help_emoji} **The leaderboard always shows the data from the previous interval, e.g. the best users who have invited the most users in the last week**""", color=bot_colour)        
        await ctx.respond(embed=emb)

def setup(bot):
    bot.add_cog(InviteTrackerSystem(bot))


