
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
from Import_file import * 
from typing import List



class RPSButtons(discord.ui.View):
    def __init__(self, game_mode, second_user, first_user):
        self.game_mode = game_mode
        self.second_user = second_user
        self.first_user = first_user
        super().__init__(timeout=None)

        self.check_useres = {"first_user":self.first_user.id, "second_user":self.second_user.id}
        self.user_choice = {"first_user_choice":"", "second_user_choice":""}

        self.false_user_emb = discord.Embed(title=f"{Emojis.help_emoji} Du kannst nicht an diesem Spiel Teilnehmen {Emojis.exclamation_mark_emoji}", 
            description=f"""{Emojis.dot_emoji} Du kannst hier nichts auswählen da du nicht zu dieser Partie eingeladen wurdest.""", color=bot_colour)
        self.wait_emb = discord.Embed(title=f"{Emojis.help_emoji} Warte nocht etwas", 
            description=f"""{Emojis.dot_emoji} Warte auf die antwort deines Spiel partners""", color=bot_colour)
    
    def rps_analysis(self):

        bot_choice = random.choice(["rock", "paper", "scissors"])
        choice_line = f"""{Emojis.dot_emoji} {f'Wahl von {self.second_user.mention}: {bot_choice}' if self.user_choice["second_user_choice"] == None else f'Wahl von {self.second_user.mention}: {self.user_choice["second_user_choice"]}'}"""
    
        win_emb = discord.Embed(description=f"""{'#Du hast gewonnen!' if self.game_mode == 0 else f'#{self.first_user.name} hat gegen {self.second_user.name} gewonnen'}
            {Emojis.dot_emoji} Wahl von {self.first_user.mention}: {self.user_choice["first_user_choice"]}\n{choice_line}""",color=bot_colour)

        lose_emb = discord.Embed(description=f"""{'#Du hast verloren!' if self.game_mode == 0 else f'#{self.second_user.name} hat gegen {self.first_user.name} gewonnen'}
            {Emojis.dot_emoji} Wahl von {self.first_user.mention}: {self.user_choice["first_user_choice"]}\n{choice_line}""", color=bot_colour)

        tie_emb = discord.Embed(description=f"""#Unentschieden!
            {Emojis.dot_emoji} Wahl von {self.first_user.mention}: {self.user_choice["first_user_choice"]}\n{choice_line}""", color=bot_colour)

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
            
        else:

            self.check_useres["first_user"], self.user_choice["first_user_choice"], self.user_choice["second_user_choice"] = True, choice, None
            return [self.rps_analysis(), None]

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
      

    @commands.slash_command(name = "rps")
    async def rps(self, ctx:commands.Context, user:Option(discord.Member, description="Wähle einen user mit den herausfordern möchtest du kann auch gegen einen bot spielen") = None):

        if user == None or user.bot:
            user = user if user != None else bot.get_user(928073958891347989)
            emb = discord.Embed(title="Single player", description=f"""{Emojis.dot_emoji} {ctx.author.name} gegen {user.name}\n {ctx.author.mention} wähle aus Stein 🪨, Papier 🧻 oder Schere ✂️ {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await ctx.respond(embed=emb, view=RPSButtons(game_mode=0, second_user=user, first_user=ctx.author))

        else:

            emb = discord.Embed(title=f"Multiplayer", description=f"""{Emojis.dot_emoji} {ctx.author.name} vordert {user.name} zu einer runde Stein 🪨, Papier 🧻, Schere ✂️, heraus {Emojis.exclamation_mark_emoji}
            {user.mention} Nimmst du die herausvoerderun an?""")
            await ctx.respond(embed=emb, view=RPSButtons(game_mode=1, second_user=user, first_user=ctx.author))


    @commands.command()
    async def coinflip(self, ctx):
        
        Tail = discord.File("assets/coin_flip/tail_coin.png", filename="tail_coin.png")
        Head = discord.File("assets/coin_flip/head_coin.png", filename="head_coin.png")
        emb = discord.Embed(title="", description=f"**{ctx.author.mention} has flipped the coin!**", color=discord.Colour.random())
        emb.set_image(url = "https://cdn.dribbble.com/users/1102039/screenshots/6574749/multi-coin-flip.gif")
        coin = [Tail, Head]
        coinsite = ""
        random_flip = random.choice(coin)
        
        if random_flip == Tail:
            coinsite = "Tale"

        elif random_flip == Head:
            coinsite = "Head"
        
        embed1 = await ctx.send(embed=emb)
        await asyncio.sleep(5)
        
        emb = discord.Embed(title=f"You flipped {coinsite}", description="", color=discord.Colour.random())
        emb.set_image(url=f"attachment://{random_flip}")
        await embed1.edit (embed=emb, file=random_flip)



    @commands.slash_command(description="Gives you a random cocktail recipe.")
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
        
        """, color=discord.Colour.random())
        emb.set_image(url=DrinkThumb)
        await ctx.respond(embed=emb)



def setup(bot):
    bot.add_cog(Fun(bot))





