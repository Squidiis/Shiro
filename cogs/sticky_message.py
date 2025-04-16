from discord.interactions import Interaction
from utils import *
from discord.ext import tasks
from sql_function import *
from datetime import timezone
from typing import Union


class StickyMessage(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.check_sticky_message_task.start()


    async def add_views(self):

        return [
            SetStickyMessage(),
            PaginatorViewStickyMessage(pages=[no_page]),
            OverwriteChannelSelect(),
            AddStickyMessageText(),
            EditStickyMessage()
            ]


    async def update_paginator(guild_id):

        all_pages = await DatabaseCheck.check_sticky_message(guild_id = guild_id)

        pages = []

        if all_pages:

            embed = discord.Embed(description=f"""## Overview of all sticky messages
                {Emojis.dot_emoji} With the lower buttons you can scroll between the individual sticky messages
                {Emojis.dot_emoji} With the lower `delete` button you can delete single sticky messages
                {Emojis.dot_emoji} It is also possible to deactivate or activate individual sticky messages with the `on / off switch` button""", color=bot_colour)

            pages.append(embed)
            for page in all_pages:

                emb = discord.Embed(description=f"""## Sticky message
                    {Emojis.dot_emoji} This sticky message is assigned to the channel <#{page[1]}>
                    {Emojis.dot_emoji} Currently this sticky message {'switched on' if page[4] == 1 else 'switched off'}
                
                    ```{page[3] if page[3] != None else 'No message has been set for this channel yet'}```""", color=bot_colour)
                
                pages.append(emb)

        return pages
    

    async def delete_old_sticky_message(guild_id:int, channel_id:int = None, reset = None):

        channel = bot.get_channel(channel_id)

        if reset is not None:

            all_messages = await DatabaseCheck.check_sticky_message(guild_id = guild_id)

            if all_messages is None:
                return

            for sticky_message in all_messages:

                try:
                    
                    message = await DatabaseCheck.check_sticky_message(guild_id = guild_id, channel_id = sticky_message[1])

                    if message[2] is not None:

                        channel = bot.get_channel(message[1])
                        sticky_message = await channel.fetch_message(message[2])
                        await sticky_message.delete()

                except discord.NotFound:
                    pass

        else:

            sticky_message = await DatabaseCheck.check_sticky_message(guild_id = guild_id, channel_id = channel.id)

            if sticky_message is None:
                return

            try:

                if sticky_message[2] is not None:      
                        
                    sticky_message = await channel.fetch_message(sticky_message[2])
                    await sticky_message.delete()

            except discord.NotFound:
                pass 


    @commands.slash_command(name = "set-sticky-message", description = "Set the sticky message system!")
    @commands.has_permissions(administrator = True)
    async def set_sticky_message(self, ctx:discord.ApplicationContext):

        check_settings = await DatabaseCheck.check_sticky_message_settings(guild_id = ctx.guild.id)
        
        if check_settings == None:

            await DatabaseUpdates.manage_sticky_message(operation = "insert", guild_id = ctx.guild.id)
            check_settings = await DatabaseCheck.check_sticky_message_settings(guild_id = ctx.guild.id)

        view = SetStickyMessage()
        view.add_item(ShowStickyMessage())

        emb = discord.Embed(description=f"""## Set the sticky message system
            {Emojis.dot_emoji} Currently the sticky message system is {'enabled' if check_settings[1] == 1 else 'disabled'}
            {Emojis.dot_emoji} If you want to add a new sticky message use the `add new sticky message` button
            {Emojis.dot_emoji} With the `show sticky message` button you can view all already set sticky messages""", color=bot_colour)
        await ctx.respond(embed=emb, view=view)

    
    @commands.slash_command(name = "add-sticky-message", description = "Add a sticky message of your choice!")
    @commands.has_permissions(administrator = True)
    @discord.option("channel", discord.TextChannel, description="Select a channel for a sticky message", required=True)
    async def add_sticky_message(self, ctx:discord.ApplicationContext, channel:discord.TextChannel):

        check_channel = await DatabaseCheck.check_sticky_message(guild_id = ctx.guild.id, channel_id = channel.id)

        if check_channel:

            if check_channel[2] != None:

                emb = discord.Embed(description=f"""## The channel has already been selected for a sticky message
                    {Emojis.dot_emoji} An sticky message has already been defined for the channel {channel.mention} and a message has also already been defined
                    The following message has already been set:
                    ```{check_channel[3]}````
                    {Emojis.dot_emoji} Do you want to overwrite the message?
                    {Emojis.help_emoji} With the lower button `edit message` you can overwrite the message""", color=bot_colour)
                await ctx.respond(embed=emb, view=EditStickyMessage())

            else:
                
                emb = discord.Embed(description=f"""## This channel has already been selected for a sticky message
                    {Emojis.dot_emoji} No message has been set for the channel {channel.mention}
                    {Emojis.dot_emoji} Do you want to set a message now? 
                    {Emojis.help_emoji} You can add a sticky message with the `edit message` button below""", color=bot_colour)
                await ctx.respond(embed=emb, view=EditStickyMessage())

        else:

            settings = await DatabaseCheck.check_sticky_message_settings(guild_id = ctx.guild.id)

            if settings is None:

                await DatabaseUpdates.manage_sticky_message(guild_id = ctx.guild.id, operation = "insert")

            await DatabaseUpdates.manage_sticky_message(guild_id = ctx.guild.id, channel_id = channel.id, operation = "insert")

            emb = discord.Embed(description=f"""## A channel for this sticky message has been defined
                {Emojis.dot_emoji} The channel {channel.mention} is now equipped with a sticky message
                {Emojis.dot_emoji} Please set a text for the sticky message now
                {Emojis.help_emoji} Press the lower button `add message` to add the text""", color=bot_colour)
            await ctx.respond(embed=emb, view=AddStickyMessageText())

    
    @commands.slash_command(name = "remove-sticky-message", description = "Deletes a sticky message!")
    @commands.has_permissions(administrator = True)
    @discord.option("channel", discord.TextChannel, description="Choose which sticky message you want to delete", required=True)
    async def remove_sticky_message(self, ctx:discord.ApplicationContext, channel:discord.TextChannel):

        check_channel = await DatabaseCheck.check_sticky_message(guild_id = ctx.guild.id, channel_id = channel.id)

        if check_channel:
                
            emb = discord.Embed(description=f"""## Sticky message has been deleted
                {Emojis.dot_emoji} The sticky message for the channel {channel.mention} has been deleted
                {Emojis.dot_emoji} You can create a new sticky message at any time using the `/add-sticky-message` command""", color=bot_colour)
            await ctx.respond(embed=emb)

            await DatabaseUpdates.manage_sticky_message(guild_id = ctx.guild.id, channel_id = channel.id, operation = "delete")
            await StickyMessage.delete_old_sticky_message(guild_id = ctx.guild.id, channel_id = channel.id)

        else:

            view = View()
            view.add_item(ShowStickyMessage())

            emb = discord.Embed(description=f"""## There is no sticky message for this channel
                {Emojis.dot_emoji} No sticky message was found
                {Emojis.dot_emoji} With the buttons below you can view the current sticky messages""", color=bot_colour)
            await ctx.respond(embed=emb, view=view)


    @commands.slash_command(name = "show-sticky-message", description = "Shows all sticky messages!")
    @commands.has_permissions(administrator = True)
    async def show_sticky_message(self, ctx:discord.ApplicationContext):

        pages = await StickyMessage.update_paginator(guild_id=ctx.guild.id)

        if pages != []:

            paginator_view = PaginatorViewStickyMessage(pages=pages)
            paginator_view.add_item(CancelButton(system="sticky message system"))
            await ctx.respond(embed=pages[0], view=paginator_view)

        else:

            await ctx.respond(embed=GetEmbed.get_embed(embed_index=13), view=None)

    
    @commands.slash_command(name = "reset-sticky-message", description = "Resets all sticky messages!")
    @commands.has_permissions(administrator = True)
    async def reset_sticky_message(self, ctx:discord.ApplicationContext):

        check_channel = await DatabaseCheck.check_sticky_message(guild_id = ctx.guild.id)

        if check_channel:
                
            emb = discord.Embed(description=f"""## Sticky messages have been reset
                {Emojis.dot_emoji} All sticky messages have been deleted
                {Emojis.dot_emoji} You can easily create new sticky message at any time by using the `/add-sticky-message` command""", color=bot_colour)
            await ctx.respond(embed=emb)

            await StickyMessage.delete_old_sticky_message(guild_id = ctx.guild.id, reset = True)
            await DatabaseUpdates.manage_sticky_message(guild_id = ctx.guild.id, operation = "delete")

        else:

            await ctx.respond(embed=GetEmbed.get_embed(embed_index=13))
    

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        if message.author.bot or isinstance(message.channel, discord.DMChannel):
            return

        settings = await DatabaseCheck.check_sticky_message_settings(guild_id = message.guild.id)

        if settings is None or settings[1] == 0:
            return

        sticky_message = await DatabaseCheck.check_sticky_message(guild_id = message.guild.id, channel_id = message.channel.id)

        if sticky_message:

            await asyncio.sleep(10)

            async for recent_message in message.channel.history(limit=1):
                if recent_message.id != message.id:
                    return

            try:
                old_message = await message.channel.fetch_message(sticky_message[2])
                await old_message.delete()
            except discord.NotFound:
                pass 
                
            emb = discord.Embed(description=f"""{sticky_message[3]}""", color=bot_colour)
                
            new_message = await message.channel.send(embed=emb, allowed_mentions=discord.AllowedMentions(everyone=True, users=True, roles=True))
            await DatabaseUpdates.manage_sticky_message(guild_id = message.guild.id, channel_id = message.channel.id, message_id = new_message.id, operation = "update")
            

    @tasks.loop(hours=24)
    async def check_sticky_message_task(self):

        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:
            
            settings = await DatabaseCheck.check_sticky_message_settings(guild_id = guild.id)
           
            if settings is None:
                return

            if settings[1] == 0:
                return
            
            all_sticky_messages = await DatabaseCheck.check_sticky_message(guild_id = guild.id)
            
            if all_sticky_messages is None:
                return

            for sticky_message in all_sticky_messages:
                
                if sticky_message[4] == 0:
                    continue

                channel = bot.get_channel(sticky_message[1])
                is_latest = False

                async for recent_message in channel.history(limit=1):
                    if recent_message.id == sticky_message[2]:
                        is_latest = True

                if is_latest:
                    continue
                
                try:
                    old_message = await channel.fetch_message(sticky_message[2])
                    await old_message.delete()
                except discord.NotFound:
                    pass
                    
                emb = discord.Embed(description=f"""{sticky_message[3]}""", color=bot_colour)
                message = await channel.send(embed=emb)
                await DatabaseUpdates.manage_sticky_message(guild_id = guild.id, channel_id = channel.id, message_id = message.id, operation = "update")



            

def setup(bot):
    bot.add_cog(StickyMessage(bot))



#######################################  Sticky message system interactions  #######################################


class SetStickyMessage(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "sticky message system"))

    
    @discord.ui.button(
        label="on / off switch",
        style=discord.ButtonStyle.blurple,
        custom_id="on_off_switch_sticky_message_system"
    )

    async def sticky_message_on_off_system(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            check_status = await DatabaseCheck.check_sticky_message_settings(guild_id = interaction.guild.id)
            await DatabaseUpdates.manage_sticky_message(guild_id = interaction.guild.id, operation = "update_settings", status = 0 if check_status[1] == 1 else 1)

            emb = discord.Embed(description=f"""## The sticky message system has been {'deactivated' if check_status[1] == 1 else 'activated'}
                {Emojis.dot_emoji} {'From now on all sticky messages are no longer active' if check_status[1] == 1 else 'From now on all sticky messages are active and will always be displayed at the end of the chat'}
                {Emojis.help_emoji} If you activate the system again {'all sticky messages that have not been deactivated manually will be placed at the end of the chat again' 
                    if check_status[1] == 1 else 'deactivate the sticky messages will no longer be displayed at the end of the chat'}""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class PaginatorViewStickyMessage(discord.ui.View):

    def __init__(self, pages):
        super().__init__(timeout=None)
        self.pages = pages
        self.current_page = 0
        self.update_buttons()


    def update_buttons(self):

        self.children[0].disabled = self.current_page == 0  
        self.children[1].disabled = self.current_page == 0  
        self.children[2].disabled = self.current_page == len(self.pages) - 1 
        self.children[3].disabled = self.current_page == len(self.pages) - 1  


    async def update_message(self, interaction):
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)


    @discord.ui.button(
        label="To the first page", 
        style=discord.ButtonStyle.blurple,
        custom_id="to_first_page_sticky_message"
    )
    
    async def go_to_first_page(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            self.current_page = 0
            await self.update_message(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="Back", 
        style=discord.ButtonStyle.blurple,
        custom_id="back_sticky_message"
    )

    async def back_button(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            
            if self.current_page > 0:
                self.current_page -= 1
            await self.update_message(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="Next", 
        style=discord.ButtonStyle.blurple,
        custom_id="next_sticky_message"
    )

    async def next_button(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            if self.current_page < len(self.pages) - 1:
                self.current_page += 1
            await self.update_message(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="To the last page", 
        style=discord.ButtonStyle.blurple,
        custom_id="to_last_page_sticky_message"
    )

    async def go_to_last_page(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            self.current_page = len(self.pages) - 1
            await self.update_message(interaction)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="on / off switch", 
        style=discord.ButtonStyle.blurple, 
        row=2,
        custom_id="on_off_switch_sticky_message"
    )

    async def on_off_switch_sticky_message(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            embed_text = interaction.message.embeds[0].description
        
            channel_id = await extracts_channel_id(text=embed_text)
            channel = await bot.fetch_channel(int(channel_id))
            if channel_id:

                settings = await DatabaseCheck.check_sticky_message(guild_id = interaction.guild.id, channel_id=int(channel_id))

                emb = discord.Embed(description=f"""## Sticky message has been {'deactivated' if settings[4] == 1 else 'activated'}
                    {Emojis.dot_emoji} The sticky message for the channel {channel.mention} is now {'disabled' if settings[4] == 1 else 'enabled'}
                    {Emojis.dot_emoji} {'From now on, the message will no longer be placed at the end of the channel but will remain in the channel' 
                        if settings[4] == 1 else 'The sticky message has been moved to the end of the channel again'}""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

                if settings[4] == 0:
                    
                    emb = discord.Embed(description=f"""{settings[3]}""", color=bot_colour)

                    message = await channel.fetch_message(settings[2])
                    await message.delete()

                    new_message = await channel.send(embed=emb, allowed_mentions=discord.AllowedMentions(everyone=True, users=True, roles=True))
                    await DatabaseUpdates.manage_sticky_message(guild_id = interaction.guild.id, message_id = new_message.id, channel_id = channel.id, operation = "update", status = 0 if settings[4] == 1 else 1)
                
                elif settings[4] == 1:

                    await DatabaseUpdates.manage_sticky_message(guild_id = interaction.guild.id, channel_id = channel.id, operation = "update", status = 0 if settings[4] == 1 else 1)

                paginator_embed = await StickyMessage.update_paginator(guild_id=interaction.guild.id)

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
        custom_id="delete_sticky_message"
    )

    async def delete_entry_sticky_message(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            embed_text = interaction.message.embeds[0].description
            channel_id = await extracts_channel_id(text=embed_text)

            if channel_id:
                
                emb = discord.Embed(description=f"""## Sticky message has been deleted
                    {Emojis.dot_emoji} The sticky message has been successfully deleted, the message already sent was also deleted
                    {Emojis.dot_emoji} You can easily create a new sticky message at any time by using the `/add-sticky-message` command""", color=bot_colour)
                await interaction.response.send_message(embed=emb, ephemeral=True, view=None)

                await DatabaseUpdates.manage_sticky_message(guild_id = interaction.guild.id, channel_id = int(channel_id), operation = "delete")
                
                paginator_embed = await StickyMessage.update_paginator(guild_id=interaction.guild.id)

                await interaction.followup.edit_message(embed=paginator_embed[0], message_id=interaction.message.id)

                await StickyMessage.delete_old_sticky_message(guild_id = interaction.guild.id, channel_id = channel_id)

            else:

                await interaction.response.send_message(embed=GetEmbed.get_embed(embed_index=12), view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="overwrite channel", 
        style=discord.ButtonStyle.blurple, 
        row=2,
        custom_id="overwrite_channel_sticky_message"
    )

    async def overwrite_channel_sticky_message(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            embed_text = interaction.message.embeds[0].description
            channel_id = await extracts_channel_id(text=embed_text)

            if channel_id:

                sticky_message = await DatabaseCheck.check_sticky_message(guild_id = interaction.guild.id, channel_id = channel_id)
                channel = bot.get_channel(sticky_message[1])

                emb = discord.Embed(description=f"""## New channel has been defined
                    {Emojis.dot_emoji} With the lower select menu you can define a new channel <#{channel.id}> for the following sticky message:
                    ```{sticky_message[3]}```
                    {Emojis.help_emoji} This is currently set for the following channel <#{sticky_message[1]}>""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=OverwriteChannelSelect())
                
            else:

                await interaction.response.send_message(embed=GetEmbed.get_embed(embed_index=12), view=None, ephemeral=True)   

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None) 


    @discord.ui.button(
        label="edit sticky message", 
        style=discord.ButtonStyle.blurple, 
        row=2,
        custom_id="overwrite_message_sticky_message"
    )

    async def overwrite_message_sticky_message(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            embed_text = interaction.message.embeds[0].description
            channel_id = await extracts_channel_id(text=embed_text)

            if channel_id:

                channel = bot.get_channel(channel_id)
                await interaction.response.send_modal(StickyMessageModal(channel=channel))

            else:

                await interaction.response.send_message(embed=GetEmbed.get_embed(embed_index=12), view=None, ephemeral=True) 

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)

        
class OverwriteChannelSelect(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system="sticky message system"))


    @discord.ui.channel_select(
        placeholder="Choose a channel with which you want to overwrite the old one!",
        max_values=1,
        min_values=1,
        custom_id="overwrite_channel_select",
        channel_types=[discord.ChannelType.text]
    )
    
    async def overwrite_channel_select(self, select, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            channel = await DatabaseCheck.check_sticky_message(guild_id = interaction.guild.id, channel_id = select.values[0].id)

            if channel is not None:
                
                emb = discord.Embed(description=f"""## This channel is already occupied
                    {Emojis.dot_emoji} A sticky message has already been defined for the channel
                    {Emojis.dot_emoji} Only one sticky message can exist per channel
                    {Emojis.help_emoji} Please select another channel""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            else:

                embed_text = interaction.message.embeds[0].description
                channel_id = await extracts_channel_id(text=embed_text)
                
                sticky_message = await DatabaseCheck.check_sticky_message(guild_id = interaction.guild.id, channel_id = channel_id)

                emb = discord.Embed(description=f"""## channel has been successfully changed
                    {Emojis.dot_emoji} From now on the channel: <#{select.values[0].id}> is used for the following sticky message:
                    ```{sticky_message[3]}```""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

                await DatabaseUpdates.manage_sticky_message(guild_id = interaction.guild.id, channel_id = channel_id, channel_id_new = select.values[0].id, operation = "update")
                await StickyMessage.delete_old_sticky_message(guild_id = interaction.guild.id, channel_id = channel_id)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class ShowStickyMessage(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="show sticky messages",
            style=discord.ButtonStyle.blurple,
            custom_id="show_sticky_messages_all"
        )


    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            pages = await StickyMessage.update_paginator(guild_id=interaction.guild.id)

            if pages != []:

                paginator_view = PaginatorViewStickyMessage(pages=pages)
                paginator_view.add_item(CancelButton(system="sticky message system"))
                await interaction.response.send_message(embed=pages[0], view=paginator_view)

            else:

                await interaction.response.send_message(embed=GetEmbed.get_embed(embed_index=13), view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class AddStickyMessageText(discord.ui.View):
    
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "Sticky message system"))


    @discord.ui.button(
        label="add message",
        style=discord.ButtonStyle.blurple,
        custom_id="add_message_sticky_message"
    )

    async def sticky_message_text(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            channel_id = await extracts_channel_id(text=interaction.message.embeds[0].description)
            channel = bot.get_channel(channel_id)

            await interaction.response.send_modal(StickyMessageModal(channel=channel))

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class StickyMessageModal(discord.ui.Modal):

    def __init__(self, channel,*args, **kwargs):
        self.channel = channel
        super().__init__(
            title="Define a text for the sticky message",
            timeout=None,
            custom_id="add_sticky_message_modal"
        )
        self.add_item(discord.ui.InputText(label="Enter the text for the sticky message here", style=discord.InputTextStyle.paragraph, placeholder="Write the text for the sticky message here", max_length=3000))


    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:
       
            await StickyMessage.delete_old_sticky_message(guild_id = interaction.guild.id, channel_id = self.channel.id)

            emb = discord.Embed(description=self.children[0].value, color=bot_colour)

            message = await self.channel.send(embed=emb)

            await DatabaseUpdates.manage_sticky_message(guild_id = interaction.guild.id, message = self.children[0].value, message_id = message.id, channel_id = self.channel.id, operation = "update")
            
            view = View()
            view.add_item(ShowStickyMessage())

            emb = discord.Embed(description=f"""## Text defined for the sticky message
                {Emojis.dot_emoji} Sticky message text has been set for the channel <#{self.channel.id}>
                {Emojis.dot_emoji} The following text has been set:
                ```{self.children[0].value}```
                {Emojis.help_emoji} With the button below you can also view the other sticky messages""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=view)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



class EditStickyMessage(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system="sticky message system"))
    

    @discord.ui.button(
        label="edit sticky message",
        style=discord.ButtonStyle.blurple,
        custom_id="edit_sticky_message"
        )
    
    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            channel_id = await extracts_channel_id(text=interaction.message.embeds[0].description)
            channel = bot.get_channel(channel_id)
            
            await interaction.response.send_modal(StickyMessageModal(channel=channel))

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)