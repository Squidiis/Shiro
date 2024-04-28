
from cogs.level_system import *
from cogs.mod_tools import *
from dotenv import load_dotenv
from cogs.fun_commands import *
from utils import *



@bot.slash_command(description="Shows you the ping.")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is ``{round(bot.latency*1000)}`` ms")



class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Creates all the necessary tables that the bot needs right at the beginning
    async def create_db_table():

        db_connect = DatabaseSetup.db_connector()
        cursor = db_connect.cursor()

        tables = [
            # Level system Tables
            '''
            CREATE TABLE IF NOT EXISTS `LevelSystemStats` (
                guildId BIGINT UNSIGNED NOT NULL, 
                userId BIGINT UNSIGNED NOT NULL,
                userLevel BIGINT UNSIGNED NOT NULL,
                userXp BIGINT UNSIGNED NOT NULL,
                userName VARCHAR(255) NOT NULL,
                voiceTime TIMESTAMP(6) NULL,
                wholeXp BIGINT UNSIGNED NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LevelSystemBlacklist (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                roleId BIGINT UNSIGNED NULL,
                userId BIGINT UNSIGNED NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LevelSystemRoles (
                guildId BIGINT UNSIGNED NOT NULL,
                roleId BIGINT UNSIGNED NOT NULL,
                roleLevel INT UNSIGNED NOT NULL,
                guildName VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LevelSystemSettings (
                guildId BIGINT UNSIGNED NOT NULL,
                xpRate INT UNSIGNED DEFAULT 20,
                levelStatus VARCHAR(50) DEFAULT 'on',
                levelUpChannel BIGINT UNSIGNED NULL,
                levelUpMessage VARCHAR(500) DEFAULT 'Oh nice {user} you have a new level, your newlevel is {level}',
                bonusXpPercentage INT UNSIGNED DEFAULT 10
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE IF NOT EXISTS BonusXpList (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                roleId BIGINT UNSIGNED NULL,
                userId BIGINT UNSIGNED NULL,
                PercentBonusXp INT UNSIGNED DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            '''
            CREATE TABLE If NOT EXISTS AntiLinkWhiteList (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                roleId BIGINT UNSIGNED NULL,
                userId BIGINT UNSIGNED NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            ''',
            # Bot settings Table
            '''
            CREATE TABLE IF NOT EXISTS BotSettings (
                guildId BIGINT UNSIGNED NOT NULL,
                botColour VARCHAR(20) NULL,
                ghostPing BIT DEFAULT 0,
                antiLink BIT(4) DEFAULT 3,
                antiLinkTimeout INT DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            '''
        ]  

        try:

            for table in tables:
                cursor.execute(table)
                db_connect.commit()
        
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))


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
        self.bot.add_view(LevelRolesButtons(role_id=None, role_level=None, status=None))
        self.bot.add_view(ResetLevelStatsButton())
        self.bot.add_view(ResetBlacklistLevelButton())

        # Level system settings
        self.bot.add_view(LevelSystemSetting())
        self.bot.add_view(SetLevelUpChannelSelect())
        self.bot.add_view(BonusXpPercentage())
        self.bot.add_view(SetXpRate())
        self.bot.add_view(LevelSystemDefault())
        self.bot.add_view(ShowLevelSettingsSelect())
        view.add_item(LevelUpMessageButton())
        view.add_item(SetLevelUpChannelButton())
        view.add_item(LevelSystemOnOffSwitch())
        view.add_item(SetBonusXpPercentageButton())
        view.add_item(CancelSetLevelSystem())
        view.add_item(SendXpBonusModal())
        view.add_item(ShowLevelSettings())

        self.bot.add_view(HelpMenüSelect())

        self.bot.add_view(ApplicationButton())

        # Mod tools
        self.bot.add_view(GhostPingButtons())

        # Other Systems
        self.bot.add_view(GhostPingButtons())
        self.bot.add_view(RPSButtons(game_mode=None, second_user=None, first_user=None))

        self.bot.add_view(view)

        await Main.create_db_table()


# Status task while the bot is active, the status is permanently updated
async def status_task():
    while True:
        await bot.change_presence(activity=discord.Game('/help to see all commands'), status=discord.Status.online)
        await asyncio.sleep(15)
        await bot.change_presence(activity=discord.Game('Developed by Squidi'), status=discord.Status.online)
        await asyncio.sleep(15)

bot.add_cog(Main(bot))


class ApplicationButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Choose what you want to apply as", min_values=1, max_values=1, custom_id="interaction:aplication", options = [
        discord.SelectOption(label="Moderator", description="Click here to apply as a moderator", value="moderator"),
        discord.SelectOption(label="Developer", description="Click here to apply as a developer", value="developer"),
        discord.SelectOption(label="Hentai Konzern", description="Click here to apply as a Hentai Group member", value="hentai_konzern"),
        discord.SelectOption(label="Artist", description="Click here to apply as an artist", value="artist"),
        discord.SelectOption(label="Assistant", description="Click here to apply as an assistant", value="assistant"),
    ])

    async def callback(self, select, interaction: discord.Interaction): 

        overwrites = {
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        }
        channels = await interaction.guild.create_text_channel(name="waiting room", overwrites=overwrites)

        emb_respond = discord.Embed(description=f"""## Your application has been successfully delivered
            A channel has been created for you in which an admin will contact you
            Your application waiting room: {channels.mention}""", color=bot_colour)
        await interaction.response.send_message(embed=emb_respond, ephemeral=True, view=None)

        emb = discord.Embed(title=f"Wait here for a moment, an admin will contact you", 
            description=f"An admin will get right back to you on this channel!", color=bot_colour)
        emb.add_field(name=f"Infos {Emojis.help_emoji}", 
            value=f"{Emojis.dot_emoji} user: {interaction.user.mention}\n{Emojis.dot_emoji} Id: {interaction.user.id}\n{Emojis.dot_emoji} Applies as: {select.values[0]}")
        emb.set_footer(icon_url=interaction.user.avatar.url, text=f"Applicant: {interaction.user.name}")
        await channels.send(embed=emb)


@bot.command()
async def application(ctx):

    emb = discord.Embed(description=f"""# Application
        Hello Members,
        Cause of the rising of our members we decided to seek for more staff members.

        We offer:

        ```Moderator,```
        > here you have to watch a few channels like Global chat and look if everyone follows the rules. If not, then please respond in a comprehensible way. You also should look for other things like spam or if someone writes in one of the hanime channels then please delete the message.
        
        ```Developers,```
        > you are able to help programming and testing our bots. We prefer Python but we also take Java, HTML CSS, Java script. Some things you are able to do is creating and developing future Minigames.
        
        ```Hentai Konzern,```
        > Here your Task is to refill the hentai Channels with a minimum of 5 channels and 10 pictures. Its ok if you fill them up every 2 or 3 days. There are also some rules witch type of pictures are not allowed. These Types are: Loli, Gore and other things that contain children or other disturbing stuff.
        
        ```Artist,```
        > As an artist your job is it to create banners, mascots and other stuff. Another thing you are able to do is helping to design and create mascots and to create assets for future Minigames.
        
        ```Assistant,```
        > As an Assistant you have to help the owners with a few tasks like organising events and other stuff we might need help with. Another task is to help setting up streams, for example an Hanime stream or gaming stream.
        
        **Other things you should know about:**

        > You must be nice to the members and other staff members or there will be consiquencies.
        > If you should´t be available for a few day then please let us know.
        > In case you are noticed in a negative way to often you will be dismissed.

        **So, want to join our Team?**
        Then please contact one of the owners!
        Or press the button below""", color=bot_colour)
    await ctx.send(embed=emb, view=ApplicationButton())


class AntiSpam(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.anti_spam = commands.CooldownMapping.from_cooldown(5, 15, commands.BucketType.member)
        self.too_many_violations = commands.CooldownMapping.from_cooldown(4, 60, commands.BucketType.member)

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        if type(message.channel) is not discord.TextChannel or message.author.bot: 
            return
        
        bucket = self.anti_spam.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        
        if retry_after:

            await message.delete()
            await message.channel.send(f"{message.author.mention}, don't spam!", delete_after = 10)

            violations = self.too_many_violations.get_bucket(message)
            check = violations.update_rate_limit()

            if check:

                await message.author.timeout(timedelta(minutes=10))

                try: 

                    await message.author.send("You have been muted for spamming!")

                except:

                    return
                
bot.add_cog(AntiSpam(bot))


class AutoReaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        if message.guild:
            if message.guild.id == 865899808183287848:
                categorys = [996846958536835203, 927683692695027772, 998934946708205598, 930157270275350598, 897544467266011177, 873622071484252200, 927668688239353926, 1084219817269149747]
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

