from discord.ui.input_text import InputText
from utils import *
from sql_function import *
import re
import string
from datetime import timezone
from datetime import datetime



class TicketSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    async def get_layers(guild_id:int):

        layers = await DatabaseCheck.check_ticket_system_layers(guild_id=guild_id)
        
        if layers:

            options = []
            for layer in layers:
                
                options.append(
                    discord.SelectOption(
                        label=layer[2],
                        description=layer[3],
                        value=str(layer[2] + f"{''.join(random.choices(string.ascii_letters + string.digits, k=4))}")
                    )
                )

        else:

            options = [discord.SelectOption(
                label="No layers have been defined",
                description="If you want to set layers use the add layer button",
                value="no_layers_remove"
            )]

        return options
    

    async def resend_ticket_message(guild_id:int):

        settings = await DatabaseCheck.check_ticket_system_settings(guild_id = guild_id)

        if settings is None:
            return

        if settings[1] == 0:
            return

        channel = settings[2] is not None
        message = settings[4] is not None
      
        if channel and message:
           
            layers = await DatabaseCheck.check_ticket_system_layers(guild_id = guild_id)
        
            if layers:
              
                if settings[3] is not None:
                    
                    try:
                       
                        current_channel = bot.get_channel(settings[2])
                        current_message = await current_channel.fetch_message(settings[3])
                        await current_message.delete()

                    except discord.NotFound:
                        pass

                emb = discord.Embed(description=f"""{settings[4]}""", color=bot_colour)

                if settings[5]:
                    emb.set_image(url=settings[5])

                return emb
                
        return None

    
    @commands.slash_command(name = "set-ticket-system", description = "Set the ticket system!")
    @commands.has_permissions(administrator = True)
    async def set_ticket_system(self, ctx:discord.ApplicationContext):

        check_settings = await DatabaseCheck.check_ticket_system_settings(guild_id = ctx.guild.id)

        if check_settings is None:
        
            await DatabaseUpdates.manage_ticket_system_settings(guild_id = ctx.guild.id, operation = "insert")
            check_settings = await DatabaseCheck.check_ticket_system_settings(guild_id = ctx.guild.id)

        view = SetTicketSystemView()
        view.add_item(CancelButton(system="Ticket system"))

        emb = discord.Embed(description=f"""## Set the Ticket system
        With the following buttons, you can customize the various functions according to your preferences:
        {Emojis.dot_emoji} The `Set Layer button` allows you to define options that users can select
        {Emojis.dot_emoji} The `Set Message Text` button lets you define the text that will appear in the ticket message (this is the message through which tickets can be created)
        {Emojis.dot_emoji} The `Set Ticket Channel` button lets you specify in which channel the ticket message should be sent
        {Emojis.dot_emoji} The `On / Off switch` button allows you to enable or disable the ticket system. Currently, the ticket system is: {'enabled' if check_settings[1] == 1 else 'disabled'}
        {Emojis.dot_emoji} The `Show settings` button lets you view the current settings and their status
        ```The system will only be active once a message, a channel, and an layer have been selected```""", color=bot_colour)
        await ctx.respond(embed=emb, view=view)


    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        
        check_settings = await DatabaseCheck.check_ticket_system_settings(guild_id=message.guild.id)
        
        if check_settings:

            if message.id == check_settings[3]:
                
                await DatabaseUpdates.manage_ticket_system_settings(guild_id=message.guild.id, operation="update", status=0)



def setup(bot):
    bot.add_cog(TicketSystem(bot))





class TicketSystemView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(label="Add User", style=discord.ButtonStyle.blurple, custom_id="add_user")
    async def add_user_button(self, button:discord.ui.Button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Choose a user
                {Emojis.dot_emoji} Choose a user you want to add to this ticket
                {Emojis.dot_emoji} The user you select will then be able to see this ticket""", color=bot_colour)

            await interaction.response.send_message(embed=emb, view=AddUserTicket(), ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(label="Show User List", style=discord.ButtonStyle.blurple, custom_id="show_user_list")
    async def show_user_list_button(self, button:discord.ui.Button, interaction:discord.Interaction):

        channel = await bot.fetch_channel(interaction.channel.id)
        visible_members = [f"{Emojis.dot_emoji} {member.mention}" for member in channel.members if not member.bot]
        user_list = "\n".join(visible_members)
         
        emb = discord.Embed(description=f"""## Overview of all authorized users
            {Emojis.dot_emoji} Here you can see an overview of all users who can see this channel:
            {user_list}""", color=bot_colour)
        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)


    @discord.ui.button(label="Create Temp Voice Channel", style=discord.ButtonStyle.blurple, custom_id="create_temp_voice_channel")
    async def create_temp_voice_channel_button(self, button:discord.ui.Button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            check_temp_channel = await DatabaseCheck.check_ticket_system_temp_voice(guild_id = interaction.guild.id, name = "Temp-voice-"+interaction.channel.name)
            
            if check_temp_channel:

                emb = discord.Embed(description=f"""## A Temp voice channel already exists for this ticket
                    {Emojis.dot_emoji} There is already a Temp voice channel for this ticket this is <#{check_temp_channel[1]}>
                    {Emojis.dot_emoji} Only one Temp voice channel can be created per ticket""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            else:

                channel = await bot.fetch_channel(interaction.channel.id)

                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)
                }

                for member in channel.members:

                    if not member.bot:

                        overwrites[member] = discord.PermissionOverwrite(view_channel=True, connect=True, speak=True)

                temp_channel = await interaction.guild.create_voice_channel(name="Temp-voice-"+interaction.channel.name, overwrites=overwrites)

                await DatabaseUpdates.manage_ticket_system_temp_voice(guild_id = interaction.guild.id, name = "Temp-voice-"+interaction.channel.name, channel_id = temp_channel.id, operation = "insert")
                
                emb = discord.Embed(description=f"""## Temp channel has been created
                    {Emojis.dot_emoji} A Temp voice channel has been created, the voice channel is now available for this ticket: Temp-voice-{interaction.channel.name}
                    {Emojis.help_emoji} Only one channel can be created per ticket""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket_button(self, button:discord.ui.Button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            check_temp_channel = await DatabaseCheck.check_ticket_system_temp_voice(guild_id = interaction.guild.id, name = "Temp-voice-"+interaction.channel.name)
            await interaction.channel.delete()

            if check_temp_channel:

                temp_channel = bot.get_channel(check_temp_channel[1])
                await temp_channel.delete()

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class AddUserTicket(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system="ticket system"))

    
    @discord.ui.user_select(placeholder="Choose a user you want to add to this ticket!", min_values=1, max_values=1, custom_id="add_user_ticket_select")
    async def add_user_ticket_select(self, select, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            overwrites = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            await interaction.channel.set_permissions(overwrite=overwrites, target=select.values[0])

            emb = discord.Embed(description=f"""## User has been added
                {Emojis.dot_emoji} From now on the user {select.values[0].mention} has access to this ticket""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class SetTicketSystemView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system="ticket system"))


    @discord.ui.button(label="Set Layers", style=discord.ButtonStyle.blurple, custom_id="set_new_layer")
    async def set_new_layer_button(self, button:discord.ui.Button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Set Layers
                {Emojis.dot_emoji} With the buttons below you can choose what you want to set
                {Emojis.dot_emoji} The layers you can set are the selection options that users have later when creating a ticket
                {Emojis.help_emoji} You can add a new layer, delete existing layers or display all existing layers""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=SetLayers(), ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(label="Set Ticket Channel", style=discord.ButtonStyle.blurple, custom_id="set_ticket_channel")
    async def set_ticket_channel_button(self, button:discord.ui.Button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            check_settings = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)

            emb = discord.Embed(description=f"""## Set ticket channel
                {Emojis.dot_emoji} With the lower select menu you can choose from which channel you want to be able to create tickers
                {Emojis.dot_emoji} {f'No channel has been set yet' if check_settings[2] == None else f'Currently <#{check_settings[2]}> is set as ticket channel'}""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=SetTicketChannelSelect(), ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(label="Set Message Text", style=discord.ButtonStyle.blurple, custom_id="add_message_text")
    async def add_message_text_button(self, button:discord.ui.Button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            await interaction.response.send_modal(AddMessageModal())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(label="On / Off switch", style=discord.ButtonStyle.blurple, custom_id="on_off_switch_ticket")
    async def on_off_switch_ticket(self, button:discord.ui.Button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            check = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)

            await DatabaseUpdates.manage_ticket_system_settings(guild_id = interaction.guild.id, operation = "update", status = 0 if check[1] == 1 else 1)
            ticket_message = None

            if check[1] == 1:

                try:

                    channel = bot.get_channel(check[2])
                    message = await channel.fetch_message(check[3])
                    await message.delete()

                except discord.NotFound:
                    pass

            if check[1] == 0:

                channel = bot.get_channel(check[2])
                check_message = await TicketSystem.resend_ticket_message(guild_id = interaction.guild.id)

                if check_message:

                    options = await TicketSystem.get_layers(guild_id = interaction.guild.id)
                    ticket_message = (await channel.send(embed=check_message, view=TicketCreateSelect(options=options))).id

            await DatabaseUpdates.manage_ticket_system_settings(guild_id = interaction.guild.id, operation = "update", status = 0 if check[1] == 1 else 1, message_id = ticket_message)

            emb = discord.Embed(description=f"""## Ticket system was {'Switched off' if check[1] == 1 else 'Switched on'}
                {Emojis.dot_emoji} {'The ticket message has been deleted' if check[1] == 1 else 'The ticket message has been sent'}
                {Emojis.help_emoji} {'When you reactivate the ticket system, the ticket message will be sent again provided all required settings are present' if check[1] == 1 else 'As soon as the ticket system is deactivated, the ticket message will be deleted'}""",  color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)

    
    @discord.ui.button(label="Show settings", style=discord.ButtonStyle.blurple, custom_id="show_ticket_system_settings")
    async def show_ticket_system_settings(self, button:discord.ui.Button, interaction:discord.Interaction):
        
        settings = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)

        options = await TicketSystem.get_layers(guild_id = interaction.guild.id)
        view = ShowLayers(options=options)
        view.add_item(ShowTicketMessage())
        view.add_item(CancelButton(system="ticket system"))

        emb = discord.Embed(description=f"""## Here you can see all settings of the ticket system
            {Emojis.dot_emoji} The ticket system is currently {'switched on' if settings[1] == 1 else 'switched off'}
            {Emojis.dot_emoji} {'No ticket channel has been set yet' if settings[2] == None else f'The ticket channel has been set to <#{settings[2]}>, which means that you can only create tickets from this channel'}
            {Emojis.dot_emoji} In the lower select menu you can see which layers are set for the ticket system, a maximum of 10 can be set
            {Emojis.dot_emoji} With the lower button you can also see what the ticket message looks like
            {Emojis.help_emoji} The ticket message is only sent if something is set for everything""", color=bot_colour)
        await interaction.response.send_message(embed=emb, view=view, ephemeral=True)
        

class SetLayers(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system="ticket system"))

    
    @discord.ui.button(label="Add Layer", style=discord.ButtonStyle.blurple, custom_id="add_layer")
    async def add_layer_button(self, button:discord.ui.Button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            check_layers = await DatabaseCheck.check_ticket_system_layers(guild_id = interaction.guild.id)

            if len(check_layers) >= 10:

                emb = discord.Embed(description=f"""## Limit has been reached
                    {Emojis.dot_emoji} You can only set a maximum of 10 layers for the ticket system
                    {Emojis.dot_emoji} If you want to have other layers, please delete the ones you don't need beforehand
                    {Emojis.help_emoji} Layers can be deleted using the interaction menu within the command""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            else:

                await interaction.response.send_modal(AddLayerDetailsModal())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(label="Remove Layer", style=discord.ButtonStyle.blurple, custom_id="remove_layer")
    async def remove_layer_button(self, button:discord.ui.Button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Remove Layer
                {Emojis.dot_emoji} Choose in the lower select menu which layers you want to remove
                {Emojis.dot_emoji} These will then no longer be displayed in the ticket system
                {Emojis.help_emoji} The ticket message will be deleted after each change and re-posted if all settings are available""", color=bot_colour)

            options = await TicketSystem.get_layers(guild_id = interaction.guild.id)
            await interaction.response.send_message(embed=emb, view=RemoveLayer(options=options), ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)
            

    @discord.ui.button(label="Show Layers", style=discord.ButtonStyle.blurple, custom_id="show_layers")
    async def show_layers_button(self, button:discord.ui.Button, interaction:discord.Interaction):
        
        options = await TicketSystem.get_layers(guild_id = interaction.guild.id)

        emb = discord.Embed(description=f"""## Show Layers
            {Emojis.dot_emoji} In the lower select menu you can see all layers that are currently set
            {Emojis.dot_emoji} With the add function you can add new layers and with the remove function you can remove them again""", color=bot_colour)
        await interaction.response.send_message(embed=emb, view=ShowLayers(options=options), ephemeral=True)


class TicketCreateSelect(discord.ui.View):

    def __init__(self, options):
        super().__init__(timeout=None)
        self.options = options if options is not None else [
            discord.SelectOption(
                label="An error has occurred",
                description="I have lost the connection or the interaction took too long, try again",
                value="none_layers_remove"
            )
        ]

        self.select = discord.ui.Select(
            placeholder="What would you like to report?",
            min_values=1,
            max_values=1,
            options=self.options,
            row=2,
            custom_id="ticket_create_select"
        )
        self.select.callback = self.ticket_create_select
        self.add_item(self.select)
        self.add_item(CancelButton(system="ticket system"))


    async def ticket_create_select(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            overwrites = {
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            }
            random_code = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            channels = await interaction.guild.create_text_channel(name=f"Ticket-{random_code}", overwrites=overwrites)

            emb = discord.Embed(description=f"""## The ticket has been successfully created
                {Emojis.dot_emoji} The ticket has been created, please wait in {channels.mention} until a responsible user takes care of your problem
                {Emojis.help_emoji} Please create only one ticket""", color=bot_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True)

            emb = discord.Embed(description=f"""## Ticket {random_code}
                {Emojis.dot_emoji} Name of the creator: {interaction.user.name}
                {Emojis.dot_emoji} ID of the creator: {interaction.user.id}
                {Emojis.dot_emoji} Topic of the ticket: {self.select.values[0][:-5]}""", color=bot_colour)
            emb.set_footer(text=f"Creation time: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
            await channels.send(embed=emb, view=TicketSystemView())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class RemoveLayer(discord.ui.View):

    def __init__(self, options):
        super().__init__(timeout=None)
        self.options = options if options is not None else [
            discord.SelectOption(
                label="An error has occurred",
                description="I have lost the connection or the interaction took too long, try again",
                value="none_layers_remove"
            )
        ]

        self.select = discord.ui.Select(
            placeholder="Choose which layers you want to remove",
            min_values=1,
            max_values=1,
            options=self.options,
            row=1,
            custom_id="remove_layer_select"
        )
        self.select.callback = self.remove_layer_select
        self.add_item(self.select)
        self.add_item(CancelButton(system="ticket system"))


    async def remove_layer_select(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            layer = self.select.values[0][:-4]

            await DatabaseUpdates.manage_ticket_system_layers(guild_id=interaction.guild.id, operation="delete", layer_name=layer)

            if self.select.values[0] == "none_layers_remove" or self.select.values[0] == "no_layers_remove":

                emb = discord.Embed(description=f"""## Layer could not be removed
                    {Emojis.dot_emoji} Either no layer was set or the layers could not be retrieved
                    {Emojis.dot_emoji} If no layers are set, set some otherwise the ticket system will not work""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            else:

                emb = discord.Embed(description=f"""## Layer has been removed
                    {Emojis.dot_emoji} The layer {layer} has been successfully removed
                    {Emojis.help_emoji} If you want to remove more layers you can run the command again""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            check = await DatabaseCheck.check_ticket_system_layers(guild_id = interaction.guild.id)

            if check == None:

                settings = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)

                channel = bot.get_channel(settings[2])
                message = await channel.fetch_message(settings[3])

                if message:
                    await message.delete()

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)

    
    @discord.ui.button(label="Reset layers", style=discord.ButtonStyle.blurple, custom_id="reset_layers", row=2)
    async def reset_layers_button(self, button:discord.ui.Button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            check = await DatabaseCheck.check_ticket_system_layers(guild_id = interaction.guild.id)

            if check:

                await DatabaseUpdates.manage_ticket_system_layers(guild_id = interaction.guild.id, operation = "delete")

                settings = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)

                channel = bot.get_channel(settings[2])
                message = await channel.fetch_message(settings[3])
                
                if message:

                    await message.delete()

                emb = discord.Embed(description=f"""## All layers have been removed
                    {Emojis.dot_emoji} The ticket system will no longer respond and the message will be deleted
                    {Emojis.dot_emoji} If you want to add new layers use the add layer function of the command""")
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

            else:

                emb = discord.Embed(description=f"""## No layers have been defined
                    {Emojis.dot_emoji} No layers can be removed because no layers have been set
                    {Emojis.dot_emoji} If you want to set layers use the `add layer` button""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class ShowLayers(discord.ui.View):

    def __init__(self, options):
        super().__init__(timeout=None)
        self.options = options if options is not None else [
            discord.SelectOption(
                label="An error has occurred",
                description="I have lost the connection or the interaction took too long, try again",
                value="none_layers_show"
            )
        ]

        self.select = discord.ui.Select(
            placeholder="Here you can see which layers are currently available",
            min_values=1,
            max_values=1,
            options=self.options,
            row=1,
            custom_id="show_layer_select"
        )
        self.select.callback = self.show_layer_select
        self.add_item(self.select)
        self.add_item(CancelButton(system="ticket system"))


    async def show_layer_select(self, interaction: discord.Interaction):

        emb = discord.Embed(description=f"""## This is just an overview
            {Emojis.dot_emoji} This is just an overview of the currently available layers
            {Emojis.dot_emoji} If you want to remove or add any use the previous buttons""", color=bot_colour)
        await interaction.response.send_message(embed=emb, view=None, ephemeral=True)


class AddMessageModal(discord.ui.Modal):

    def __init__(self, *args, **kwargs):
        super().__init__(title="Add Message")
        self.add_item(discord.ui.InputText(label="Enter the text for the ticket message here", style=discord.InputTextStyle.long, max_length=3000, required=True,
            placeholder="Insert the text here that will later appear in the ticket message"))
        self.add_item(discord.ui.InputText(label="Enter a link for an image or gif", style=discord.InputTextStyle.long, max_length=300, required=False,
            placeholder="Enter a link for an image or gif to be displayed below the message"))


    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            check_url = await validate_image_url(url=self.children[1].value)
            
            if not check_url:

                emb = discord.Embed(description=f"""## No valid link
                    {Emojis.dot_emoji} The link you provided is invalid, either the content is not accessible or the link does not have the required format
                    {Emojis.help_emoji} Only links to image or gif files are accepted""", color=bot_colour)
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
            

            await DatabaseUpdates.manage_ticket_system_settings(guild_id = interaction.guild.id, operation = "update", message = self.children[0].value, message_url = self.children[1].value if self.children[1].value != '' else None)
            settings = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)
            check = await TicketSystem.resend_ticket_message(guild_id = interaction.guild.id)
            
            ticket_message = None
            if check:
            
                options = await TicketSystem.get_layers(guild_id = interaction.guild.id)
                channel = bot.get_channel(settings[2])
                
                ticket_message = await channel.send(embed=check, view=TicketCreateSelect(options=options))

            await DatabaseUpdates.manage_ticket_system_settings(guild_id = interaction.guild.id, operation = "update", message_id = ticket_message.id)

            view = View()
            view.add_item(ShowTicketMessage())
            view.add_item(CancelButton(system="ticket system"))

            emb = discord.Embed(description=f"""## Text for the ticket message has been set
                {Emojis.dot_emoji} The ticket message will be sent to the ticket channel when all settings are completed
                {Emojis.dot_emoji} If you want to view the message you can click on the `Show Message` button below""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=view, ephemeral=True)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class AddLayerDetailsModal(discord.ui.Modal):

    def __init__(self, *args, **kwargs):
        super().__init__(title="Add Layer details")
        self.add_item(discord.ui.InputText(label="Title", style=discord.InputTextStyle.short, max_length=100, required=True,
            placeholder="Enter the title of the layer here"))
        self.add_item(discord.ui.InputText(label="Description", style=discord.InputTextStyle.long, max_length=100, required=False,
            placeholder="Enter a description of the layer heres"))


    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            await DatabaseUpdates.manage_ticket_system_layers(
                guild_id = interaction.guild.id,
                operation = "insert",
                layer_name = self.children[0].value,
                description = self.children[1].value if self.children[1].value != '' else None)
            
            check = await TicketSystem.resend_ticket_message(guild_id = interaction.guild.id)
        
            if check:
            
                settings = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)
                channel = bot.get_channel(settings[2])
                options = await TicketSystem.get_layers(guild_id = interaction.guild.id)
                ticket_message = await channel.send(embed=check,  view=TicketCreateSelect(options=options))
                await DatabaseUpdates.manage_ticket_system_settings(guild_id = interaction.guild.id, operation = "update", message_id = ticket_message.id)
            
            emb = discord.Embed(description=f"""## A new layer has been defined
                {Emojis.dot_emoji} The layer is displayed in the ticket message and can be selected by users to classify their problem more precisely
                {Emojis.dot_emoji} From now on the layer **{self.children[0].value}** is available in the ticket system
                {'' if self.children[1].value == '' else f'''{Emojis.dot_emoji} Description:
                ```{self.children[1].value}```'''}
                {Emojis.help_emoji} If you want to add more layers you can run the command again""", color=bot_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)
        

class SetTicketChannelSelect(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "ticket system"))

    
    @discord.ui.channel_select(placeholder="Select a channel that you want to set as a ticket channel!", custom_id="select_ticket_channel", min_values=1, max_values=1, channel_types=[discord.ChannelType.text])
    async def set_ticket_channel(self, select:discord.ui.Select, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            check_settings = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)

            if check_settings[2] == select.values[0]:

                emb = discord.Embed(description=f"""## This channel has already been set as the ticket channel
                    {Emojis.dot_emoji} If you want to change it you can run the command again and select another channel
                    {Emojis.help_emoji} If you set a ticket channel, tickets can only be created from this channel""", color=bot_colour)
                await interaction.response.edit_message(embed=emb)
            
            elif check_settings[2] is not None and check_settings[2] != select.values[0]:

                emb = discord.Embed(description=f"""## A ticket channel is being set
                    {Emojis.dot_emoji} The new ticket channel will be {select.values[0].mention}.
                    {Emojis.dot_emoji} Currently, the ticket channel is set to <#{check_settings[2]}>.
                    {Emojis.dot_emoji} Would you like to overwrite the current channel with the new one?""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=OverwriteTicketChannel())

            else:

                await DatabaseUpdates.manage_ticket_system_settings(guild_id = interaction.guild.id, operation = "update", channel_id = select.values[0].id)

                check = await TicketSystem.resend_ticket_message(guild_id = interaction.guild.id)

                if check:

                    options = TicketSystem.get_layers(guild_id = interaction.guild.id)
                    ticket_message = await select.values[0].send(embed=check, view=TicketCreateSelect(options=options))
                    await DatabaseUpdates.manage_ticket_system_settings(guild_id = interaction.guild.id, operation = "update", message_id = ticket_message.id)

                emb = discord.Embed(description=f"""## Ticket channel has been successfully set
                    {Emojis.dot_emoji} From now on <#{select.values[0].id}> is set as ticket channel
                    {Emojis.dot_emoji} The ticket message is then created in this channel with which users can then create tickets
                    {Emojis.help_emoji} Next, set the layers and the message text to complete the ticket system""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class OverwriteTicketChannel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CancelButton(system="ticket system"))


    @discord.ui.button(label="Keep Channel", style=discord.ButtonStyle.blurple, custom_id="keep_channel")
    async def keep_channel_button(self, button:discord.ui.Button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            check_settings = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)

            emb = discord.Embed(description=f"""## Ticket channel was not overwritten
                {Emojis.dot_emoji} The channel <#{check_settings[2]}> remains as ticket channel
                {Emojis.help_emoji} Thus, tickets can still be created from this channel""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(label="Overwrite Channel", style=discord.ButtonStyle.blurple, custom_id="overwrite_channel")
    async def overwrite_channel_button(self, button:discord.ui.Button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            new_channel = await extracts_channel_id(text=interaction.message.embeds[0].description)

            check = await TicketSystem.resend_ticket_message(guild_id = interaction.guild.id)

            ticket_message = None
            if check:

                options = await TicketSystem.get_layers(guild_id = interaction.guild.id)
                
                channel = bot.get_channel(new_channel)
                ticket_message = await channel.send(embed=check, view=TicketCreateSelect(options=options))

            await DatabaseUpdates.manage_ticket_system_settings(guild_id=interaction.guild.id, operation="update", channel_id=new_channel, message_id = ticket_message.id)

            emb = discord.Embed(description=f"""## The ticket channel has been overwritten
                {Emojis.dot_emoji} From now on <#{new_channel}> is set as ticket channel
                {Emojis.help_emoji} This means that tickets can now only be created from <#{new_channel}>""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class ShowTicketMessage(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Show Message", 
            style=discord.ButtonStyle.blurple,
            custom_id="show_ticket_message",
            row=2)


    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            check_settings = await DatabaseCheck.check_ticket_system_settings(guild_id = interaction.guild.id)

            if check_settings[4] is not None:

                emb = discord.Embed(description=f"""
                    {check_settings[4]}""", color=bot_colour)
                
                if check_settings[5] is not None:
                    emb.set_image(url=check_settings[5])

            else:

                emb = discord.Embed(description=f"""## No ticket message has been set
                    {Emojis.dot_emoji} The ticket message could not be retrieved because you have not set one 
                    {Emojis.help_emoji} To set a ticket message you can click on the button `add message text`""", color=bot_colour)

            await interaction.response.send_message(embed=emb, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)

