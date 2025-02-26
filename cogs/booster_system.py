from utils import *
from sql_function import *


class BoosterSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    
    @commands.slash_command(name = "set-booster-channel", description = "Set the booster channel system!")
    @commands.has_permissions(administrator = True)
    async def set_booster_channel(self, ctx:discord.ApplicationContext):

        settings = await DatabaseCheck.check_booster_channel(guild_id = ctx.guild.id)

        if settings:

            view = ShowBoosterMessage()
            view.add_item(SetBoosterChannel())
            view.add_item(OverwriteBoosterChannel())
            view.add_item(CancelButton(system="booster channel system"))

            emb = discord.Embed(description=f"""## Set booster channel
                {Emojis.dot_emoji} With the buttons below you can activate or deactivate the booster channel currently the system is **{'deactivated' if settings[1] == 0 else 'activated'}**
                {Emojis.dot_emoji} Currently <#{settings[2]}> is the booster channel which you can change with the lower button
                {Emojis.help_emoji} You can set the system using the button below""", color=bot_colour)
            await ctx.respond(embed=emb, view=view)

        else:

            emb = discord.Embed(description=f"""## No booster channel has been set
                {Emojis.dot_emoji} The booster system cannot be set because no booster channel has been set
                {Emojis.dot_emoji} If you want to set a booster channel use the `add-booster-channel` command""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "add-booster-channel", description = "Add a booster channel!")
    @commands.has_permissions(administrator = True)
    async def add_booster_channel(self, ctx:discord.ApplicationContext, channel:Option(discord.TextChannel, description="Choose a channel you want to set as booster channel!")):

        settings = await DatabaseCheck.check_booster_channel(guild_id = ctx.guild.id)

        if settings:
            
            view = ShowBoosterMessage()
            view.add_item(CancelButton(system="booster channel system"))

            if settings[2] == channel.id:

                emb = discord.Embed(description=f"""## This channel is already set as a booster channel
                    {Emojis.dot_emoji} The channel <#{settings[2]}> is already set as a booster channel 
                    {Emojis.dot_emoji} With the button below you can display the booster message
                    {Emojis.help_emoji} This message is always sent when a user boosts the server""", color=bot_colour)
                await ctx.respond(embed=emb, view=view)

            else:

                emb = discord.Embed(description=f"""## A booster channel is already defined
                    {Emojis.dot_emoji} The channel <#{settings[2]}> is currently set as the booster channel
                    {Emojis.dot_emoji} With the button below you can display the booster message
                    {Emojis.help_emoji} This message is always sent when a user boosts the server""", color=bot_colour)
                await ctx.respond(embed=emb, view=view)

        else:
            
            await DatabaseUpdates.manage_booster_channel(guild_id = ctx.guild.id, operation = "insert", channel_id = channel.id)

            view = View()
            view.add_item(SetBoosterMessage())

            emb = discord.Embed(description=f"""## A new booster channel has been defined
                {Emojis.dot_emoji} From now on the channel {channel.mention} is set as booster channel
                {Emojis.dot_emoji} From now on all booster notifications will be sent to this channel
                {Emojis.dot_emoji} Use the button below to set the booster message otherwise a standard message will be sent""", color=bot_colour)
            await ctx.respond(embed=emb, view=view)

    
    @commands.slash_command(name = "remove-booster-channel", description = "Remove the booster channel from the server!")
    @commands.has_permissions(administrator = True)
    async def remove_booster_channel(self, ctx:discord.ApplicationContext):

        settings = await DatabaseCheck.check_booster_channel(guild_id = ctx.guild.id)

        if settings:

            await DatabaseUpdates.manage_booster_channel(guild_id = ctx.guild.id, operation = "delete")

            emb = discord.Embed(description=f"""## The booster channel has been removed
                {Emojis.dot_emoji} The channel <#{settings[2]}> has been removed as a booster channel
                {Emojis.dot_emoji} From now on, booster notifications will no longer be sent to this channel
                {Emojis.dot_emoji} If you want to set a booster channel again use the `add-booster-channel` command""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            emb = discord.Embed(description=f"""## No booster channel has been set
                {Emojis.dot_emoji} The booster channel could not be removed because none was set
                {Emojis.dot_emoji} If you want to set a booster channel use the `add-booster-channel` command""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "show-booster-channel", description = "Shows the settings of the booster channel")
    @commands.has_permissions(administrator = True)
    async def show_booster_channel(self, ctx:discord.ApplicationContext):

        settings = await DatabaseCheck.check_booster_channel(guild_id = ctx.guild.id)

        if settings:

            view = ShowBoosterMessage()
            view.add_item(CancelButton(system="booster channel system"))

            emb = discord.Embed(description=f"""## Current booster channel
                {Emojis.dot_emoji} The channel <#{settings[2]}> is currently set as the booster channel
                {Emojis.dot_emoji} Whenever someone boosts the server, a message is sent
                {Emojis.help_emoji} With the button below you can view the message and customize it at the place where the user should be mentioned insert [user]""", color=bot_colour)
            await ctx.respond(embed=emb, view=view)

        else:

            emb = discord.Embed(description=f"""## The Booster channel could not be found
                {Emojis.dot_emoji} No booster channel has been set
                {Emojis.dot_emoji} If you want to set a booster channel you can use the `add-booster-channel` command""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        
        if before.premium_since is None and after.premium_since is not None:

            settings = await DatabaseCheck.check_booster_channel(guild_id = after.guild.id)

            if settings[1] == 1:

                boost_channel = bot.get_channel(settings[2])

                if boost_channel:
                  
                    text = settings[3].replace("[user]", after.mention)
                    emb = discord.Embed(description=f"""{text}""", color=bot_colour)
                    await boost_channel.send(embed=emb, allowed_mentions=discord.AllowedMentions(everyone=True, users=True, roles=True))


def setup(bot):
    bot.add_cog(BoosterSystem(bot))



#######################################  Booster system interactions  #######################################


class SetBoosterChannel(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="on / off switch",
            style=discord.ButtonStyle.blurple,
            custom_id="on_off_switch_booster_system"
        )
    
    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            settings = await DatabaseCheck.check_booster_channel(guild_id = interaction.guild.id)

            await DatabaseUpdates.manage_booster_channel(guild_id = interaction.guild.id, operation = "update", status = 1 if settings[1] == 0 else 0)

            emb = discord.Embed(description=f"""## Booster channel has been {'enabled' if settings[1] == 0 else 'disabled'}
                {Emojis.dot_emoji} {f'From now on, all booster notifications will be sent in <#{settings[2]}>' if settings[1] != 0 else f'From now on, no more notifications will be sent in <#{settings[2]}>.'}
                {Emojis.help_emoji} If the system is activated, a notification is always sent to the booster channel when a user boosts the server""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            new_emb = discord.Embed(description=f"""## Set booster channel
                {Emojis.dot_emoji} With the buttons below you can activate or deactivate the booster channel currently the system is **{'deactivated' if settings[1] == 1 else 'activated'}**
                {Emojis.dot_emoji} Currently <#{settings[2]}> is the booster channel which you can change with the lower button
                {Emojis.help_emoji} If you want to see the current booster message use the `show booster message` button you can also edit the message with the `overwrite message` button""", color=bot_colour)
            await interaction.followup.edit_message(embed=new_emb, message_id=interaction.message.id)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class BoosterMessageModal(discord.ui.Modal):

    def __init__(self, *args, **kwargs):
        super().__init__(title="Enter a text for the booster message")
        self.add_item(discord.ui.InputText(label="Insert the text for the booster message here", style=discord.InputTextStyle.long))


    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            await DatabaseUpdates.manage_booster_channel(guild_id = interaction.guild.id, operation = "update", message = self.children[0].value)

            view = ShowBoosterMessage()
            view.add_item(CancelButton(system="booster channel system"))


            emb = discord.Embed(description=f"""## Booster message has been set
                {Emojis.dot_emoji} Booster message has been successfully overwritten
                {Emojis.dot_emoji} From now on this message will always be sent when someone boosts the server
                {Emojis.help_emoji} If you want to see what the message looks like use the `show booster message` button below""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=view)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class OverwriteBoosterChannel(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="overwrite booster channel", 
            style=discord.ButtonStyle.blurple,
            custom_id="overwrite_booster_channel")


    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            settings = await DatabaseCheck.check_booster_channel(guild_id = interaction.guild.id)

            emb = discord.Embed(description=f"""## Overwrite booster channel
                {Emojis.dot_emoji} With the lower select menu you can overwrite the booster channel, currently <#{settings[2]}> is set as booster channel
                {Emojis.dot_emoji} Select the channel to which you want all booster notifications to be sent
                {Emojis.help_emoji} Whenever someone boosts the server, a message will be sent to this channel""")
            await interaction.response.send_message(embed=emb, view=OverwriteBoosterChannelSelect())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)
 

class OverwriteBoosterChannelSelect(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system="booster channel system"))


    @discord.ui.channel_select(
        placeholder="Select a channel for the booster system!",
        custom_id="overwrite_booster_channel_select",
        min_values=1,
        max_values=1,
        channel_types=discord.ChannelType.text
    )

    async def overwrite_booster_channel_select(self, select, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            settings = await DatabaseCheck.check_booster_channel(guild_id = interaction.guild.id)

            if settings[2] == select.values[0].id:

                emb = discord.Embed(description=f"""## This channel is already set as a booster channel
                    {Emojis.dot_emoji} The channel <#{settings[2]}> is already set as a booster channel 
                    {Emojis.dot_emoji} Please choose another channel""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            else:
                
                view = ShowBoosterMessage()
                view.add_item(CancelButton(system="booster channel system"))

                emb = discord.Embed(description=f"""## The channel has been overwritten
                    {Emojis.dot_emoji} From now on <#{select.values[0].id}> is set as booster channel
                    {Emojis.dot_emoji} All booster notifications are now sent to this channel
                    {Emojis.help_emoji} Whenever someone boosts the server a message will be sent to this channel if you want to view this message use the `show booster message` button""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=view)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class ShowBoosterMessage(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    
    @discord.ui.button(
        label="show booster message",
        style=discord.ButtonStyle.blurple,
        custom_id="show_booster_message"
    )
    
    async def show_booster_messages(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            settings = await DatabaseCheck.check_booster_channel(guild_id = interaction.guild.id)

            view = View()
            view.add_item(OverwriteBoosterMessage())

            text = settings[3].replace("[user]", interaction.user.mention)

            emb = discord.Embed(description=f"""{text}""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=view, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class OverwriteBoosterMessage(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="overwrite booster message",
            style=discord.ButtonStyle.blurple,
            custom_id="overwrite_booster_message"
        )


    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            await interaction.response.send_modal(BoosterMessageModal())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class SetBoosterMessage(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="set booster message",
            style=discord.ButtonStyle.blurple,
            custom_id="set_booster_message"
        )


    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            await interaction.response.send_modal(BoosterMessageModal())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)