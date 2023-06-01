from Import_file import *
from Liest import *

class Admin_Funktion:
    @bot.command()
    @commands.has_permissions(administrator=True, manage_roles=True)

    
    async def rule_deutsch(ctx: commands.Context): 
        view = discord.ui.View(timeout=None)

       
        embed = discord.Embed(title="Rules", description="""
        **Allgemeine Regeln**

        1. Nicht Spammen.

        2. Keine Eigenwerbung egal welcher art.

        3. Freundlicher Umgang (Keine Beleidigungen oder Rassistische, diskriminierende aussagen).

        4. Keine Belästigung von anderen Personen.

        5. Keine Gewalt Videos oder andere verstörenden Inhalte.

        6. Bitte posten, chatten nur in die dafür vorgegebenen Chanels.

        7. Haltet euch auch an die Richtlinien.

        8. Solltest du einen Regel verstoß bemerke bitten wir dich diesen einen Team Mitglied zu melden.

        9. Wenn du selbst gegen die regeln verstoßt werden selbst verständlich Konsequenzen folgen.

        10. Keine radikalen politische themen.

        11. Keine Eigenwerbung für deinen Server außer er ist mit den Owner oder Moderator abgesprochen.

        12. Keine Privaten Informationen anderer Menschen reinposten bzw. (zum beispiel Adresse, voller name oder Ausweise).

        13. Nur weil etwas nicht in den regeln steht heißt es nicht das es direkt erlaubt ist.


        **Regeln für NSFW Chats**

        1. Keine Lolicons oder sehr junge Personen schicken.

        2. Keine Gore oder zu verstörende Inhalte schicken.

        3. Keine konversationen in NSFW channels (Stattdessen einfach Community channels benutzen)

        4. Bitte die Discord Richtlinien einhalten.

        ``Die Discord Richtlinien findest du unter:``
        
        https://discord.com/guidelines""", color=0xf409d7)
        embed.set_image(url="https://media.discordapp.net/attachments/865911796292780073/974770465199509544/Rules_banner.gif")
        
        await ctx.send(view=view, embed=embed)



    @bot.command()
    async def rule_english(ctx: commands.Context):
        view = discord.ui.View(timeout=None)
        
        
        embed = discord.Embed(title= "Rules in English: ", description="""
        **General rules**

        1. No spam.

        2. no self-promotion of any kind.

        3. friendly contact (no insults or racist statements, discriminatory statements).

        4. no harassment of other persons.

        5. no violent videos or other disturbing content.

        6. please post, chat only in the designated channels.

        7. follow the guidelines as well.

        8. if you notice a rule violation, please report it to a team member.

        9. if you break the rules yourself, there will be consequences.

        10. no radical political topics.

        11. no self-promotion for your server, unless it is agreed with the owner or moderator.

        12. don't post private information of other people (e.g. address, full name or IDs).

        13. just because something is not in the rules does not mean it is directly allowed.


        **Rules for NSFW Chats** 

        1. Don't send lolicons or very young people.

        2. don't send bloody or too disturbing content.

        3. do not have conversations in NSFW channels (use community channels instead).

        4. please respect the Discord guidelines.

        ``The Discord guidelines can be found at:``

        https://discord.com/guidelines
        """, color=0xf409d7)
        embed.set_image(url="https://media.discordapp.net/attachments/865911796292780073/974770465199509544/Rules_banner.gif")

        await ctx.send(view=view, embed=embed)



@bot.command()
async def ruleD(ctx):
    embed = discord.Embed(title="Rules", description="""
    **General rules**

    1. no spam.

    2. No self-promotion of any kind.

    3. Friendly interaction (no insults or racist or discriminatory remarks).

    4. No harassment of other persons.

    5. no violent videos or other disturbing content.

    6. please post and chat only in the designated channels.

    7. pay attention to the guidelines as well.

    8. if you notice a rule violation, please report it to a team member.

    9. if you break the rules yourself, there will be consequences.

    10. no radical political topics.

    11. no self-promotion for your server, unless it is agreed with the owner or moderator.

    12. don't post private information of other people (e.g. address, full name or IDs).

    13. just because something is not in the rules, does not mean that it is directly allowed.

    14. No NSFW or offensive content.

    **Cooking rules**

    Only post recipes that you have tried yourself.

    If it goes no exclusive ingredients.

    Please respect the Discord guidelines.

    ``The Discord guidelines can be found at:``

        
    https://discord.com/guidelines""", color=0xf409d7)
    embed.set_image(url="https://media.discordapp.net/attachments/865911796292780073/974770465199509544/Rules_banner.gif")
        
    await ctx.send(embed=embed)



@bot.command()
async def ruleE(ctx):
    embed = discord.Embed(title= "Rules in English: ", description="""
    **General rules**

    1. No spam.

    2. no self-promotion of any kind.

    3. friendly contact (no insults or racist statements, discriminatory statements).

    4. no harassment of other persons.

    5. no violent videos or other disturbing content.

    6. please post, chat only in the designated channels.

    7. follow the guidelines as well.

    8. if you notice a rule violation, please report it to a team member.

    9. if you break the rules yourself, there will be consequences.

    10. no radical political topics.

    11. no self-promotion for your server, unless it is agreed with the owner or moderator.

    12. don't post private information of other people (e.g. address, full name or IDs).

    13. just because something is not in the rules does not mean it is directly allowed.


    **Rules for NSFW Chats** 

    1. Don't send lolicons or very young people.

    2. don't send bloody or too disturbing content.


    3. do not have conversations in NSFW channels (use community channels instead).

    4. please respect the Discord guidelines.
    
    ``The Discord guidelines can be found at:``

    https://discord.com/guidelines
        """, color=0xf409d7)
    embed.set_image(url="https://media.discordapp.net/attachments/865911796292780073/974770465199509544/Rules_banner.gif")

    await ctx.send(embed=embed)

@bot.command()
async def ruleG(ctx):
    embed = discord.Embed(title= "Rules", description="""
    **General rules**

    General rules

    1. No spam.

    2. No self-promotion of any kind.

    3. Friendly contact (no insults or racist statements, discriminatory statements).

    4. No harassment of other persons.

    5. No violent videos or other disturbing content.

    6. Please post, chat only in the designated channels.

    7. Follow the guidelines as well.

    8. If you notice a rule violation, please report it to a team member.

    9. If you break the rules yourself, there will be consequences.

    10. No radical political topics.

    11. No self-promotion for your server, unless it is agreed with the owner or moderator.

    12. Don't post private information of other people (e.g. address, full name or IDs).

    13. Just because something is not in the rules does not mean it is directly allowed.
    
    **Art rules**

    1. Do not badmouth pictures or drawings unnecessarily.

    2. Do not take back orders without reason.

    3. Upload only your own images or mention the artist.

    4. Do not upload images simply from the Internet 

    ``The Discord guidelines can be found at:``
    https://discord.com/guidelines
        """, color=0xf409d7)

    await ctx.send(embed=embed)



@bot.command()
async def Hanime(ctx):
    emb = discord.Embed(title="New Hanime system", description="""
    Hello this is the new hanime system because we slowly many new channels it has become quite confusing, 
    so we have added this system that everything for you remains nice and clear 
    """, color=discord.Colour.nitro_pink())
    
    emb.add_field(name="all hanime", value="With <@&1002950560670027926> you can see everything we have to offer", inline=False)
    emb.add_field(name="game hanime", value="With <@&1002949414500970666> you can see all our exclusive game hentais ", inline=False)
    emb.add_field(name="character hanime", value="With <@&1002949615890477107> you can see our collection of specific character hentais", inline=False)
    emb.add_field(name="hanime video", value="With <@&1002950079348494477> you can see whole hentais", inline=False)
    emb.add_field(name="Specific hanime", value="With <@&1002951148463984751> you can see only certain categories of hentais", inline=False)
    emb.set_image(url="https://cdn.discordapp.com/attachments/879599055062306866/905641540234383380/image0.gif")
    await ctx.send(embed=emb)


class Funpark(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def Gaming(ctx):
        emb = discord.Embed(title="Funpark Gaming", description="Play together with your friends and win! ", color=discord.Colour.green())
        emb.set_image()

@bot.command()
async def hanimeinfo():
    emb = discord.Embed(title="Info", description=
    """
    Hello we want to inform you that we now have a new Hentai system, you can pick up the new Hentai rolls in <#1001944180278435850>. 
    <@&865907711832227840>
    """, color=discord.Colour.nitro_pink())
    emb.set_image(url="https://cdn.discordapp.com/attachments/865911796292780073/1003949800359723059/unknown.png")
