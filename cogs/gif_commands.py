from Import_file import requests, discord, os, random, bot_colour
from discord.ext import commands
from discord.commands import Option
import aiohttp
import json


class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def search_gif(self, tags:str):
        
        key = os.getenv("API_KEY")

        params = {
            "q": tags,
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }

        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()
        print(data)

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']
        return url
    

    @commands.slash_command(description = "Send an anime kiss gif you can also mention someone!")
    async def kiss(self, ctx, user:discord.Member = None):
        
        url = self.search_gif(tags="Anime_kiss")

        emb = discord.Embed(title=f"Kiss", description=f"**{ctx.author.mention} kissed himself? ok**" if user == None else f"**{ctx.author.mention} has kissed {user.mention}**", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="via Tenor")
        await ctx.respond(embed=emb)


    @commands.slash_command(description = "Send a anime hug gif you can also mention someone!")
    async def hug(self, ctx, user:discord.Member = None):
       
        url = self.search_gif(tags="Anime_hug")

        emb = discord.Embed(title="Hug", description=f"**There you go {ctx.author.mention} hugs**" if user == None else f"**{ctx.author.mention} has hug {user.mention}**", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="Via Tenor")
        await ctx.send(embed=emb)
    

    @commands.slash_command(description = "Send a anime lick gif you can also mention someone!")
    async def lick(self, ctx, user:discord.Member = None):
        
        url = self.search_gif(tags="Anime_lick")
    
        emb = discord.Embed(title="Lick", description=f"**{ctx.author.mention} is licking... themselves?**" if user == None else f"**{ctx.author.mention} has licked {user.mention}**", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="Via Tenor")
        await ctx.send(embed=emb)


    @commands.slash_command(description = "Send a anime punch gif you also mention someone!")
    async def punch(self, ctx, user:discord.Member = None):

        url = self.search_gif(tags="Anime_punch")

        emb = discord.Embed(title="Punch", description=f"**{ctx.author.mention} punch himself?**" if user == None else f"**{ctx.author.mention} has punch {user.mention}**", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="Via Tenor")
        await ctx.send(embed=emb)


    @commands.command()
    async def idk(self, ctx, user:discord.Member = None):

        url = self.search_gif(tags="Anime_idk")

        emb = discord.Embed(title="Idk", description=f"**{ctx.author.mention} is shrugging ¯\_(ツ)_/**" if user == None else f"**{ctx.author.mention} is shrugging at {user.mention} ¯\_(ツ)_/¯**", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="Via Tenor")
        await ctx.send(embed=emb)

        
    @commands.command()
    async def dance(self, ctx, user:discord.Member = None):

        url = self.search_gif(tags="Anime_dace")

        emb = discord.Embed(title="Dance", description=f"**{ctx.author.mention} shows his moves! Nice**" if user == None else f"**Cute {ctx.author.mention} dancing with {user.mention}**", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="Via Tenor")
        await ctx.send(embed=emb)


    @commands.command()
    async def slap(self, ctx, user:discord.Member = None):
        
        url = self.search_gif("Anime_slap")

        emb = discord.Embed(title="Slap", description=f"**{ctx.author.mention} slaps himself?**" if user == None else f"**{ctx.author.mention} slaps {user.mention}**", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="Via Tenor")
        await ctx.send(embed=emb)


    @commands.command()
    async def fbi(self, ctx, user:discord.Member = None):
    
        url = self.search_gif(tags="Anime_fbi")
        
        emb = discord.Embed(title="FBI", description=f"**{ctx.author.mention} calls the Fbi!**" if user == None else f"**{ctx.author.mention} calls the FBI about {user.mention}**", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="Via Tenor")
        await ctx.send(embed=emb)


    @commands.command()
    async def embarres(self, ctx, user:discord.Member = None):
        
        url = self.search_gif(tags="Anime_embarres")

        emb = discord.Embed(title="Embarres", description=f"**{ctx.author.mention} is embarrassed, only what?**" if user == None else f"**{ctx.author.mention} was embarrassed by {user.mention}**", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="Via Tenor")
        await ctx.send(embed=emb)


    @commands.command()
    async def pet(self, ctx, user:discord.Member = None):
        
        url = self.search_gif(tags="Anime_pet")
      
        emb = discord.Embed(title="Pet", description=f"**{ctx.author.mention} will you pet someone, I wonder who it will be?**" if user == None else f"**{ctx.author.mention} pats {user.mention}** how cute UwU", color=bot_colour)
        emb.set_image(url=url)
        emb.set_footer(text="Via Tenor")
        await ctx.send(embed=emb)

    
    
    @commands.slash_command()
    async def rule34(self, ctx, tag:Option(str, description="Gebe einen tag ein nach dem gesucht werden soll achte dabei auf die schreibweiße")):
        tag.lower()

        if " " in tag:
            newtag = tag.replace(" ", "_")
        else:
            newtag = tag
        
        params = {
        "tags":newtag,
        "json":1
        }

        result = requests.get("https://api.rule34.xxx/index.php?page=dapi&s=post&q=index", params=params)
        
        data = result.json()
        r = random.choice(data)
        url = r["sample_url"]

        embed = discord.Embed(
            title="Hentai",description =f"url: {url}",
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via rule 34")
        await ctx.respond(embed=embed)


    @commands.command()
    async def animememe(self, ctx):
        async with aiohttp.ClientSession() as cd:
            async with cd.get('https://www.reddit.com/r/animememes.json') as r:
                animememe = await r.json()
                emb = discord.Embed(color=discord.Colour.random())
                emb.set_image(url=animememe["data"]["children"][random.randint(0, 20)]["data"]["url"])
                emb.set_footer(text=f"Meme send by {ctx.author}")
                await ctx.send(embed=emb)

    
def setup(bot):
    bot.add_cog(API(bot))


