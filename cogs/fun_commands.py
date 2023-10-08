
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
    def __init__(self, game_mode, second_user):
        self.game_mode = game_mode
        self.second_user = second_user
        super().__init__(timeout=None)
    
    @staticmethod
    def get_choice():

        choices = ["rock", "paper", "scissors"]
        choice = random.choice(choices)
        return choice
    
    def rps_analysis(self, choice_user:str, first_user:str, second_user = None, second_user_choice:str = None):

        choice_bot = self.get_choice()

        win_emb = discord.Embed(title=f"{'Du hast gewonnen!' if second_user_choice == None else f'{first_user} hat gegen {second_user} gewonnen'}", 
            description=f"""{Emojis.dot_emoji} Deine wahl: {choice_user}
            {Emojis.dot_emoji} {f'Die Wahl des bots: {choice_bot}' if second_user_choice == None else f'Die wahl von {second_user}: {second_user_choice}'}""", color=bot_colour)

        lose_emb = discord.Embed()

        tie_emb = discord.Embed()

        if self.game_mode == None:

            if choice_user == "rock":

                if choice_bot == "scissors":
                    return win_emb
                
                elif choice_bot == "paper":
                    return lose_emb

                elif choice_bot == "rock":
                    return tie_emb
                
            elif choice_user == "paper":

                if choice_bot == "rock":
                    return win_emb

                elif choice_bot == "scissors":
                    return lose_emb
                
                elif choice_bot == "paper":
                    return tie_emb

            elif choice_user == "scissors":

                if choice_bot == "paper":
                    return win_emb

                elif choice_bot == "rock":
                    return lose_emb
                
                elif choice_bot == "scissors":
                    return tie_emb
            

    @discord.ui.button(label="rock", style=discord.ButtonStyle.blurple, custom_id="rock")
    async def rock_callback(self, interaction:discord.Interaction, button):

        emb = self.rps_analysis(choice_user="rock", first_user = interaction.user.name, second_user = self.second_user)
        await interaction.response.send_message(embed=emb, view=None)

    @discord.ui.button(label="paper", style=discord.ButtonStyle.blurple, custom_id="paper")
    async def paper_callback(self, interaction:discord.Interaction, button):

        emb = self.rps_analysis()

    @discord.ui.button(label="scissors", style=discord.ButtonStyle.blurple, custom_id="scissors")
    async def scissors_callback(self, interaction:discord.Interaction, button):

        emb = self.rps_analysis()


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      

    @commands.slash_command(name = "rps")
    async def rps(self, ctx:commands.Context, user:Option(discord.Member, description="Wähle einen user mit den herausfordern möchtest du kann auch gegen einen bot spielen") = None):

        if user == None or user == user.bot:

            emb = discord.Embed()
            await ctx.respond(embed=emb, view=RPSButtons(game_mode=0))

        else:

            emb = discord.Embed()
        await ctx.respond(embed=emb, view=RPSButtons(game_mode=0))


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

    

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class TicTacToe(discord.ui.View):

    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


class TicTacToeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('?'))


bott = TicTacToeBot()

@bot.command()
async def tic(ctx: commands.Context):
    """Starts a tic-tac-toe game with yourself."""
    await ctx.send('Tic Tac Toe: X goes first', view=TicTacToe())



def setup(bot):
    bot.add_cog(Fun(bot))





