from discord.interactions import Interaction
from utils import *
from sql_function import *
from discord.ext import tasks

# Dictionary for the check functions (does not have to be in each command individually)
interval_list = {
    "day":"daily leaderboard",
    "week":"weekly leaderboard",
    "month":"monthly leaderboard",
    "general":"general leaderboard"
    }


interval_text = {
    "daily":("one day", 1),
    "weekly":("one week", 7),
    "monthly":("one month", 30)
    }


class Messageleaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name = "set-message-leaderboard", description = "Set the message leaderboard system!")
    @commands.has_permissions(administrator = True)
    async def set_message_leaderboard(self, ctx:discord.ApplicationContext):

        settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild_id, system = "message")
        
        if settings == None:

            await DatabaseUpdates.create_leaderboard_settings(guild_id = ctx.guild.id, system = "message")
            settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild_id, system = "message")

        emb = discord.Embed(description=f"""## Set the message leaderboard
            {Emojis.dot_emoji} With the lower select menu you can define a channel in which the leaderboard should be sent
            {Emojis.dot_emoji} Then you can also set an interval at which time intervals the leaderboard should be updated
            {Emojis.dot_emoji} You can also switch the system off or on currently it is {'switched off' if settings[1] else 'switched on'}. (as soon as it is switched off, no more messages are counted and when it is switched on, the leaderboard is reset)
            {Emojis.dot_emoji} The leaderboard is edited when you update it, so you should make sure that no one else can write in the channel you specified
            {Emojis.help_emoji} **The leaderboard always shows the data of the past interval, for example it shows the best users who wrote the most messages yesterday**""", color=bot_colour)        
        await ctx.respond(embed=emb, view=SetleaderboardChannel())


    @commands.slash_command(name = "show-message-leaderboard-setting", description = "Shows all settings of the message leaderboard!")
    async def show_message_leaderboard_settings(self, ctx:discord.ApplicationContext):
        
        settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild.id, system = "message")
        
        if settings == None:

            await DatabaseUpdates.create_leaderboard_settings(guild_id = ctx.guild.id, system = "message")

            await ctx.respond(embed = GetEmbed.get_embed(embed_index=8))

        elif settings[6] == None or all(x for x in [settings[2], settings[3], settings[4]]) == None:

            await ctx.respond(embed = GetEmbed.get_embed(embed_index=8))

        else:

            intervals = {
                settings[2]:"Daily",
                settings[3]:"Weekly",
                settings[4]:"Monthly"
            }
            intervals_text = []
            for i in settings[2], settings[3], settings[4]:

                if i != None:

                    intervals_text.append(f"{Emojis.dot_emoji} {intervals[i]} updating Message leaderboard\n")

            emb = discord.Embed(description=f"""## Here you can see all the settings of the message leaderboard
                {Emojis.dot_emoji} Das message leaderboard ist aktuell {'angeschalten' if settings[1] == 0 else 'ausgeschalten'}
                {Emojis.dot_emoji} {f'Currently <#{settings[6]}> is set as' if settings[5] != None else 'No'} message leaderboard channel has been set
                {Emojis.dot_emoji} **The following intervals are currently defined for which a leaderboard exists:**

                {"".join(intervals_text) if intervals_text != [] else f'{Emojis.dot_emoji} No intervals have been defined yet'}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    def check_interval_role(self, guild_id, interval):

        roles = DatabaseCheck.check_leaderboard_roles(guild_id = guild_id)

        for role in roles:

            if role[2] == 0 and role[4] == interval:

                return True

        return False 


    @commands.slash_command(name = "add-message-leaderboard-role", description = "Define roles for the message leaderboard that are assigned when you reach a certain position!")
    @commands.has_permissions(administrator = True)
    async def add_leaderboard_role_message(self, ctx:discord.ApplicationContext, 
        role:Option(discord.Role, required = True, description="Define a role for the leaderboard to assign upon reaching a specific position"), 
        position:Option(required = True, choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "general role"], description="Select the position to assign this role (if general, it’s always assigned if on the leaderboard)"),
        interval:Option(str, description="Select the leaderboard for which this role is to be assigned", choices = ["daily leaderboard", "weekly leaderboard", "monthly leaderboard", "general leaderboard"])):
    
        interval_db = next((key for key, value in interval_list.items() if value == interval), None)
        position_db = 0 if "general role" == position else int(position)

        check_role = DatabaseCheck.check_leaderboard_roles(guild_id = ctx.guild.id, role_id = role.id, position = position_db)

        if check_role is not None and check_role[4] == interval_db:
            
            if check_role[2] == position_db and check_role[1] == role.id and interval_db == check_role[4]:
                
                emb = discord.Embed(description=f"""## This role has already been assigned to this position
                    {Emojis.dot_emoji} The role {role.mention} {f'is already assigned to the {position} space' if position_db != 0 else f'is defined as a general role for the {interval_list[check_role[4]]}'}
                    {Emojis.dot_emoji} If you want to overwrite the role, position or the associated interval, you can simply execute this command again""", color=bot_colour)
                await ctx.respond(embed=emb)

            elif check_role[2] == 0 and position_db != 0:
            
                emb = discord.Embed(description=f"""## Diese rolle ist aktuell als geneal role festgelegt
                    {Emojis.dot_emoji} Aktuell ist <@&{check_role[1]}> als generelle rolle festgelegt möchtest du diese rolle für den {position} platz festlegen?
                    {Emojis.dot_emoji} Mit den unteren Button kannst du deine entscheidung bestätigen""", color=bot_colour)
                await ctx.respond(embed=emb, view=OverwriteRole(role=role, position=position_db, interval=interval_db, settings="position", delete=check_role[1]))

            elif check_role[2] == 0 or self.check_interval_role(guild_id=ctx.guild.id, interval=interval_db):
                
                emb = discord.Embed(description=f"""## {'This role is currently set as a general role' if check_role[1] != role.id else 'This interval already has a general role'}
                    {Emojis.dot_emoji} The role <@&{check_role[1]}> is currently defined as the general role for the interval {interval_list[check_role[4]]}
                    {Emojis.dot_emoji} {f'Would you like to replace the role <@&{check_role[1]}> with the role {role.mention} and set this as a new general role?\n{Emojis.dot_emoji} Everyone who is then listed on the leaderboard will then receive this role' 
                    if check_role[1] != role.id else 
                    f'Do you want to assign the role <@&{check_role[1]}> as a normal role for the {position} space?'}""", color=bot_colour)
                await ctx.respond(embed=emb, view=OverwriteRole(role=role, position=position_db, interval=interval_db, settings="role" if check_role[1] != role.id else "interval", delete=check_role))

            else:
                
                emb = discord.Embed(description=f"""## {'This role' if check_role[1] != role.id else 'This position'} has already been assigned
                    {Emojis.dot_emoji} Currently, the role <@&{check_role[1]}> is assigned for the {check_role[2]} place, for the {interval_list[check_role[4]]}
                    {Emojis.dot_emoji} Do you want to {f'replace the role <@&{check_role[1]}> with the role {role.mention} for the position {position} for the {interval_list[check_role[4]]}' if check_role[1] != role.id else f'change the place for which the role {role.mention} is assigned to {position}? this role is then always assigned when someone reaches the {position} place on the {interval}'}""", color=bot_colour)
                await ctx.respond(embed=emb, view=OverwriteRole(role=role, position=position_db, interval=interval_db, settings="role" if check_role[1] != role.id else "position", delete=check_role))

        else:
                
            await DatabaseUpdates.manage_leaderboard_roles(guild_id = ctx.guild.id, role_id = role.id, position = position_db, status = "message", interval = interval_db)

            emb = discord.Embed(description=f"""## The new leaderboard role has been successfully established
                {Emojis.dot_emoji} The role {role.mention} was successfully {f'set for the {position} place' if position_db != 0 else f'set as general role'}
                {Emojis.dot_emoji} {f'If a user now reaches the {position} place on the {interval} he gets the role {role.mention}' if position_db != 0 else f'If a user is now listed on the {interval} he gets the role {role.mention} until the leaderboard is updated again and a new user gets this role'}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name = "remove-message-leaderboard-role")
    @commands.has_permissions(administrator = True)
    async def remove_leaderboard_role_message(self, ctx:discord.ApplicationContext, 
        role:Option(discord.Role, description="Remove a role from the leaderboard roles!"), 
        interval:Option(str, description="Choose from which leaderboard the roll should be removed!", choices = ["daily leaderboard", "weekly leaderboard", "monthly leaderboard", "general leaderboard"])):

        check = DatabaseCheck.check_leaderboard_roles(guild_id = ctx.guild.id, role_id = role.id, interval = interval)

        if check:

            await DatabaseRemoveDatas.remove_leaderboard_role(guild_id = ctx.guild.id, role_id = role.id, interval = interval_list[interval])
            
            emb = discord.Embed(description=f"""## The role was successfully removed from the leaderboard
                {Emojis.dot_emoji} The role {role.mention} was deleted from {interval}
                {Emojis.dot_emoji} With the button below you can see which other roles are defined as leaderbaord roles""", color=bot_colour)
            await ctx.respond(embed=emb, view=ShowLeaderboardRolesButton())

        else:

            emb = discord.Embed(description=f"""## This role has not been set for this interval
                {Emojis.dot_emoji} The role you specified is not listed for this interval
                {Emojis.dot_emoji} Here you have an overview of all roles that are listed on the respective intervals with the lower select menu you can display the other intervals
                {Emojis.dot_emoji} All leaderboard roles for the {interval}
                
                {show_leaderboard_roles(guild_id=ctx.guild.id, interval=interval_list[interval])}""", color=bot_colour)
            await ctx.respond(embed=emb, view=ShowLeaderboardRolesSelect())

    
    @commands.slash_command(name = "show-message-leaderboard-roles")
    async def show_leaderboard_roles_message(self, ctx:discord.ApplicationContext):

        emb = discord.Embed(description=f"""## Choose from which leaderboard you want to see the roles
            {Emojis.dot_emoji} With the lower select menu you can choose from which interval you want to see the corresponding roles:
            

            > {Emojis.dot_emoji} **Daily leaderboard:** Every day, the system checks which users have posted the most messages. The previously counted messages are deleted
            
            > {Emojis.dot_emoji} **Weekly leaderboard:** Every week, the system checks which users have posted the most messages. The previously counted messages are deleted

            > {Emojis.dot_emoji} **Monthly leaderboard:** Every month, the system checks which users have posted the most messages. The previously counted messages are deleted

            > {Emojis.dot_emoji} **General leaderboard:** This checks which users have written the most messages (updated daily). The previously counted messages are not deleted""", color=bot_colour)
        await ctx.respond(embed=emb, view=ShowLeaderboardRolesSelect())


    @commands.slash_command(name = "reset-message-leaderboard-roles")
    @commands.has_permissions(administrator = True)
    async def reset_leaderboard_roles_message(self, ctx:discord.ApplicationContext, interval:Option(str, description="Wähle welche Leaderboard rollen zurück gesetzt werden sollen", choices = ["daily leaderboard", "weekly leaderboard", "monthly leaderboard", "general leaderboard"])):

        check = DatabaseCheck.check_leaderboard_roles(guild_id = ctx.guild.id, interval = interval_list[interval])

        if check:

            await DatabaseRemoveDatas.remove_leaderboard_role(guild_id = ctx.guild.id)

            emb = discord.Embed(description=f"""## Leaderboard roles have been reset
                {Emojis.dot_emoji} All leaderbaord roles of the {interval} have been successfully reset
                {Emojis.dot_emoji} If you want to see which roles are listed on the other intervals use the select menu below""", color=bot_colour)
            await ctx.respond(embed=emb, view=ShowLeaderboardRolesSelect())

        else:

            emb = discord.Embed(description=f"""## No roles have been added to this leaderboard
                {Emojis.dot_emoji} No roles have been added to the {interval}
                {Emojis.dot_emoji} With the lower select menu you can check the other intervals and view the defined roles""", color=bot_colour)
            await ctx.respond(embed=emb, view=ShowLeaderboardRolesSelect())


    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        if message.author.bot:
            return
        
        check = DatabaseCheck.check_leaderboard_settings(guild_id = message.guild.id, system = "message")

        if check[1] == 1:
            
            await DatabaseUpdates.manage_leaderboard_message(guild_id = message.guild.id, user_id = message.author.id, interval = "countMessage")


##########################################  Invite Leaderboard  ##########################################
            

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


##########################################  System events  ###########################################
    @commands.Cog.listener()
    async def on_message_delete(self, message:discord.Message):

        check = DatabaseCheck.check_leaderboard_settings(guild_id = message.guild.id, system = "message")

        if check:

            if message.id == check[2]:

                await DatabaseUpdates.manage_leaderboard_message(guild_id = message.guild.id, back_to_none = "daily")

            elif message.id == check[3]:

                await DatabaseUpdates.manage_leaderboard_message(guild_id = message.guild.id, back_to_none = "weekly")


            elif message.id == check[4]:

                await DatabaseUpdates.manage_leaderboard_message(guild_id = message.guild.id, back_to_none = "monthly")

        check = DatabaseCheck.check_leaderboard_settings(guild_id = message.guild.id, system = "invite")

        if check:

            if message.id == check[2]:

                await DatabaseUpdates.manage_leaderboard_invite(guild_id = message.guild.id, back_to_none = "weekly")

            elif message.id == check[3]:

                await DatabaseUpdates.manage_leaderboard_invite(guild_id = message.guild.id, back_to_none = "monthly")

            elif message.id == check[4]:

                await DatabaseUpdates.manage_leaderboard_invite(guild_id = message.guild.id, back_to_none = "quarterly")


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        for system in ["message", "invite"]:

            check = DatabaseCheck.check_leaderboard_settings(guild_id = channel.guild.id, system = system)

            if check[5] == channel.id:

                await DatabaseRemoveDatas.remove_leaderboard_settings(guild_id = channel.guild.id, system = system)

    
def setup(bot):
    bot.add_cog(Messageleaderboard(bot))


async def remove_leaderboard_roles(guild:int, interval:str):
    
    check_role = DatabaseCheck.check_leaderboard_roles_users(guild_id = guild.id, interval = interval, status = "message")
    await DatabaseUpdates.manage_leaderboard_roles_users(guild_id = guild.id, interval = interval, status = "message", operation = "remove")
    
    for _, role, user, _, _ in check_role:

        user = await guild.fetch_member(user)
        leaderboard_role = guild.get_role(role)
        await user.remove_roles(leaderboard_role)


async def sort_leaderboard(user_list, interval, guild_id):
    
    guild = bot.get_guild(guild_id)
    interval_list = ["", "day", "week", "month", "whole"]
    check_roles = DatabaseCheck.check_leaderboard_roles(guild_id = guild_id, interval = interval_list[interval])
    
    general_role = None
    if check_roles:

        for i in check_roles:

            if i[2] == 0:

                general_role = guild.get_role(i[1])

    max_lengths = [
        max(len(str(t[i])) for t in user_list)
        for i in range(9)
    ]
    
    user_names, users = [], []
    for t in user_list:

        user = await guild.fetch_member(t[1])
        user_names.append(user.name)
        users.append(user)
        max_lengths[0] = max(max_lengths[0], len(user.name))

    padded_tuples = [
        (
            user_names[i].ljust(max_lengths[0]), 
            str(t[2]).ljust(max_lengths[2]),
            str(t[3]).ljust(max_lengths[3]),
            str(t[4]).ljust(max_lengths[4]),
            str(t[5]).ljust(max_lengths[5])
        )
        for i, t in enumerate(user_list)
    ]
    
    await remove_leaderboard_roles(guild=guild, interval=interval_list[interval])
    
    leaderboard, count = [], 0
    for i in range(min(len(user_list), 15)):
        
        if check_roles and i != None:
            
            role = DatabaseCheck.check_leaderboard_roles(guild_id = guild_id, position = i + 1)

            if general_role != None and count < 1:
                
                await users[i].add_roles(general_role)
                await DatabaseUpdates.manage_leaderboard_roles_users(guild_id = guild_id, user_id = users[i].id, role_id = general_role.id, operation = "add", status = "message", interval = interval_list[interval])
                count =+ 1

            if role != None:

                leaderboard_role = guild.get_role(role[1])
                await users[i].add_roles(leaderboard_role)
                await DatabaseUpdates.manage_leaderboard_roles_users(guild_id = guild_id, user_id = users[i].id, role_id = role[1], operation = "add", status = "message", interval = interval_list[interval])
            
        num_str = str(i + 1)
        if len(num_str) == 1:
            num_str = f" #{num_str}  "
        elif len(num_str) == 2:
            num_str = f" #{num_str} "
        
        leaderboard.append(f"`{num_str}` `{padded_tuples[i][0]}` `messages {padded_tuples[i][interval]}`\n")
        
    return "".join(leaderboard)


@tasks.loop(hours=1)
async def edit_leaderboard(bot):

    for guild in bot.guilds:

        leaderboard_settings = DatabaseCheck.check_leaderboard_settings(guild_id = guild.id, system = "message")

        if leaderboard_settings:

            if leaderboard_settings[1] == 1:
                message_ids = [
                    ("1_day_old", leaderboard_settings[2]),
                    ("1_week_old", leaderboard_settings[3]),
                    ("1_month_old", leaderboard_settings[4]),
                    ("whole", leaderboard_settings[5])
                ]
                
                if leaderboard_settings[1] == 1 and leaderboard_settings[6] != None:

                    try:
                        
                        current_date = datetime.now(UTC)

                        for message_name, message_id in message_ids:

                            if message_id != None:
                                
                                channel = bot.get_channel(leaderboard_settings[6])

                                if leaderboard_settings[5] != None:
                                    
                                    message = await channel.fetch_message(message_id)
                                    message_age = message.edited_at if message.edited_at != None else message.created_at

                                    if (current_date - message_age) > timedelta(minutes=1) and message_name == "whole":

                                        user_list = DatabaseCheck.check_leaderboard_message(guild_id = guild.id, interval = 3)
                                        users = await sort_leaderboard(user_list=user_list, interval=4, guild_id = guild.id)
                                        emb = discord.Embed(description=f"""## Whole Messages Leaderboard
                                            The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=1)).timestamp())}>
                                            {users}""", color=bot_colour)

                                        await message.edit(embed = emb, view=ShowLeaderboardGivenRoles())

                                if leaderboard_settings[2] != None:

                                    message = await channel.fetch_message(message_id)
                                    message_age = message.edited_at if message.edited_at != None else message.created_at

                                    if (current_date - message_age) > timedelta(minutes=1) and message_name == "1_day_old":

                                        user_list = DatabaseCheck.check_leaderboard_message(guild_id = guild.id, interval = 0)
                                        users = await sort_leaderboard(user_list=user_list, interval=1, guild_id = guild.id)
                                        emb = discord.Embed(description=f"""## Daily Messages Leaderboard
                                            {Emojis.dot_emoji} These are the users who have written the most messages in the period from <t:{int((datetime.now() - timedelta(days=1)).timestamp())}> to <t:{int((datetime.now()).timestamp())}>

                                            {users}
                                            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=30)).timestamp())}>""", color=bot_colour)

                                        await message.edit(embed = emb, view=ShowLeaderboardGivenRoles())

                                        await DatabaseUpdates.manage_leaderboard_message(guild_id = message.guild.id, back_to_none = "daily", settings = "tracking")

                                if leaderboard_settings[3] != None:
                                    
                                    message = await channel.fetch_message(message_id)
                                    message_age = message.edited_at if message.edited_at != None else message.created_at

                                    if (current_date - message_age) > timedelta(weeks=1) and message_name == "1_week_old":
                                        
                                        user_list = DatabaseCheck.check_leaderboard_message(guild_id = guild.id, interval = 1)
                                        users = await sort_leaderboard(user_list=user_list, interval=2, guild_id = guild.id)
                                        emb = discord.Embed(description=f"""## Weekly Messages Leaderboard
                                            {Emojis.dot_emoji} These are the users who have written the most messages in the period from <t:{int((datetime.now() - timedelta(weeks=1)).timestamp())}> to <t:{int((datetime.now()).timestamp())}>
                                            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(weeks=1)).timestamp())}>

                                            {users}
                                            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=30)).timestamp())}>""", color=bot_colour)
                                            
                                        await message.edit(embed = emb, view=ShowLeaderboardGivenRoles())

                                        await DatabaseUpdates.manage_leaderboard_message(guild_id = message.guild.id, back_to_none = "weekly", settings = "tracking")

                                if leaderboard_settings[4] != None:
                                    
                                    message = await channel.fetch_message(message_id)
                                    message_age = message.edited_at if message.edited_at != None else message.created_at

                                    if (current_date - message_age) > timedelta(days=30) and message_name == "1_month_old":
                                        
                                        user_list = DatabaseCheck.check_leaderboard_message(guild_id = guild.id, interval = 2)
                                        users = await sort_leaderboard(user_list=user_list, interval=3, guild_id=guild.id)
                                        emb = discord.Embed(description=f"""## Monthly Messages Leaderboard (30 days)
                                            {Emojis.dot_emoji} These are the users who have written the most messages in the period from <t:{int((datetime.now() - timedelta(days=30)).timestamp())}> to <t:{int((datetime.now()).timestamp())}>
            
                                            {users}
                                            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=30)).timestamp())}>""", color=bot_colour)

                                        await message.edit(embed = emb, view=ShowLeaderboardGivenRoles())

                                        await DatabaseUpdates.manage_leaderboard_message(guild_id = message.guild.id, back_to_none = "monthly", settings = "tracking")


                    except Exception as error:
                        print("parameterized query failed {}".format(error))


class SetleaderboardChannel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(LeaderboardOnOffSwitch())
        self.add_item(DefaultSettingsLeaderboard())
        self.add_item(CancelButton(system = None))

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


                    await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=4, settings=select.values[0].mention), view=SetInviteleaderboard() if system == "invite" else SetMessageleaderboard())

                elif settings[6] == select.values[0].id:

                    await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=5), view=ContinueSettingLeaderboard())

                else:
                    
                    emb = discord.Embed(description=f"""## A channel has already been defined for the {system} leaderboard
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

                emb = discord.Embed(description=f"""## Setting the channel from the {system} leaderboard
                    {GetEmbed.get_embed(embed_index=3)}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=SetInviteleaderboard() if system == "invite" else SetMessageleaderboard())

            else:

                emb = discord.Embed(description=f"""## Setting cannot be skipped
                    {Emojis.dot_emoji} The setting can only be skipped if a channel has been assigned to the {system} leaderboard
                    {Emojis.dot_emoji} You must first set a channel before you can continue""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class SetMessageleaderboard(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SkipIntervalSetting())
        self.add_item(CancelButton(system = "message leaderboard system"))

    @discord.ui.select(
        placeholder = "Select the intervals at which the activities should be displayed!",
        min_values = 1,
        max_values = 3,
        custom_id = "set_leaderboard",
        options = [
            discord.SelectOption(
                label="Update daily",
                description="The leaderboard is updated every day", 
                value="daily"
            ),
            discord.SelectOption(
                label="Update weekly", 
                description="The leaderboard is updated every week", 
                value="weekly"
            ),
            discord.SelectOption(
                label="Update monthly", 
                description="The leaderboard is updated every month", 
                value="monthly"
            )
        ]
    )
    
    async def set_leaderboard_select(self, select, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            settings = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = "message")

            value_check = {
                "daily":settings[2],
                "weekly":settings[3],
                "monthly":settings[4]
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

                    emb = discord.Embed(description=f"""## Intervals have already been defined for the message leaderboard
                        {Emojis.dot_emoji} The following intervals are currently active:\n
                            {''.join(check_list)}
                        {Emojis.help_emoji} Do you want to overwrite them? the previously sent leaderboard will be deleted""", color=bot_colour)
                    await interaction.response.edit_message(embed=emb, view=OverwriteMessageInterval(intervals=select.values))

            else:

                option_list = []
                channel = bot.get_channel(settings[6])

                message = await channel.send(embed=GetEmbed.get_embed(embed_index=7))
                await DatabaseUpdates.manage_leaderboard_message(guild_id = interaction.guild.id, settings = "whole", message_id = message.id)

                order = sorted(select.values, key=lambda item: ["daily", "weekly", "monthly"].index(item))
                for i in order:
                    option_list.append(f"{Emojis.dot_emoji} {i} update\n")
                    check_list.append(i)

                    if i != None:

                        emb = discord.Embed(
                            description=f"""## The number of messages is saved for {interval_text[i][0]}.
                            {Emojis.dot_emoji} This message will be edited on <t:{int((datetime.now() + timedelta(days=interval_text[i][1])).timestamp())}> and will then act as a leaderboard and show who has written the most messages on the server""", color=bot_colour)
                        message = await channel.send(embed=emb)
                        
                        await DatabaseUpdates.manage_leaderboard_message(guild_id = interaction.guild.id, settings = i, message_id = message.id)

                for i in [value for value in ["daily", "weekly", "monthly"] if value not in check_list]:

                    await DatabaseUpdates.manage_leaderboard_message(guild_id = interaction.guild.id, back_to_none = i)

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=6, settings=select.values, settings2=option_list, settings3=channel.mention), view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class SkipIntervalSetting(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="skip interval setting",
            style=discord.ButtonStyle.blurple,
            custom_id="skip_interval_setting"
        )

    async def callback(self, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            system = 'message' if 'message leaderboard' in interaction.message.embeds[0].description else 'invite'
            
            interval = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = system)

            intervals = {
                interval[2]:"weekly" if system == "invite" else "daily",
                interval[3]:"monthly" if system == "invite" else "weekly", 
                interval[4]:"quarterly" if system == "invite" else "monthly"
            }
            
            if interval[2] or interval[3] or interval[4]:
                
                check_interval = "".join([f"{intervals[i]}, " for i in [interval[2], interval[3], interval[4]] if i is not None])

                emb = discord.Embed(description=f"""## Setting the intervals was skipped
                    {Emojis.dot_emoji} {f'The intervals {check_interval} will be kept as intervals' if len(check_interval) != 1 else f'The interval {check_interval} will be kept'}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                emb = discord.Embed(description=f"""## Setting cannot be skipped
                    {Emojis.dot_emoji} The setting can only be skipped if at least one interval has been assigned to the message leaderboard
                    {Emojis.dot_emoji} You must first set an interval before you can continue""", color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)
    



class SetInviteleaderboard(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SkipIntervalSetting())
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
                        {Emojis.dot_emoji} You have already defined these intervals for the invite leaderboard
                        {Emojis.help_emoji} If you want to have other intervals you can simply execute this command again and overwrite them""", color=bot_colour)
                    await interaction.response.edit_message(embed=emb, view=None)

                else:

                    for i in select.values:

                        if value_check[i]:

                            check_list.append(f"> {Emojis.dot_emoji} {i} update\n")
                    
                    if check_list == []:
                        check_list = [f"> {Emojis.dot_emoji} None of the intervals you mentioned are currently active"]

                    emb = discord.Embed(description=f"""## Intervals have already been defined for the invite leaderboard
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

            system = 'message' if 'message leaderboard' in interaction.message.embeds[0].description else 'invite'
        
            if self.channel_id == None:

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=10, settings="channel", settings2="to set leaderboard", settings3=f"set-{system}-leaderboard"), view=None)

            else:
                
                get_messages = DatabaseCheck.check_leaderboard_settings(guild_id = interaction.guild.id, system = system)
                await (DatabaseUpdates.manage_leaderboard_invite if system == "invite" else DatabaseUpdates.manage_leaderboard_message)(
                    guild_id = interaction.guild.id, settings = "channel", channel_id = self.channel_id)

                system_intervals = {
                    "invite":[(get_messages[2], "weekly"), (get_messages[3], "monthly"), (get_messages[4], "quarterly")],
                    "message":[(get_messages[2], "daily"), (get_messages[3], "weekly"), (get_messages[4], "monthly")]
                }
                
                for i, index in system_intervals[system]:
                    
                    if i != None:
                    
                        leaderboard_channel = bot.get_channel(get_messages[6])
                        
                        msg = await leaderboard_channel.fetch_message(i)
                        await msg.delete()

                        await (DatabaseUpdates.manage_leaderboard_invite if system == "invite" else DatabaseUpdates.manage_leaderboard_message)(
                            guild_id = interaction.guild.id, back_to_none = index)

                emb = discord.Embed(description=f"""## Leaderboard channel has been overwritten
                    {Emojis.dot_emoji} As of now, <#{self.channel_id}> is the new leaderboard channel
                    {Emojis.dot_emoji} The leaderboard is deleted from the old leaderboard channel
                    {Emojis.dot_emoji} You can continue with the setting using the selection menu below
                    {Emojis.help_emoji} You can select several intervals and each interval is a single leaderboard""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=SetInviteleaderboard() if system == "invite" else SetMessageleaderboard())

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
            await interaction.response.edit_message(embed=emb, view=SetInviteleaderboard() if system == "invite" else SetMessageleaderboard())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)
        


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
            await interaction.response.edit_message(embed=emb, view=SetInviteleaderboard() if system == "invite" else SetMessageleaderboard())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class OverwriteMessageInterval(discord.ui.View):

    def __init__(self, intervals):
        self.intervals = intervals
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "message leaderboard system"))

    @discord.ui.button(
        label="overwrite the intervals",
        style=discord.ButtonStyle.blurple,
        custom_id="overwrite_intervals"
    )

    async def overwrite_intervals(self, button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            system = 'message' if 'message leaderboard' in interaction.message.embeds[0].description else 'invite'

            if self.intervals is None:
                embed_index = 10
                settings3 = "set-invite-leaderboard" if system == "invite" else "set-message-leaderboard"
                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=embed_index, settings=system, settings2="to overwrite the interval", settings3=settings3), view=None)
            
            else:
                settings = DatabaseCheck.check_leaderboard_settings(guild_id=interaction.guild.id, system=system)

                option_list, check_list = [], []
                
                order = sorted(self.intervals, key=lambda item: ["weekly", "monthly", "quarterly"].index(item) if system == "invite" else ["daily", "weekly", "monthly"].index(item))

                channel = bot.get_channel(settings[6])

                message = await channel.send(embed=GetEmbed.get_embed(embed_index=7))
                await (DatabaseUpdates.manage_leaderboard_invite if system == "invite" else DatabaseUpdates.manage_leaderboard_message)(
                    guild_id=interaction.guild.id, settings="whole", message_id=message.id)

                interval_text = {
                    "daily": ["daily", 1],
                    "weekly": ["weekly", 7],
                    "monthly": ["monthly", 30],
                    "quarterly": ["quarterly", 90]
                }

                for i in order:

                    option_list.append(f"> {Emojis.dot_emoji} {i} update\n")
                    check_list.append(i)

                    if i is not None:

                        emb = discord.Embed(
                            description=f"""## The number of messages is saved for {interval_text[i][0]}.
                                {Emojis.dot_emoji} This message will be edited on <t:{int((datetime.now() + timedelta(days=interval_text[i][1])).timestamp())}> and will then act as a leaderboard and show who has written the most messages on the server""",
                            color=bot_colour)
                        message = await channel.send(embed=emb)

                        await (DatabaseUpdates.manage_leaderboard_invite if system == "invite" else DatabaseUpdates.manage_leaderboard_message)(
                            guild_id=interaction.guild.id, settings=i, message_id=message.id)

                for i in [value for value in (["weekly", "monthly", "quarterly"] if system == "invite" else ["daily", "weekly", "monthly"]) if value not in check_list]:

                    await (DatabaseUpdates.manage_leaderboard_invite if system == "invite" else DatabaseUpdates.manage_leaderboard_message)(
                        guild_id=interaction.guild.id, back_to_none=i)

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=6, settings=self.intervals, settings2=option_list, settings3=channel.mention), view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="keep intervals",
        style=discord.ButtonStyle.blurple,
        custom_id="keep_intervals_message"
    )

    async def keep_intervals(self, button: Button, interaction: discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            system = 'message' if 'Set the message leaderboard' in interaction.message.embeds[0].description else 'invite'

            check_settings = DatabaseCheck.check_leaderboard_settings(guild_id=interaction.guild.id, system=system)

            list_intervals = []
            if system == "message":

                for _, _, day, week, month, _, _ in check_settings:

                    if day is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Daily updated leaderboard")
                    if week is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Weekly updated leaderboard")
                    if month is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Monthly updated leaderboard")

            else:

                for _, _, week, month, quarter, _, _ in check_settings:

                    if week is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Weekly updated leaderboard")
                    if month is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Monthly updated leaderboard")
                    if quarter is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Quarterly updated leaderboard")

            emb = discord.Embed(
                description=f"""## The current intervals are retained
                {Emojis.dot_emoji} Here you can see an overview of the currently defined intervals
                {"\n".join(list_intervals)}""",
                color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class LeaderboardOnOffSwitch(discord.ui.Button):

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

            await (DatabaseUpdates.manage_leaderboard_invite if system == "invite" else DatabaseUpdates.manage_leaderboard_message)(
                guild_id = interaction.guild.id, settings = "status")

            emb = discord.Embed(description=f"""## The {system} leaderboard system is now {'activated' if settings[1] == 0 else 'deactivated'}.
                {Emojis.dot_emoji} {f'''From now on all {'message' if system == 'message' else 'invitation'}s will be added to the {system} leaderboard and a ranking will be created showing who has {'written the most messages' if system == 'message' else 'invited the most users'}
                {Emojis.help_emoji} However, an interval and a channel must also be defined for this'''
                if settings[1] == 0 else f'''From now on, no {'message' if system == 'message' else 'invitation'}s will be added to the {system} leaderboard and the ranking will no longer be updated when you activate it again, the leaderboard will be reset and counted from the new interval.
                {Emojis.dot_emoji} The other settings remain as they are'''}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    
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



################################  Message leaderboard roles  ####################################
        

class OverwriteRole(discord.ui.View):

    def __init__(
        self,
        role,
        interval,
        position,
        settings,
        delete
    ):
        self.role = role
        self.interval = interval
        self.position = position
        self.settings = settings
        self.delete = delete
        super().__init__(timeout=None)
        self.add_item(CancelButton(system = "message leaderboard roles"))

    @discord.ui.button(
        label="overwrite entry",
        style=discord.ButtonStyle.blurple,
        custom_id="overwrite_role_entry"
    )

    async def overwrite_role_button(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            
            if any(x != None for x in [self.role, self.interval, self.settings, self.position, self.delete]):

                check_role = DatabaseCheck.check_leaderboard_roles(guild_id = interaction.guild.id, role_id = self.delete[1])
                if check_role:
                    await DatabaseRemoveDatas.remove_leaderboard_role(guild_id = interaction.guild.id, role_id = self.delete[1], interval = self.interval)
                check_positon = DatabaseCheck.check_leaderboard_roles(guild_id = interaction.guild.id, position = self.position)
                if check_positon:
                    await DatabaseRemoveDatas.remove_leaderboard_role(guild_id = interaction.guild.id, role_id = check_positon[1], interval = self.interval)

                await DatabaseUpdates.manage_leaderboard_roles(guild_id = interaction.guild.id, role_id = self.role.id, position = self.position, status = "message", interval = self.interval)

                emb = discord.Embed(description=f"""## The entry has been overwritten
                    {Emojis.dot_emoji} From now on the role <@&{self.role.id}> is assigned to the {self.position} place, this applies to the {self.interval}{'ly' if self.interval != 'general' else ''} leaderboard
                    {Emojis.dot_emoji} If you want to change the settings of the message leaderboard system you can do this with the `set-messageleaderboard` command""", color=bot_colour)  
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=10, settings="leaderboard role", settings2="to overwrite the role", settings3="add-message-leaderboard-role"), view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


    @discord.ui.button(
        label="keep entry",
        style=discord.ButtonStyle.blurple,
        custom_id="keep_role_entry"
    )

    async def keep_role_button(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Role and position is retained
                {Emojis.dot_emoji} The overwriting of the entry was canceled
                {Emojis.dot_emoji} If you want to change a role or a position, you can simply execute this command again""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


def show_leaderboard_roles(guild_id, interval):

    check = DatabaseCheck.check_leaderboard_roles(guild_id = guild_id, interval = interval)
    leaderboard = []

    if check:

        for _, role, poistion, _, _ in check:

            if poistion != 0:

                leaderboard.append(f"{Emojis.dot_emoji} <@&{role}> is used for place {poistion}")

            else:

                leaderboard.append(f"{Emojis.dot_emoji} <@&{role}> is defined as a general role and is assigned to every user who is on the leaderboard")
    
    else:

        leaderboard.append(f"**{Emojis.dot_emoji} No roles have been defined for this leaderboard**")

    return "\n".join(leaderboard)


class ShowLeaderboardRolesButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
            label = "show all Leaderboard Roles",
            style = discord.ButtonStyle.blurple,
            custom_id = "show_leaderboard_roles_button"
        )
    
    async def callback(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Leaderboard roles
                {Emojis.dot_emoji} With the lower select menu you can see which roles are set for which leaderboard
                {Emojis.dot_emoji} The following leaderboards are available
                
                {Emojis.dot_emoji} Daily leaderboard: Every day, the system checks which users have posted the most messages. The previously counted messages are deleted
                {Emojis.dot_emoji} Weekly leaderboard: Every week, the system checks which users have posted the most messages. The previously counted messages are deleted
                {Emojis.dot_emoji} Monthly leaderboard: Every month, the system checks which users have posted the most messages. The previously counted messages are deleted
                {Emojis.dot_emoji} General leaderboard: This checks which users have written the most messages (updated daily). The previously counted messages are not deleted""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=ShowLeaderboardRolesSelect())
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class ShowLeaderboardRolesSelect(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder = "Choose from which leaderboard you want to see all roles!",
        min_values = 1,
        max_values = 1,
        custom_id = "show_leaderboard_roles",
        options = [
            discord.SelectOption(label="Daily leaderboard", description="Take a look at which roles are defined for the Daily leaderboard", value="daily"),
            discord.SelectOption(label="Weekly leaderboard", description="Take a look at which roles are defined for the weekly leaderboard", value="weekly"),
            discord.SelectOption(label="Monthly leaderboard", description="Take a look at which roles are defined for the Monthly leaderboard", value="monthly"),
            discord.SelectOption(label="General leaderboard", description="Take a look at which roles are defined for the Gernal leaderboard", value="general")
        ]
    )

    async def show_leaderboard_roles_select(self, select, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Leaderboard roles
                {Emojis.dot_emoji} Here you can see an overview of all roles that are listed on the {select.values[0]} leaderboard

                {show_leaderboard_roles(guild_id=interaction.guild.id, interval=select.values[0])}""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class ShowLeaderboardGivenRoles(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(
        label="Take a look at who has been given which role",
        style=discord.ButtonStyle.blurple,
        custom_id="show_leaderboar_given_roles"
    )
    
    async def show_leaderboard_given_roles(self, button, interaction:discord.Interaction):

        interval_text = {
            "Whole":"whole",
            "Daily":"day",
            "Weekly":"week",
            "Monthly":"month"
        }
        
        for key, interval in interval_text.items():

            if key in interaction.message.embeds[0].description:
            
                check_roles = DatabaseCheck.check_leaderboard_roles_users(guild_id = interaction.guild.id, status = "message", interval = interval)
                user_list, general_role = [], None
                for role in check_roles:
                    
                    check_position = DatabaseCheck.check_leaderboard_roles(guild_id = interaction.guild.id, role_id = role[1])

                    if check_position[2] != 0:

                        user_list.append(f"{Emojis.dot_emoji} The user <@{role[2]}> has received the role <@&{role[1]}> for reaching place {check_position[2]}\n")

                    else:

                        general_role = f"\n {Emojis.dot_emoji} In addition, each of the listed users was assigned the <@&{role[1]}> role as this role was defined as a general role"
                
                if user_list == []:
                    user_list.append(f"{Emojis.dot_emoji} No roles were assigned as no roles were defined for specific positions")

                emb = discord.Embed(description=f"""## The following roles have been assigned
                    {Emojis.dot_emoji} Here you can see which roles have been awarded for reaching certain places on the {key.lower()} leaderboard {general_role if general_role != None else ''}
                        
                    {"".join(user_list)}
                    """, color=bot_colour)
                await interaction.response.send_message(embed=emb, view=None, ephemeral=True)