from utils import *
from sql_function import *
from discord.ext import tasks

class InviteSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    
    #@commands.Cog.listener()
    #async def on_member_join(member):
    #    if not member.bot:
    #        guild = member.guild
    #        invites = await guild.invites()
            #for invite in invites:
                #if invite.uses > 0:
                    # Speichere die Einladung in der Datenbank
                    # cursor.execute("INSERT INTO invites (inviter_id, invitee_id) VALUES (%s, %s)", (invite.inviter.id, member.id))
                    # db.commit()

    @commands.slash_command(name = "show-invites")
    async def show_invites(self, ctx:discord.ApplicationContext, user:Option(discord.Member)):

        if user is None:

            total_invites = 0
            for invite in await ctx.guild.invites():
                if invite.inviter == ctx.author:
                    total_invites += invite.uses

            emb = discord.Embed(description=f"""## Anzahl an eingeladenen Mitgliedern {ctx.author.name}
                {Emojis.dot_emoji} {f'Du hast {total_invites} user' if total_invites != 0 else 'Du hast noch keine anderen user'} auf den Server {ctx.guild.name} eingeladen.
                {Emojis.help_emoji} Die einladungen werden nur dann gezählt wenn du den einladungs link erstellt hast!""", color=bot_colour)
            
            await ctx.respond(embed=emb)
        else:

            total_invites = 0
            for invite in await ctx.guild.invites():
                if invite.inviter == user:
                    total_invites += invite.uses
            await ctx.respond(f"{user.mention} hat {total_invites} Mitglied{'er' if total_invites != 1 else ''} auf den Server eingeladen.")


    @commands.Cog.listener()
    async def on_member_join(member):

        print(member)
    

    @commands.slash_command(name = "set-message-leaderbourd", description = "Set the message leaderbourd system!")
    async def set_message_leaderbourd(self, ctx:discord.ApplicationContext):

        emb = discord.Embed(description=f"""## Set the message leaderbourd
            {Emojis.dot_emoji} Mit den unteren Select menü kannst du einen channel festlegen in dem das leaderbourd gesendet werden soll
            {Emojis.dot_emoji} Danach kannst du auch ein Intervall festlegen in welchen Zeit abständen das leaderbourd aktualisiert werden soll
            {Emojis.help_emoji} Das leaderbourd wird beim aktualisieren editiert daher solltest du sicher stellen das kein anderer in den von dir angegeben channel schreiben kann""", color=bot_colour)
        await ctx.respond(embed=emb, view=SetLeaderbourdChannel())


    @tasks.loop(hours=24)  # Intervall von 24 Stunden (einmal täglich)
    async def edit_leaderbourd(self, bot):

        leaderboard_settings = DatabaseCheck.check_leaderbourd_settings(guild_id = bot.guild.id)

        message_ids = {
            "1_days_old": leaderboard_settings[2],
            "1_week_old": leaderboard_settings[3],
            "1_month_old": leaderboard_settings[4]
        }

        if leaderboard_settings[1] == 1:

            try:
            
                current_date = datetime.utcnow()

                for message_name, message_id in message_ids.items():

                    message = await bot.guild.fetch_message(message_id)

                    if current_date - message.created_at > timedelta(days=1) and message_name == "1_days_old":
                        await bot.edit_message("Diese Nachricht ist älter als 3 Tage.")
                    elif current_date - message.created_at > timedelta(weeks=1) and message_name == "1_week_old":
                        await bot.response.edit_message("Diese Nachricht ist älter als 1 Woche.")
                    elif current_date - message.created_at > timedelta(days=30) and message_name == "1_month_old":
                        await bot.response.edit_message("Diese Nachricht ist älter als 1 Monat.")

            except Exception as e:
                print(f"Ein Fehler ist aufgetreten: {e}")

def setup(bot):
    bot.add_cog(InviteSystem(bot))



class SetLeaderbourdChannel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "message leaderbourd system"))

    @discord.ui.channel_select(
        placeholder = "Choose a channel that you want to set as the leaderbourd channel!",
        min_values = 1,
        max_values = 1,
        custom_id = "leaderbourd_channel_select",
        channel_types = [
            discord.ChannelType.text, 
            discord.ChannelType.forum, 
            discord.ChannelType.news
        ]
    )

    async def set_leaderbourd_channel(self, select, interaction:discord.Interaction):
        
        settings = DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)

        if settings:

            if settings[5] == select.values[0].id:

                emb = discord.Embed(description=f"""## Dieser channel wurde bereits als leaderbourd channel festgelegt
                    {Emojis.dot_emoji} Dieser channel wurde bereits für das message leaderbourd festgelegt
                    {Emojis.dot_emoji} Möchstest du mit dem einstellen des message leaderbourds vortfaren oder einen anderen channel festlegen?""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=SameChannelButtons())

            else:
                
                emb = discord.Embed(description=f""" ## Es wurde bereits ein channel für das leaderbourd festgelegt
                    {Emojis.dot_emoji} Möchstest du diesen überschreibe?
                    {Emojis.dot_emoji} aktuell ist <#{settings[5]}> als channel für das leaderbourd festlegegt""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=OverwriteChannel())

                DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, settings = "channel", channel_id = select.values[0].id)

        else:

            DatabaseUpdates.create_leaderbourd_settings(guild_id = interaction.guild.id, settings = "create", channel_id = select.values[0].id)

        emb = discord.Embed(description=f"""## Channel für das Leaderbourd wurde festgelegt
            {Emojis.dot_emoji} Ab sofort wird in {select.values[0].mention} das liederbourd gesendet
            {GetEmbed.get_embed(embed_index=3)}
            """, color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())


class SetLeaderbourd(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "message leaderbourd system"))

    @discord.ui.select(
        placeholder = "Select the intervals at which the activities should be displayed!",
        min_values = 1,
        max_values = 3,
        custom_id = "set_leaderbourd",
        options = [
            discord.SelectOption(label="Update daily", description="Das Leaderbourd wird jeden Tag aktualisiert", value="daily"),
            discord.SelectOption(label="Update weekly", description="Das Leaderbourd wird jede Woche aktualisiert", value="weekly"),
            discord.SelectOption(label="Update monthly", description="Das Leaderbourd wird jedes Monat aktualisiert", value="monthly")
        ]
    )
    
    async def set_leaderbourd_select(self, select, interaction:discord.Interaction):

        text_dict = {
            "daily":"einen Tag",
            "weekly":"eine Woche",
            "monthly":"ein Monat"
        }

        channel_id = DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)[5]

        option_list, check_list = [], []
        for i in select.values:
            option_list.append(f"{Emojis.dot_emoji} {i} aktualisierung\n")
            check_list.append(i)

            if i != None:

                emb = discord.Embed(
                    description=f"""## Die anzahl der nachrichten wird für {text_dict[i]} gespeichert
                        {Emojis.dot_emoji} Wenn die Zeit dann um ist wird diese Nachricht zu einen leaderbourd editiert die die user anzeigt die am meisten Nachrichten geschrieben haben""", color=bot_colour)

                channel = bot.get_channel(channel_id)
                message = await channel.send(embed=emb)
                DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, settings = i, message_id = message.id)

        for i in [value for value in ["daily", "weekly", "monthly"] if value not in check_list]:

            DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, back_to_none = i)

        emb = discord.Embed(description=f"""## Intervall wurde festgelegt
            {Emojis.dot_emoji} {'Die folgenden leaderbourd optionen wurden ausgewählt' if len(select.values) != 1 else 'Die foldende leaderbourd option wurde ausgewählt'}:
                {"".join(option_list)}
            {Emojis.dot_emoji} {'Das leaderbourd wird' if len(select.values) == 1 else 'Die leaderbourds werden'} in <#{DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)[5]}> gesendet
            {Emojis.help_emoji} Die Leaderbourds werden erst nach dem ersten intervall zu den volständigen Leaderbourds""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)


class SameChannelButtons(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "message leaderbourd system"))

    @discord.ui.button(
        label="Continue with the settings", 
        style=discord.ButtonStyle.blurple, 
        custom_id="continue_settings"
    )

    async def continue_set_leaderbourd(self, button, interaction:discord.Interaction):

        emb = discord.Embed(description=f"""## Weitere einstellung des leaderbourds
            {Emojis.dot_emoji} Der leaderbourd channel wird beibehalten
            {GetEmbed.get_embed(embed_index=3)}""", color=bot_colour)
        await interaction.response.edit_message(embed=emb)


    @discord.ui.button(
        label="set new channel",
        style=discord.ButtonStyle.blurple,
        custom_id="set_new_channel"
    )

    async def set_new_channel(self, button, interaction:discord.Interaction):

        emb = discord.Embed(description=f"""## Wähle einen neuen channel
            {Emojis.dot_emoji} Wähle aus den unteren select menü einen neuen channel aus in den das message leaderbourd gesendet werden soll
            {Emojis.dot_emoji} Aktuell ist der channel <#{DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)[5]}> als leaderbourd channel festgelegt""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=SetLeaderbourdChannel())


class OverwriteChannel(discord.ui.View):

    def __init__(
            self,
            channel_id = None
        ):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.add_item(CancelButton(system = "message leaderbourd system"))

    @discord.ui.button(
        label="overwrite channel",
        style=discord.ButtonStyle.blurple,
        custom_id="overwrite_channel"
    )

    async def overwrite_channel(self, button, interaction:discord.Interaction):
        
        if self.channel_id == None:

            emb = discord.Embed(description=f"""## Ein fehler ist aufgetreten
                {Emojis.dot_emoji} Der channel konnte nicht überschrieben werden das passiert wenn die option zu lange unbeantwortet bleibt oder wenn ich die verbindung verliere
                {Emojis.dot_emoji} Wenn du das leaderbourd weiter einstellen möchtest muss du nur den command `/set-message-leaderbourd` neu ausführen""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            emb = discord.Embed(description=f"""## Leaderbourd channel wurde überschrieben
                {Emojis.dot_emoji} Ab sofort ist <#{self.channel_id}> der neue leaderbourd channel
                {Emojis.dot_emoji} Das leaderbourd wird aus dem alten leaderbourd channel gelöscht
                {Emojis.dot_emoji} Mit den unseren select menü kannst du mit dem einstellen fortfahren
                {Emojis.help_emoji} Du kannst mehrere intervalle auswählen auch ist jedes intervall ein einzelnes leaderbourd""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())
        
    @discord.ui.button()
    async def keep_channel(self, button, interaction:discord.Interaction):

        emb = discord.Embed(description=f"""## Channel wird beibehalten
            {Emojis.dot_emoji} Der channel <#{DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)[5]}> wird als leaderbourd channel beibehalten
            {Emojis.dot_emoji} Mit den unseren select menü kannst du mit dem einstellen fortfahren
            {Emojis.help_emoji} Du kannst mehrere intervalle auswählen auch ist jedes intervall ein einzelnes leaderbourd""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())

