from discord.interactions import Interaction
from utils import discord, Option, commands, Emojis, no_permissions_emb, bot_colour
from typing import Union
from sql_function import DatabaseCheck, DatabaseRemoveDatas, DatabaseUpdates
from mod_tools import ModeratorCommands, formats


class AutoReaction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    '''
    
    '''
    def show_auto_reactions_all(guild_id:int):

        all_auto_reactions = DatabaseCheck.check_auto_reaction(guild_id = guild_id)

        if all_auto_reactions:

            final_reactions = []
            for _, channel, category, parameter, emoji in all_auto_reactions:

                final_reactions.append(f"{Emojis.dot_emoji} In {f'dem channel <#{channel}>' if channel != None else f'der Kategorie <#{category}> wird aud {parameter} mit dem emoji {emoji} reagiert'}")

            return "\n".join(final_reactions)

        else:

            return f"{Emojis.dot_emoji} No level roles have been set"
        

    '''
    
    '''
    def should_react(parameter:str, message:discord.Message):

        if parameter == "links, images and videos":
            return 'https://' in message.content and any(word in message.content for word in formats) and message.attachments or ModeratorCommands.contains_invite(content = message.content) == True
        elif parameter == "text messages":
            return 'https://' not in message.content and not any(word in message.content for word in formats) and not message.attachments or ModeratorCommands.contains_invite(content = message.content) == True
        elif parameter == "any message":
            return True
        return False


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if not message.guild:
            return

        check_settings = DatabaseCheck.check_bot_settings(guild_id = message.guild.id)

        if check_settings[5] == 0:
            return

        recations = DatabaseCheck.check_auto_reaction(guild_id=message.guild.id)

        if not recations:
            return

        for _, channel, category, parameter, emoji in recations:

            if (channel is not None and message.channel.id == channel) or (category is not None and message.channel.category_id == category):

                if self.should_react(parameter=parameter, message=message):

                    await message.add_reaction(emoji=emoji)
            
    
    @commands.slash_command(name = "set-auto-reaction")
    @commands.has_permissions(administrator = True)
    async def set_auto_reaction(self, ctx:discord.ApplicationContext):

        emb = discord.Embed(description=f"""## Einstellungs menü für das Auto reaction system
            {Emojis.dot_emoji} Wähle aus den unteren Buttons und Select menüs aus was du einstellen willst
            
            {Emojis.dot_emoji} Folgende einstellungen stehen zur verfügung:""")
        await ctx.respond(embed=emb, view = AutoReactionOnOffSwitch())


    @commands.slash_command(name = "add-auto-reaction")
    @commands.has_permissions(administrator = True)
    async def add_auto_reaction(self, ctx:discord.ApplicationContext, 
        area:Option(Union[discord.TextChannel, discord.CategoryChannel], required = True, description="Wähle aus in welchen channel oder Kategorie die auto-reaction erstellt werden soll!"), 
        parameter:Option(str, required = True, description="Wähle aus auf was diese auto-reaction reagieren soll!",
            choices = ["links, images and videos", "text messages", "any message"]), 
        emoji:Option(str, required = True, description="Gebe hier den emoji ein denn du für diese auto-reaction festlegen möchtest (Einfach emoji einfügen dieser wird automatisch konventiert)")):

        check_reaction = DatabaseCheck.check_auto_reaction(
            guild_id=ctx.guild.id, 
            channel_id=area.id if isinstance(area, discord.TextChannel) else None,
            category_id=None if isinstance(area, discord.TextChannel) else area.id,
            parameter=parameter,
            emoji=emoji
            )
        
        if check_reaction:

            emb = discord.Embed(description=f"""## Es wurde bereits eine auto-reaction role festgelegt die genau diese parameter besitzt
                {Emojis.dot_emoji} Es giebt bereits eine auto-reaction die für {f'den channel {area.id}' if isinstance(area, discord.TextChannel) else f'die Kategorie {area.id}'} festgelegt ist
                {Emojis.dot_emoji} Diese reagiert bereits auch auf {parameter} mit dem emoji {emoji}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            await DatabaseUpdates.manage_auto_reaction(guild_id = ctx.guild.id, channel_id = area.id, parameter = parameter, emoji = emoji, operation = "add")

            emb = discord.Embed(description=f"""## Eine neue auto-reaction wurde festgelegt
                {Emojis.dot_emoji} Die neue auto-reaction reagiert in {'dem channel' if isinstance(area, discord.TextChannel) else 'der Kategorie'} {area.mention}
                {Emojis.dot_emoji} Als parameter wurde festgelegt das die auto reaction auf {parameter} reagieren soll
                {Emojis.dot_emoji} Als Emoji wurde {emoji} festgelgt""", color=bot_colour)
            await ctx.respond(embed=emb)

        
    @commands.slash_command(name = "remove-auto-reaction")
    @commands.has_permissions(administrator = True)
    async def remove_auto_reactions(self, ctx:discord.ApplicationContext, 
        area:Option(Union[discord.TextChannel, discord.CategoryChannel], required = True, description="Wähle aus welchen channel oder Kategorie du vom auto-reaction system streichen willst!")):

        check_auto_reaction = DatabaseCheck.check_auto_reaction(guild_id = ctx.guild.id, channel_id = area.id if isinstance(area, discord.TextChannel) else None, category_id = None if isinstance(area, discord.TextChannel) else area.id)

        if check_auto_reaction:

            emb = discord.Embed()

        else:

            emb = discord.Embed()


    @commands.slash_command(name = "show-auto-reactions")
    @commands.has_permissions(administrator = True)
    async def show_auto_reactions(self, ctx:discord.ApplicationContext):
        
        all_auto_reactions = DatabaseCheck.check_auto_reaction(guild_id = ctx.guild.id)

        if all_auto_reactions:

            emb = discord.Embed(description=f"""## Aktuelle Auto-reactions
                {Emojis.dot_emoji} Hier siehst du alle auto-reactions die für dem server {ctx.guild.name} festgelegt wurden
                
                {self.show_auto_reactions_all(guild_id = ctx.guild.id)}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "reset-auto-reactions")
    @commands.has_permissions(administrator = True)
    async def reset_auto_reactions(self, ctx:discord.ApplicationContext):

        all_auto_reactions = DatabaseCheck.check_auto_reaction(guild_id = ctx.guild.id)

        if all_auto_reactions:

            DatabaseRemoveDatas.remove_auto_reactions(guild_id = ctx.guild.id)

            emb = discord.Embed(description=f"""## Auto-reactions wurden zurück gesetzt
                {Emojis.dot_emoji} Alle auto-reactions wurden gelöscht
                {Emojis.dot_emoji} Wenn du neue auto-reactions festlegen möchtest kannst du den `add-auto-reaction` command dafür nutzen""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(description=f"""## Keine einträge gefunden
                {Emojis.dot_emoji} Es konnten keine auto-reactions gelöscht werden da keine festgelegt worden sind
                {Emojis.dot_emoji} Wenn du welche festlegen möchtest kannst du den `add-auto-reaction` command dafür verwenden""", color=bot_colour)
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
