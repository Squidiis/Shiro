from discord.interactions import Interaction
from utils import *
from sql_function import *
from discord.ext import tasks
import pytz

class MessageLeaderbourd(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name = "show-invites")
    async def show_invites(self, ctx:discord.ApplicationContext, user:Option(discord.Member)):

        if user is None:

            total_invites = 0
            for invite in await ctx.guild.invites():
                if invite.inviter == ctx.author:
                    total_invites += invite.uses

            emb = discord.Embed(description=f"""## Number of invited members of {user.name}
                {Emojis.dot_emoji} {f'{user.mention} has invited {total_invites} users' if total_invites != 0 else f'{user.mention} has not yet invited any other users'} to the server {ctx.guild.name}.
                {Emojis.help_emoji} The invitations are only counted if the user has created the invitation link!""", color=bot_colour)
            
            await ctx.respond(embed=emb)
        else:

            total_invites = 0
            for invite in await ctx.guild.invites():
                if invite.inviter == user:
                    total_invites += invite.uses
            await ctx.respond(f"{user.mention} has invited {total_invites} member to the server.")


    @commands.slash_command(name = "set-message-leaderbourd", description = "Set the message leaderbourd system!")
    async def set_message_leaderbourd(self, ctx:discord.ApplicationContext):

        settings = DatabaseCheck.check_leaderbourd_settings(guild_id = ctx.guild_id)

        emb = discord.Embed(description=f"""## Set the message leaderbourd
            {Emojis.dot_emoji} With the lower select menu you can define a channel in which the leaderbourd should be sent
            {Emojis.dot_emoji} Then you can also set an interval at which time intervals the leaderboard should be updated
            {Emojis.dot_emoji} You can also switch the system off or on currently it is {'switched off' if settings[0] else 'switched on'}. (as soon as it is switched off, no more messages are counted and when it is switched on, the leaderbourd is reset)
            {Emojis.help_emoji} The leaderbourd is edited when you update it, so you should make sure that no one else can write in the channel you specified""", color=bot_colour)        
        await ctx.respond(embed=emb, view=SetLeaderbourdChannel())


    @commands.slash_command(name = "show-message-leaderbourd-setting", description = "All show you how the message leaderbourd is set!")
    async def show_message_leaderbourd_settings(self, ctx:discord.ApplicationContext):
        
        settings = DatabaseCheck.check_leaderbourd_settings(guild_id = ctx.guild.id)

        intervals = {
            settings[2]:"Daily",
            settings[3]:"Weekly",
            settings[4]:"Monthly"
        }
        intervals_text = []
        for i in settings[2], settings[3], settings[4]:

            if i != None:

                intervals_text.append(f"{Emojis.dot_emoji} {intervals[i]} updating Message leaderbourd\n")

        emb = discord.Embed(description=f"""## Here you can see all the settings of the message leaderboard
            {Emojis.dot_emoji} {f'Currently <#{settings[5]}> is set as' if settings[5] != None else 'No'} message leaderbourd channel has been set
            {Emojis.dot_emoji} The following intervals are currently defined for which a leaderboard exists:
            {"".join(intervals_text) if intervals_text != [] else f'{Emojis.dot_emoji} No intervals have been defined yet'}""", color=bot_colour)
        await ctx.respond(embed = emb)


    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        
        check = DatabaseCheck.check_leaderbourd_settings(guild_id = message.guild.id)

        if message.author.bot:
            return
        
        if check[1] == 1:
            
            DatabaseUpdates.manage_leaderbourd(guild_id = message.guild.id, user_id = message.author.id, interval = "count")

def setup(bot):
    bot.add_cog(MessageLeaderbourd(bot))


async def sort_leaderbourd(user_list, interval):

    max_lengths = [
        max(len(str(t[i])) for t in user_list)
        for i in range(6)
    ]
    
    user_names = []
    for t in user_list:

        user = await bot.get_or_fetch_user(t[1])
        user_names.append(user.name)
        max_lengths[0] = max(max_lengths[0], len(user.name))
    
    padded_tuples = [
        (
            user_names[i].ljust(max_lengths[0]), 
            str(t[1]).ljust(max_lengths[1]),
            str(t[2]).ljust(max_lengths[2]),
            str(t[3]).ljust(max_lengths[3]),
            str(t[4]).ljust(max_lengths[4])
        )
        for i, t in enumerate(user_list)
    ]

    leaderboard = []
    for i in range(min(len(user_list), 15)):
        num_str = str(i + 1)
        if len(num_str) == 1:
            num_str = f" #{num_str}  "
        elif len(num_str) == 2:
            num_str = f" #{num_str} "

        leaderboard.append(f"`{num_str}` `{padded_tuples[i][0]}` `messages {padded_tuples[i][interval]}`\n")

    return "".join(leaderboard)


@tasks.loop(minutes=2)
async def edit_leaderbourd(bot):

    for guild in bot.guilds:

        leaderboard_settings = DatabaseCheck.check_leaderbourd_settings(guild_id = guild.id)

        if leaderboard_settings:

            message_ids = [
                ("1_day_old", leaderboard_settings[2]),
                ("1_week_old", leaderboard_settings[3]),
                ("1_month_old", leaderboard_settings[4])
            ]
            
            if leaderboard_settings[1] == 1 and leaderboard_settings[5] != None:

                try:
                    
                    current_date = datetime.now(UTC)

                    for message_name, message_id in message_ids:

                        if message_id != None:
                            
                            channel = bot.get_channel(leaderboard_settings[5])
                            message = await channel.fetch_message(message_id)

                            if leaderboard_settings[2] != None:
                                    
                                    #if (current_date - message.edited_at) > timedelta(minutes=5) and message_name == "1_day_old":
                                    #    
                                    #    user_list = DatabaseCheck.check_leaderbourd(guild_id = guild.id, interval = 0)
                                    #    users = await sort_leaderbourd(user_list=user_list, interval=2)
                                    #    emb = discord.Embed(description=f"""**Daily Messages Leaderboard**
                                    #        {users} editet5""", color=bot_colour)
                                        
                                    #    await message.edit(embed = emb)

                                if (current_date - message.edited_at) > timedelta(days=1) and message_name == "1_day_old":

                                    user_list = DatabaseCheck.check_leaderbourd(guild_id = guild.id, interval = 0)
                                    users = await sort_leaderbourd(user_list=user_list, interval=3)
                                    emb = discord.Embed(description=f"""**Daily Messages Leaderboard**
                                        {users} edit 3""", color=bot_colour)

                                    await message.edit(embed = emb)

                            if leaderboard_settings[3] != None:

                                if (current_date - message.edited_at) > timedelta(weeks=1) and message_name == "1_week_old":
                                    
                                    user_list = DatabaseCheck.check_leaderbourd(guild_id = guild.id, interval = 1)
                                    users = await sort_leaderbourd(user_list=user_list, interval=3)
                                    emb = discord.Embed(description=f"""**weekly Messages Leaderboard**
                                        {users}""", color=bot_colour)

                                    await message.edit(embed = emb)

                            if leaderboard_settings[4] != None:

                                if (current_date - message.edited_at) > timedelta(days=30) and message_name == "1_month_old":
                                    
                                    user_list = DatabaseCheck.check_leaderbourd(guild_id = guild.id, interval = 2)
                                    users = await sort_leaderbourd(user_list=user_list, interval=4)
                                    emb = discord.Embed(description=f"""**Monthly Messages Leaderboard (30 days)**
                                        {users}""", color=bot_colour)

                                    await message.edit(embed = emb)

                except Exception as e:
                    print(f"Ein Fehler ist aufgetreten: {e}")


class SetLeaderbourdChannel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(LeaderbourdOnOffSwitch())
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

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=4), view=ContinueSetting())

            else:
                
                emb = discord.Embed(description=f"""## Es wurde bereits ein channel für das leaderbourd festgelegt
                    {Emojis.dot_emoji} Möchstest du diesen überschreibe?
                    {Emojis.dot_emoji} aktuell ist <#{settings[5]}> als channel für das leaderbourd festlegegt""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=OverwriteChannel(channel_id=select.values[0].id))

        else:

            DatabaseUpdates.create_leaderbourd_settings(guild_id = interaction.guild.id, settings = "create", channel_id = select.values[0].id)

        emb = discord.Embed(description=f"""## Channel für das Leaderbourd wurde festgelegt
            {Emojis.dot_emoji} Ab sofort wird in {select.values[0].mention} das liederbourd gesendet
            {GetEmbed.get_embed(embed_index=3)}
            """, color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())


    @discord.ui.button(
        label="skip channel setting",
        style=discord.ButtonStyle.blurple,
        custom_id="skip_channel"
    )
    async def skip_set_channel(self, button, interaction:discord.Interaction):
        
        if DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)[5]:

            emb = discord.Embed(description=f"""## Einstellen des Channel wurde übersprungen
                {GetEmbed.get_embed(embed_index=3)}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())

        else:

            emb = discord.Embed(description=f"""## Einstellung kann nicht übersprungen werden
                {Emojis.dot_emoji} Die einstellung kann nur übersprungen werden wenn ein channel dem message leaderbourd zugeweisen wurde
                {Emojis.dot_emoji} Du musst erst einen channel festlegen bevor du weiter machen kannst""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)


class SetLeaderbourd(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "message leaderbourd system"))

    def compare_lists(self, list1, list2):

        sorted_list1 = sorted(list1, key=lambda x: (x is None, x))
        sorted_list2 = sorted(list2, key=lambda x: (x is None, x))

        return sorted_list1 == sorted_list2


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

        settings = DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)
        check_list = []
        if any(elem is not None for elem in [settings[2], settings[3], settings[4]]):
            
            if self.compare_lists(list1=select.values, list2=[settings[2], settings[3], settings[4]]):

                emb = discord.Embed(description=f"""## Diese Intervalle sind bereits festgelegt
                    {Emojis.dot_emoji} Du hast bereits diese Intervalle für das Message leaderbourd festgelegt
                    {Emojis.help_emoji} Wenn du andere Intervalle haben möchstest kannst du diesen command einfach nochmal ausführen und sie überschreiben""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                for i in select.values[0]:

                    if i in [settings[2], settings[3], settings[4]]:

                        check_list.append(f"{Emojis.dot_emoji} {i} aktualisierung\n")

                emb = discord.Embed(description=f"""## Es wurden bereits intervalle festgelegt
                    {Emojis.dot_emoji} Aktuell sind folgende intervalle aktiv:
                        {check_list}
                    {Emojis.dot_emoji} Willst du dieser überschreiben?""", color=bot_colour)
                await interaction.response.edit_message(embed=emb)

        else:

            option_list, check_list = [], []
            for i in select.values:
                option_list.append(f"{Emojis.dot_emoji} {i} aktualisierung\n")
                check_list.append(i)

                if i != None:

                    emb = discord.Embed(
                        description=f"""## Die anzahl der nachrichten wird für {text_dict[i]} gespeichert
                            {Emojis.dot_emoji} Wenn die Zeit dann um ist wird diese Nachricht zu einen leaderbourd editiert die die user anzeigt die am meisten Nachrichten geschrieben haben""", color=bot_colour)

                    channel = bot.get_channel(settings[5])
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


    @discord.ui.button(
        label="skip interval setting",
        style=discord.ButtonStyle.blurple,
        custom_id="skip_interval"
    )
    async def skip_set_channel(self, button, interaction:discord.Interaction):
        
        interval = DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)

        intervals = {
            interval[2]:"daily",
            interval[3]:"weekly",
            interval[4]:"monthly"
        }

        if interval[2] or interval[3] or interval[4]:
            
            check_interval = "".join([intervals[i] for i in [interval[2], interval[3], interval[4]] if i is not None])

            emb = discord.Embed(description=f"""## Einstellen der intervalle wurde übersprungen
                {Emojis.dot_emoji} {f'Die intervalle {check_interval} werden als intervalle' if len(check_interval) != 1 else f'Das interval {check_interval} wird'} beibehalten""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())

        else:

            emb = discord.Embed(description=f"""## Einstellung kann nicht übersprungen werden
                {Emojis.dot_emoji} Die einstellung kann nur übersprungen werden wenn mindestens ein interval dem message leaderbourd zugeweisen wurde
                {Emojis.dot_emoji} Du musst erst ein interval festlegen bevor du weiter machen kannst""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)



class OverwriteChannel(discord.ui.View):

    def __init__(
            self, channel_id):
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

        elif self.channel_id == DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)[5]:
            
            await interaction.response.edit_message(GetEmbed.get_embed(embed_index=4), view=ContinueSetting())

        else:
            
            get_messages = DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)
            DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, settings = "channel", channel_id = self.channel_id)

            for i, index in (get_messages[2], "daily"), (get_messages[3], "weekly"), (get_messages[4], "monthly"):
                
                if i != None:
                
                    leaderbourd_channel = bot.get_channel(get_messages[5])
                    
                    msg = await leaderbourd_channel.fetch_message(i)
                    await msg.delete()

                    DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, back_to_none = index)

            emb = discord.Embed(description=f"""## Leaderbourd channel wurde überschrieben
                {Emojis.dot_emoji} Ab sofort ist <#{self.channel_id}> der neue leaderbourd channel
                {Emojis.dot_emoji} Das leaderbourd wird aus dem alten leaderbourd channel gelöscht
                {Emojis.dot_emoji} Mit den unseren select menü kannst du mit dem einstellen fortfahren
                {Emojis.help_emoji} Du kannst mehrere intervalle auswählen auch ist jedes intervall ein einzelnes leaderbourd""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())
        

    @discord.ui.button(
        label="keep current channel",
        style=discord.ButtonStyle.blurple,
        custom_id="keep_channel"
    )

    async def keep_channel(self, button, interaction:discord.Interaction):

        emb = discord.Embed(description=f"""## Channel wird beibehalten
            {Emojis.dot_emoji} Der channel <#{DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)[5]}> wird als leaderbourd channel beibehalten
            {Emojis.dot_emoji} Mit den unseren select menü kannst du mit dem einstellen fortfahren
            {Emojis.help_emoji} Du kannst mehrere intervalle auswählen auch ist jedes intervall ein einzelnes leaderbourd""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())


class ContinueSetting(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="continue settings",
        style=discord.ButtonStyle.blurple,
        custom_id="continue_setting"
    )

    async def continue_setting_button(self, button, interaction:discord.Interaction):

        emb = discord.Embed(description=f"""## Lege Intervalle fest
            {Emojis.dot_emoji} Mit den unteren Selectmenü kannst du einen Intervall festlegen in welchen zeiträumen das message leaderbourd geupdaitet werden soll
            {Emojis.dot_emoji} Du kannst auch merhrere Intervalle auswählen es muss aber nur mindestens eines gewählt werden
            {Emojis.help_emoji} Sobald du die Intervalle ausgewählt hast werden die leaderbourds in den vorher verstgelegten channel gesendet und dann immer in den entsprechenden Zeit räumen geupdaitet""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=SetLeaderbourd())


class LeaderbourdOnOffSwitch(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label = "On / Off switch",
            style = discord.ButtonStyle.blurple,
            custom_id = "on_off_switch"
        )

    async def callback(self, interaction:discord.Interaction):
        
        settings = DatabaseCheck.check_leaderbourd_settings(guild_id = interaction.guild.id)
        DatabaseUpdates.manage_leaderbourd(guild_id = interaction.guild.id, settings = "status")

        emb = discord.Embed(description=f"""## Das message Leaderbourd system ist jetzt {'aktiviert' if settings[1] == 0 else 'deaktiviert'}
            {Emojis.dot_emoji} {f'''Ab jetzt werden alle Nachrichten zu dem message leaderbourd zu gerechnet und eine Rangliste erstellt die zeigt wer am meisten nachrichten geschrieben hat
            {Emojis.help_emoji} dafür muss jedoch auch ein Intervall und ein Channel festgelegt werden'''
            if settings[1] == 0 else f'''Ab jetzt werden keine Nachrichten menr zu den Message leaderbourd dazu gezählt die rangliste wird auch nicht mehr geupdaitet wenn du es wieder aktivierst wird das leaderbourd zurück gesetzt und ab dem neuen intervall gezählt
            {Emojis.dot_emoji} Die anderen einstellungen bleiben wie so wie sind'''}""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)


