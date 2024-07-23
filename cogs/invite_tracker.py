from utils import *
from sql_function import *
from discord.ext import tasks
from message_leaderboard import SetMessageleaderboardMessage

# Dictionary for the check functions (does not have to be in each command individually)
interval_list = {
    "week":"weekly leaderboard",
    "month":"monthly leaderboard",
    "quarter":"quarterly leaderboard",
    "general":"general leaderboard"
    }


interval_text = {
    "daily":("one day", 1),
    "weekly":("one week", 7),
    "monthly":("one month", 30)
    }


class InviteTrackerSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name = "set-invite-leaderboard", description = "Set up the invite leaderboard system!")
    async def set_invite_leaderboard(self, ctx:discord.ApplicationContext):

        settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild_id, system = "invite")
        
        if settings == None:

            await DatabaseUpdates.create_leaderboard_settings(guild_id = ctx.guild.id, system = "invite")
            settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild_id, system = "invite")

        emb = discord.Embed(description=f"""## Set the invite leaderboard
            {Emojis.dot_emoji} With the lower select menu you can define a channel in which the leaderboard should be sent
            {Emojis.dot_emoji} Then you can also set an interval at which time intervals the leaderboard should be updated
            {Emojis.dot_emoji} You can also switch the system off or on currently it is {'switched off' if settings[0] else 'switched on'}. (as soon as it is switched off, no more invites are counted and when it is switched on, the leaderboard is reset)
            {Emojis.help_emoji} The leaderboard is edited when you update it, so you should make sure that no one else can write in the channel you specified
            {Emojis.help_emoji} **The leaderboard always shows the data from the previous interval, e.g. the best users who have invited the most users in the last week**""", color=bot_colour)        
        await ctx.respond(embed=emb, view = SetleaderboardChannel())

def setup(bot):
    bot.add_cog(InviteTrackerSystem(bot))


# angepasst
class SetleaderboardChannel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(LeaderboardOnOffSwitchInvite())
        self.add_item(DefaultSettingsLeaderboard())
        self.add_item(CancelButton(system = "invite leaderboard system"))

    @discord.ui.channel_select(
        placeholder = "Choose a channel that you want to set as the leaderboard channel for the inivte leaderboard!",
        min_values = 1,
        max_values = 1,
        custom_id = "leaderboard_channel_select_invite",
        channel_types = [
            discord.ChannelType.text, 
            discord.ChannelType.forum, 
            discord.ChannelType.news
        ]
    )

    async def set_leaderboard_channel(self, select, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            system = 'message' if 'Set the message leaderboard' in interaction.message.embeds[0].description else 'invite'
            settings = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = system)
            
            if settings:
                
                if settings[6] == None:
                    
                    if system == "invite":

                        await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, settings = "channel", channel_id = select.values[0].id)
                    
                    else:

                        await DatabaseUpdates.manage_leaderboard_message(guild_id = interaction.guild.id, settings = "channel", channel_id = select.values[0].id)


                    await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=4, settings=select.values[0].mention), view=SetInviteleaderboardInvite() if system == "invite" else SetMessageleaderboardMessage())

                elif settings[6] == select.values[0].id:

                    await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=5), view=ContinueSettingLeaderboard())

                else:
                    
                    emb = discord.Embed(description=f"""## A channel has already been defined for the leaderboard
                        {Emojis.dot_emoji} Would you like to overwrite this?
                        {Emojis.dot_emoji} Currently is <#{settings[6]}> set as the channel for the leaderboard""", color=bot_colour)
                    await interaction.response.edit_message(embed=emb, view=OverwriteMessageChannel(channel_id=select.values[0].id))

            else:

                await DatabaseUpdates.create_leaderboard_settings(guild_id = interaction.guild.id, channel_id = select.values[0].id, system = system)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="skip channel setting",
        style=discord.ButtonStyle.blurple,
        custom_id="skip_channel"
    )
    
    async def skip_set_channel(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            system = 'message' if 'Set the message leaderboard' in interaction.message.embeds[0].description else 'invite'

            if DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = system)[6]:

                emb = discord.Embed(description=f"""## Setting the channel was skipped
                    {GetEmbed.get_embed(embed_index=3)}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=SetInviteleaderboardInvite())

            else:

                emb = discord.Embed(description=f"""## Setting cannot be skipped
                    {Emojis.dot_emoji} The setting can only be skipped if a channel has been assigned to the {system} leaderboard
                    {Emojis.dot_emoji} You must first set a channel before you can continue""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


# Edetiert, ab jetzt für beide systeme funktional
class LeaderboardOnOffSwitchInvite(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label = "on / off switch",
            style = discord.ButtonStyle.blurple,
            custom_id = "on_off_switch"
        )

    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            system = 'message' if 'Set the message leaderboard' in interaction.message.embeds[0].description else 'invite'
            settings = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = system)
            await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, settings = "status")

            emb = discord.Embed(description=f"""## The {system} leaderboard system is now {'activated' if settings[1] == 0 else 'deactivated'}.
                {Emojis.dot_emoji} {f'''From now on all {'message' if system == 'message' else 'invitation'}s will be added to the {system} leaderboard and a ranking will be created showing who has {'written the most messages' if system == 'message' else 'invited the most users'}
                {Emojis.help_emoji} However, an interval and a channel must also be defined for this'''
                if settings[1] == 0 else f'''From now on, no {'message' if system == 'message' else 'invitation'}s will be added to the {system} leaderboard and the ranking will no longer be updated when you activate it again, the leaderboard will be reset and counted from the new interval.
                {Emojis.dot_emoji} The other settings remain as they are'''}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


# angepasst
class SetInviteleaderboardInvite(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "invite leaderboard system"))

    @discord.ui.select(
        placeholder = "Select the intervals at which the activities should be displayed!",
        min_values = 1,
        max_values = 3,
        custom_id = "set_leaderboard_invite",
        options = [
            discord.SelectOption(
                label="Update weekly", 
                description="The leaderboard is updated every week", 
                value="weekly"
            ),
            discord.SelectOption(
                label="Update monthly", 
                description="The leaderboard is updated every month", 
                value="monthly"
            ),
            discord.SelectOption(
                label="Update quarterly", 
                description="The leaderboard is updated every three month", 
                value="quarterly"
            )
        ]
    )
    
    async def set_leaderboard_select(self, select, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            settings = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = "invite")

            value_check = {
                "weekly":settings[2],
                "monthly":settings[3],
                "quarterly":settings[4]
            }

            check_list = []

            if any(elem is not None for elem in [settings[2], settings[3], settings[4]]):
                
                if all(elem in value_check.keys() and value_check[elem] is not None for elem in select.values):
                            
                    emb = discord.Embed(description=f"""## These intervals are already set
                        {Emojis.dot_emoji} You have already defined these intervals for the message leaderboard
                        {Emojis.help_emoji} If you want to have other intervals you can simply execute this command again and overwrite them""", color=bot_colour)
                    await interaction.response.edit_message(embed=emb, view=None)

                else:

                    for i in select.values:

                        if value_check[i]:

                            check_list.append(f"> {Emojis.dot_emoji} {i} update\n")
                    
                    if check_list == []:
                        check_list = [f"> {Emojis.dot_emoji} None of the intervals you mentioned are currently active"]

                    emb = discord.Embed(description=f"""## Intervals have already been defined
                        {Emojis.dot_emoji} The following intervals are currently active:\n
                            {''.join(check_list)}
                        {Emojis.help_emoji} Do you want to overwrite them? the previously sent leaderboard will be deleted""", color=bot_colour)
                    await interaction.response.edit_message(embed=emb, view=OverwriteMessageInterval(intervals=select.values))

            else:

                option_list = []
                channel = bot.get_channel(settings[6])

                message = await channel.send(embed=GetEmbed.get_embed(embed_index=7))
                await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, settings = "whole", message_id = message.id)

                order = sorted(select.values, key=lambda item: ["weekly", "monthly", "quarterly"].index(item))
                for i in order:
                    option_list.append(f"{Emojis.dot_emoji} {i} update\n")
                    check_list.append(i)

                    if i != None:

                        emb = discord.Embed(
                            description=f"""## The number of messages is saved for {interval_text[i][0]}.
                            {Emojis.dot_emoji} This message will be edited on <t:{int((datetime.now() + timedelta(days=interval_text[i][1])).timestamp())}> and will then act as a leaderboard and show who has written the most messages on the server""", color=bot_colour)
                        message = await channel.send(embed=emb)
                        
                        await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, settings = i, message_id = message.id)

                for i in [value for value in ["weekly", "monthly", "quarterly"] if value not in check_list]:

                    await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, back_to_none = i)

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=6, settings=select.values, settings2=option_list, settings3=channel.mention), view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="skip interval setting",
        style=discord.ButtonStyle.blurple,
        custom_id="skip_interval"
    )

    async def skip_set_channel(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            interval = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = "invite")

            intervals = {
                interval[2]:"weekly",
                interval[3]:"monthly",
                interval[4]:"quarterly"
            }

            if interval[2] or interval[3] or interval[4]:
                
                check_interval = "".join([intervals[i] for i in [interval[2], interval[3], interval[4]] if i is not None])

                emb = discord.Embed(description=f"""## Setting the intervals was skipped
                    {Emojis.dot_emoji} {f'The intervals {check_interval} will be kept as intervals' if len(check_interval) != 1 else f'The interval {check_interval} will be kept'}""", color=bot_colour)
                
            else:

                emb = discord.Embed(description=f"""## Setting cannot be skipped
                    {Emojis.dot_emoji} The setting can only be skipped if at least one interval has been assigned to the message leaderboard
                    {Emojis.dot_emoji} You must first set an interval before you can continue""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


# Angepasst
class OverwriteMessageInterval(discord.ui.View):

    def __init__(self, intervals):
        self.intervals = intervals
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "invite leaderboard system"))

    @discord.ui.button(
        label="overwrite the intervals",
        style=discord.ButtonStyle.blurple,
        custom_id="overwrite_intervals"
    )

    async def overwrite_intervals_message(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            if self.intervals == None:
                
                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=10, settings="invite", settings2="to overwrite the interval", settings3=f"set-invite-leaderboard"), view=None)

            else:

                settings = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = "invite")

                option_list, check_list = [], []
                order = sorted(self.intervals, key=lambda item: ["weekly", "monthly", "quarterly"].index(item))

                channel = bot.get_channel(settings[6])

                message = await channel.send(embed=GetEmbed.get_embed(embed_index=7))
                await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, settings = "whole", message_id = message.id)

                for i in order:
                    option_list.append(f"> {Emojis.dot_emoji} {i} update\n")
                    check_list.append(i)

                    if i != None:

                        emb = discord.Embed(
                            description=f"""## The number of messages is saved for {interval_text[i][0]}.
                                {Emojis.dot_emoji} This message will be edited on <t:{int((datetime.now() + timedelta(days=interval_text[i][1])).timestamp())}> and will then act as a leaderboard and show who has written the most messages on the server""", color=bot_colour)
                        message = await channel.send(embed=emb)
                        await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, settings = i, message_id = message.id)

                for i in [value for value in ["weekly", "monthly", "quarterly"] if value not in check_list]:

                    await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, back_to_none = i)

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=6, settings=self.intervals, settings2=option_list, settings3=channel.mention), view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="keep intervals",
        style=discord.ButtonStyle.blurple,
        custom_id="keep_intervals"
    )

    async def keep_intervals_message(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            check_settings = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = "invite")

            list_intervals = []
            for _, _, week, month, quarter, _, _ in check_settings:

                if week != None:
                    list_intervals.append(f"{Emojis.dot_emoji} Weekly updated leaderboard")

                if month != None:
                    list_intervals.append(f"{Emojis.dot_emoji} Monthly updated leaderboard")

                if quarter != None:
                    list_intervals.append(f"{Emojis.dot_emoji} quarterly updated leaderboard")

            emb = discord.Embed(description=f"""## The current intervals are retained
                {Emojis.dot_emoji} Here you can see an overview of the currently defined intervals
                {"\n".join(list_intervals)}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


# Edetiert für beide systeme
class DefaultSettingsLeaderboard(discord.ui.Button):
    
    def __init__(self):
        super().__init__(
            label="Settings back to default",
            style=discord.ButtonStyle.blurple,
            custom_id="default_leaderboard"
        )

    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            system = 'message' if 'Set the message leaderboard' in interaction.message.embeds[0].description else 'invite'

            await DatabaseRemoveDatas.remove_leaderboard_settings(guild_id = interaction.guild.id)

            emb = discord.Embed(description=f"""## The settings have been reset
                {Emojis.dot_emoji} The settings of the {system} leaderboard system have been reset to default
                {Emojis.dot_emoji} The leaderboard system is switched off and the previously set intervals have been deleted
                {Emojis.help_emoji} You can simply set the {system} leaderboard again as soon as you wish""", color=bot_colour)
            await interaction.response.edit_message(embed=emb)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


# Edetiert für beide systeme
class ContinueSettingLeaderboard(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system=None))

    @discord.ui.button(
        label="continue settings",
        style=discord.ButtonStyle.blurple,
        custom_id="continue_setting_leaderbaord"
    )

    async def continue_setting_leaderboard_button(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            system = 'message' if 'Set the message leaderboard' in interaction.message.embeds[0].description else 'invite'

            emb = discord.Embed(description=f"""## Set intervals
                {Emojis.dot_emoji} With the lower select menu you can define an interval in which periods the {system} leaderboard should be updated
                {Emojis.dot_emoji} You can also select several intervals, but you only need to select at least one
                {Emojis.help_emoji} As soon as you have selected the intervals, the leaderboards are sent to the channel you have previously set up and then always updated in the corresponding time periods""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=SetInviteleaderboardInvite())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


# Angepasst für beide systeme
class OverwriteMessageChannel(discord.ui.View):

    def __init__(
            self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.add_item(CancelButton(system=None))

    @discord.ui.button(
        label="overwrite channel",
        style=discord.ButtonStyle.blurple,
        custom_id="overwrite_leaderboard_channel"
    )

    async def overwrite_leaderboard_channel(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            system = 'message' if 'Set the message leaderboard' in interaction.message.embeds[0].description else 'invite'

            if self.channel_id == None:

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=10, settings="channel", settings2="to set leaderboard", settings3=f"set-{system}-leaderboard"), view=None)

            else:
                
                get_messages = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = system)
                await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, settings = "channel", channel_id = self.channel_id)

                system_intervals = {
                    "invite":[(get_messages[2], "weekly"), (get_messages[3], "monthly"), (get_messages[4], "quarterly")],
                    "message":[(get_messages[2], "daily"), (get_messages[3], "weekly"), (get_messages[4], "monthly")]
                }
                
                for i, index in system_intervals[system]:
                    
                    if i != None:
                    
                        leaderboard_channel = bot.get_channel(get_messages[6])
                        
                        msg = await leaderboard_channel.fetch_message(i)
                        await msg.delete()

                        await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, back_to_none = index)

                emb = discord.Embed(description=f"""## Leaderboard channel has been overwritten
                    {Emojis.dot_emoji} As of now, <#{self.channel_id}> is the new leaderboard channel
                    {Emojis.dot_emoji} The leaderboard is deleted from the old leaderboard channel
                    {Emojis.dot_emoji} You can continue with the setting using the selection menu below
                    {Emojis.help_emoji} You can select several intervals and each interval is a single leaderboard""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=SetInviteleaderboardInvite())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="keep current channel",
        style=discord.ButtonStyle.blurple,
        custom_id="keep_channel"
    )

    async def keep_channel(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            
            system = 'message' if 'Set the message leaderboard' in interaction.message.embeds[0].description else 'invite'

            emb = discord.Embed(description=f"""## Channel is retained
                {Emojis.dot_emoji} The channel <#{DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = system)[6]}> will be retained as a leaderboard channel
                {Emojis.dot_emoji} You can continue with the setting using the selection menu below
                {Emojis.help_emoji} You can select several intervals and each interval is a single leaderboard""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=SetInviteleaderboardInvite())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)
