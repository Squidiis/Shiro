
from dotenv import load_dotenv
from utils import *
import logging
import importlib
from sql_function import DatabaseUpdates, DatabaseSetup


for filename in os.listdir("cogs"):

    if filename.endswith(".py") and filename != "__init__.py":
        cog_name = f"cogs.{filename[:-3]}"

        try:
            importlib.import_module(cog_name)

        except Exception as e:
            print(f"Error when loading: {cog_name}: {e}")


logging.basicConfig(level=logging.INFO)


class Main(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # Creates all important tables for the bot 
    async def create_db_table():

        db_connect = await DatabaseSetup.db_connector()
        cursor = await db_connect.cursor()

        tables = [
            # Level system tables
            '''
            CREATE TABLE IF NOT EXISTS `LevelSystemStats` (
                guildId BIGINT UNSIGNED NOT NULL, 
                userId BIGINT UNSIGNED NOT NULL,
                userLevel BIGINT UNSIGNED NOT NULL,
                userXp BIGINT UNSIGNED NOT NULL,
                userName VARCHAR(255) NOT NULL,
                voiceTime TIMESTAMP(6) NULL,
                wholeXp BIGINT UNSIGNED NOT NULL
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LevelSystemBlacklist (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                roleId BIGINT UNSIGNED NULL,
                userId BIGINT UNSIGNED NULL
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LevelSystemRoles (
                guildId BIGINT UNSIGNED NOT NULL,
                roleId BIGINT UNSIGNED NOT NULL,
                roleLevel INT UNSIGNED NOT NULL
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LevelSystemSettings (
                guildId BIGINT UNSIGNED NOT NULL,
                xpRate INT UNSIGNED DEFAULT 20,
                levelStatus INT DEFAULT 0,
                levelUpChannel BIGINT UNSIGNED NULL,
                levelUpMessage VARCHAR(1000) DEFAULT 'Oh nice {user} you have a new level, your newlevel is {level}',
                bonusXpPercentage INT UNSIGNED DEFAULT 10
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS BonusXpList (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                roleId BIGINT UNSIGNED NULL,
                userId BIGINT UNSIGNED NULL,
                PercentBonusXp INT UNSIGNED DEFAULT 0
            );
            ''',
            # Anti-link system table
            '''
            CREATE TABLE If NOT EXISTS AntiLinkWhiteList (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                roleId BIGINT UNSIGNED NULL,
                userId BIGINT UNSIGNED NULL
            );
            ''',
            # Bot settings table
            '''
            CREATE TABLE IF NOT EXISTS BotSettings (
                guildId BIGINT UNSIGNED NOT NULL,
                botColour VARCHAR(20) NULL,
                ghostPing INT DEFAULT 0,
                antiLink INT DEFAULT 3,
                antiLinkTimeout INT DEFAULT 0,
                autoReaction INT DEFAULT 0
            );
            ''',
            # Leaderboard tables
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardSettingsMessage (
                guildId BIGINT UNSIGNED NOT NULL,
                statusMessage INT UNSIGNED NOT NULL DEFAULT 0,
                bourdMessageIdDay BIGINT UNSIGNED NULL,
                bourdMessageIdWeek BIGINT UNSIGNED NULL,
                bourdMessageIdMonth BIGINT UNSIGNED NULL,
                bourdMessageIdWhole BIGINT UNSIGNED NULL,
                leaderboardChannel BIGINT UNSIGNED NULL
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardTacking (
                guildId BIGINT UNSIGNED NOT NULL,
                userId BIGINT UNSIGNED NOT NULL,
                dailyCountMessage INT UNSIGNED DEFAULT 0,
                weeklyCountMessage INT UNSIGNED DEFAULT 0,
                monthlyCountMessage INT UNSIGNED DEFAULT 0,
                wholeCountMessage INT UNSIGNED DEFAULT 0,
                weeklyCountInvite INT UNSIGNED DEFAULT 0,
                monthlyCountInvite INT UNSIGNED DEFAULT 0,
                quarterlyCountInvite INT UNSIGNED DEFAULT 0,
                wholeCountInvite INT UNSIGNED DEFAULT 0
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardRoles (
                guildId BIGINT UNSIGNED NOT NULL,
                roleId BIGINT UNSIGNED NOT NULL,
                rankingPosition INT UNSIGNED NOT NULL,
                status VARCHAR(20) NOT NULL,
                roleInterval VARCHAR(10) NOT NUll
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardGivenRoles (
                guildId BIGINT UNSIGNED NOT NULL,
                roleId BIGINT UNSIGNED NOT NULL,
                userId BIGINT UNSIGNED NOT NULL,
                roleInterval VARCHAR(10) NOT NULL,
                status VARCHAR(20) NOT NULL,
                rankingPosition INT UNSIGNED NOT NULL
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardSettingsInvite (
                guildId BIGINT UNSIGNED NOT NULL,
                statusInvite INT UNSIGNED NOT NULL DEFAULT 0,
                invitebourdMessageIdWeek BIGINT UNSIGNED NULL,
                invitebourdMessageIdMonth BIGINT UNSIGNED NULL,
                invitebourdMessageIdQuarter BIGINT UNSIGNED NULL,
                invitebourdMessageIdWhole BIGINT UNSIGNED NULL,
                leaderboardChannel BIGINT UNSIGNED NULL
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS LeaderboardInviteTracking (
                guildId BIGINT UNSIGNED NOT NULL,
                userId BIGINT UNSIGNED NOT NULL,
                inviteCode VARCHAR(20) NOT NULL,
                usesCount INT NOT NULL,
                UNIQUE KEY unique_invite (guildId, inviteCode)
            );
            ''',
            # Auto reaction table
            '''
            CREATE TABLE IF NOT EXISTS AutoReactions (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NULL,
                categoryId BIGINT UNSIGNED NULL,
                parameter VARCHAR(255) NOT NULL,
                emoji VARCHAR(255) NOT NULL
            );
            ''',
            # Booster system
            '''
            CREATE TABLE IF NOT EXISTS BoosterSystem (
                guildId BIGINT UNSIGNED NOT NULL,
                status INT UNSIGNED DEFAULT 1,
                channelId BIGINT UNSIGNED NULL,
                message VARCHAR(4000) DEFAULT 'Thank you, [user], for boosting the server! Your support helps make this community even better. We appreciate you!'
            );
            ''',
            # Sticky message
            '''
            CREATE TABLE IF NOT EXISTS StickyMessage (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NOT NULL,
                messageId BIGINT UNSIGNED NULL,
                message VARCHAR(3000) NULL,
                status INT DEFAULT 1
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS StickyMessageSettings (
                guildId BIGINT UNSIGNED NOT NULL,
                status INT UNSIGNED DEFAULT 1
            );
            ''',
            # Auto message
            '''
            CREATE TABLE IF NOT EXISTS AutoMessage (
                guildId BIGINT UNSIGNED NOT NULL,
                channelId BIGINT UNSIGNED NOT NULL,
                messageId BIGINT UNSIGNED NULL,
                message VARCHAR(3000) NULL,
                status INT DEFAULT 1,
                sendInterval INT NOT NULL,
                messageSendTime TIMESTAMP NULL
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS AutoMessageSettings (
                guildId BIGINT UNSIGNED NOT NULL,
                status INT UNSIGNED DEFAULT 1
            );
            ''',
            # Ticket system
            '''
            CREATE TABLE IF NOT EXISTS TicketSystemSettings (
                guildId BIGINT UNSIGNED NOT NULL,
                status INT UNSIGNED DEFAULT 1,
                ticketChannelId BIGINT UNSIGNED NULL,
                ticketMessageId BIGINT UNSIGNED NULL,
                ticketMessage VARCHAR(3000) NULL,
                ticketMessageUrl VARCHAR(250) NULL
            );
            ''',
            '''
            CREATE TABLE IF NOT EXISTS TicketSystemLayers (
                guildId BIGINT UNSIGNED NOT NULL,
                status INT UNSIGNED DEFAULT 1,
                layerName VARCHAR(100) NOT NULL,         
                description VARCHAR(100) DEFAULT NULL
            );
            ''',
            ''' 
            CREATE TABLE IF NOT EXISTS TempVoiceChannelTicketSystem (
                guildId BIGINT UNSIGNED NOT NuLL,
                channelId BIGINT UNSIGNED NOT NULL,
                ticektName VARCHAR(100) NOT NULL
            );
            '''
            ]

        try:

            for table in tables:
                await cursor.execute(table)
                await db_connect.commit()
        
        except aiomysql.Error as error:
            print("parameterized query failed {}".format(error))


    async def add_views_and_buttons(self, bot):
       
        for cog in bot.cogs.values():
            
            if hasattr(cog, 'add_views'):
                views = await cog.add_views()
                for view in views:
                    bot.add_view(view)


    @commands.Cog.listener()
    async def on_ready(self):

        view = View(timeout=None)
        print(f'Logged in as: {bot.user.name}')
        print(f'With ID: {bot.user.id}')

        print("┏━━━┓ ┏━━━┓ ┏┓ ┏┓ ┏━━┓ ┏━━━┓ ┏━━┓")
        print("┃┏━┓┃ ┃┏━┓┃ ┃┃ ┃┃ ┗┫┣┛ ┗┓┏┓┃ ┗┫┣┛")
        print("┃┗━━┓ ┃┃ ┃┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃")
        print("┗━━┓┃ ┃┗━┛┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃")
        print("┃┗━┛┃ ┗━━┓┃ ┃┗━┛┃ ┏┫┣┓ ┏┛┗┛┃ ┏┫┣┓")
        print("┗━━━┛    ┗┛ ┗━━━┛ ┗━━┛ ┗━━━┛ ┗━━┛")
        
        await self.add_views_and_buttons(bot)

        self.bot.add_view(HelpMenuSelect())
        
        self.bot.add_view(view)

        await Main.create_db_table()


    @commands.slash_command(description="Shows you the ping.")
    async def ping(self, ctx):
        await ctx.respond(f"Pong! Latency is ``{round(bot.latency*1000)}`` ms")


    @commands.Cog.listener()
    async def on_error(event, *args, **kwargs):
        logging.error(f"An error occurred in event {event}: {args} {kwargs}", exc_info=True)

    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        await DatabaseUpdates._create_bot_settings(guild_id=guild.id)


    @commands.Cog.listener()
    async def on_disconnect(self):

        print(f"Bot has lost the connection {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
        
        cog = self.bot.get_cog("LeaderboardSystem")

        if cog:

            cog.edit_leaderboard_invite.stop()
            cog.edit_leaderboard_message.stop()

        sticky_cog = self.bot.get_cog("StickyMessage")

        if sticky_cog:

            sticky_cog.check_sticky_message_task.stop()

        auto_cog = self.bot.get_cog("AutoMessageSystem")

        if auto_cog:
            
            auto_cog.auto_message.stop()


    @commands.Cog.listener()
    async def on_resumed(self):
        
        print(f"Connection restored {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
        
        cog = self.bot.get_cog("LeaderboardSystem")

        if cog:

            if not cog.edit_leaderboard_invite.is_running():

                cog.edit_leaderboard_invite.start()

            if not cog.edit_leaderboard_message.is_running():

                cog.edit_leaderboard_message.start()

        sticky_cog = self.bot.get_cog("StickyMessage")

        if sticky_cog and not sticky_cog.check_sticky_message_task.is_running():

            sticky_cog.check_sticky_message_task.start()

        auto_cog = self.bot.get_cog("AutoMessageSystem")

        if auto_cog and not auto_cog.auto_message.is_running():

            auto_cog.auto_message.start()


class BotManager:
    
    def __init__(self, bot):

        self.bot = bot
        self.configure_logging()
        self.loop = asyncio.get_event_loop()
        self.loop.set_exception_handler(self.handle_exception)


    def configure_logging(self):

        logging.basicConfig(filename='bot_errors.log', level=logging.ERROR, 
            format='%(asctime)s - %(levelname)s - %(message)s')


    def log_error_to_file(self, message):

        logging.error(message)


    def handle_exception(self, loop, context):

        msg = context.get("exception", context["message"])
        self.log_error_to_file(f"Caught exception: {msg}")
        print(f"Caught exception: {msg}")


    def load_cogs(self):

        for filename in os.listdir("cogs"):

            if filename.endswith(".py"):

                cog_name = f"cogs.{filename[:-3]}"

                try:

                    self.bot.load_extension(cog_name)
                    print(f"Loaded {cog_name}")

                except Exception as e:

                    self.log_error_to_file(f"Failed to load {cog_name}: {e}")
                    print(f"Failed to load {cog_name}: {e}")


bot.add_cog(Main(bot))



if __name__ == "__main__":

    load_dotenv()
    bot_manager = BotManager(bot)

    try:

        bot_manager.load_cogs()
        bot.run(os.getenv("TOKEN"))

    except Exception as e:

        bot_manager.log_error_to_file(f"Bot crashed with error: {e}")
        print(f"Bot crashed with error: {e}")