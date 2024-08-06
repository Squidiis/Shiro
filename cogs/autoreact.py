from utils import discord, Option, commands, Emojis, no_permissions_emb, bot_colour
from typing import Union
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
    async def set_auto_reaction(self, ctx:discord.ApplicationContext):

        emb = discord.Embed(description=f"""## Einstellungs menü für das Auto reaction system
            {Emojis.dot_emoji} Wähle aus den unteren Buttons und Select menüs aus was du einstellen willst
            
            {Emojis.dot_emoji} Folgende einstellungen stehen zur verfügung:""")
        await ctx.respond(embed=emb, view = AutoReactionOnOffSwitch())


    @commands.slash_command(name = "add-auto-reaction")
    async def add_auto_reaction(self, ctx:discord.ApplicationContext, 
        area:Option(Union[discord.TextChannel, discord.CategoryChannel], required = True, description="Wähle aus in welchen channel oder Kategorie die auto-reaction erstellt werden soll!"), 
        parameter:Option(str, required = True, description="Wähle aus auf was diese auto-reaction reagieren soll!",
            choices = ["links, images and videos", "specific content only", "any message"]), 
        emoji:Option(str, required = True, description="Gebe hier den emoji ein denn du für diese auto-reaction festlegen möchtest (Wähle dazu einen gewünschten eoji aus und setzte einne \ davor)")):

        check_reaction = DatabaseCheck.check_auto_reaction(
            guild_id=ctx.guild.id, 
            channel_id=area.id if isinstance(area, discord.TextChannel) else None,
            category_id=None if isinstance(area, discord.TextChannel) else area.id,
            parameter=parameter,
            emoji=emoji
            )
        
        if check_reaction:

            emb = discord.Embed()

        else:

            if parameter == "specific content only":

                emb = discord.Embed(description=f"""""")

            else:

                await DatabaseUpdates.manage_auto_reaction(guild_id = ctx.guild.id, channel_id = area.id, parameter = parameter, emoji = emoji, operation = "add")

                emb = discord.Embed(description=f"""## Eine neue auto-reaction wurde festgelegt
                    {Emojis.dot_emoji} Die neue auto-reaction reagiert in {'dem channel' if isinstance(area, discord.TextChannel) else 'der Kategorie'} {area.mention}
                    {Emojis.dot_emoji} Als parameter wurde festgelegt das die auto reaction auf {parameter} reagieren soll
                    {Emojis.dot_emoji} Als Emoji wurde {emoji} festgelgt""", color=bot_colour)
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



class ParameterModalAutoReaction(discord.ui.Modal):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(title="Lege die spezifischen reaction wörter fest")
        self.add_item(discord.ui.InputText(label="Schreibe hier die Wörter rein auf der doe auto-raction reagieren soll (Sind es mehre Wörter trenne dise mit einen komma)", style=discord.InputTextStyle.long))

    async def callback(self, interaction:discord.Interaction):

        check = DatabaseCheck.check_auto_reaction(guild_id = interaction.guild.id, parameter = "placeholder")

        if check:

            emb = discord.Embed(description=f"""## Die auto-reaction parameter wurden festgelegt
                {Emojis.dot_emoji} Ab jetzt reagiert die auto reaction auf die folgenden schlag wörter {self.children[0].value}
                {Emojis.dot_emoji} Auf diese Wörter wird ab jetzt mit dem emoji {check[4]} reagiert""", color=bot_colour)
            await interaction.response.send_message(embeds=[emb], view=None)

        else:

            emb = discord.Embed(description=f"""## Eintrag konnte nicht gefunden
                {Emojis.dot_emoji} Ein fehler ist aufgetreten es konnte kein eintrag zu deiner jetzigen aktion zu geordnet werden
                {Emojis.dot_emoji} Versuche sie es erneut falls dieser fehler bestehen bleibt konntaktieren sie den support https://discord.gg/3sZhp3q6bD""", color=bot_colour)
            await interaction.response.send_message(embed=emb)