
from Import_file import *

from cogs.level_system import *
from cogs.Moderator_tolls import *
from dotenv import load_dotenv


@bot.slash_command(description="Shows you the ping.")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is ``{round(bot.latency*1000)}`` ms")



class main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        view = View(timeout=None)
        print(f'Logged in as: {bot.user.name}')
        print(f'With ID: {bot.user.id}')
        self.bot.loop.create_task(status_task())
        
        print("┏━━━┓ ┏━━━┓ ┏┓ ┏┓ ┏━━┓ ┏━━━┓ ┏━━┓")
        print("┃┏━┓┃ ┃┏━┓┃ ┃┃ ┃┃ ┗┫┣┛ ┗┓┏┓┃ ┗┫┣┛")
        print("┃┗━━┓ ┃┃ ┃┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃")
        print("┗━━┓┃ ┃┗━┛┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃")
        print("┃┗━┛┃ ┗━━┓┃ ┃┗━┛┃ ┏┫┣┓ ┏┛┗┛┃ ┏┫┣┓")
        print("┗━━━┛    ┗┛ ┗━━━┛ ┗━━┛ ┗━━━┛ ┗━━┛")

        # level system
        self.bot.add_view(LevelUpChannelButtons(channel=None))
        self.bot.add_view(LevelRolesButtons(role_id=None, role_level=None, status=None))
        self.bot.add_view(ResetLevelStatsButton())
        self.bot.add_view(LevelSystemSettings())
        self.bot.add_view(ResetBlacklistLevelButton())

        # level system blacklist manager
        self.bot.add_view(BlacklistManagerButtons())
        self.bot.add_view(BlacklistManagerSelectAdd())
        self.bot.add_view(BlacklistManagerSelectRemove())
        view.add_item(TempBlackklistLevelSaveButton())
        view.add_item(ShowBlacklistLevelSystemButton())
        
        # Applycation
        self.bot.add_view(ApplicationButton())

        self.bot.add_view(GhostPingButtons())

        self.bot.add_view(view)
        

async def status_task():
    while True:
        await bot.change_presence(activity=discord.Game('?help to see all commands'), status=discord.Status.online)
        await asyncio.sleep(15)
        await bot.change_presence(activity=discord.Game('Funpark.net'), status=discord.Status.online)
        await asyncio.sleep(15)


bot.add_cog(main(bot))


class ApplicationButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Choose what you want to apply as", min_values=1, max_values=1, custom_id="interaction:aplication", options = [

        discord.SelectOption(label="Moderator", description="Click here to apply as a moderator", value="moderator"),
        discord.SelectOption(label="Developer", description="Click here to apply as a developer", value="developer"),
        discord.SelectOption(label="Hentai Konzern", description="Click here to apply as a Hentai Group member", value="hentai_konzern"),
        discord.SelectOption(label="Artist", description="Click here to apply as an artist", value="artist"),
        discord.SelectOption(label="Assistant", description="Click here to apply as an assistant", value="sssistant"),
    ])

    async def callback(self, select, interaction: discord.Interaction): 

        overwrites = {
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        }
        channels = await interaction.guild.create_text_channel(name="waiting room", overwrites=overwrites)

        emb = discord.Embed(title=f"Wait here for a moment, an admin will contact you in a moment", 
            description=f"An admin will get right back to you on this channel!", color=0x09ebdf)
        emb.add_field(name=f"Infos {Emojis.help_emoji}", 
            value=f"{Emojis.dot_emoji} user: {interaction.user.mention}\n{Emojis.dot_emoji} Id: {interaction.user.id}\n{Emojis.dot_emoji} Advertising as: {select.values[0]}")
        emb.set_footer(icon_url=interaction.user.avatar.url, text=f"Applicant: {interaction.user.name}")
        await channels.send(embed=emb)



@bot.command()
async def application(ctx):

    emb = discord.Embed(title="Hello Members,", description="""
    Cause of the rising of our members we decided to seek for more staff members.

    We offer: 

    > ```Moderator,```
    > here you have to watch a few channels like Global chat and look if everyone follows the rules. If not, then please respond in a comprehensible way. You also should look for other things like spam or if someone writes in one of the hanime channels then please delete the message. 

    > ```Developers,```
    > you are able to help programming and testing our bots. We prefer Python but we also take Java, HTML CSS, Java script. Some things you are able to do is creating and developing future Minigames.

    > ```Hentai Konzern,```
    > Here your Task is to refill the hentai Channels with a minimum of 5 channels and 10 pictures. Its ok if you fill them up every 2 or 3 days. There are also some rules witch type of pictures are not allowed. These Types are: Loli, Gore and other things that contain children or other disturbing stuff.

    > ```Artist,```
    > As an artist your job is it to create banners, mascots and other stuff. Another thing you are able to do is helping to design and create mascots and to create assets for future Minigames. 

    > ```Assistant,```
    > As an Assistant you have to help the owners with a few tasks like organising events and other stuff we might need help with. Another task is to help setting up streams, for example an Hanime stream or gaming stream. 

    *Other things you should know about:*

    > You must be nice to the members and other staff members or there will be consiquencies.
    > If you should´t be available for a few day then please let us know. 
    > In case you are noticed in a negative way to often you will be dismissed.

    So, want to join our Team?
    **Then please contact one of the owners!**
    **Or press the button**
    <@&865907711832227840>
    """, color=0x09ebdf)
    await ctx.send(embed=emb, view=ApplicationButton())

class AutoReaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild:
            if message.guild.id == 865899808183287848:
                categorys = [996846958536835203, 927683692695027772, 998934946708205598, 930157270275350598, 897544467266011177, 873622071484252200, 927668688239353926]
                if message.channel.category_id in categorys:
                    if len(message.attachments) > 0 or message.content.startswith("https://"):
                        await message.add_reaction("❤")
        else:
            return
        
bot.add_cog(AutoReaction(bot)) 
    

if __name__ == "__main__":
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

    load_dotenv()
    bot.run(os.getenv("TOKEN"))

