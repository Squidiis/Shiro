
"""
┏━━━┓ ┏━━━┓ ┏┓ ┏┓ ┏━━┓ ┏━━━┓ ┏━━┓
┃┏━┓┃ ┃┏━┓┃ ┃┃ ┃┃ ┗┫┣┛ ┗┓┏┓┃ ┗┫┣┛
┃┗━━┓ ┃┃ ┃┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┗━━┓┃ ┃┗━┛┃ ┃┃ ┃┃  ┃┃   ┃┃┃┃  ┃┃
┃┗━┛┃ ┗━━┓┃ ┃┗━┛┃ ┏┫┣┓ ┏┛┗┛┃ ┏┫┣┓
┗━━━┛    ┗┛ ┗━━━┛ ┗━━┛ ┗━━━┛ ┗━━┛
"""

from datetime import * 
from discord import ButtonStyle, Interaction
import requests
from utils import *
from typing import List



##########################################  RPS Game  #############################################


class RPSButtons(discord.ui.View):
    
    def __init__(self, game_mode, second_user, first_user):
        self.game_mode = game_mode
        self.second_user = second_user
        self.first_user = first_user
        super().__init__(timeout=None)

        if any(x is not None for x in [self.second_user, self.first_user]):
            self.check_useres = {"first_user":self.first_user.id, "second_user":self.second_user.id}
            self.user_choice = {"first_user_choice":"", "second_user_choice":""}

        self.false_user_emb = discord.Embed(title=f"{Emojis.help_emoji} You can not participate in this game {Emojis.exclamation_mark_emoji}", 
            description=f"""{Emojis.dot_emoji} You can't select anything here because you are not invited to this game.""", color=bot_colour)
        self.wait_emb = discord.Embed(title=f"{Emojis.help_emoji} Wait a little longer", 
            description=f"""{Emojis.dot_emoji} Wait for the answer from your opponent""", color=bot_colour)
    

    def rps_analysis(self):

        bot_choice = random.choice(["rock", "paper", "scissors"])
        choice_line = f"""{Emojis.dot_emoji} {f'Choice from {self.second_user.mention}: {bot_choice}' if self.user_choice["second_user_choice"] == None else f'Choice from {self.second_user.mention}: {self.user_choice["second_user_choice"]}'}"""
    
        win_emb = discord.Embed(description=f"""{'## :tada: You have won!' if self.game_mode == 0 else f'## :tada: {self.first_user.name} has won against {self.second_user.name}'}
            {Emojis.dot_emoji} Choice from {self.first_user.mention}: {self.user_choice["first_user_choice"]}\n{choice_line}""",color=bot_colour)

        lose_emb = discord.Embed(description=f"""{'## You have lost!' if self.game_mode == 0 else f'## :tada: {self.second_user.name} has won against {self.first_user.name}'}
            {Emojis.dot_emoji} Choice from {self.first_user.mention}: {self.user_choice["first_user_choice"]}\n{choice_line}""", color=bot_colour)

        tie_emb = discord.Embed(description=f"""## Tie!
            {Emojis.dot_emoji} Choice from {self.first_user.mention}: {self.user_choice["first_user_choice"]}\n{choice_line}""", color=bot_colour)

        results = {
        "rock": {"rock": tie_emb, "paper": lose_emb, "scissors": win_emb},
        "paper": {"rock": win_emb, "paper": tie_emb, "scissors": lose_emb},
        "scissors": {"rock": lose_emb, "paper": win_emb, "scissors": tie_emb}}

        return results[self.user_choice["first_user_choice"]][self.user_choice["second_user_choice"]] if self.game_mode == 1 else results[self.user_choice["first_user_choice"]][bot_choice]


    def rps_check(self, choice:str, user_id:int):

        if self.game_mode == 1:
            
            if user_id == self.second_user.id and self.check_useres["second_user"] == user_id:

                self.check_useres["second_user"], self.user_choice["second_user_choice"] = True, choice

                if self.user_choice["first_user_choice"] != "":

                    return [self.rps_analysis(), None]

            elif user_id == self.second_user.id and self.check_useres["second_user"] == True:
                
                return  [self.wait_emb, True]

            elif user_id == self.first_user.id and self.check_useres["first_user"] == user_id:

                self.check_useres["first_user"], self.user_choice["first_user_choice"] = True, choice

                if self.user_choice["second_user_choice"] != "":
                    
                    return [self.rps_analysis(), None]

            elif user_id == self.first_user.id and self.check_useres["first_user"] == True:

                return [self.wait_emb, True]

            elif all(x != user_id for x in [self.first_user.id, self.check_useres["first_user"], self.second_user.id, self.check_useres["second_user"]]):

                return [self.false_user_emb, True]
            
        elif self.game_mode == 0:

            self.check_useres["first_user"], self.user_choice["first_user_choice"], self.user_choice["second_user_choice"] = True, choice, None
            return [self.rps_analysis(), None]
        
        else:
            
            emb = discord.Embed(title=f"{Emojis.help_emoji} The game has expired", 
                description=f"""{Emojis.dot_emoji} The game challenge has expired, just challenge someone again to rock, paper, scissors""", color=bot_colour)
            return [emb, None]


    @discord.ui.button(label="rock", style=discord.ButtonStyle.blurple, custom_id="rock", emoji="🪨")
    async def rock_callback(self, button, interaction:discord.Interaction):

        emb = self.rps_check(user_id=interaction.user.id, choice="rock")
        if emb == None:
            await interaction.response.defer()
        else:
            await interaction.response.edit_message(embed=emb[0], view=None) if emb[1] == None else await interaction.response.send_message(embed=emb[0], ephemeral=True)
           

    @discord.ui.button(label="paper", style=discord.ButtonStyle.blurple, custom_id="paper", emoji="🧻")
    async def paper_callback(self, button, interaction:discord.Interaction):

        emb = self.rps_check(user_id=interaction.user.id, choice="paper")
        if emb == None:
            await interaction.response.defer()
        else:
            await interaction.response.edit_message(embed=emb[0], view=None) if emb[1] == None else await interaction.response.send_message(embed=emb[0], ephemeral=True)


    @discord.ui.button(label="scissors", style=discord.ButtonStyle.blurple, custom_id="scissors", emoji="✂️")
    async def scissors_callback(self, button, interaction:discord.Interaction):

        emb = self.rps_check(user_id=interaction.user.id, choice="scissors")
        if emb == None:
            await interaction.response.defer()
        else:
            await interaction.response.edit_message(embed=emb[0], view=None) if emb[1] == None else await interaction.response.send_message(embed=emb[0], ephemeral=True)





class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      

    @commands.slash_command(name = "rps", description = "Play scissors, stone, paper against your friends or a bot!")
    async def rps(self, ctx:discord.ApplicationContext, user:Option(discord.Member, description="Choose a user with whom you want to challenge you can also play against a bot") = None):

        if user == None or user.bot:
            user = user if user != None else bot.get_user(928073958891347989)
            emb = discord.Embed(title="Single player", description=f"""{Emojis.dot_emoji} {ctx.author.name} against {user.name}\n {ctx.author.mention} choose from stone 🪨, paper 🧻 or scissors ✂️ {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb, view=RPSButtons(game_mode=0, second_user=user, first_user=ctx.author))

        else:

            emb = discord.Embed(title=f"Multiplayer", description=f"""{Emojis.dot_emoji} {ctx.author.name} challenges {user.name} to a round stone 🪨, paper 🧻, scissors ✂️, out {Emojis.exclamation_mark_emoji}
            {user.mention} Are you up for the challenge?""", color=bot_colour)
            await ctx.respond(embed=emb, view=RPSButtons(game_mode=1, second_user=user, first_user=ctx.author))


    @commands.slash_command(description = "Throw a coin!")
    async def coinflip(self, ctx:discord.ApplicationContext):
        
        Tail = discord.File("assets/coin_flip/tail_coin.png", filename="tail_coin.png")
        Head = discord.File("assets/coin_flip/head_coin.png", filename="head_coin.png")
        emb = discord.Embed(title="", description=f"**{ctx.author.mention} has flipped the coin!**", color=bot_colour)
        emb.set_image(url = "https://cdn.dribbble.com/users/1102039/screenshots/6574749/multi-coin-flip.gif")
        coin = [Tail, Head]
        coinsite = ""
        random_flip = random.choice(coin)
        
        if random_flip == Tail:
            coinsite = "Tale"

        elif random_flip == Head:
            coinsite = "Head"
        
        embed1 = await ctx.respond(embed=emb)
        await asyncio.sleep(5)
        
        emb = discord.Embed(title=f"You flipped {coinsite}", description="", color=bot_colour)
        emb.set_image(url=f"attachment://{random_flip}")
        await embed1.edit (embed=emb, file=random_flip)



    @commands.slash_command(description="Gives you a random cocktail recipe!")
    async def cocktails(self, ctx):
        cocktails = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php").json()["drinks"][0]
        name = cocktails['strDrink']
        
        alcohol = cocktails['strAlcoholic']
        instructions = cocktails['strInstructions']
        ingredients = []
        
        for i in range(15):
            measure = cocktails.get(f"strMeasure{i}")
            ingredient = cocktails.get(f"strIngredient{i}")
            if ingredient is not None:
                ingredients.append(f'{ingredient} {measure}')

        allIngredients_string = ", ".join(ingredients)
        measures = []
        allmeasures_string = ", ".join(measures)

        Recipe = f"{allIngredients_string} {allmeasures_string}"
            
        if alcohol == "Alcoholic":
            Alcohol = "Yes"
        else:
            Alcohol = "No"
    
        DrinkThumb = cocktails['strDrinkThumb']
        
        emb = discord.Embed(title=f"Name: {name}", description=f"""
        Alcoholic: {Alcohol}
        
        Recipe: {Recipe} 

        Instructions: {instructions}
        
        """, color=bot_colour)
        emb.set_image(url=DrinkThumb)
        await ctx.respond(embed=emb)






def setup(bot):
    bot.add_cog(Fun(bot))





