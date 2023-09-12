
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




class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def marryconnect(self):
        marry_connector = mysql.connector.connect(host='localhost', user='root', password=os.getenv("sql_passwort"), database='marry')
        return marry_connector

      
    @commands.command()
    async def marry(self ,ctx ,user:discord.User = None):

        white_color = 0xffffff

        connection_to_db_marry = self.marryconnect()

        marry_button = Button(label="Yes!", style=discord.ButtonStyle.blurple, custom_id="yes_button")
        marry_button1 = Button(label="No!", style=discord.ButtonStyle.blurple, custom_id="no_button")
        view = View(timeout=60)
        view.add_item(marry_button)
        view.add_item(marry_button1)
        random_marry = ""

        
        if user == None:
            emb = discord.Embed(title="You must specify a person you want to marry!", description="Please specify a person you want to marry! ", color=error_red)
            await ctx.send(embed=emb)

        else:

            user_ID = user.id 
            author_ID = ctx.author.id
            author_Name = ctx.author.name

            my_cursor = connection_to_db_marry.cursor()

            my_cursor.execute(f"SELECT * FROM marryinfos WHERE Person1_author_ID = {author_ID} or {user_ID} or Person2_ID = {user_ID} or {author_ID}")
            check_ID = my_cursor.fetchall()

            try:

                if check_ID:

                    for user_ids in check_ID:

                        user_id_check = str(user_ID)
                        author_id_check = str(author_ID)

                        if user.bot:
                            emb = discord.Embed(title="You can not marry a bot! ", description="If you want to marry someone just execute the command again and specify another person ", color=error_red)
                            await ctx.send(embed=emb)

                            if connection_to_db_marry.is_connected():
                                my_cursor.close()
                                connection_to_db_marry.close()

                            else:
                                pass
                    
                        elif user_id_check or author_id_check in user_ids:
                            emb = discord.Embed(title="You can not get married you are already married!" , description="If you want to marry someone else, you must first get `divorced`.", color=error_red)
                            await ctx.send(embed=emb)

                            if connection_to_db_marry.is_connected():
                                my_cursor.close()
                                connection_to_db_marry.close()

                            else:
                                pass

                        elif user == ctx.author:
                            emb = discord.Embed(title="You can't marry yourself!", description="Please specify another person you want to marry! ", color=error_red)
                            await ctx.send (embed=emb)

                            if connection_to_db_marry.is_connected():

                                my_cursor.close()
                                connection_to_db_marry.close()

                            else:
                                pass

                        else:
                            emb = discord.Embed(title="Do you want to marry this person?", description=f"**{ctx.author.mention} proposes to you {user.mention}** \ndo you wish to marry she/him? (You have 60 seconds)", color=white_color)
                            embed1 = await ctx.send(embed=emb, view=view)  

                else:
                    emb = discord.Embed(title="Do you want to marry this person?", description=f"**{ctx.author.mention} proposes to you {user.mention}** \ndo you wish to marry she/him? (You have 60 seconds)", color=white_color)
                    embed1 = await ctx.send(embed=emb, view=view) 


            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))


            finally:

                if connection_to_db_marry.is_connected():

                    my_cursor.close()
                    connection_to_db_marry.close()

                else:
                    pass


        async def button_callback(interaction: discord.InteractionResponse):

            connection_to_db_marry = self.marryconnect()

            my_cursor = connection_to_db_marry.cursor()

            if interaction.user == user:  
                
                if interaction.custom_id == "yes_button":
                    marry_person_name = interaction.user.name
                    marry_person_id = interaction.user.id
                    
                    emb = discord.Embed(title="Congratulations! ", description=f"{user.mention} has accepted the marriage proposal!", color=white_color)

                    try:
            
                        times = datetime.now().timestamp()
                        
                        sql_insert_query_marry = """ INSERT INTO marryinfos
                            (Person1_author_Name,  Person1_author_ID, Person2_Name, Person2_ID, Marrydate) VALUES (%s, %s, %s, %s, %s)"""
                        
                        Marry_values = (author_Name, author_ID, marry_person_name, marry_person_id, times)

                        my_cursor.execute(sql_insert_query_marry, Marry_values)
                        
                        connection_to_db_marry.commit()
                        print("Data inserted successfully into employee table using the prepared statement")

                    except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))

                    finally:

                        if connection_to_db_marry.is_connected():
                            my_cursor.close()
                            connection_to_db_marry.close()

                    emb.set_image(url=random_marry)
                    await interaction.response.defer()
                    await embed1.edit(embed=emb, view=None)

                elif interaction.custom_id == "no_button":

                    emb = discord.Embed(title="",description=f"What a pity {user.mention} has rejected the request! ", color=white_color)
                    await embed1.edi(embed=emb, view=None)

                    if connection_to_db_marry.is_connected():
                        my_cursor.close()
                        connection_to_db_marry.close()

            else: 
                
                emb = discord.Embed(title="You are not the person who received the marriage proposal! ", description="", color=error_red)
                await interaction.response.send_message(embed=emb, ephemeral=True)

        marry_button.callback = button_callback
        marry_button1.callback = button_callback 

        async def button_callback60sec_marry():

            emb_after = discord.Embed(title="Sorry you they are too slow ", description="If you want to try again use the command again", color=error_red)
            await embed1.edit(embed=emb_after, view=None)

        view.on_timeout = button_callback60sec_marry


    #for schleife anpasseb und dann noch das date anpassen
    @commands.command()
    async def divorce(self, ctx):
        white_color = 0xffffff

        divorce_button = Button(label="Yes!", style=discord.ButtonStyle.blurple, custom_id="yes_button")
        divorce_button1 = Button(label="No!", style=discord.ButtonStyle.blurple, custom_id="no_button")

        view = View(timeout=60)

        view.add_item(divorce_button)
        view.add_item(divorce_button1)

        author_ID = ctx.author.id
        
        connection_to_db_marry = self.marryconnect()

        my_cursor = connection_to_db_marry.cursor()

        divorce_check = (f"SELECT * FROM marryinfos WHERE Person1_author_ID = %s or Person2_ID = %s")
        divorce_check_values = (author_ID, author_ID)
        my_cursor.execute(divorce_check, divorce_check_values)

        check_ID_divorce = my_cursor.fetchall()

        id_auhthor = str(author_ID)

        if check_ID_divorce:

            for check_ids in check_ID_divorce:

                user_sql = check_ids[3]
                author_sql = check_ids[1]

                if id_auhthor in user_sql or author_sql:

                    emb = discord.Embed(title="Do you really want to get divorced?", description="If you no longer want to get divorced press the no button")
                    embed1 = await ctx.send(embed=emb, view=view)

                else:

                    not_marry_emb = discord.Embed(title="You can not get a divorce!", description="You are not married yet, if you want to get married, execute the command ?marry", color=error_red)
                    await ctx.send(embed=not_marry_emb)

        else:
            not_marry_emb = discord.Embed(title="You can not get a divorce!", description="You are not married yet, if you want to get married, execute the command ?marry", color=error_red)
            await ctx.send(embed=not_marry_emb)

        async def button_callback(interaction: discord.InteractionResponse):

            author_ID = ctx.author.id
            
            if interaction.user.id == author_ID:

                if interaction.custom_id == "yes_button":
                            

                    try:
                
                        my_cursor.execute(f""" DELETE FROM marryinfos WHERE Person1_author_ID = {author_ID} or Person2_ID = {author_ID}""")
                        connection_to_db_marry.commit()
                        print("Data successfully delited")


                    except mysql.connector.Error as error:
                        print("parameterized query failed {}".format(error))


                    finally:

                        if connection_to_db_marry.is_connected():

                            my_cursor.close()
                            connection_to_db_marry.close()

                        emb = discord.Embed(title="You have successfully divorced! ", description=f"If you want to marry again just use marry again ", color=discord.Colour.orange())

                        await interaction.response.defer()
                        await embed1.edit (embed=emb, view=None)

                elif interaction.custom_id == "no_button":

                    emb = discord.Embed(title="You have successfully broken off the divorce ",description=f"If you do want to get divorced just execute this command again! ", color=white_color)
                    await embed1.edit (embed=emb, view=None)

                    if connection_to_db_marry.is_connected():

                        my_cursor.close()
                        connection_to_db_marry.close()
                        
            else:     
                emb = discord.Embed(title="You are not the person who executed this command! ", description="", color=error_red)
                await interaction.response.send_message(embed=emb, ephemeral=True)

        divorce_button.callback = button_callback
        divorce_button1.callback = button_callback 

        async def button_callback60sec_divorce():

            emb_after = discord.Embed(title="Sorry you they are too slow ", description="If you want to try again use the command again", color=error_red)
            await embed1.edit(embed=emb_after, view=None)

        view.on_timeout = button_callback60sec_divorce


    # Geht immer noch nicht! datetime
    @commands.command()
    async def marryinfo(self, ctx):

        white_color = 0xffffff
        connection_to_db_marry = self.marryconnect()

        author_ID = ctx.author.id
        my_cursor = connection_to_db_marry.cursor()


        marry_info = (f"SELECT * FROM marryinfos WHERE (Person1_author_ID = %s or Person2_ID = %s)")
        marry_info_values = (author_ID, author_ID)
        my_cursor.execute(marry_info, marry_info_values)

        result = my_cursor.fetchall()

        author_id_check = str(author_ID)

        if result:

            for infos in result:

                author_id_sql = infos[1]
                user_id_sql = infos[3]
                marryday = infos[4]

                if author_id_check in author_id_sql or user_id_sql:

                    times = datetime.datetime.strftime(marryday, "%d.%m.%Y")

                    emb = discord.Embed(title="Marriage information", description=f"Here you can see everything about your wedding! ",color=white_color)
                    emb.add_field(name="Married persons", value=f"<@{author_id_sql}> and <@{user_id_sql}>")
                    emb.add_field(name="Wedding date", value=f"{times}")
                    await ctx.send(embed=emb)

                else:

                    fail_marry_info_emb = discord.Embed(title="You are not married!", description="If you want to execute this command, you have to get married to get married use ?merry and a person you want to marry", color=error_red)
                    await ctx.send(embed=fail_marry_info_emb)

                    if connection_to_db_marry.is_connected():

                        my_cursor.close()
                        connection_to_db_marry.close()
        else:
    
            fail_marry_info_emb = discord.Embed(title="You are not married!", description="If you want to execute this command, you have to get married to get married use ?merry and a person you want to marry", color=error_red)
            await ctx.send(embed=fail_marry_info_emb)
    


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


def setup(bot):
    bot.add_cog(Fun(bot))

