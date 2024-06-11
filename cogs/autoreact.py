from utils import *

class AutoReaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        if message.guild:
            if message.guild.id == 865899808183287848:
                categorys = [996846958536835203, 927683692695027772, 998934946708205598, 930157270275350598, 
                             897544467266011177, 873622071484252200, 927668688239353926, 1084219817269149747,
                             927683692695027772, 996846958536835203, 1145775400983744522]
                
                booster_category = [1237029100430950499]
                if message.channel.category_id in categorys:
                    if len(message.attachments) > 0 or message.content.startswith("https://"):
                        await message.add_reaction("❤")
                
                if message.channel.category_id in booster_category:
                    if len(message.attachments) > 0 or message.content.startswith("https://"):
                        await message.add_reaction("💎")

        else:
            return
        

def setup(bot):
    bot.add_cog(AutoReaction(bot))
    