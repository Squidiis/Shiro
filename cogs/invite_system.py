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
    

    @commands.slash_command("set-message-leaderbourd")
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

    @discord.ui.channel_select(
        placeholder = "Choose a channel that you want to set as the leaderbourd channel!",
        min_values = 1,
        max_values = 1,
        custom_id = "leaderbourd_channel_select",
        channel_types = [
            discord.ChannelType.text, 
            discord.ChannelType.forum, 
            discord.ChannelType.news
        ])
    async def set_leaderbourd_channel(self, select, interaction:discord.Interaction):
        
        DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, settings = "channel", channel_id = select.values[0].id)

        emb = discord.Embed(description=f"""## Channel für das Leaderbourd wurde festgelegt
            {Emojis.dot_emoji} Ab sofort wird in {select.value[0].mention} das liederbourd gesendet
            {Emojis.dot_emoji} Mit dem unteren Dropdown menü kannst du auswählen welches Leaderbourd in diesen channel gesendet werden soll
            {Emojis.dot_emoji} Die Leaderbourd unterscheiden sich in der laufzeit nach wie viel Zeit die stats aktualisiert werden
            {Emojis.help_emoji} Es können auch mehrere intervalle ausgewählt werden dann werden mehrere Verschiedene Leaderbourds gesendet""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())

        DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, settings = "channel", channel_id = select.values[0].id)


class SetLeaderbourd(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder = "Wähle aus in welchen intervallen die aktivitäten angezeigt werden sollen",
        min_values = 1,
        max_values = 3,
        custom_id = "set_leaderbourd",
        options = [
            discord.SelectOption(label="Taglich aktualisieren", description="Das Leaderbourd wird jeden Tag aktualisiert", value="daily"),
            discord.SelectOption(label="Wöchentlich aktualisieren", default="Das Leaderbourd wird jede Woche aktualisiert", value="weekly"),
            discord.SelectOption(label="Monatschlich aktualisieren", default="Das Leaderbourd wird jedes Monat aktualisiert)", value="monthly")
        ])
    async def set_leaderbourd_select(self, select, interaction:discord.Interaction):

        option_list, check_list = [], []
        for i in select.values:
            option_list.append(f"{Emojis.dot_emoji} {i} aktualisierung\n")
            check_list.append(i)

            DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, settings = i)

        for i in [value for value in ["daily", "weekly", "monthly"] if value not in check_list]:

            DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, back_to_none = i)

        emb = discord.Embed(description=f"""## Intervall wurde festgelegt
            {Emojis.dot_emoji} {'Die folgenden leaderbourd optionen wurden ausgewählt' if len(select.value) != 1 else 'Die foldende leaderbourd option wurde ausgewählt'}:
                {"".join(option_list)}
            {Emojis.dot_emoji} {'Das leaderbourd wird' if len(select.values) == 1 else 'Die leaderbourds werden'} in <#{DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)[5]}> gesendet""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)


class ActivateLeaderbourd(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label = "Leaderbourd jetzt aktivieren",
            style = discord.ButtonStyle.blurple,
            custom_id = "activate_leaderbourd" 
        )

    async def callback(self, interaction:discord.Interaction):

        check_settings = DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)

        interval_list = {
            check_settings[2]:"daily",
            check_settings[3]:"wekkly",
            check_settings[4]:"monthly"
        }

        text_dict = {
            check_settings[2]:"einen Tag",
            check_settings[3]:"eine Woche",
            check_settings[4]:"ein Monat"
        }

        leaderbourd_list = []
        for i in check_settings[4], check_settings[3], check_settings[2]:

            if i != None:
                leaderbourd_list.append(f"{Emojis.dot_emoji} {interval_list[i]} aktualisierendes leaderbourd")

                emb = discord.Embed(
                    description=f"""## Die anzahl der nachrichten wird für {text_dict[i]} gespeichert
                        {Emojis.dot_emoji} Wenn die Zeit dann um ist wird diese Nachricht zu einen leaderbourd editiert die die user anzeigt die am meisten Nachrichten geschrieben haben""", color=bot_colour)

                message = await bot.get_message(i)
                await message.channel.send(embed=emb)

        emb = discord.Embed(description=f"""## Die einstellungen wurden nun vorgenommen
            {Emojis.dot_emoji} {'Das leaderbourd wird' if len(check_settings[2], check_settings[3], check_settings[4]) == 1 else 'Die leaderbourds werden'} in den channel <#{DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)[5]}> gesendet
            {Emojis.dot_emoji} Folgende Intervall leaderbourds sind ab jetzt aktiv:
            """, color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)