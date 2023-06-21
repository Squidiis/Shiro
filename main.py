
from Hanime_Funpark import *
from discord import ButtonStyle, Colour, Embed, Interaction, CategoryChannel
from Import_file import *

from cogs.level_system import *
from cogs.economy import *
from Liest import * 
from dotenv import load_dotenv
import calendar


@bot.slash_command(description="Shows you the ping.")
async def ping(ctx):
    await ctx.respond(f"Pong! Latency is ``{round(bot.latency*1000)}`` ms")
    
    


class Update(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def update(self, ctx):
        emb = discord.Embed(
            title="Update",
            description=f"""
            **Deutsch**

            Hallo, wir haben eine neue änderung gemacht.
            Wir freuen uns euch mitteilen zu düfen, dass wir eine neue Funktion haben.
            Ihr könnt euch ab jetzt ganze hentais hier von discord aus ansehen, mit einer video auswahl.
            Schaut doch mal in <#1081909438383915069> vorbei und gebt uns gerne feedback

            **English**

            Hello, we have made a new change.
            We are happy to announce that we have a new feature.
            You can now watch full hentais from discord. There is also a video selection.
            Please check out <#1081909438383915069> and feel free to give us feedback.

            <@865907711832227840>
            """,
            color= discord.Colour.purple()
        )
        await ctx.send(embed=emb)

bot.add_cog(Update(bot))



class main(commands.Cog, LevelRolesButtons):
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

        # level system blacklist manager
        self.bot.add_view(BlacklistManagerButtons())
        self.bot.add_view(BlacklistManagerSelectAdd())
        self.bot.add_view(BlacklistManagerSelectRemove())
        view.add_item(TempBlackklistLevelSaveButton())
        view.add_item(ShowBlacklistLevelSystemButton())
        
        # Applycation
        self.bot.add_view(ApplicationButton())

        # self roles 
        self.bot.add_view(DropdownColours())
        self.bot.add_view(DropdownHoppys())
        view.add_item(Genderbutton_Female())
        view.add_item(Genderbutton_Divers())
        view.add_item(Genderbutton_Male())

        # Economy
        self.bot.add_view(EconomySystemSettings())
        self.bot.add_view(ResetBlacklistEconomyButton())

        self.bot.add_view(view)

bot.add_cog(main(bot))



@bot.command(aliases=['user-info', 'about', 'whois', 'ui'])
async def userinfo(ctx, member: discord.Member = None):
    member = ctx.author if not member else member

    unix_join_time = calendar.timegm(member.joined_at.utctimetuple())
    unix_create_time = calendar.timegm(member.created_at.utctimetuple())

    badge = ""
    if member.public_flags.bug_hunter:
        badge += "<:bughunter:1045796473691979776> Bug Hunter\n"
    if member.public_flags.bug_hunter_level_2:
        badge += "<:bughunter2:1045796474744750090> Bug Hunter Level 2\n"
    if member.public_flags.early_supporter:
        badge += "<:earlysupporter:1045796475864625283> Early Suppoter\n"
    if member.public_flags.verified_bot_developer:
        badge += "<:botdev:1045796472408506368> Developer\n"
    if member.public_flags.partner:
        badge += "<:partner:1045796481518551102> Partner\n"
    if member.public_flags.staff:
        badge += "<:staff:1045796482705543168> Staff\n"
    if member.public_flags.hypesquad_balance:
        badge += f"<:hypesquad_balance:1045796476992884838> Hypesquad Balance\n"
    if member.public_flags.hypesquad_bravery:
        badge += f"<:hypesquad_bravery:1045796478507032638> Hypesquad Bravery\n"
    if member.public_flags.hypesquad_brilliance:
        badge += f"<:hypesquad_brilliance:1045796480172163152> Hypesquad Brilliance\n"

    user_banner = await bot.fetch_user(member.id)

    if user_banner.banner is not None:
        if member.avatar is not None:
            embed = discord.Embed(colour=member.color,
                                timestamp=datetime.utcnow(),
                                description=f"[User Avatar]({member.avatar.url}) | [User Banner]({user_banner.banner.url})")
            embed.set_image(url=f"{user_banner.banner.url}")
            embed.set_thumbnail(url=f'{member.display_avatar.url}')
        else:
            embed = discord.Embed(colour=member.color,
                                timestamp=datetime.utcnow(),
                                description=f"[User Banner]({user_banner.banner.url})")
            embed.set_image(url=f"{user_banner.banner.url}")
    elif member.avatar is not None:
        embed = discord.Embed(colour=member.color,
                                timestamp=datetime.utcnow(),
                                description=f"[User Avatar]({member.avatar.url})")
        embed.set_thumbnail(url=f'{member.display_avatar.url}')
    else:
        embed = discord.Embed(colour=member.color,
                                timestamp=datetime.utcnow())

    embed.set_author(name=f"Userinfo")

    embed.add_field(name="Name:",
                    value=f"`{member} (Bot)`" if member.bot else f"`{member}`",
                    inline=True)
    embed.add_field(name=f"Mention:",
                    value=member.mention,
                    inline=True)
    embed.add_field(name="Nick:",
                    value=f"`{member.nick}`" if member.nick else "Nicht gesetzt",
                    inline=True)
    embed.add_field(name="ID:",
                    value=f"`{member.id}`",
                    inline=True)

    if member.status == discord.Status.online:
        if member.is_on_mobile():
            embed.add_field(name="Status:", value="`Handy`")
        else:
            embed.add_field(name="Status", value=f"`Online`")
    elif member.status == discord.Status.idle:
        embed.add_field(name="Status:",
                        value=f"`Abwesend`")
    elif member.status == discord.Status.dnd:
        embed.add_field(name="Status:",
                        value=f"`Beschäftigt`")
    elif member.status == discord.Status.offline:
        embed.add_field(name="Status:",
                        value=f"`Offline`")
    elif member.status == discord.Status.invisible:
        embed.add_field(name="Status:",
                        value=f"`Unsichtbar`")

    embed.add_field(name="Erstellt am:",
                    value=f"<t:{unix_create_time}:f> (<t:{unix_create_time}:R>)",
                    inline=True)
    embed.add_field(name="Beigetreten am:",
                    value=f'<t:{unix_join_time}:f> (<t:{unix_join_time}:R>)',
                    inline=True)
    embed.add_field(name="Höchste Rolle:",
                    value=member.top_role.mention,
                    inline=True)
    embed.add_field(name="<:booster:1045801339780862063> Booster:",
                    value=f"`Ja`" if member.premium_since else "`Nein`",
                    inline=True)
    if badge != "":
        embed.add_field(name="Badges:",
                        value=badge,
                        inline=True)

    if member.activities:
        for activity in member.activities:
            if str(activity) == "Spotify":
                embed.add_field(name="Spotify",
                                value=f'Title: {activity.title}\nArtist: {activity.artist}\n')

    embed.set_thumbnail(url=f'{member.avatar.url}')

    await ctx.reply(embed=embed)


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
        emb.add_field(name=f"Infos {help_emoji}", 
            value=f"{dot_emoji} user: {interaction.user.mention}\n{dot_emoji} Id: {interaction.user.id}\n{dot_emoji} Advertising as: {select.values[0]}")
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


    

if __name__ == "__main__":
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

    load_dotenv()
    bot.run(os.getenv("TOKEN"))

