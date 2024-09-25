
from utils import *
import calendar
<<<<<<< HEAD
=======
from sql_function import *

>>>>>>> neues-repo/main



class ModeratorCommands(commands.Cog):
    
<<<<<<< HEAD
    # Returns the antilink whitelist completely formatted 
    def show_antilink_system_whitelist(guild_id:int):

        white_list = DatabaseCheck.check_antilink_whitelist(guild_id = guild_id)
=======
    def __init__(self, bot):
        self.bot = bot

    # Returns the antilink whitelist completely formatted 
    async def show_antilink_system_whitelist(guild_id:int):

        white_list = await DatabaseCheck.check_antilink_whitelist(guild_id = guild_id)
>>>>>>> neues-repo/main

        channel_whitelist, category_whitelist, role_whitelist, user_whitelist = [], [], [], []
        for _, channel, category, role, user in white_list:
            
            if channel != None:
                channel_whitelist.append(f"> {Emojis.dot_emoji} <#{channel}>\n")

            if category != None:
                category_whitelist.append(f"> {Emojis.dot_emoji} <#{category}>\n")

            if role != None:
                role_whitelist.append(f"> {Emojis.dot_emoji} <@&{role}>\n")

            if user != None:
                user_whitelist.append(f"> {Emojis.dot_emoji} <@{user}>\n")
        
        if all([channel_whitelist == [], category_whitelist == [], role_whitelist == [], user_whitelist == []]):
            return f"**{Emojis.dot_emoji} Nothing is listed on the whitelist**"
            
        else:
            
            whitelist = channel_whitelist + category_whitelist + role_whitelist + user_whitelist

            return "".join(whitelist)



##################################  Anti-link system  #########################################

<<<<<<< HEAD

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        check_whitelist = DatabaseCheck.check_antilink_whitelist(guild_id = message.guild.id)
        
        if check_whitelist:
            
            for _, channel, category, role, user in check_whitelist:
                
                if isinstance(message.channel, discord.channel.DMChannel):
                    return
                
                else:

                    if user == message.author.id:
                        return

                    if role != None:
                                
                        blacklist_role = message.guild.get_role(role)
                        if blacklist_role in message.author.roles:
                            return
                    
                    if message.channel.id == channel:
                        return

                    if message.channel.category_id == category:
                        return

        if message.author.bot:
            return

        else:

            formats=['png', 'jpg', 'gif' , 'webp', 'jpeg', 'jpg' , 'jpeg' ,'jfif' ,'pjpeg' , 'pjp', 'svg', 'bmp']

            if message.author.guild_permissions.administrator:
                return
            
            else:

                # Text additions for the embed
                anti_link_text = {
                    0:"discord invitation link",
                    1:"link or a discord invitations",
                    2:"link or an image / video",
                    3:""}

                check_settings = DatabaseCheck.check_bot_settings(guild_id=message.guild.id)
                channel = message.channel
            
                emb = discord.Embed(title=f'{Emojis.help_emoji} {message.author.name} you have violated the anti-link system', 
                    description=f"""{Emojis.dot_emoji} You have violated the anti-link system on {message.guild.name} it is forbidden:
                    {Emojis.dot_emoji} `You have sent an {anti_link_text[check_settings[3]]} to this chat`
                    {f"{Emojis.dot_emoji} That's why you got a timeout for {check_settings[4]} minutes" if check_settings[4] != 0 else ''}""", colour=bot_colour)
                emb.set_footer(text=f'{message.author.name}', icon_url=message.author.display_avatar.url)
                
                rule_violation = False
                
                # Is triggered when a discord invitation link is in the message (when triggered, the message is deleted)
                if check_settings[3] == 0:
            
                    if "discord.gg/" in message.content or "discord.com" in message.content:
                        await message.delete()
                        rule_violation = True

                # Is triggered when there is a link in the message, images and videos are ignored (when triggered, the message is deleted)
                elif check_settings[3] == 1:
            
                    if message.content.startswith('https://') and not any(word in message.content for word in formats) and not message.attachments: 

                        await message.delete()
                        rule_violation = True

                # Is triggered when there is any link in the message (when triggered, the message is deleted)
                elif check_settings[3] == 2:

                    if "https://" in message.content or message.attachments:

                        await message.delete()
                        rule_violation = True
                
                # Antilink system is disabled 
                elif check_settings[3] == 3:
                    return
                
                if rule_violation == True:

                    await channel.send(embed=emb, delete_after=5)
                    await message.author.timeout_for(timedelta(minutes = check_settings[4]))
=======
    
    # Checks the whitelist and checks whether there is a match in the channels, categories, roles or user entries
    @staticmethod
    async def check_whitelist_antilink(message:discord.Message):
        
        check_whitelist = await DatabaseCheck.check_antilink_whitelist(guild_id = message.guild.id)
            
        if check_whitelist:
                
            for _, channel, category, role, user in check_whitelist:
                    
                if isinstance(message.channel, discord.channel.DMChannel):
                    return True
                    
                else:

                    if user == message.author.id:
                        return True

                    if role != None:
                                    
                        blacklist_role = message.guild.get_role(role)
                        if blacklist_role in message.author.roles:
                            return True
                        
                    if message.channel.id == channel:
                        return True

                    if message.channel.category_id == category:
                        return True
                    
        return False


    # Checks whether there has been a violation of the antilink system
    async def check_rule_violation(self, check_settings, message:discord.Message):

        check_link = self.contains_invite(message.content.replace(" ", ""))

        # Is triggered when a discord invitation link is in the message (when triggered, the message is deleted)
        if check_settings[3] == 0:
                
            if "discord.gg/" in message.content or "discord.com" in message.content or check_link == True:

                return True

        # Is triggered when there is a link in the message, images and videos are ignored (when triggered, the message is deleted)
        elif check_settings[3] == 1:

            if 'https://' in message.content and not any(word in message.content for word in formats) and not message.attachments or check_link == True: 
                
                return True

        # Is triggered when there is any link in the message (when triggered, the message is deleted)
        elif check_settings[3] == 2:

            if "https://" in message.content or message.attachments or check_link == True:

                return True
            

    # Checks whether the message contains a link
    def contains_invite(self, content:str):

        invites_re = re.compile(r'(?:discord\.gg|discord\.com\/invite|\.gg)\/(\S+)')
        matches = invites_re.findall(content)
            
        if not matches:
            return False
        
        return True


    # Antilink system checks whether messages violate the antilink system, distinguishes between links that lead to images, invitation links or links in general
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        
        if message != None:

            if message.author.bot:
                return

            if await self.check_whitelist_antilink(message=message) == True:
                return

            else:
        
                if message.author.guild_permissions.administrator:
                    return

                else:

                    check_settings = await DatabaseCheck.check_bot_settings(guild_id=message.guild.id)

                    # Antilink system is disabled 
                    if check_settings[3] == 3:
                        return

                    if await self.check_rule_violation(check_settings = check_settings, message = message) == True:
            
                        await message.channel.send(embed=GetEmbed.get_embed(embed_index=9, settings=message, settings2=check_settings), delete_after=5)
                        await message.delete()
                        await message.author.timeout_for(timedelta(minutes = check_settings[4]))

    
    @commands.Cog.listener()
    async def on_message_edit(self, before:discord.Message, after:discord.Message):
        
        if await self.check_whitelist_antilink(message=after) == True:
            return
        
        if after.author.bot:
            return
        
        else:

            if after.author.guild_permissions.administrator:
                return
            
            check_settings = await DatabaseCheck.check_bot_settings(guild_id=after.guild.id)

            # Antilink system is disabled 
            if check_settings[3] == 3:
                return           

            if await self.check_rule_violation(check_settings = check_settings, message = after):
                
                await after.channel.send(embed=GetEmbed.get_embed(embed_index=9, settings=after, settings2=check_settings), delete_after=5)
                await after.delete()
                await after.author.timeout_for(timedelta(minutes = check_settings[4]))
>>>>>>> neues-repo/main


    @commands.slash_command(name = "set-antilink-system", description = "Set the anti-link system the way you want it!")
    @commands.has_permissions(administrator = True)
    async def set_antilink(self, ctx:discord.ApplicationContext,
        settings:Option(str, required = True,
            description="Choose how the anti-link system should behave!",
            choices = [
                discord.OptionChoice(name = "All messages with a discord invitation link will be deleted", value="0"),
                discord.OptionChoice(name = "Every message with a link will be deleted exept Pictures and Videos", value="1"),
                discord.OptionChoice(name = "All messages with a link will be deleted this also includes pictures and videos", value="2"),
                discord.OptionChoice(name = "Deactivate anti-link system! (no messages are deleted)", value="3")]), 
        timeout:Option(int, max_value = 60, required = True, 
            description="Choose how long the user who violates the anti link system should be timed out! (Optional)", 
            choices = [0, 5, 10, 20, 30, 40, 50, 60])):

<<<<<<< HEAD
        check_settings = DatabaseCheck.check_bot_settings(guild_id = ctx.guild.id)

        if check_settings[3] == int(settings) and check_settings[4] == timeout:

            emb = discord.Embed(description=f"""## Currently, the antilink system is already set up exactly like this
                {Emojis.dot_emoji} The antilink system is set up exactly as you just wanted to set it up""", color=bot_colour)
=======
        check_settings = await DatabaseCheck.check_bot_settings(guild_id = ctx.guild.id)

        if check_settings[3] == int(settings) and check_settings[4] == timeout:

            emb = discord.Embed(description=f"""## Currently, the anti-link system is already set up exactly like this
                {Emojis.dot_emoji} The anti-link system is set up exactly as you just wanted to set it up""", color=bot_colour)
>>>>>>> neues-repo/main
            await ctx.respond(embed=emb, ephemeral=True)

        else:

<<<<<<< HEAD
            DatabaseUpdates.update_bot_settings(guild_id=ctx.guild.id, antilink=int(settings), antilink_timeout=timeout)
=======
            await DatabaseUpdates.update_bot_settings(guild_id=ctx.guild.id, antilink=int(settings), antilink_timeout=timeout)
>>>>>>> neues-repo/main

            # Text passages for the embed
            settings_text = {
                "0":"All messages that contain a discord invitation link.",
                "1":"Every message with a link will be deleted exept Pictures and Videos",
                "2":"All messages with a link will be deleted this also includes pictures and videoso",
                "3":"Nothing because the anti-link system is deactivated"}

            emb = discord.Embed(description=f"""## The anti-link system was set up
<<<<<<< HEAD
                {Emojis.dot_emoji} The antilink system will now delete the following messages:
=======
                {Emojis.dot_emoji} The anti-link system will now delete the following messages:
>>>>>>> neues-repo/main
                `{settings_text[settings]}`
                {f'{Emojis.dot_emoji} Users who still send links will receive a timeout of **{timeout}** minutes' if settings != '3' else ''}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
<<<<<<< HEAD
    @commands.slash_command(name = "show-antilink-settings")
=======
    @commands.slash_command(name = "show-antilink-settings", description = "Shows how the anti-link system is set!")
>>>>>>> neues-repo/main
    async def show_antilink_settings(self, ctx:discord.ApplicationContext):

        settings_text = {
            0:"All messages that contain a discord invitation link will be deleted.",
            1:"Every message with a link will be deleted exept Pictures and Videos",
            2:"All messages with a link will be deleted this also includes pictures and videos",
            3:"Nothing is deleted as the Antilink system is deactivated."}

<<<<<<< HEAD
        settings = DatabaseCheck.check_bot_settings(guild_id = ctx.guild.id)

        emb = discord.Embed(description=f"""## {Emojis.help_emoji} Here you can see the current antilink settings
            {Emojis.dot_emoji} The antilink system is currently set to:\n`{settings_text[settings[3]]}`
=======
        settings = await DatabaseCheck.check_bot_settings(guild_id = ctx.guild.id)
    
        emb = discord.Embed(description=f"""## {Emojis.help_emoji} Here you can see the current anti-link settings
            {Emojis.dot_emoji} The anti-link system is currently set to:
            `{settings_text[settings[3]]}`
>>>>>>> neues-repo/main
            {Emojis.dot_emoji} In the event of violations, you will receive a timeout of {settings[4]} minutes""", color=bot_colour)
        await ctx.respond(embed=emb)

    
<<<<<<< HEAD
    async def config_antilink_whitelist(self, guild_id:int, operation:str, channel = None, category = None, role = None, user = None):

        if [x for x in [channel, category, role, user] if x]:
            
            check_channel = DatabaseCheck.check_antilink_whitelist(guild_id = guild_id, channel_id = channel.id) if channel != None else False
            check_category = DatabaseCheck.check_antilink_whitelist(guild_id = guild_id, category_id = category.id) if category != None else False
            check_role = DatabaseCheck.check_antilink_whitelist(guild_id = guild_id, role_id = role.id) if role != None else False
            check_user = DatabaseCheck.check_antilink_whitelist(guild_id = guild_id, user_id = user.id) if user != None else False
=======
    '''
    Creates the anti-link list for the anti-link system

    Parameters:
    ------------
        - guild_id
            Server id 
        - operation
            Which operation is to be performed on the anti-link
                - add: Adds an entry to the anti-link
                - remove: Removes an entry from the anti-link
        - channel
            Channel Id
        - category
            Category Id
        - role
            Role Id
        - user
            User Id

    Info:
        - guild_id must be specified
        - operation an operation must be specified
        - One of the following items must be specified channel, category, role or user
    '''
    async def config_antilink_whitelist(
        self, 
        guild_id:int, 
        operation:str, 
        channel = None, 
        category = None, 
        role = None, 
        user = None
        ):

        if [x for x in [channel, category, role, user] if x]:
            
            check_channel = await DatabaseCheck.check_antilink_whitelist(guild_id = guild_id, channel_id = channel.id) if channel != None else False
            check_category = await DatabaseCheck.check_antilink_whitelist(guild_id = guild_id, category_id = category.id) if category != None else False
            check_role = await DatabaseCheck.check_antilink_whitelist(guild_id = guild_id, role_id = role.id) if role != None else False
            check_user = await DatabaseCheck.check_antilink_whitelist(guild_id = guild_id, user_id = user.id) if user != None else False
>>>>>>> neues-repo/main


            items = {0:check_channel, 1:check_category, 2:check_role, 3:check_user}
            items_list = [channel, category, role, user]
            
            if [x for x in items.values() if x is None] and operation == "add" or any(x for x in items.values() if x is not False or None) and operation == "remove":

                res = list({ele for ele in items if items[ele]}) if operation == "add" else list({ele for ele in items if items[ele] is None})
                second_res = list({ele for ele in items if items[ele] is None}) if operation == "add" else list({ele for ele in items if items[ele]})
            
                item = [(f"> {Emojis.dot_emoji} {items_list[i].mention}") for i in res] 
                second_item = [(f"> {Emojis.dot_emoji} {items_list[i].mention}") for i in second_res]
        
                items_dict = {
                    0:channel.id if 0 in second_res else None, 
                    1:category.id if 1 in second_res else None, 
                    2:role.id if 2 in second_res else None,
                    3:user.id if 3 in second_res else None
                }
            
                if operation == "add":

                    if user != None:

                        if user.bot:

                            emb = discord.Embed(description=f"""## {Emojis.help_emoji} You cannot put a bot on the whitelist
<<<<<<< HEAD
                                {Emojis.dot_emoji} Bots are automatically excluded from the anti link system and can therefore always send links""", color=bot_colour)
                            return emb
                    
                    formatted_items = "\n".join(item) if item != [] else "\n> None of these items are on the antilink whitelist"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> None of these items can be removed from the antilink whitelist as they are not listed there"
                    
                    DatabaseUpdates.manage_antilink_whitelist(guild_id=guild_id, operation="add", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3])    
                   
                    emb = discord.Embed(title=f"{Emojis.help_emoji} The following items have been added to the antilink whitelist or were already there", 
=======
                                {Emojis.dot_emoji} Bots are automatically excluded from the anti-link system and can therefore always send links""", color=bot_colour)
                            return emb
                    
                    formatted_items = "\n".join(item) if item != [] else "\n> None of these items are on the anti-link whitelist"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> None of these items can be removed from the anti-link whitelist as they are not listed there"
                    
                    await DatabaseUpdates.manage_antilink_whitelist(guild_id=guild_id, operation="add", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3])    
                   
                    emb = discord.Embed(title=f"{Emojis.help_emoji} The following items have been added to the anti-link whitelist or were already there", 
>>>>>>> neues-repo/main
                        description=f"""### {Emojis.dot_emoji} The following were already on the whitelist:
                        {formatted_items}\n### {Emojis.dot_emoji} Newly added:
                        {formatted_add_items}

<<<<<<< HEAD
                        {Emojis.dot_emoji} The newly added items are excluded from the antilink system""", color=bot_colour)
=======
                        {Emojis.dot_emoji} The newly added items are excluded from the anti-link system""", color=bot_colour)
>>>>>>> neues-repo/main
                    return emb

                elif operation == "remove":
                
<<<<<<< HEAD
                    formatted_items = "\n".join(item) if item != [] else "> All the items you specified were on the antilink whitelist"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> None of the items you specified could be removed from the antilink whitelist because they are not on the blacklist"

                    DatabaseUpdates.manage_antilink_whitelist(guild_id=guild_id, operation="remove", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3])

                    emb = discord.Embed(title=f"{Emojis.help_emoji} The following items have been removed from the antilink whitelist or were not listed", 
=======
                    formatted_items = "\n".join(item) if item != [] else "> All the items you specified were on the anti-link whitelist"
                    formatted_add_items = "\n".join(second_item) if second_item != [] else "> None of the items you specified could be removed from the anti-link whitelist because they are not on the blacklist"

                    await DatabaseUpdates.manage_antilink_whitelist(guild_id=guild_id, operation="remove", channel_id=items_dict[0], category_id=items_dict[1], role_id=items_dict[2], user_id=items_dict[3])

                    emb = discord.Embed(title=f"{Emojis.help_emoji} The following items have been removed from the anti-link whitelist or were not listed", 
>>>>>>> neues-repo/main
                        description=f"""### {Emojis.dot_emoji} The following items were not on the whitelist:
                        {formatted_items}\n### {Emojis.dot_emoji} Was deleted from the white list:
                        {formatted_add_items}""", color=bot_colour)
                    return emb
                
            else:

<<<<<<< HEAD
                emb = discord.Embed(title=f"{Emojis.help_emoji} Nothing can be {'added to the antilink whitelist' if operation == 'add' else 'removed from the antilink whitelist'}", 
                    description=f"""{Emojis.dot_emoji} {"All the things you have specified are already on the antilink whitelist" 
                        if operation == "add" else 
                        "None of the things you mentioned are on the antilink whitelist"}""", color=bot_colour)
=======
                emb = discord.Embed(title=f"{Emojis.help_emoji} Nothing can be {'added to the anti-link whitelist' if operation == 'add' else 'removed from the anti-link whitelist'}", 
                    description=f"""{Emojis.dot_emoji} {"All the things you have specified are already on the anti-link whitelist" 
                        if operation == "add" else 
                        "None of the things you mentioned are on the anti-link whitelist"}""", color=bot_colour)
>>>>>>> neues-repo/main
                return emb
            
        else:

            emb = discord.Embed(title=f"{Emojis.help_emoji} You have not specified anything!", 
<<<<<<< HEAD
                description=f"""{Emojis.dot_emoji}You have not specified anything {"what should be added to the antilink whitelist" 
=======
                description=f"""{Emojis.dot_emoji}You have not specified anything {"what should be added to the anti-link whitelist" 
>>>>>>> neues-repo/main
                    if operation == "add" else
                    "what should be removed from the bonus XP list"}""", color=bot_colour)
            return emb


<<<<<<< HEAD
    @commands.slash_command(name = "add-antilink-whitelist", description = "Exclude channels, roles, and categories from the antilink system!")
    @commands.has_permissions(administrator = True)
    async def add_antilink_whitelist(self, ctx:discord.ApplicationContext,
        channel:Option(discord.TextChannel, description="Select a channel to be excluded from the antilink system") = None,
        category:Option(discord.CategoryChannel, description="Select a category to be excluded from the anti link system") = None,
        role:Option(discord.Role, description="Select a role to be excluded from the anti link system") = None,
        user:Option(discord.User, description="Select a user to be excluded from the anti link system") = None
=======
    @commands.slash_command(name = "add-antilink-whitelist", description = "Exclude channels, roles, and categories from the anti-link system!")
    @commands.has_permissions(administrator = True)
    async def add_antilink_whitelist(self, ctx:discord.ApplicationContext,
        channel:Option(discord.TextChannel, description="Select a channel to be excluded from the anti-link system") = None,
        category:Option(discord.CategoryChannel, description="Select a category to be excluded from the anti-link system") = None,
        role:Option(discord.Role, description="Select a role to be excluded from the anti-link system") = None,
        user:Option(discord.User, description="Select a user to be excluded from the anti-link system") = None
>>>>>>> neues-repo/main
        ):

        emb = await self.config_antilink_whitelist(guild_id=ctx.guild.id, channel=channel, category=category, role=role, user=user, operation="add")
        await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "remove-antilink-whitelist", description = "Select channels, categories, roles or users to be removed from the whitelist!")
    @commands.has_permissions(administrator = True)
    async def remove_antilink_whitelist(self, ctx:discord.ApplicationContext,
<<<<<<< HEAD
        channel:Option(discord.TextChannel, description="Select a channel to be removed from the antilink whitelist") = None,
        category:Option(discord.CategoryChannel, description="Select a category to be removed from the antilink whitelist") = None,
        role:Option(discord.Role, description="Select a role to be removed from the antilink whitelist") = None,
        user:Option(discord.User, description="Select a user to be removed from the antilink whitelist") = None
=======
        channel:Option(discord.TextChannel, description="Select a channel to be removed from the anti-link whitelist") = None,
        category:Option(discord.CategoryChannel, description="Select a category to be removed from the anti-link whitelist") = None,
        role:Option(discord.Role, description="Select a role to be removed from the anti-link whitelist") = None,
        user:Option(discord.User, description="Select a user to be removed from the anti-link whitelist") = None
>>>>>>> neues-repo/main
        ):

        emb = await self.config_antilink_whitelist(guild_id=ctx.guild.id, channel=channel, category=category, role=role, user=user, operation="remove")
        await ctx.respond(embed=emb)
        

<<<<<<< HEAD
    @commands.slash_command(name = "show-antilink-whitelist", description = "Shows what is listed on the antilink whitelist")
    async def show_antilink_whitelist(self, ctx:discord.ApplicationContext):

        white_list = ModeratorCommands.show_antilink_system_whitelist(guild_id = ctx.guild.id)
        
        emb = discord.Embed(description=f"""## Antilink whitelist
            {Emojis.dot_emoji} Here you can see all entries of the antilink whitelist:
=======
    @commands.slash_command(name = "show-antilink-whitelist", description = "Shows what is listed on the anti-link whitelist")
    async def show_antilink_whitelist(self, ctx:discord.ApplicationContext):

        white_list = await ModeratorCommands.show_antilink_system_whitelist(guild_id = ctx.guild.id)
        
        emb = discord.Embed(description=f"""## Anti-link whitelist
            {Emojis.dot_emoji} Here you can see all entries of the anti-link whitelist:
>>>>>>> neues-repo/main
            
            {white_list}""", color=bot_colour)
        await ctx.respond(embed=emb)

    
<<<<<<< HEAD
    @commands.slash_command(name = "reset-antilink-whitelist", description = "Resets the antilink whitelist and thus deletes everything on it!")
    @commands.has_permissions(administrator = True)
    async def reset_antilink_whitelist(self, ctx:discord.ApplicationContext):
        
        check_whitelist = DatabaseCheck.check_antilink_whitelist(guild_id = ctx.guild.id)

        if check_whitelist:
            
            DatabaseUpdates.manage_antilink_whitelist(guild_id = ctx.guild.id, operation = "reset")

            emb = discord.Embed(description=f"""## The antilink whitelist has been successfully reset
                {Emojis.dot_emoji} All channels, categories, roles and users that were on the whitelist have been removed from it
                {Emojis.dot_emoji} If you want to put items back on the whitelist you can use the /add-antilink-whitelist command""", color=bot_colour)
=======
    @commands.slash_command(name = "reset-antilink-whitelist", description = "Resets the anti-link whitelist and thus deletes everything on it!")
    @commands.has_permissions(administrator = True)
    async def reset_antilink_whitelist(self, ctx:discord.ApplicationContext):
        
        check_whitelist = await DatabaseCheck.check_antilink_whitelist(guild_id = ctx.guild.id)

        if check_whitelist:
            
            await DatabaseUpdates.manage_antilink_whitelist(guild_id = ctx.guild.id, operation = "reset")

            emb = discord.Embed(description=f"""## The anti-link whitelist has been successfully reset
                {Emojis.dot_emoji} All channels, categories, roles and users that were on the whitelist have been removed from it
                {Emojis.dot_emoji} If you want to put items back on the whitelist you can use the /add-anti-link-whitelist command""", color=bot_colour)
>>>>>>> neues-repo/main
            await ctx.respond(embed=emb)

        else:

<<<<<<< HEAD
            emb = discord.Embed(description=f"""## The antilink whitelist could not be reset
                {Emojis.dot_emoji} No entries were found
                {Emojis.dot_emoji} Therefore the antilink whitelist could not be reset""",color=bot_colour)
=======
            emb = discord.Embed(description=f"""## The anti-link whitelist could not be reset
                {Emojis.dot_emoji} No entries were found
                {Emojis.dot_emoji} Therefore the anti-link whitelist could not be reset""",color=bot_colour)
>>>>>>> neues-repo/main
            await ctx.respond(embed=emb)


        
####################################  Moderation commands  ###################################


    @commands.slash_command(name = "ban", description = "Ban a user so that he can no longer join the server!")
    @commands.has_permissions(ban_members = True, administrator = True)
    async def ban(self, ctx:discord.ApplicationContext, 
        member:Option(discord.Member, required = True, description = "Choose the user you want to ban!"), 
        reason:Option(str, description = "Give a reason why this user should be banned! (optional)", required = False)):

        if member.id == ctx.author.id:

            emb = discord.Embed(title=f"{Emojis.help_emoji} You can't ban yourself!",
                description=f"""{Emojis.dot_emoji} Select another user you want to ban.""", color=bot_colour)
            await ctx.respond(embed=emb)

        elif member.guild_permissions.administrator:

            emb = discord.Embed(title=f"{Emojis.help_emoji} You can't ban an admin", 
                description=f"""{Emojis.dot_emoji} Choose another user you want to ban who is not an admin.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            if reason == None:
                reason = f"No reason was given"
            emb=discord.Embed(title=f"{member.name} was successfully banned {Emojis.succesfully_emoji}", description=f"{Emojis.dot_emoji} {reason}", color=bot_colour)
            await member.ban(reason = reason)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "unban", description = "Pick up the ban of a user!")
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx:discord.ApplicationContext, id:Option(str, description = "Enter the ID of the user you want to unban here!", required = True)):
        
        try:

            member = await bot.get_or_fetch_user(int(id))
            await ctx.guild.unban(member)

            emb = discord.Embed(title=f"{member.name} was successfully unbanned {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} {member.mention} has been successfully unbanned and can now enter the server again.""", color=bot_colour)
            await ctx.respond(embed=emb)

        except:    
            
            emb = discord.Embed(title=f"{Emojis.help_emoji} The user whose ID you entered was not banned", 
                description=f"""{Emojis.dot_emoji} The ID you entered does not belong to a user who has been banned on this server.""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name = "kick", description = "Kick a member off the server!")
    @commands.has_permissions(kick_members = True, administrator = True)
    async def kick(self, ctx:discord.ApplicationContext, member:Option(discord.Member, description = "Enter a user you want to remove from the server!")):

        if member.id == ctx.author.id:
            emb = discord.Embed(title=f"{Emojis.help_emoji} You can't kick yourself!", 
                description=f"""{Emojis.dot_emoji} Select another user you want to kick.""", color=bot_colour)
            await ctx.respond(embed=emb)

        elif member.guild_permissions.administrator:
            
            emb = discord.Embed(title=f"{Emojis.help_emoji} You can't kick an admin!",
                description=f"""{Emojis.dot_emoji} Choose another user you want to kick who is not an admin.""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:
            
            emb=discord.Embed(title=f"{member.name} was successfully kicked {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} You have successfully kicked {member.mention}.""", color=bot_colour)
            await ctx.respond(embed=emb)
            await member.kick()


<<<<<<< HEAD
    @commands.slash_command(name = 'timeout', description = "Send a user to timeout!")
=======
    @commands.slash_command(name = "timeout", description = "Send a user to timeout!")
>>>>>>> neues-repo/main
    @commands.has_permissions(moderate_members = True)
    async def timeout(self, ctx:discord.ApplicationContext, 
        user:Option(discord.Member, required = True, description="Select the user you want to timeout!"), 
        reason:Option(str, required = False, description="Enter a reason why you want to timeout this user! (optional)"), 
        days: Option(int, max_value = 27, default = 0, required = False, description="Enter how many days you want to timeout this user! (optional)"), 
        hours: Option(int, max_value = 24, default = 0, required = False, description="Enter how many hours you want to timeout this user! (optional)"), 
        minutes: Option(int, max_value = 60, default = 0, required = False, description="Enter how many minutes you want to timeout this user! (optional)"), 
        seconds: Option(int, max_value  = 60, default = 0, required = False, description="Enter how many seconds you want to timeout this user! (optional)")):

        duration = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)

        if user.id == ctx.author.id:

            emb = discord.Embed(title=f"{Emojis.help_emoji} You can't timeout yourself!", 
                description=f"""{Emojis.dot_emoji} Select another user that you want to timeout.""", color=bot_colour)
            await ctx.respond(embed=emb)
            
        elif user.guild_permissions.moderate_members:

            emb = discord.Embed(title=f"{Emojis.help_emoji} You can't timeout admins!", 
                description=f"""{Emojis.dot_emoji} Select another user you want to timeout who is not an admin.""")
            await ctx.respond(embed=emb)
            
        else:

            await user.timeout_for(duration)
            emb = discord.Embed(title=f"{user.name} Has been successfully timed out", 
                description=f"""{Emojis.dot_emoji} {user.mention} was timed out for: {days} days, {hours} hours, {minutes} minutes and {seconds} seconds.
                {Emojis.dot_emoji} Reason for the timeout: {reason if reason != None else 'no reason given'}.""", color=bot_colour)
            await ctx.respond(embed=emb)


<<<<<<< HEAD
    @commands.slash_command(name = 'remove-timeout', description = "Cancel the timeout of a user!")
=======
    @commands.slash_command(name = "remove-timeout", description = "Cancel the timeout of a user!")
>>>>>>> neues-repo/main
    @commands.has_permissions(moderate_members = True)
    async def remove_timeout(self, ctx:discord.ApplicationContext, member:Option(discord.Member, required = True, description="Select a user from whom you want to cancel the timeout!")):

        try:

            await member.remove_timeout()
            emb = discord.Embed(title=f"The timeout of {member.name} was successfully canceled {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} {member.mention} can now write messages again and actively participate in conversations.""", color=bot_colour)
            await ctx.respond(embed=emb)

        except:

            emb = discord.Embed(title=f"{Emojis.help_emoji} {member.name} was not timed out!", 
                description=f"{Emojis.dot_emoji} Select another user whose timeout you want to cancel.", color=bot_colour)
            await ctx.respond(embed=emb)


<<<<<<< HEAD
=======
    @commands.slash_command(name = "give-role", description = "Add a role to a specific user!")
    @commands.has_permissions(moderate_members = True)
    async def give_role(self, ctx:discord.ApplicationContext, 
        user:Option(discord.User, description="Choose a user you want to add the role to!"),
        role:Option(discord.Role, description="Choose a role that you want to add to the user!")):

        if role.permissions.administrator or role.permissions.moderate_members:

            emb = discord.Embed(description=f"""## The role has admin or moderation rights
                {Emojis.dot_emoji} I can't give the role to a user because it has admin or moderation rights
                {Emojis.help_emoji} If you want to give another role to a user just use the `give-role` command""")

        else:

            try:

                await user.add_roles(role)

                emb = discord.Embed(description=f"""## The role was successfully added
                    {Emojis.dot_emoji} The role {role.mention} would be successfully added to the user {user.mention}
                    {Emojis.help_emoji} If you want to remove the role again, you can do this using the `remove-role` command""", color=bot_colour)
                await ctx.respond(embed=emb)

            except:

                emb = discord.Embed(description=f"""## The role could not be added
                    {Emojis.dot_emoji} The role {role.mention} could not be added because {user.mention} already has it
                    {Emojis.help_emoji} If you want to add another role you can do this via the `give-role` command""", color=bot_colour)
                await ctx.respond(embed=emb)


    @commands.slash_command(name = "remove-role", description = "Removes a role from a specific user!")
    @commands.has_permissions(moderate_members = True)
    async def remove_role(self, ctx:discord.ApplicationContext,
        user:Option(discord.User, description="Choose from which user you want to remove the role!"),
        role:Option(discord.Role, description="Select which role you want to remove from the user!")):
        
        try:

            emb = discord.Embed(description=f"""## The role has been successfully removed
                {Emojis.dot_emoji} {user.mention} was successfully removed from the {role.mention} role
                {Emojis.dot_emoji} If you want to add a role again you can use the `give-role` command""", color=bot_colour)
            await ctx.respond(embed=emb)

        except:

            emb = discord.Embed(description=f"""## The role could not be removed
                {Emojis.dot_emoji} The {role.mention} role could not be removed because {user.mention} does not have it
                {Emojis.help_emoji} If you want to remove another role, you can do this using the `remove-role` command""", color=bot_colour)
            await ctx.respond(embed=emb)


>>>>>>> neues-repo/main
    @commands.slash_command(name = "clear", description = "Delete messages in the channel!")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx:discord.ApplicationContext, quantity:Option(int, description = "How many messages do you want to delete?", required = True)):
        await ctx.defer()
        z = await ctx.channel.purge(limit = quantity)
        await ctx.send(f"I have deleted {len(z)} messages.")


<<<<<<< HEAD
    @commands.slash_command(name = "server-info", description="Server info!")
    async def serverinfo(self, ctx):

        embed = discord.Embed(title=f"{ctx.guild.name} Info", description="Information of this Server", color=discord.Colour.blue())
        embed.add_field(name='🆔Server ID', value=f"{ctx.guild.id}")
        embed.add_field(name='📆Created On', value=ctx.guild.created_at.strftime("%b %d %Y"))
        embed.add_field(name='👑Owner', value=f"{ctx.guild.owner.mention}")
        embed.add_field(name='👥Members', value=f'{ctx.guild.member_count} Members')
        embed.add_field(name='🌎Region', value=f'{ctx.guild.preferred_locale}')
        embed.add_field(name='🌎Roles', value=f'{len(ctx.guild.roles)}')
        embed.add_field(name='🌎Boosts', value=f'{len(ctx.guild.premium_subscribers)}')
=======
    @commands.slash_command(name = "server-info", description="Displays all server data!")
    async def serverinfo(self, ctx):

        embed = discord.Embed(title=f"{ctx.guild.name} Info", description="Information of this Server", color=bot_colour)
        embed.add_field(name='Server ID', value=f"{ctx.guild.id}")
        embed.add_field(name='📆Created On', value=ctx.guild.created_at.strftime("%b %d %Y"))
        embed.add_field(name='👑Owner', value=f"{ctx.guild.owner.mention}")
        embed.add_field(name='👥Members', value=f'{ctx.guild.member_count} Members')
        embed.add_field(name='Region', value=f'{ctx.guild.preferred_locale}')
        embed.add_field(name='Roles', value=f'{len(ctx.guild.roles)}')
        embed.add_field(name=f'{Emojis.boost}Boosts', value=f'{len(ctx.guild.premium_subscribers)}')
>>>>>>> neues-repo/main
        embed.add_field(name='💬 Channels', value=f'Text [{len(ctx.guild.text_channels)}], Voice [{len(ctx.guild.voice_channels)}], \nCategories [{len(ctx.guild.categories)}], \nThreads [{len(ctx.guild.threads)}], Stage [{len(ctx.guild.stage_channels)}]', inline=False)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_author(name=str(ctx.author.name), icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)


    # Anti ghost ping system
    @commands.Cog.listener()
    async def on_message_delete(self, message:discord.Message):

<<<<<<< HEAD
        check_settings = DatabaseCheck.check_bot_settings(guild_id=message.guild.id)
=======
        check_settings = await DatabaseCheck.check_bot_settings(guild_id=message.guild.id)
>>>>>>> neues-repo/main

        if isinstance(message.channel, discord.DMChannel):
            return
        
        else:

            # If the value is above 0, the ghost ping system is deactivated
            if message.author.bot:
                return

            if check_settings[2] != 0 and check_settings[2] != None:

                if message.mentions != 0:
                    if len(message.mentions) < 3:
                        for m in message.mentions:
                            if m == message.author or m.bot:
                                pass
                            else:
                                embed=discord.Embed(title=f":ghost: | Ghost ping", description=f"{Emojis.dot_emoji} **{m}** you were ghostping from {message.author.mention}.\n \n**message:** {message.content}", color=bot_colour)
                                await message.channel.send(embed=embed)
                    else:
                        embed=discord.Embed(title=f":ghost: | Ghost ping", description=f"{Emojis.dot_emoji} **{len(message.mentions)} User** have been ghostpinged.\n \n**message by {message.author.mention}:** {message.content}", color=bot_colour)
                        await message.channel.send(embed=embed)


<<<<<<< HEAD
    @commands.slash_command(name = "ghost-ping-settings", description = "Schalte das ghost ping system ein oder aus!")
    async def ghost_ping_settings(self, ctx:discord.ApplicationContext):

        # If the database contains 0, the system is deactivated; if it contains 1, it is activated
        check_settings = DatabaseCheck.check_bot_settings(guild_id=ctx.guild.id)
=======
    @commands.slash_command(name = "ghost-ping-settings", description = "Switch the ghost ping system on or off!")
    async def ghost_ping_settings(self, ctx:discord.ApplicationContext):

        # If the database contains 0, the system is deactivated; if it contains 1, it is activated
        check_settings = await DatabaseCheck.check_bot_settings(guild_id=ctx.guild.id)
>>>>>>> neues-repo/main

        emb = discord.Embed(title=f"{Emojis.settings_emoji} Here you can set the anti ghost ping system ", 
            description=f"""{Emojis.dot_emoji} Currently the anti ghost ping system is {'**enabled**' if check_settings[2] == 0 else '**disabled**'}
            {Emojis.dot_emoji} If you want it to {'**turn it on**' if check_settings[2] == 0 else '**turn it off**'} press the lower button""", color=bot_colour)
        await ctx.respond(embed=emb, view=GhostPingButtons())


<<<<<<< HEAD
    @commands.slash_command()
    async def userinfo(ctx:discord.ApplicationContext, member:Option(discord.Member, description="Select a user from whom you want to view the user infos!")):
=======
    @commands.slash_command(name = "show-invites", description = "Shows how many users have been invited by a specific user!")
    async def show_invites(self, ctx:discord.ApplicationContext, user:Option(discord.Member, description="Choose a user of whom you want to see how many other users he has invited!")):

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


    @commands.slash_command(description = "Displays all information about a user!")
    async def userinfo(self, ctx:discord.ApplicationContext, member:Option(discord.Member, description="Select a user from whom you want to view the user infos!")):
>>>>>>> neues-repo/main
        member = ctx.author if not member else member

        unix_join_time = calendar.timegm(member.joined_at.utctimetuple())
        unix_create_time = calendar.timegm(member.created_at.utctimetuple())

        badge = ""
        if member.public_flags.bug_hunter:
<<<<<<< HEAD
            badge += "<:bughunter:1045796473691979776> Bug Hunter\n"
        if member.public_flags.bug_hunter_level_2:
            badge += "<:bughunter2:1045796474744750090> Bug Hunter Level 2\n"
        if member.public_flags.early_supporter:
            badge += "<:earlysupporter:1045796475864625283> Early Suppoter\n"
        if member.public_flags.verified_bot_developer:
            badge += "<:botdev:1045796472408506368> Developer\n"
        if member.public_flags.partner:
            badge += "<:partner:1045796481518551102> Partner\n"
        if member.public_flags.staff:
            badge += "<:staff:1045796482705543168> Staff\n"
        if member.public_flags.hypesquad_balance:
            badge += f"<:hypesquad_balance:1045796476992884838> Hypesquad Balance\n"
        if member.public_flags.hypesquad_bravery:
            badge += f"<:hypesquad_bravery:1045796478507032638> Hypesquad Bravery\n"
        if member.public_flags.hypesquad_brilliance:
            badge += f"<:hypesquad_brilliance:1045796480172163152> Hypesquad Brilliance\n"
=======
            badge += Emojis.bughunter
        if member.public_flags.bug_hunter_level_2:
            badge += Emojis.bughunter2
        if member.public_flags.early_supporter:
            badge += Emojis.earlysupporter
        if member.public_flags.verified_bot_developer:
            badge += Emojis.botdev
        if member.public_flags.partner:
            badge += Emojis.partner
        if member.public_flags.staff:
            badge += Emojis.staff
        if member.public_flags.hypesquad_balance:
            badge += Emojis.hypesquad_balance
        if member.public_flags.hypesquad_bravery:
            badge += Emojis.hypesquad_bravery
        if member.public_flags.hypesquad_brilliance:
            badge += Emojis.hypesquad_brilliance
        if member.public_flags.active_developer:
            badge += Emojis.dev
>>>>>>> neues-repo/main

        user_banner = await bot.fetch_user(member.id)

        if user_banner.banner is not None:
            if member.avatar is not None:
<<<<<<< HEAD
                embed = discord.Embed(colour=member.color,
=======
                embed = discord.Embed(colour=bot_colour,
>>>>>>> neues-repo/main
                                    timestamp=datetime.utcnow(),
                                    description=f"[User Avatar]({member.avatar.url}) | [User Banner]({user_banner.banner.url})")
                embed.set_image(url=f"{user_banner.banner.url}")
                embed.set_thumbnail(url=f'{member.display_avatar.url}')
            else:
<<<<<<< HEAD
                embed = discord.Embed(colour=member.color,
=======
                embed = discord.Embed(colour=bot_colour,
>>>>>>> neues-repo/main
                                    timestamp=datetime.utcnow(),
                                    description=f"[User Banner]({user_banner.banner.url})")
                embed.set_image(url=f"{user_banner.banner.url}")
        elif member.avatar is not None:
<<<<<<< HEAD
            embed = discord.Embed(colour=member.color,
=======
            embed = discord.Embed(colour=bot_colour,
>>>>>>> neues-repo/main
                                    timestamp=datetime.utcnow(),
                                    description=f"[User Avatar]({member.avatar.url})")
            embed.set_thumbnail(url=f'{member.display_avatar.url}')
        else:
<<<<<<< HEAD
            embed = discord.Embed(colour=member.color,
=======
            embed = discord.Embed(colour=bot_colour,
>>>>>>> neues-repo/main
                                    timestamp=datetime.utcnow())

        embed.set_author(name=f"Userinfo")

        embed.add_field(name="Name:",
                        value=f"`{member} (Bot)`" if member.bot else f"`{member}`",
                        inline=True)
        embed.add_field(name=f"Mention:",
                        value=member.mention,
                        inline=True)
        embed.add_field(name="Nick:",
<<<<<<< HEAD
                        value=f"`{member.nick}`" if member.nick else "Nicht gesetzt",
=======
                        value=f"`{member.nick}`" if member.nick else "Not set",
>>>>>>> neues-repo/main
                        inline=True)
        embed.add_field(name="ID:",
                        value=f"`{member.id}`",
                        inline=True)

        if member.status == discord.Status.online:
            if member.is_on_mobile():
<<<<<<< HEAD
                embed.add_field(name="Status:", value="`Handy`")
            else:
                embed.add_field(name="Status", value=f"`Online`")
        elif member.status == discord.Status.idle:
            embed.add_field(name="Status:",
                            value=f"`Abwesend`")
        elif member.status == discord.Status.dnd:
            embed.add_field(name="Status:",
                            value=f"`Beschäftigt`")
        elif member.status == discord.Status.offline:
            embed.add_field(name="Status:",
                            value=f"`Offline`")
        elif member.status == discord.Status.invisible:
            embed.add_field(name="Status:",
                            value=f"`Unsichtbar`")

        embed.add_field(name="Erstellt am:",
                        value=f"<t:{unix_create_time}:f> (<t:{unix_create_time}:R>)",
                        inline=True)
        embed.add_field(name="Beigetreten am:",
                        value=f'<t:{unix_join_time}:f> (<t:{unix_join_time}:R>)',
                        inline=True)
        embed.add_field(name="Höchste Rolle:",
                        value=member.top_role.mention,
                        inline=True)
        embed.add_field(name="<:booster:1045801339780862063> Booster:",
                        value=f"`Ja`" if member.premium_since else "`Nein`",
=======
                embed.add_field(name="Status:", value=f"{Emojis.phone} `Mobile`")
            else:
                embed.add_field(name="Status", value=f"{Emojis.online} `Online`")
        elif member.status == discord.Status.idle:
            embed.add_field(name="Status:",
                            value=f"{Emojis.idle} `Idle`")
        elif member.status == discord.Status.dnd:
            embed.add_field(name="Status:",
                            value=f"{Emojis.dnd} `Do not disturb`")
        elif member.status == discord.Status.offline:
            embed.add_field(name="Status:",
                            value=f"{Emojis.invisible} `Offline`")
        elif member.status == discord.Status.invisible:
            embed.add_field(name="Status:",
                            value=f"{Emojis.invisible} `Invisible`")

        embed.add_field(name="Created on:",
                        value=f"<t:{unix_create_time}:f> (<t:{unix_create_time}:R>)",
                        inline=True)
        embed.add_field(name="Joined on:",
                        value=f'<t:{unix_join_time}:f> (<t:{unix_join_time}:R>)',
                        inline=True)
        embed.add_field(name="Highest role:",
                        value=member.top_role.mention,
                        inline=True)
        embed.add_field(name=f"{Emojis.boost} Booster:",
                        value=f"`Yes`" if member.premium_since else "`No`",
>>>>>>> neues-repo/main
                        inline=True)
        if badge != "":
            embed.add_field(name="Badges:",
                            value=badge,
                            inline=True)

        if member.activities:
            for activity in member.activities:
                if str(activity) == "Spotify":
                    embed.add_field(name="Spotify",
                                    value=f'Title: {activity.title}\nArtist: {activity.artist}\n')

        embed.set_thumbnail(url=f'{member.avatar.url}')

<<<<<<< HEAD
        await ctx.reply(embed=embed)
=======
        await ctx.respond(embed=embed)
>>>>>>> neues-repo/main
            

def setup(bot):
    bot.add_cog(ModeratorCommands(bot))



<<<<<<< HEAD
=======
#################################################  Interactions form mod tools  ##########################################


>>>>>>> neues-repo/main
class GhostPingButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Turn off / on the Ghost ping system", style=discord.ButtonStyle.blurple, custom_id="turn_off_on", row=1)
    async def on_off_ghost_ping(self, button, interaction:discord.Interaction):

<<<<<<< HEAD
        check_settings = DatabaseCheck.check_bot_settings(guild_id=interaction.guild.id)
        DatabaseUpdates.update_bot_settings(guild_id=interaction.guild.id, ghost_ping=1 if check_settings[2] == 0 else 0)
=======
        check_settings = await DatabaseCheck.check_bot_settings(guild_id=interaction.guild.id)
        await DatabaseUpdates.update_bot_settings(guild_id=interaction.guild.id, ghost_ping=1 if check_settings[2] == 0 else 0)
>>>>>>> neues-repo/main

        emb = discord.Embed(title=f"{Emojis.help_emoji} You have successfully switched the ghost ping system {'**off**' if check_settings[2] != 0 else '**on**'}", 
            description=f"""{Emojis.dot_emoji} The anti ghost ping system is now {'**disabled**.' if check_settings[2] != 0 else f'''**enabled**.
            {Emojis.dot_emoji} From now on a message is always sent when a user marks someone and deletes this message.'''}""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label="Cancel from setting ghost ping system", style=discord.ButtonStyle.blurple, custom_id="cancel_ghost_ping", row=2)
    async def cancel_ghost_ping_settings(self, button, interaction:discord.Interaction):

        emb = discord.Embed(title=f"{Emojis.help_emoji} The setting of the anti ghost ping system was canceled", 
            description=f"""{Emojis.dot_emoji} The setting was successfully canceled but you can change the settings at any time.""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)

