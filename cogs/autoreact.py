from utils import *
from sql_function import DatabaseCheck, DatabaseRemoveDatas, DatabaseUpdates

class AutoReaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        if message.guild:
            if message.guild.id == 865899808183287848:
                categorys = [996846958536835203, 927683692695027772, 998934946708205598, 930157270275350598, 
                             897544467266011177, 873622071484252200, 927668688239353926, 1084219817269149747,
                             927683692695027772, 996846958536835203, 1145775400983744522]
                
                booster_category = [1237029100430950499]
                if message.channel.category_id in categorys:
                    if len(message.attachments) > 0 or message.content.startswith("https://"):
                        await message.add_reaction("❤")
                
                if message.channel.category_id in booster_category:
                    if len(message.attachments) > 0 or message.content.startswith("https://"):
                        await message.add_reaction("💎")

        else:
            return
        
    
    @commands.slash_command(name = "set-auto-reaction")
    async def set_auto_reaction(self, ctx:discord.ApplicationContext, area:Option(), parameter:Option(), emoji:Option()):

        emb = discord.Embed(description=f"""## Einstellungs menü für das Auto reaction system
            {Emojis.dot_emoji} Wähle aus den unteren Buttons und Select menüs aus was du einstellen willst
            
            {Emojis.dot_emoji} Folgende einstellungen stehen zur verfügung:""")
        await ctx.respond(embed=emb)

def setup(bot):
    bot.add_cog(AutoReaction(bot))



class AutoReactionOnOffSwitch(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="on / off switch",
            style=discord.ButtonStyle.blurple,
            custom_id="on_off_switch_auto_react"
        )

    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            settings = DatabaseCheck.check_bot_settings(guild_id = interaction.guild.id)

            emb = discord.Embed(description=f"""## The auto reaction system is now {'activated' if settings[5] == 0 else 'deactivated'}.
                {Emojis.dot_emoji} {'Von jetzt an werden reactionen automatisch nach den vorher eingestellten parametern vergeben' if settings[5] == 0 else 'Ab jetzt werden keine neuen reactionen mehr automatisch hinzugefügt'}
                {Emojis.dot_emoji} Wenn du das system weiter einstellen willst kannst du den `set-auto-reaction` einfach erneut ausführen""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class SetAutoReactionArea(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    
    @discord.ui.select(
        placeholder = "Lege fest in welchen Bereich das auto reaction system reagieren soll!",
        min_values = 1,
        max_values = 1,
        custom_id = "set_auto_react_area",
        options = [
            discord.SelectOption(label="Channel", description="Wenn du einen channel festlegt werden alle nachrichten die in diesen channel gesendet werden mit einer reaction versehen", value="channel"),
            discord.SelectOption(label="Category", description="Wenn du eine Kategorie festlegst werden alle nachrichten die in die channel der Kategorei gesendet werden mit einer reaction versehen", value="category")
        ]
    )

    async def set_auto_reaction_area(self, select, interaction:discord.Interaction):

        emb = discord.Embed()



class SetAutoReactionParameter(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.select(
        placeholder = "Lege fest auf was das auto reaction system reagieren soll",
        min_values = 1,
        max_values = 1,
        custom_id = "set_auto_react_parameter",
        options = [
            discord.SelectOption(label="Links, Bilder & Videos"),
            discord.SelectOption(label="Text nachrichten"),
            discord.SelectOption(label="Individuell"),
            discord.SelectOption(label="Alle Inhalte")
        ]
    )

    async def set_auto_reaction_parameter(self, select, interaction:discord.Interaction):

        emb = discord.Embed()