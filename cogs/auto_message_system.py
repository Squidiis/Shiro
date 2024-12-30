from utils import *
from sql_function import DatabaseCheck, DatabaseUpdates
from discord.ext import tasks


class AutoMessageSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.auto_message.start()


    async def check_lines_auto_message(text:str):

        match = re.search(r"<#(\d+)>", text)
        return int(match.group(1)) if match else None


    async def delete_old_auto_message(guild_id:int, channel_id:int = None, reset = None):

        channel = bot.get_channel(channel_id)

        if reset is not None:

            all_messages = await DatabaseCheck.check_auto_message(guild_id = guild_id)

            if all_messages is None:
                return
            
            for auto_message in all_messages:

                try:
                    
                    message = await DatabaseCheck.check_auto_message(guild_id = guild_id, channel_id = auto_message[1])

                    if message[2] is not None:

                        channel = bot.get_channel(message[1])
                        auto_message = await channel.fetch_message(message[2])
                        await auto_message.delete()

                except discord.NotFound:
                    pass

        else:

            auto_message = await DatabaseCheck.check_auto_message(guild_id = guild_id, channel_id = channel.id)

            if auto_message is None:
                return
            
            try:

                if auto_message[2] is not None:      
                        
                    auto_message = await channel.fetch_message(auto_message[2])
                    await auto_message.delete()

            except discord.NotFound:
                pass 

    
    async def update_auto_message_paginator(guild_id):

        all_pages = await DatabaseCheck.check_auto_message(guild_id = guild_id)

        pages = []

        if all_pages:

            embed = discord.Embed(description=f"""## Overview of all auto-messages
                {Emojis.dot_emoji} With the lower buttons you can scroll between the individual auto-messages
                {Emojis.dot_emoji} With the lower `delete` button you can delete single auto-messages
                {Emojis.dot_emoji} It is also possible to deactivate or activate individual auto-messages with the `on / off switch` button""", color=bot_colour)

            pages.append(embed)
            for page in all_pages:

                emb = discord.Embed(description=f"""## Auto-message
                    {Emojis.dot_emoji} This auto-message is assigned to the <#{page[1]}> channel and is sent every {page[5]} days
                    {Emojis.dot_emoji} Currently this auto-message {'switched on' if page[4] == 1 else 'switched off'}
                
                    ```{page[3] if page[3] != None else 'No message has been set for this channel yet'}```""", color=bot_colour)
                
                pages.append(emb)

        return pages


    @commands.slash_command(name = "set-auto-message", description = "Set the auto-message system!")
    @commands.has_permissions(administrator = True)
    async def set_auto_message(self, ctx:discord.ApplicationContext):

        check_settings = await DatabaseCheck.check_auto_message_settings(guild_id = ctx.guild.id)
        
        if check_settings == None:

            await DatabaseUpdates.manage_auto_message(operation = "insert", guild_id = ctx.guild.id)
            check_settings = await DatabaseCheck.check_auto_message_settings(guild_id = ctx.guild.id)

        view = SetAutoMessage()
        view.add_item(ShowAutoMessage())

        emb = discord.Embed(description=f"""## Set the auto-message system
            {Emojis.dot_emoji} Currently the auto-message system is {'enabled' if check_settings[1] == 1 else 'disabled'}
            {Emojis.dot_emoji} If you want to add a new auto-message use the `add new auto message` button
            {Emojis.dot_emoji} With the `show auto-message` button you can view all already set auto-messages""", color=bot_colour)
        await ctx.respond(embed=emb, view=view)

        
    @commands.slash_command(name = "add-auto-message", description = "Add a new auto-message!")
    @commands.has_permissions(administrator = True)
    async def add_auto_message(self, ctx:discord.ApplicationContext, 
        channel:Option(discord.TextChannel, description="Select a channel in which the auto-message should be sent!"), 
        interval:Option(int, min_value=1, max_value=30, description="Specifies an interval after how many days the message should always be sent!")):

        check_channel = await DatabaseCheck.check_auto_message(guild_id = ctx.guild.id, channel_id = channel.id)

        if check_channel:

            if check_channel[5] != interval and check_channel[1] == channel.id:

                emb = discord.Embed(description=f"""## An auto-message has already been defined for this channel
                    {Emojis.dot_emoji} An auto-message has already been defined for the channel {channel.mention}, currently with an interval of {check_channel[5]} {'days' if check_channel[5] != 1 else 'day'}
                    {Emojis.dot_emoji} Do you want to overwrite this with the interval of {interval} {'days' if check_channel[5] != 1 else 'day'}?""", color=bot_colour)
                await ctx.respond(embed=emb, view=OverwriteIntervalAutoMessage(interval = interval))

            elif check_channel[2] != None:

                emb = discord.Embed(description=f"""## An auto-message has already been defined for this channel
                    {Emojis.dot_emoji} An auto-message has already been defined for the channel {channel.mention} and a message has also already been defined
                    The following message has already been set:
                    ```{check_channel[3]}```
                    {Emojis.dot_emoji} Do you want to overwrite the message?
                    {Emojis.help_emoji} With the lower button `edit message` you can overwrite the message""", color=bot_colour)
                await ctx.respond(embed=emb, view=EditAutoMessage())

            else:
                
                emb = discord.Embed(description=f"""## This channel has already been selected for an auto-message
                    {Emojis.dot_emoji} No message has been set for the channel {channel.mention}
                    {Emojis.dot_emoji} Do you want to set a message now? 
                    {Emojis.help_emoji} You can add a auto-message with the `edit message` button below""", color=bot_colour)
                await ctx.respond(embed=emb, view=EditAutoMessage())

        else:

            settings = await DatabaseCheck.check_auto_message_settings(guild_id = ctx.guild.id)

            if settings is None:

                await DatabaseUpdates.manage_auto_message(guild_id = ctx.guild.id, operation = "insert")

            await DatabaseUpdates.manage_auto_message(guild_id = ctx.guild.id, channel_id = channel.id, operation = "insert", interval = interval)

            emb = discord.Embed(description=f"""## A channel for the auto-message has been defined
                {Emojis.dot_emoji} The channel {channel.mention} is now equipped with a auto-message
                {Emojis.dot_emoji} Please set a text for the auto-message now
                {Emojis.help_emoji} Press the lower button `add message` to add the text""", color=bot_colour)
            await ctx.respond(embed=emb, view=AddAutoMessageText())
    

    @commands.slash_command(name = "remove-auto-message", description = "Remove an auto-message!")
    @commands.has_permissions(administrator = True)
    async def remove_auto_message(self, ctx:discord.ApplicationContext, 
        channel:Option(discord.TextChannel, description="Specify the channel from which the auto-message should be removed!")):

        check_channel = await DatabaseCheck.check_auto_message(guild_id = ctx.guild.id, channel_id = channel.id)

        if check_channel:
                
            emb = discord.Embed(description=f"""## The auto-message has been deleted
                {Emojis.dot_emoji} The auto-message for the channel {channel.mention} has been deleted
                {Emojis.dot_emoji} You can create a new auto-message at any time using the `/add-auto-message` command""", color=bot_colour)
            await ctx.respond(embed=emb)

            await DatabaseUpdates.manage_auto_message(guild_id = ctx.guild.id, channel_id = channel.id, operation = "delete")
            await AutoMessageSystem.delete_old_auto_message(guild_id = ctx.guild.id, channel_id = channel.id)

        else:

            view = View()
            view.add_item(ShowAutoMessage())

            emb = discord.Embed(description=f"""## There is no auto-message for this channel
                {Emojis.dot_emoji} No auto-message was found
                {Emojis.dot_emoji} With the buttons below you can view the current auto-messages""", color=bot_colour)
            await ctx.respond(embed=emb, view=view)


    @commands.slash_command(name = "show-auto-message", description = "Shows you all auto-messages that have been created for this server!")
    async def show_auto_message(self, ctx:discord.ApplicationContext):

        pages = await AutoMessageSystem.update_auto_message_paginator(guild_id=ctx.guild.id)

        if pages != []:

            paginator_view = PaginatorViewAutoMessage(pages=pages)
            paginator_view.add_item(CancelButton(system="auto message system"))
            await ctx.respond(embed=pages[0], view=paginator_view)

        else:

            await ctx.respond(embed=GetEmbed.get_embed(embed_index=14), view=None)


    @commands.slash_command(name = "reset-auto-message", description = "Deletes all auto-messages created on this server!")
    @commands.has_permissions(administrator = True)
    async def reset_auto_message(self, ctx:discord.ApplicationContext):

        check_channel = await DatabaseCheck.check_auto_message(guild_id = ctx.guild.id)

        if check_channel:
                
            emb = discord.Embed(description=f"""## Auto-messages have been reset
                {Emojis.dot_emoji} All auto-messages have been deleted
                {Emojis.dot_emoji} You can easily create new auto-message at any time by using the `/add-auto-message` command""", color=bot_colour)
            await ctx.respond(embed=emb)

            await AutoMessageSystem.delete_old_auto_message(guild_id = ctx.guild.id, reset = True)
            await DatabaseUpdates.manage_auto_message(guild_id = ctx.guild.id, operation = "delete")

        else:

            await ctx.respond(embed=GetEmbed.get_embed(embed_index=14))


    @tasks.loop(hours=12)
    async def auto_message(self):

        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:

            settings = await DatabaseCheck.check_auto_message_settings(guild_id = guild.id)
            
            if settings is None or settings[1] == 0:
                return
            
            auto_messages = await DatabaseCheck.check_auto_message(guild_id = guild.id)

            if auto_messages is None:
                return
            
            for message in auto_messages:
              
                if message[4] == 0:
                    return

                current_time = datetime.utcnow()
                difference = current_time - message[6]

                if difference > timedelta(days=message[5]):
                    channel = bot.get_channel(message[1])

                    try:

                        old_message = await channel.fetch_message(message[2])
                        await old_message.delete()

                    except discord.NotFound:
                        pass 

                    emb = discord.Embed(description=f"""{message[3]}""", color=bot_colour)
                    new_message = await channel.send(embed=emb)
                    await DatabaseUpdates.manage_auto_message(guild_id = guild.id, message_id = new_message.id, send_time = new_message.created_at, channel_id = new_message.channel.id, operation = "update")


def setup(bot):
    bot.add_cog(AutoMessageSystem(bot))



#######################################  Auto-message system interactions  #######################################
    

class OverwriteIntervalAutoMessage(discord.ui.View):

    def __init__(self, interval):
        super().__init__(timeout=None)
        self.interval = interval
        self.add_item(CancelButton(system="auto message system"))

    
    @discord.ui.button(
        label="overrite interval",
        style=discord.ButtonStyle.blurple,
        custom_id="overwrite_interval_auto_message"        
    )

    async def overwrite_interval_auto_message(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            if self.interval == None:

                emb = discord.Embed(description=f"""## An error has occurred
                    {Emojis.dot_emoji} I have lost the connection, therefore the interval could not be overwritten
                    {Emojis.help_emoji} Please try again later by simply executing the command again""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

            channel_id = await AutoMessageSystem.check_lines_auto_message(text=interaction.message.embeds[0].description)
            settings = await DatabaseCheck.check_auto_message(guild_id = interaction.guild.id, channel_id = channel_id)
            
            view = View()
            view.add_item(ShowAutoMessage())
            view.add_item(CancelButton(system="auto-message system"))

            await DatabaseUpdates.manage_auto_message(guild_id = interaction.guild.id, operation = "update", channel_id = channel_id, interval = self.interval)

            emb = discord.Embed(description=f"""## Interval was overwritten
                {Emojis.dot_emoji} The interval was overwritten from {settings[5]} {'days' if settings[5] != 1 else 'day'} to {self.interval} {'days' if self.interval != 1 else 'day'} 
                {Emojis.dot_emoji} From now on, a message will be sent in <#{channel_id}> every {self.interval} {'days' if self.interval != 1 else 'day'} 
                {Emojis.help_emoji} If you want to see the message press the button below""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=view)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class SetAutoMessage(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "auto-message system"))

    
    @discord.ui.button(
        label="on / off switch",
        style=discord.ButtonStyle.blurple,
        custom_id="on_off_switch_auto_message_system"
    )

    async def auto_message_on_off_system(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            check_status = await DatabaseCheck.check_auto_message_settings(guild_id = interaction.guild.id)
            await DatabaseUpdates.manage_auto_message(guild_id = interaction.guild.id, operation = "update_settings", status = 0 if check_status[1] == 1 else 1)

            emb = discord.Embed(description=f"""## The auto-message system has been {'deactivated' if check_status[1] == 1 else 'activated'}
                {Emojis.dot_emoji} {'From now on all auto messages are no longer active' if check_status[1] == 1 else 'From now on all auto-messages are active and will be sent for the specified interval'}
                {Emojis.help_emoji} If you {'activate the system again all auto-messages that have not been manually deactivated are sent to the previously specified channels at the specified interval' 
                    if check_status[1] == 1 else 'deactivate the auto-messages are no longer automatically sent to the specified channel'}""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class EditAutoMessage(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton("auto-message system"))


    @discord.ui.button(label="edit auto message", style=discord.ButtonStyle.blurple, custom_id="edit_auto_message")
    async def callback(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            channel_id = await AutoMessageSystem.check_lines_auto_message(text=interaction.message.embeds[0].description)
            channel = bot.get_channel(channel_id)

            await interaction.response.send_modal(AutoMessageModal(channel=channel))

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class AddAutoMessageText(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "AUto-message system"))


    @discord.ui.button(
        label="add message",
        style=discord.ButtonStyle.blurple,
        custom_id="add_message_auto_message"
    )

    async def auto_message_text(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            channel_id = await AutoMessageSystem.check_lines_auto_message(text=interaction.message.embeds[0].description)
            channel = bot.get_channel(channel_id)

            await interaction.response.send_modal(AutoMessageModal(channel=channel))

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class ShowAutoMessage(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="show auto message",
            style=discord.ButtonStyle.blurple,
            custom_id="show_auto_message_button"
        )


    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            pages = await AutoMessageSystem.update_auto_message_paginator(guild_id=interaction.guild.id)

            if pages != []:

                paginator_view = PaginatorViewAutoMessage(pages=pages)
                paginator_view.add_item(CancelButton(system="auto message system"))
                await interaction.response.send_message(embed=pages[0], view=paginator_view)

            else:

                await interaction.response.send_message(embed=GetEmbed.get_embed(embed_index=14), view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)
    



class PaginatorViewAutoMessage(discord.ui.View):

    def __init__(self, pages):
        super().__init__(timeout=None)
        self.pages = pages
        self.current_page = 0
        self.update_buttons_auto_message()


    def update_buttons_auto_message(self):

        self.children[0].disabled = self.current_page == 0  
        self.children[1].disabled = self.current_page == 0  
        self.children[2].disabled = self.current_page == len(self.pages) - 1 
        self.children[3].disabled = self.current_page == len(self.pages) - 1  


    async def update_message_auto_message(self, interaction):
        self.update_buttons_auto_message()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)


    @discord.ui.button(
        label="To the first page", 
        style=discord.ButtonStyle.blurple,
        custom_id="to_first_page_auto_message"
    )
    
    async def go_to_first_page_auto_message(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            self.current_page = 0
            await self.update_message_auto_message(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="Back", 
        style=discord.ButtonStyle.blurple,
        custom_id="back_auto_message"
    )

    async def back_button_auto_message(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            
            if self.current_page > 0:
                self.current_page -= 1
            await self.update_message_auto_message(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="Next", 
        style=discord.ButtonStyle.blurple,
        custom_id="next_auto_message"
    )

    async def next_button_auto_message(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            if self.current_page < len(self.pages) - 1:
                self.current_page += 1
            await self.update_message_auto_message(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="To the last page", 
        style=discord.ButtonStyle.blurple,
        custom_id="to_last_page_auto_message"
    )

    async def go_to_last_page_auto_message(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            self.current_page = len(self.pages) - 1
            await self.update_message_auto_message(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="on / off switch", 
        style=discord.ButtonStyle.blurple, 
        row=2,
        custom_id="on_off_switch_auto_message_message"
    )

    async def on_off_switch_auto_message(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            embed_text = interaction.message.embeds[0].description
        
            channel_id = await AutoMessageSystem.check_lines_auto_message(text=embed_text)
            channel = await bot.fetch_channel(int(channel_id))
            if channel_id:

                settings = await DatabaseCheck.check_auto_message(guild_id = interaction.guild.id, channel_id=int(channel_id))

                emb = discord.Embed(description=f"""## Auto message has been {'deactivated' if settings[4] == 1 else 'activated'}
                    {Emojis.dot_emoji} The Auto message for the channel {channel.mention} is now {'disabled' if settings[4] == 1 else 'enabled'}
                    {Emojis.dot_emoji} {'From now on this message will no longer be sent regularly' 
                        if settings[4] == 1 else 'The auto-message was sent to the specified channel'}""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

                if settings[4] == 0:
                    
                    emb = discord.Embed(description=f"""{settings[3]}""", color=bot_colour)

                    message = await channel.fetch_message(settings[2])
                    await message.delete()

                    new_message = await channel.send(embed=emb)
                    await DatabaseUpdates.manage_auto_message(guild_id = interaction.guild.id, message_id = new_message.id, channel_id = channel.id, operation = "update", status = 0 if settings[4] == 1 else 1, send_time = new_message.created_at)
                
                elif settings[4] == 1:

                    await DatabaseUpdates.manage_auto_message(guild_id = interaction.guild.id, channel_id = channel.id, operation = "update", status = 0 if settings[4] == 1 else 1)

                paginator_embed = await AutoMessageSystem.update_auto_message_paginator(guild_id=interaction.guild.id)

                if paginator_embed != []:

                    await interaction.followup.edit_message(embed=paginator_embed[self.current_page], message_id=interaction.message.id)
            
            else:

                await interaction.response.send_message(embed=GetEmbed.get_embed(embed_index=12), view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)
    

    @discord.ui.button(
        label="delete", 
        style=discord.ButtonStyle.blurple, 
        row=2,
        custom_id="delete_auto_message"
    )

    async def delete_entry_auto_message(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            embed_text = interaction.message.embeds[0].description
            channel_id = await AutoMessageSystem.check_lines_auto_message(text=embed_text)

            if channel_id:
                
                emb = discord.Embed(description=f"""## Auto-message has been deleted
                    {Emojis.dot_emoji} The auto-message has been successfully deleted, the message already sent was also deleted
                    {Emojis.dot_emoji} You can easily create a new auto-message at any time by using the `/add-auto-message` command""", color=bot_colour)
                await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

                await DatabaseUpdates.manage_auto_message(guild_id = interaction.guild.id, channel_id = int(channel_id), operation = "delete")
                
                paginator_embed = await AutoMessageSystem.update_auto_message_paginator(guild_id=interaction.guild.id)

                await interaction.followup.edit_message(embed=paginator_embed[0], message_id=interaction.message.id)

                await AutoMessageSystem.delete_old_auto_message(guild_id = interaction.guild.id, channel_id = channel_id)

            else:

                await interaction.response.send_message(embed=GetEmbed.get_embed(embed_index=12), view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="overwrite channel", 
        style=discord.ButtonStyle.blurple, 
        row=2,
        custom_id="overwrite_channel_auto_message"
    )

    async def overwrite_channel_auto_message(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            embed_text = interaction.message.embeds[0].description
            channel_id = await AutoMessageSystem.check_lines_auto_message(text=embed_text)

            if channel_id:

                auto_message = await DatabaseCheck.check_auto_message(guild_id = interaction.guild.id, channel_id = channel_id)
                channel = bot.get_channel(auto_message[1])

                emb = discord.Embed(description=f"""## New channel has been defined
                    {Emojis.dot_emoji} With the lower select menu you can define a new channel <#{channel.id}> for the following auto message:
                    ```{auto_message[3]}```
                    {Emojis.help_emoji} This is currently set for the following channel <#{auto_message[1]}>""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=OverwriteChannelSelectAutoMessage())
                
            else:

                await interaction.response.send_message(embed=GetEmbed.get_embed(embed_index=12), view=None, ephemeral=True)   

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None) 


    @discord.ui.button(
        label="edit auto message", 
        style=discord.ButtonStyle.blurple, 
        row=2,
        custom_id="edit_auto_message"
    )

    async def overwrite_message_auto_message(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            embed_text = interaction.message.embeds[0].description
            channel_id = await AutoMessageSystem.check_lines_auto_message(text=embed_text)

            if channel_id:

                channel = bot.get_channel(channel_id)
                await interaction.response.send_modal(AutoMessageModal(channel=channel))

            else:

                await interaction.response.send_message(embed=GetEmbed.get_embed(embed_index=12), view=None, ephemeral=True) 

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



class OverwriteChannelSelectAutoMessage(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system="auto message system"))


    @discord.ui.channel_select(
        placeholder="Choose a channel with which you want to overwrite the old one!",
        max_values=1,
        min_values=1,
        custom_id="overwrite_channel_auto_message",
        channel_types=[discord.ChannelType.text]
    )
    
    async def overwrite_channel_select_auto_message(self, select, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            channel = await DatabaseCheck.check_auto_message(guild_id = interaction.guild.id, channel_id = select.values[0].id)

            if channel is not None:
                
                emb = discord.Embed(description=f"""## This channel is already occupied
                    {Emojis.dot_emoji} A auto-message has already been defined for the channel
                    {Emojis.dot_emoji} Only one auto-message can exist per channel
                    {Emojis.help_emoji} Please select another channel""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            else:

                embed_text = interaction.message.embeds[0].description
                channel_id = await AutoMessageSystem.check_lines_auto_message(text=embed_text)
                
                auto_message = await DatabaseCheck.check_auto_message(guild_id = interaction.guild.id, channel_id = channel_id)

                emb = discord.Embed(description=f"""## channel has been successfully changed
                    {Emojis.dot_emoji} From now on the channel: <#{select.values[0].id}> is used for the following auto-message:
                    ```{auto_message[3]}```""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

                await DatabaseUpdates.manage_auto_message(guild_id = interaction.guild.id, channel_id = channel_id, channel_id_new = select.values[0].id, operation = "update")
                await AutoMessageSystem.delete_old_auto_message(guild_id = interaction.guild.id, channel_id = channel_id)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class AutoMessageModal(discord.ui.Modal):

    def __init__(self, channel,*args, **kwargs):
        self.channel = channel
        super().__init__(
            title="Define a text for the auto message",
            timeout=None,
            custom_id="add_auto_message_modal"
        )
        self.add_item(discord.ui.InputText(label="Enter the text for the auto message here", style=discord.InputTextStyle.paragraph, placeholder="Write the text for the auto message here", max_length=3000))


    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:
       
            await AutoMessageSystem.delete_old_auto_message(guild_id = interaction.guild.id, channel_id = self.channel.id)

            emb = discord.Embed(description=self.children[0].value, color=bot_colour)

            message = await self.channel.send(embed=emb)

            await DatabaseUpdates.manage_auto_message(guild_id = interaction.guild.id, message = self.children[0].value, message_id = message.id, channel_id = self.channel.id, operation = "update", send_time = message.created_at)
            
            view = View()
            view.add_item(ShowAutoMessage())

            emb = discord.Embed(description=f"""## Text defined for the auto-message
                {Emojis.dot_emoji} Auto message text has been set for the channel <#{self.channel.id}>
                {Emojis.dot_emoji} The following text has been set:
                ```{self.children[0].value}```
                {Emojis.help_emoji} With the button below you can also view the other auto messages""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=view)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)