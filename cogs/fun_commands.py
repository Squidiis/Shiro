
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
    def __init__(self, second_user, game_mode):
        self.second_user = second_user
        self.game_mode = game_mode
        super().__init__(timeout=None)
    
    @staticmethod
    def get_choice():

        choices = ["rock", "paper", "scissors"]
        choice = random.choice(choices)
        return choice
    
    @classmethod
    def rps_analysis(cls, choice_user:str, first_user:str, second_user = None, second_user_choice:str = None):

        choice_bot = cls.get_choice()

        win_emb = discord.Embed(title=f"{'Du hast gewonnen!' if second_user_choice == None else f'{first_user} hat gegen {second_user} gewonnen'}", 
            description=f"""{f'Du hast mit {choice_user} gegen den bot mit {choice_bot} gewonnen' if second_user_choice == None else f'{Emojis.dot_emoji} {first_user} hat mit {choice_user} gegen {second_user} mit {second_user_choice} gewonnen'}""", color=bot_colour)

        lose_emb = discord.Embed()

        tie_emb = discord.Embed()

        if second_user_choice == None:

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
            

    @discord.ui.button()
    async def rock_callback(self, interaction:discord.Interaction, button):

        emb = self.rps_analysis(choice_user="rock", first_user = interaction.user.name, second_user = self.second_user)
        await interaction.response.send_message(embed=emb, view=None)

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
        await ctx.respond(embed=emb)

    
    @commands.command()
    async def RPS(self, ctx, user:discord.User = None):

        view = View(timeout=10)

        author_ID = ctx.author.id
        
        button = Button(label="Scissors", style=discord.ButtonStyle.blurple, emoji="✂️", custom_id="scissors")
        button1 = Button(label="Rock", style=discord.ButtonStyle.blurple, emoji="🪨", custom_id="rock")
        button2 = Button(label="Paper", style=discord.ButtonStyle.blurple, emoji="🧻", custom_id="paper")
        Repeat_game = Button(label="Play again",style=discord.ButtonStyle.grey, emoji="🔄", custom_id="Paly_again")

        color1=discord.Colour.random()

        anime_Rock_Paper_Scissors_gif = ["https://c.tenor.com/NuJegnXdEmkAAAAC/dragon-ball-z-rock-paper-scissors.gif", "https://c.tenor.com/Ak6YQ5-DT7kAAAAd/megumin-konosuba.gif", 
            "https://c.tenor.com/KuaWztRBQ2UAAAAM/anime-takagi-san.gif", "https://c.tenor.com/fB3dSgnhM8YAAAAC/toaru-kagaku-no-railgun-t-a-certain-scientific-railgun-t.gif", 
            "https://c.tenor.com/jGc8F6thm10AAAAC/liella-sumire-heanna.gif"]

        random_anime_Rock_Paper_Scissors_gif = random.choice(anime_Rock_Paper_Scissors_gif)
        
        if user == None:

            botchoices = ["Rock", "Paper", "Scissors"]
            bot_choices = random.choice(botchoices)

            emb = discord.Embed(
                title="Rock Paper Scissors", description=f"{ctx.author.mention} Choose a button to play scissors stone paper\nIf you want to continue playing wait 10 seconds after the game is over", color=color1)
            emb.set_image(url=random_anime_Rock_Paper_Scissors_gif)

            async def button_callback(interaction: discord.InteractionResponse):
                
                if interaction.user.id == author_ID: 
                    
                    
                    Game = False
                    Gamechoice = ""
                    Stone_png = "https://cdn.discordapp.com/attachments/976935263802650674/997547263104663714/rock-g84470a236_640.png"
                    Paper_png = "https://cdn.discordapp.com/attachments/976935263802650674/997547262743949456/paper_drawing_tutorial-removebg-preview.png"
                    Scissors_png = "https://cdn.discordapp.com/attachments/976935263802650674/997547264086114464/Scissors-clipart-2-clipartix.png"
                    
                    
                    if interaction.custom_id == "scissors":
                        
                        view1=View()
                        Game = True
                        
                        if bot_choices == "Scissors" :
                            Gamechoice = "It is a Tie!"
                            emb = discord.Embed(title=Gamechoice, description="Wait 10 seconds for a new round", color=color1)
                            emb.set_image(url=Scissors_png)
                            choice_emb = await embed1.edit(embed=emb, view=None)
                            
                        if bot_choices == "Paper":
                            Gamechoice = "You Win!"
                            emb = discord.Embed(title=Gamechoice, description="Wait 10 seconds for a new round", color=color1)
                            emb.set_image(url=Paper_png)
                            choice_emb = await embed1.edit(embed=emb, view=None)
                        
                        if bot_choices == "Rock":
                            Gamechoice = "You lost!"
                            emb = discord.Embed(title=Gamechoice, description="Wait 10 seconds for a new round", color=color1)
                            emb.set_image(url=Stone_png)
                            choice_emb = await embed1.edit(embed=emb, view=None)
                        

                    elif interaction.custom_id == "rock":
                        
                        view1=View()
                        Game = True
                    
                        if bot_choices == "Rock" :
                            Gamechoice = "It is a Tie!"
                            emb = discord.Embed(title=Gamechoice, description="Wait 10 seconds for a new round", color=color1)
                            emb.set_image(url=Stone_png)
                            choice_emb = await embed1.edit(embed=emb, view=None)
                            
                        if bot_choices == "Paper":
                            Gamechoice = "You lost!"
                            emb = discord.Embed(title=Gamechoice, description="Wait 10 seconds for a new round", color=color1)
                            emb.set_image(url=Paper_png)
                            choice_emb = await embed1.edit(embed=emb, view=None)
                        
                        if bot_choices == "Scissors":
                            Gamechoice = "You Win!"
                            emb = discord.Embed(title=Gamechoice, description="Wait 10 seconds for a new round", color=color1)
                            emb.set_image(url=Scissors_png)
                            choice_emb = await embed1.edit(embed=emb, view=None)


                    elif interaction.custom_id == "paper":
                        
                        view1=View()
                        Game = True
                    
                        if bot_choices == "Paper" :
                            Gamechoice = "It is a Tie!"
                            emb = discord.Embed(title=Gamechoice, description="Wait 10 seconds for a new round", color=color1)
                            emb.set_image(url=Paper_png)
                            await embed1.edit(embed=emb, view=None)
                        
                        if bot_choices == "Rock":
                            Gamechoice = "You Win!"
                            emb = discord.Embed(title=Gamechoice, description="Wait 10 seconds for a new round", color=color1)
                            emb.set_image(url=Stone_png)
                            await embed1.edit(embed=emb, view=None) 
                        
                        if bot_choices == "Scissors":
                            Gamechoice = "You lost!"
                            emb = discord.Embed(title=Gamechoice, description="Wait 10 seconds for a new round", color=color1)
                            emb.set_image(url=Scissors_png)
                            await embed1.edit(embed=emb, view=None)
                    
                    emb1 = discord.Embed(title="Rock Paper Scissors", description=f"{ctx.author.mention} Do you want to play again?\nThis message is automatically deleted", color=color1)

                    if Game == True:
                        await interaction.response.defer()
                        view1.add_item(Repeat_game)
                        await asyncio.sleep(10)

                        await choice_emb.edit (embed=emb1, view=view1, delete_after=10)
                        
                    if interaction.custom_id == "Paly_again":

                        await interaction.response.edit_message(view=None, delete_after=5)        
                        await self.RPS(ctx)

                else:     

                    emb = discord.Embed(title="You are not the person who executed this command! ", description="", color=error_red)
                    await interaction.response.send_message(embed=emb, ephemeral=True)


            async def button_callback10sec():

                emb_after = discord.Embed(title="Sorry you they are too slow ", description="If you want to try again use the command again", color=color1)
                await embed1.edit(embed=emb_after, view=None)

            view.on_timeout = button_callback10sec

            button.callback = button_callback
            button1.callback = button_callback
            button2.callback = button_callback
            Repeat_game.callback = button_callback
            view.add_item(button)
            view.add_item(button1)
            view.add_item(button2)
            
            embed1 = await ctx.send(embed=emb, view=view)
            
        else:
            emb = discord.Embed(title="You can play this game only alone", description="If you want to play the game execute the command again", color=color1)
            await ctx.respond(embed=emb)
                     


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





