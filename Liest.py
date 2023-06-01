
from Import_file import *
from typing import List

class Genderbutton_Male(discord.ui.Button):
    def __init__(self):
        super().__init__(
                label="Male",  
                style=discord.enums.ButtonStyle.gray,  
                custom_id="Male")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user

        if interaction.custom_id == "Male":
            genderrole_id_male = 910623615697961011
            malerole = interaction.guild.get_role(genderrole_id_male)
               
            if malerole not in user.roles:
                await user.add_roles(malerole)
                emb = discord.Embed(title=f"You get the Male role", 
                description="if you don't want the roll anymore just press the button again!", color=0x41bdfc)
                await interaction.followup.send(embed=emb, ephemeral=True)

            else:
                await user.remove_roles(malerole)
                emb = discord.Embed(title="You Removed the Male role", 
                description="if you want the <@&910623615697961011> back click the button again!", color=0x41bdfc)
                await interaction.followup.send(embed=emb, ephemeral=True)

class Genderbutton_Female(discord.ui.Button):
    def __init__(self):
        super().__init__(
                label="Female",  
                style=discord.enums.ButtonStyle.gray,  
                custom_id="Female")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user

        if interaction.custom_id == "Female":
                genderrole_id_female = 910624095509545051
                femalerole = interaction.guild.get_role(genderrole_id_female)

                if femalerole not in user.roles:
                    await user.add_roles(femalerole)
                    emb = discord.Embed(title=f"You get the Female role", 
                    description="if you don't want the roll anymore just press the button again!", color=0xe752dc)
                    await interaction.followup.send(embed=emb, ephemeral=True)

                else:
                    await user.remove_roles(femalerole)
                    emb = discord.Embed(title="You Removed the Female role", 
                    description="if you want the <@&910624095509545051> back click the button again!", color=0xe752dc)
                    await interaction.followup.send(embed=emb, ephemeral=True)

class Genderbutton_Divers(discord.ui.Button):
    def __init__(self):
        super().__init__(
                label="Divers",  
                style=discord.enums.ButtonStyle.gray,  
                custom_id="Divers")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user = interaction.user

        if interaction.custom_id == "Divers":
                genderrole_id_divers = 926632004664066048
                diversrole = interaction.guild.get_role(genderrole_id_divers)

                if  diversrole not in user.roles:
                    await user.add_roles( diversrole)
                    emb = discord.Embed(title="You get the Divers role", 
                    description="if you don't want the roll anymore just press the button again!", color=0xe4e6e3)
                    await interaction.followup.send(embed=emb, ephemeral=True)

                else:
                    await user.remove_roles(diversrole)
                    emb = discord.Embed(title="You Removed the Divers role", 
                    description="if you want the <@&926632004664066048> back click the button again!", color=0xe4e6e3)
                    await interaction.followup.send(embed=emb, ephemeral=True)


       
class DropdownColours(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
     
    @discord.ui.select(placeholder="Select your favorite color...", min_values=1, max_values=1, custom_id="interaction:DropdownColours", options = [

        discord.SelectOption(label="Red", description="Your favorite color is red", emoji="🟥", value="Red"),

        discord.SelectOption(label="Green", description="Your favorite color is green", emoji="🟩", value="Green"),

        discord.SelectOption(label="Blue", description="Your favorite color is blue", emoji="🟦", value="Blue"),

        discord.SelectOption(label="Orange", description="Your favorite color is orange", emoji="🟧", value="Orange"),

        discord.SelectOption(label="Yellow", description="Your favorite color is yellow", emoji="🟨", value="Yellow"),

        discord.SelectOption(label="Purple", description="Your favorite color is purple", emoji="🟪", value="Purple"),

        discord.SelectOption(label="Remove color", description="Remove your favorite color", emoji="🗑️", value="Remove")
        ])
        
    
    async def callback(self, select, interaction: discord.Interaction): 

        RED = 926440250534924328 #Rollen
        GREEN = 926441508893233212
        BLUE = 925791399151034448
        ORANGE = 926442658736517120
        YELLOW = 926435332856115210
        Purple = 1005055168523534346
       

        users = interaction.user
        red_role = interaction.guild.get_role(RED)
        green_role = interaction.guild.get_role(GREEN)  
        blue_role = interaction.guild.get_role(BLUE)
        orange_role = interaction.guild.get_role(ORANGE)
        yellow_role = interaction.guild.get_role(YELLOW)
        purple_role = interaction.guild.get_role(Purple)
        COLOURS = [RED, BLUE, GREEN, ORANGE, YELLOW, Purple]
        

        if select.values[0] == "Red":
            if red_role not in users.roles:
                
                await users.add_roles(red_role)
                emb = discord.Embed(title=f"You get your favorit color role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.red())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            else:
                youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.red())
                await interaction.response.send_message(embed=youhaveemb, ephemeral=True)

        if select.values[0] == "Green":
            if green_role not in users.roles:
                await users.add_roles(green_role)
                
                emb = discord.Embed(title=f"You get your favorit color role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.green())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            else:
                youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.red())
                await interaction.response.send_message(embed=youhaveemb, ephemeral=True)
                
        if select.values[0] == "Blue":
            if blue_role not in users.roles:
                await users.add_roles(blue_role)
                emb = discord.Embed(title=f"You get your favorit color role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            else:
                youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.red())
                await interaction.response.send_message(embed=youhaveemb, ephemeral=True)
                
        if select.values[0] == "Orange":
            if orange_role not in users.roles:
                await users.add_roles(orange_role)
                emb = discord.Embed(title=f"You get your favorit color role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.orange())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            else:
                youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.red())
                await interaction.response.send_message(embed=youhaveemb, ephemeral=True)
            
        if select.values[0] == "Yellow":
            if yellow_role not in users.roles:
                await users.add_roles(yellow_role)
                emb = discord.Embed(title=f"You get your favorit color role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.yellow())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            else:
                youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.red())
                await interaction.response.send_message(embed=youhaveemb, ephemeral=True)


        if select.values[0] == "Purple":
            if purple_role not in users.roles:
                
                await users.add_roles(purple_role)
                emb = discord.Embed(title=f"You get your favorit color role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.purple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            else:
                    youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.red())
                    await interaction.response.send_message(embed=youhaveemb, ephemeral=True)

        if select.values[0] == "Remove":
            for i in COLOURS:
                rolle = interaction.guild.get_role(i)
                await interaction.user.remove_roles(rolle)
            emb = discord.Embed(title="all colors rolls have been removed", description="If you want the colour rolls back, select your favorit color roll", color=discord.Colour.random())
            await interaction.response.send_message(embed=emb, ephemeral=True)



class DropdownHoppys(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
     
    @discord.ui.select(placeholder="Select your hobby...", min_values=1, max_values=1, custom_id="interaction:DropdownHobbys", options = [

        discord.SelectOption(label="Computer stuff", description="Your hobby is Computer stuff", emoji="🖥️", value="Computer_stuff"),

        discord.SelectOption(label="Travel", description="Your hobby is traveling", emoji="✈️", value="Travel"),

        discord.SelectOption(label="Art", description="Your hobby is art", emoji="🎨", value="Art"),

        discord.SelectOption(label="Music", description="Your hobby is music", emoji="🎶", value="Music"),

        discord.SelectOption(label="Cooking", description="Your hobby is cooking", emoji="🍳", value="Cooking"),

        discord.SelectOption(label="Sport", description="Your hobby is sport", emoji="👟", value="Sport"),

        discord.SelectOption(label="Programming", description="Your hobby is programming", emoji="🧑‍💻", value="Programming"),

        discord.SelectOption(label="Other hobbies", description="Your hobby is something else", emoji="🧑‍💻", value="Other_hobbies"),

        discord.SelectOption(label="Remove Hobbys", description="Remove your Hobbys", emoji="🗑️", value="Remove")
        ])
        
    
    async def callback(self, select, interaction: discord.Interaction): 
        await interaction.response.defer()
        COMPUTER_STUFF = 946127059174957101
        TRAVEL = 947120945678671932
        ART = 947120941387874324
        MUSIC = 947122093588357140
        COOKING = 947122625568718908
        SPORTS = 947123873776820256
        PROGRAMMING = 947124182620180491
        OTHER_HOBBIES = 947584021439873064

        users = interaction.user
        cumputer_stuff_role = interaction.guild.get_role(COMPUTER_STUFF)
        travel_role = interaction.guild.get_role(TRAVEL)  
        art_role = interaction.guild.get_role(ART)
        music_role = interaction.guild.get_role(MUSIC)
        cooking_role = interaction.guild.get_role(COOKING)
        sports_role = interaction.guild.get_role(SPORTS)
        programming_role = interaction.guild.get_role(PROGRAMMING)
        other_hobbies_role = interaction.guild.get_role(OTHER_HOBBIES)
        HOBBYS = [COMPUTER_STUFF, TRAVEL, ART, MUSIC, COOKING, SPORTS, PROGRAMMING]
        

        if select.values[0] == "Computer_stuff":
            if cumputer_stuff_role not in users.roles:
                
                await users.add_roles(cumputer_stuff_role)
                emb = discord.Embed(title=f"You get your hobby role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            if cumputer_stuff_role in users.roles:
                    youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.blurple())
                    await interaction.response.send_message(embed=youhaveemb, ephemeral=True)

        if select.values[0] == "Travel":
            if travel_role not in users.roles:
                await users.add_roles(travel_role)
                
                emb = discord.Embed(title=f"You get your hobby role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            if travel_role in users.roles:
                youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=youhaveemb, ephemeral=True)
                
        if select.values[0] == "Art":
            if art_role not in users.roles:
                await users.add_roles(art_role)
                emb = discord.Embed(title=f"You get your hobby role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            if art_role in users.roles:
                youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=youhaveemb, ephemeral=True)
                
        if select.values[0] == "Music":
            if music_role not in users.roles:
                await users.add_roles(music_role)
                emb = discord.Embed(title=f"You get your hobby role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            if music_role in users.roles:
                youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=youhaveemb, ephemeral=True)
            
        if select.values[0] == "Cooking":
            if cooking_role not in users.roles:
                await users.add_roles(cooking_role)
                emb = discord.Embed(title=f"You get your hobby role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            if cooking_role in users.roles:
                youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=youhaveemb, ephemeral=True)

        if select.values[0] == "Sport":
            if sports_role not in users.roles:
                
                await users.add_roles(sports_role)
                emb = discord.Embed(title=f"You get your hobby role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            if sports_role in users.roles:
                    youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.blurple())
                    await interaction.response.send_message(embed=youhaveemb, ephemeral=True)

        if select.values[0] == "Programming":
            if programming_role not in users.roles:
                
                await users.add_roles(programming_role)
                emb = discord.Embed(title=f"You get your hobby role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            if programming_role in users.roles:
                    youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.blurple())
                    await interaction.response.send_message(embed=youhaveemb, ephemeral=True)

        if select.values[0] == "Other_hobbies":
            if other_hobbies_role not in users.roles:
                
                await users.add_roles(other_hobbies_role)
                emb = discord.Embed(title=f"You get your hobby role", description="if you don't want the roll anymore just press the Remove buttom!", color=discord.Colour.blurple())
                await interaction.response.send_message(embed=emb, ephemeral=True)
                
            if programming_role in users.roles:
                    youhaveemb = discord.Embed(title="You have already received the role", description="If you no longer want this role select the remove button", color=discord.Colour.blurple())
                    await interaction.response.send_message(embed=youhaveemb, ephemeral=True)

        if select.values[0] == "Remove":
            for i in HOBBYS:
                rolle = interaction.guild.get_role(i)
                await interaction.user.remove_roles(rolle)
            emb = discord.Embed(title="all hobby rolls have been removed", description="If you want the hobby rolls back, select your hobby", color=discord.Colour.blurple())
            await interaction.response.send_message(embed=emb, ephemeral=True)


async def status_task():
    while True:
        await bot.change_presence(activity=discord.Game('?help to see all commands'), status=discord.Status.online)
        await asyncio.sleep(15)
        await bot.change_presence(activity=discord.Game('Funpark.net'), status=discord.Status.online)
        await asyncio.sleep(15)

class SelfRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def role_colours(self, ctx):
        emb = discord.Embed(title="Colors roll", description=
            """
            Here you can pick out your favorite color
            <@&926440250534924328> 
            <@&926441508893233212> 
            <@&926442658736517120> 
            <@&926435332856115210> 
            <@&925791399151034448> 
            <@&1005055168523534346>
            """, color=0x1dc9c9)
        emb.set_image(url="https://cdn.discordapp.com/attachments/1000427727691718806/1005057006081679382/unknown.png")
        
        dropdowns=DropdownColours()
        
        await ctx.send(embed=emb, view=dropdowns)
        
        
    @commands.command()
    async def role_gender(self, ctx):
        view = View(timeout=None)
        view.add_item(Genderbutton_Male())
        view.add_item(Genderbutton_Female())
        view.add_item(Genderbutton_Divers())

        emb = discord.Embed(
            title="What is your gender?",
            description=""" 
            Select your gender by clicking on the button 
            <@&910623615697961011>
            <@&910624095509545051>
            <@&926632004664066048>"""
            , color=0xab19cf)

        await ctx.send(embed=emb, view=view)

    @commands.command()
    async def role_hobby(self, ctx):
        emb = discord.Embed()

bot.add_cog(SelfRoles(bot))

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