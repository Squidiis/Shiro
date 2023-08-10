from Import_file import *
from Liest import *

@bot.command()
async def rule(ctx):
    embed = discord.Embed(title= "Rules", description="""
    **General rules**

    •  No spam!

    •  No self-promotion of any kind!
    
    •  Friendly contact (no insults or racist statements, discriminatory statements)!

    •  No harassment of other persons!

    •  No violent videos or other disturbing content!

    •  Please chat only in the designated channels!

    •  No radical political topics!

    •  Don't post private information of other people (e.g. address, full name or IDs)!

    •  Please do not write to other members privately if they have not given you permission to do so!

    •  Please settle your disputes privately!
                          
    •  If you notice a rule violation, please report it to a team member!

    •  If you break the rules yourself, there will be consequences!

    •  Just because something isn`t mentioned doesnt mean its allowed!


    **Rules for  NSFW Chats**

    •  Don't post pictures of Lolicons or gore!

    •  Please only sent your pictures in the designated channel and category!

    •  Don´t write in the NSFW channels!

                          
    **Please respect the Discord guidelines!**
    The Discord guidelines can be found at:

    https://discord.com/guidelines

    Have Fun!^^
        """, color=0xf409d7)
    embed.set_image(url="https://media.discordapp.net/attachments/865911796292780073/974770465199509544/Rules_banner.gif")

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


@bot.command()
async def hanimeinfo():
    emb = discord.Embed(title="Info", description=
    """
    Hello we want to inform you that we now have a new Hentai system, you can pick up the new Hentai rolls in <#1001944180278435850>. 
    <@&865907711832227840>
    """, color=discord.Colour.nitro_pink())
    emb.set_image(url="https://cdn.discordapp.com/attachments/865911796292780073/1003949800359723059/unknown.png")
