from Import_file import requests, discord, os, random
from discord.ext import commands
from discord.commands import Option
import aiohttp
import json


class API(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kiss(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")
        
        params = {
            "q": "Anime_kiss",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Kiss = f"**{ctx.author.mention} kissed himself? ok**"
        else:
            Kiss = f"**{ctx.author.mention} has kissed {user.mention}**"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="Kiss",description=Kiss,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)


    @commands.command()
    async def hug(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")

        params = {
            "q": "Anime_hug",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Hug = f"**There you go {ctx.author.mention} hugs**"
        else:
            Hug = f"**{ctx.author.mention} has hug {user.mention}**"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="Hug",description=Hug,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)
    

    @commands.command()
    async def lick(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")

        params = {
            "q": "Anime_lick",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Lick = f"**{ctx.author.mention} is licking... themselves?**"
        else:
            Lick = f"**{ctx.author.mention} has licked {user.mention}**"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="lick",description=Lick,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)


    @commands.command()
    async def punch(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")

        params = {
            "q": "Anime_punch",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Punch = f"**{ctx.author.mention} punch himself?**"
        else:
            Punch = f"**{ctx.author.mention} has punch {user.mention}**"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="punch",description=Punch,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)


    @commands.command()
    async def idk(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")

        params = {
            "q": "Anime_idk",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Idk = f"**{ctx.author.mention} is shrugging ¯\_(ツ)_/**"
        else:
            Idk = f"**{ctx.author.mention} is shrugging at {user.mention} ¯\_(ツ)_/¯**"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="idk",description=Idk,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)

        
    @commands.command()
    async def dance(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")

        params = {
            "q": "Anime_dance",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Dance = f"**{ctx.author.mention} shows his moves! Nice**"
        else:
            Dance = f"**Cute {ctx.author.mention} dancing with {user.mention}**"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="dance",description=Dance,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)


    @commands.command()
    async def slap(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")

        params = {
            "q": "Anime_slap",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Slap = f"**{ctx.author.mention} slaps himself?**"
        else:
            Slap = f"**{ctx.author.mention} slaps {user.mention}**"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="slap",description=Slap,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)


    @commands.command()
    async def fbi(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")

        params = {
            "q": "Anime_fbi",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Fbi = f"**{ctx.author.mention} calls the Fbi!**"
        else:
            Fbi = f"**{ctx.author.mention} calls the FBI about {user.mention}**"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="fbi",description=Fbi,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)


    @commands.command()
    async def embarres(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")

        params = {
            "q": "Anime_embarrassed",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Embarres = f"**{ctx.author.mention} is embarrassed, only what?**"
        else:
            Embarres = f"**{ctx.author.mention} was embarrassed by {user.mention}**"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="embarres",description=Embarres,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)


    @commands.command()
    async def pet(self, ctx, user: discord.User = None):
        key = os.getenv("API_KEY")

        params = {
            "q": "Anime_pet",
            "key": key,
            "limit": "10",
            "client_key": "Discord_bot",
            "media_filter": "gif"
        }
        result = requests.get("https://tenor.googleapis.com/v2/search", params=params)
        data = result.json()

        if user == None:
            Embarres = f"**{ctx.author.mention} will you pet someone, I wonder who it will be?**"
        else:
            Embarres = f"**{ctx.author.mention} pats {user.mention}** how cute UwU"

        number = random.randint(0, 9)
        url = data['results'][number]['media_formats']['gif']['url']

        embed = discord.Embed(
            title="embarres",description=Embarres,
            color=discord.Colour.random()
        )
        embed.set_image(url=url)
        embed.set_footer(text="Via Tenor")
        await ctx.send(embed=embed)
    
    
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


