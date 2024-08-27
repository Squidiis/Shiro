from discord.interactions import Interaction
from utils import *
from sql_function import *
from discord.ext import tasks
from datetime import timezone

# Dictionary for the check functions (does not have to be in each command individually)
interval_list_message = {
    "day":"daily leaderboard",
    "week":"weekly leaderboard",
    "month":"monthly leaderboard",
    "general":"general leaderboard"
    }

interval_list_invite = {
    "week":"weekly leaderboard",
    "month":"monthly leaderboard",
    "quarter":"quarterly leaderboard",
    "general":"general leaderboard"
    }

interval_text_message = {
    "daily":("one day", 1),
    "weekly":("one week", 7),
    "monthly":("one month", 30)
    }

interval_text_invite = {
    "weekly":("one week", 7),
    "monthly":("one month", 30),
    "quarterly":("a quarter of a year", 90)
    }


class LeaderboardSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.edit_leaderboard_invite.start()
        self.edit_leaderboard_message.start()
        self.check_expired_invite_liks.start()


    '''
    Adds all existing Invite links to a database

    Info:
        - Required for the Invite Leaderboard
    '''
    @classmethod
    async def collects_invitation_links(cls):

        for guild in bot.guilds:

            for invite in await guild.invites():

                if invite.inviter.bot:

                    pass
                
                else:

                    await DatabaseUpdates.manage_leaderboard_invite_list(guild_id = guild.id, user_id = invite.inviter.id, invite_code = invite.code, uses = invite.uses)
    

    '''
    Searches all invites and compares them with the database, all expired invites are deleted
    
    Info:
        - Required for the Invite Leaderboard
    '''
    @classmethod
    async def check_expired_invites(cls):
        
        for guild in bot.guilds:

            invite_codes = DatabaseCheck.check_invite_codes(guild_id = guild.id, remove_value = "")
            
            for (invite_code,) in invite_codes:
                
                try:

                    invite = await bot.fetch_invite(invite_code)
                    if invite.revoked or invite.max_uses and invite.uses >= invite.max_uses:
                 
                        await DatabaseRemoveDatas.remove_invite_links(guild_id = guild.id, invite_code = invite_code)

                except discord.NotFound:

                    await DatabaseRemoveDatas.remove_invite_links(guild_id = guild.id, invite_code = invite_code)


    '''
    Check all servers every 24 hours for expired links and then deletes them from the database, adds newly created links at the same time
    '''
    @tasks.loop(hours=24)
    async def check_expired_invite_liks(self):

        await self.check_expired_invites()
        await self.collects_invitation_links()


    '''
    Exported logic of the set-leaderboard commands

    Parameters:
    ------------
        - system
            Which system is to be set
                - message: Sets the message leaderboard
                - invite: Sets the invite leaderboard
    '''
    async def process_set_leaderboard(self, ctx:discord.ApplicationContext, system:str):

        settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild_id, system = system)
        
        if settings == None:

            await DatabaseUpdates.create_leaderboard_settings(guild_id = ctx.guild.id, system = system)
            settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild_id, system = system)

        emb = discord.Embed(description=f"""## Set the {system} leaderboard
            {Emojis.dot_emoji} With the lower select menu you can define a channel in which the leaderboard should be sent
            {Emojis.dot_emoji} Then you can also set an interval at which time intervals the leaderboard should be updated
            {Emojis.dot_emoji} You can also switch the system off or on currently it is {'switched off' if settings[0] else 'switched on'}. (as soon as it is switched off, no more {'invitations' if system == 'invite' else 'message'} are counted and when it is switched on, the leaderboard is reset)
            {Emojis.help_emoji} The leaderboard is edited when you update it, so you should make sure that no one else can write in the channel you specified
            {Emojis.help_emoji} **The leaderboard always shows the data from the previous interval, e.g. the best users who have {'invited' if system == "invite" else "wrote"} the most {'users' if system == "invite" else 'messages'} in the last week**""", color=bot_colour)        
        await ctx.respond(embed=emb, view = SetleaderboardChannel())


    '''
    Exported logic of the show-leaderboard commands

    Parameters:
    ------------
        - system
            Which system should be shown
                - message: Shows the message leaderboard
                - invite: Shows the invite leaderboard
        - settings
            What should be displayed?
        - invtervals
            Which interval should be displayed
   '''
    async def process_show_leaderboard_settings(self, ctx:discord.ApplicationContext, system:str, settings, intervals):

        if settings is None:

            await DatabaseUpdates.create_leaderboard_settings(guild_id=ctx.guild.id, system=system)
            await ctx.respond(embed=GetEmbed.get_embed(embed_index=8))

        elif settings[6] is None or all(x is None for x in [settings[2], settings[3], settings[4]]):

            await ctx.respond(embed=GetEmbed.get_embed(embed_index=8))

        else:

            intervals_text = []
            for i in [settings[2], settings[3], settings[4]]:
                if i is not None:
                    intervals_text.append(f"{Emojis.dot_emoji} {intervals[i]} updating {system} leaderboard\n")
            
            emb = discord.Embed(f"""## Here you can see all the settings of the {system} leaderboard
            {Emojis.dot_emoji} The {system} leaderboard is currently {'switched on' if settings[1] == 0 else 'switched off'}
            {Emojis.dot_emoji} {f'Currently <#{settings[6]}> is set as' if settings[5] is not None else 'No'} {system} leaderboard channel has been set
            {Emojis.dot_emoji} **The following intervals are currently defined for which a leaderboard exists:**
            {"".join(intervals_text) if intervals_text else f'{Emojis.dot_emoji} No intervals have been defined yet'}""", color=bot_colour)
            await ctx.respond(embed=emb)


    '''
    Exported logic of the add-leaderboard-role commands

    Parameters:
    ------------
        - system
            To which system the role should be added
                - message: Add role to the message leaderboard
                - invite: Add role to the invite leaderboard
        - role
            Role id
        - position
            To which position the role should be assigned

    Info:
        - If possition is 0, the role is assigned to every user listed on the leaderboard
    '''
    async def process_add_leaderboard_role(self, ctx:discord.ApplicationContext, role:discord.Role, position:str, interval:str, system:str):

        interval_list = interval_list_message if system == "message" else interval_list_invite

        interval_db = next((key for key, value in interval_list.items() if value == interval), None)
        position_db = 0 if "general role" == position else int(position)

        check_role = DatabaseCheck.check_leaderboard_roles(guild_id=ctx.guild.id, role_id=role.id, position=position_db, system=system)

        if check_role is not None and check_role[4] == interval_db:
            
            if check_role[2] == position_db and check_role[1] == role.id and interval_db == check_role[4]:

                emb = discord.Embed(description=f"""## This role has already been assigned to this position
                    {Emojis.dot_emoji} The role {role.mention} {f'is already assigned to the {position} space' if position_db != 0 else f'is defined as a general role for the {interval_list[check_role[4]]}'}
                    {Emojis.dot_emoji} If you want to overwrite the role, position or the associated interval, you can simply execute this command again""", color=bot_colour)
                await ctx.respond(embed=emb)

            elif check_role[2] == 0 and position_db != 0:

                emb = discord.Embed(description=f"""## This role is currently set as a generic role for {system} leaderboard
                    {Emojis.dot_emoji} Currently <@&{check_role[1]}> is set as a general role do you want to set this role for the {position} place?
                    {Emojis.dot_emoji} You can confirm your decision with the button below""", color=bot_colour)
                await ctx.respond(embed=emb, view=OverwriteRole(role=role, position=position_db, interval=interval_db, settings="position", delete=check_role[1]))

            elif check_role[2] == 0 or self.check_interval_role(guild_id=ctx.guild.id, interval=interval_db, system=system):

                emb = discord.Embed(description=f"""## {'This role is currently set as a general role' if check_role[1] != role.id else 'This interval already has a general role'} for the {system} leaderboard
                    {Emojis.dot_emoji} The role <@&{check_role[1]}> is currently defined as the general role for the interval {interval_list[check_role[4]]}
                    {Emojis.dot_emoji} {f'''Would you like to replace the role <@&{check_role[1]}> with the role {role.mention} and set this as a new general role?
                    {Emojis.dot_emoji} Everyone who is then listed on the leaderboard will then receive this role'''
                    if check_role[1] != role.id else 
                    f'Do you want to assign the role <@&{check_role[1]}> as a normal role for the {position} space?'}""", color=bot_colour)
                await ctx.respond(embed=emb, view=OverwriteRole(role=role, position=position_db, interval=interval_db, settings="role" if check_role[1] != role.id else "interval", delete=check_role))
            
            else:

                emb = discord.Embed(description=f"""## {'This role' if check_role[1] != role.id else 'This position'} has already been assigned for the {system} leaderboard
                    {Emojis.dot_emoji} Currently, the role <@&{check_role[1]}> is assigned for the {check_role[2]} place, for the {interval_list[check_role[4]]}
                    {Emojis.dot_emoji} Do you want to {f'replace the role <@&{check_role[1]}> with the role {role.mention} for the position {position} for the {interval_list[check_role[4]]}' if check_role[1] != role.id else f'change the place for which the role {role.mention} is assigned to {position}? this role is then always assigned when someone reaches the {position} place on the {interval}'}""", color=bot_colour)
                await ctx.respond(embed=emb, view=OverwriteRole(role=role, position=position_db, interval=interval_db, settings="role" if check_role[1] != role.id else "position", delete=check_role))
        
        else:
            
            await DatabaseUpdates.manage_leaderboard_roles(guild_id=ctx.guild.id, role_id=role.id, position=position_db, status=system, interval=interval_db)

            emb = discord.Embed(description=f"""## The new leaderboard role has been successfully established
                {Emojis.dot_emoji} The role {role.mention} was successfully {f'set for the {position} place' if position_db != 0 else f'set as general role'}
                {Emojis.dot_emoji} {f'If a user now reaches the {position} place on the {interval} he gets the role {role.mention}' if position_db != 0 else f'If a user is now listed on the {interval} he gets the role {role.mention} until the leaderboard is updated again and a new user gets this role'}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    '''
    Exported logic of the remove-leaderboard-role commands

    Parameters:
    ------------
        - System
        From which leaderboard the role should be removed
            - Message: Removes the role from the message leaderboard
            - Invite: Removes the role from the invite leaderboard
        - Role ID
            Role ID
        - Interval
            From which interval the role should be removed
    '''
    async def process_remove_leaderboard_role(self, ctx:discord.ApplicationContext, role:discord.Role, interval:str, system:str):

        check = DatabaseCheck.check_leaderboard_roles(guild_id=ctx.guild.id, role_id=role.id, interval=interval, system=system)

        interval_list = interval_list_message if system == "message" else interval_list_invite

        if check:

            await DatabaseRemoveDatas.remove_leaderboard_role(guild_id=ctx.guild.id, role_id=role.id, interval=interval_list[interval], system=system)
            
            emb = discord.Embed(description=f"""## The role was successfully removed from the {system} leaderboard
                {Emojis.dot_emoji} The role {role.mention} was deleted from {interval}
                {Emojis.dot_emoji} With the button below you can see which other roles are defined as leaderboard roles""", color=bot_colour)
            await ctx.respond(embed=emb, view=ShowLeaderboardRolesButton())

        else:

            emb = discord.Embed(description=f"""## This role has not been set for this interval
                {Emojis.dot_emoji} The role you specified is not listed for this interval
                {Emojis.dot_emoji} Here you have an overview of all roles that are listed on the respective intervals with the lower select menu you can display the other intervals
                {Emojis.dot_emoji} All leaderboard roles for the {interval}
                
                {show_leaderboard_roles(guild_id=ctx.guild.id, interval=interval_list[interval], system=system)}""", color=bot_colour)
            await ctx.respond(embed=emb, view=ShowLeaderboardRolesSelectMessage() if system == "message" else ShowLeaderboardRolesSelectInvite())

    
    '''
    Exported logic of the reset-leaderboard-roles commands

    Parameters:
    ------------

        - system
        From which system the roles are to be reset
            - message: Resets all roles of the message leaderboard
            - invite: Resets all roles of the invite leaderboard
        - interval
            For which interval the roles should be reset
    '''
    async def process_reset_leaderboard_roles(self, ctx:discord.ApplicationContext, interval:str, system:str):
        
        interval_list = interval_list_message if system == "message" else interval_list_invite

        check = DatabaseCheck.check_leaderboard_roles(guild_id=ctx.guild.id, interval=interval_list[interval], system=system)

        if check:
            await DatabaseRemoveDatas.remove_leaderboard_role(guild_id=ctx.guild.id, system=system)

            emb = discord.Embed(description=f"""## Leaderboard roles have been reset
                {Emojis.dot_emoji} All leaderboard roles of the {interval} have been successfully reset
                {Emojis.dot_emoji} If you want to see which roles are listed on the other intervals, use the select menu below""", color=bot_colour)
            await ctx.respond(embed=emb, view=ShowLeaderboardRolesSelectMessage() if system == "message" else ShowLeaderboardRolesSelectInvite())

        else:
            emb = discord.Embed(description=f"""## No roles have been added to this leaderboard
                {Emojis.dot_emoji} No roles have been added to the {interval}
                {Emojis.dot_emoji} With the lower select menu you can check the other intervals and view the defined roles""", color=bot_colour)
            await ctx.respond(embed=emb, view=ShowLeaderboardRolesSelectMessage() if system == "message" else ShowLeaderboardRolesSelectInvite())

    
    '''
    Returns all roles of an interval, also check whether it is a general role

    Parameters:
    ------------
        - guild_id
            Server id
        - intervals
            The interval at which the role is set
        - system
            Which system is to be checked 
    '''
    def check_interval_role(self, guild_id, interval, system):

        roles = DatabaseCheck.check_leaderboard_roles(guild_id = guild_id, system = system)

        for role in roles:

            if role[2] == 0 and role[4] == interval:

                return True

        return False



#############################################  Message leaderboard commands  #####################################
            

    @commands.slash_command(name = "set-message-leaderboard", description = "Set the message leaderboard system!")
    @commands.has_permissions(administrator = True)
    async def set_message_leaderboard(self, ctx:discord.ApplicationContext):

        await self.process_set_leaderboard(ctx=ctx, system="message")


    @commands.slash_command(name = "show-message-leaderboard-setting", description = "Shows all settings of the message leaderboard!")
    async def show_message_leaderboard_settings(self, ctx:discord.ApplicationContext):
        
        settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild.id, system = "message")
        
        intervals = {
            settings[2]:"Daily",
            settings[3]:"Weekly",
            settings[4]:"Monthly"
        }

        await self.process_show_leaderboard_settings(ctx=ctx, system="message", settings=settings, intervals=intervals)


    @commands.slash_command(name = "add-message-leaderboard-role", description = "Define roles for the message leaderboard that are assigned when you reach a certain position!")
    @commands.has_permissions(administrator = True)
    async def add_leaderboard_role_message(self, ctx:discord.ApplicationContext, 
        role:Option(discord.Role, required = True, description="Define a role for the leaderboard to assign upon reaching a specific position"), 
        position:Option(required = True, description="Select the position to assign this role (if general, it’s always assigned if on the leaderboard)", 
            choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "general role"]),
        interval:Option(str, description="Select the leaderboard for which this role is to be assigned", 
            choices = ["daily leaderboard", "weekly leaderboard", "monthly leaderboard", "general leaderboard"])):

        if role.permissions.administrator or role.permissions.moderate_members:

            await ctx.respond(embed=GetEmbed.get_embed(embed_index=11))

        await self.process_add_leaderboard_role(ctx=ctx, role=role, position=position, interval=interval, system="message")

    
    @commands.slash_command(name = "remove-message-leaderboard-role", description = "Removes a specific role from a specific interval of the message leaderboard!")
    @commands.has_permissions(administrator = True)
    async def remove_leaderboard_role_message(self, ctx:discord.ApplicationContext, 
        role:Option(discord.Role, description="Remove a role from the leaderboard roles!"), 
        interval:Option(str, description="Choose from which leaderboard the roll should be removed!", choices = ["daily leaderboard", "weekly leaderboard", "monthly leaderboard", "general leaderboard"])):

        await self.process_remove_leaderboard_role(ctx=ctx, role=role, interval=interval, system="message")

    
    @commands.slash_command(name = "show-message-leaderboard-roles", description = "Shows all roles that have been defined for the message leaderboard!")
    async def show_leaderboard_roles_message(self, ctx:discord.ApplicationContext):

        emb = discord.Embed(description=f"""## Choose from which leaderboard you want to see the roles
            {Emojis.dot_emoji} With the lower select menu you can choose from which interval you want to see the corresponding roles:
            

            > {Emojis.dot_emoji} **Daily leaderboard:** Every day, the system checks which users have posted the most messages. The previously counted messages are deleted
            
            > {Emojis.dot_emoji} **Weekly leaderboard:** Every week, the system checks which users have posted the most messages. The previously counted messages are deleted

            > {Emojis.dot_emoji} **Monthly leaderboard:** Every month, the system checks which users have posted the most messages. The previously counted messages are deleted

            > {Emojis.dot_emoji} **General leaderboard:** This checks which users have written the most messages (updated daily). The previously counted messages are not deleted""", color=bot_colour)
        await ctx.respond(embed=emb, view=ShowLeaderboardRolesSelectMessage())


    @commands.slash_command(name = "reset-message-leaderboard-roles", description = "Resets all roles that have been set for the message leaderboard!")
    @commands.has_permissions(administrator = True)
    async def reset_leaderboard_roles_message(self, ctx:discord.ApplicationContext, 
        interval:Option(str, description="Select which leaderboard roles should be reset", 
            choices = ["daily leaderboard", "weekly leaderboard", "monthly leaderboard", "general leaderboard"])):

        await self.process_reset_leaderboard_roles(ctx=ctx, interval=interval, system="message")



##########################################  Invite Leaderboard  ##########################################
            

    @commands.slash_command(name = "set-invite-leaderboard", description = "Set up the invite leaderboard system!")
    async def set_invite_leaderboard(self, ctx:discord.ApplicationContext):

        await self.process_set_leaderboard(ctx=ctx, system="invite")

    
    @commands.slash_command(name = "show-invite-leaderboard-setting", description = "Shows all settings of the invite leaderboard!")
    async def show_message_leaderboard_settings(self, ctx:discord.ApplicationContext):
        
        settings = DatabaseCheck.check_leaderboard_settings(guild_id = ctx.guild.id, system = "invite")

        intervals = {
            settings[2]:"Weekly",
            settings[3]:"Monthly",
            settings[4]:"Quarterly"
        }

        await self.process_show_leaderboard_settings(ctx=ctx, system="invite", settings=settings, intervals=intervals)


    @commands.slash_command(name = "add-invite-leaderboard-role", description = "Define roles for the invite leaderboard that are assigned when you reach a certain position!")
    @commands.has_permissions(administrator = True)
    async def add_leaderboard_role_invite(self, ctx:discord.ApplicationContext, 
        role:Option(discord.Role, required = True, description="Define a role for the leaderboard to assign upon reaching a specific position"), 
        position:Option(required = True, description="Select the position to assign this role (if general, it’s always assigned if on the leaderboard)",
            choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "general role"]),
        interval:Option(str, description="Select the leaderboard for which this role is to be assigned", 
            choices = ["weekly leaderboard", "monthly leaderboard", "quarterly leaderboard", "general leaderboard"])):

        if role.permissions.administrator or role.permissions.moderate_members:

            await ctx.respond(embed=GetEmbed.get_embed(embed_index=11))

        await self.process_add_leaderboard_role(ctx=ctx, role=role, position=position, interval=interval, system="invite")

    
    @commands.slash_command(name = "remove-invite-leaderboard-role", description = "Removes a specific role from a specific interval of the invite leaderboard!")
    @commands.has_permissions(administrator = True)
    async def remove_leaderboard_role_invite(self, ctx:discord.ApplicationContext, 
        role:Option(discord.Role, description="Remove a role from the leaderboard roles!"), 
        interval:Option(str, description="Choose from which leaderboard the roll should be removed!", 
            choices = ["weekly leaderboard", "monthly leaderboard", "quarterly leaderboard", "general leaderboard"])):

        await self.process_remove_leaderboard_role(ctx=ctx, role=role, interval=interval, system="invite")

    
    @commands.slash_command(name = "show-invite-leaderboard-roles", description = "Shows all roles that have been defined for the invite leaderboard!")
    async def show_leaderboard_roles_invite(self, ctx:discord.ApplicationContext):

        emb = discord.Embed(description=f"""## Choose from which leaderboard you want to see the roles
            {Emojis.dot_emoji} With the lower select menu you can choose from which interval you want to see the corresponding roles:
            
            
            > {Emojis.dot_emoji} **Weekly ranking:** Every week, the system checks which users have invited the most users. The previously counted invitations are deleted
            
            > {Emojis.dot_emoji} **Monthly leaderboard:** Every month, the system checks which users have invited the most users. The previously counted invitations  are deleted

            > {Emojis.dot_emoji} **Quarterly leaderboard:** Every quarter, the system checks which users have invited the most users. The previously counted invitations are deleted

            > {Emojis.dot_emoji} **General leaderboard:** This checks which users have written the most users (updated daily). The previously counted invitations are not deleted""", color=bot_colour)
        await ctx.respond(embed=emb, view=ShowLeaderboardRolesSelectInvite())

    
    @commands.slash_command(name = "reset-invite-leaderboard-roles", description = "Resets all roles that have been set for the invite leaderboard!")
    @commands.has_permissions(administrator = True)
    async def reset_leaderboard_roles_invite(self, ctx:discord.ApplicationContext, 
        interval:Option(str, description="Select which leaderboard roles should be reset!", 
            choices = ["weekly leaderboard", "monthly leaderboard", "quarterly leaderboard", "general leaderboard"])):

        await self.process_reset_leaderboard_roles(ctx=ctx, interval=interval, system="invite")



##########################################  System events  ###########################################
        

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        if message.author.bot:
            return
        
        if message != None:
        
            check = DatabaseCheck.check_leaderboard_settings(guild_id = message.guild.id, system = "message")

            if check:

                if check[1] == 1:
                    
                    await DatabaseUpdates.manage_leaderboard_message(guild_id = message.guild.id, user_id = message.author.id, interval = "countMessage")

    
    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        
        if member.bot:
            return
    
        invites_before = DatabaseCheck.check_invite_codes(guild_id = member.guild.id)
        invites_after = await member.guild.invites()

        summary = {}
        for _, user_id, code , uses in invites_before:

            if user_id in summary:

                summary[user_id]['codes'].add(code)
                summary[user_id]['uses'][code] = summary[user_id]['uses'].get(code, 0) + uses

            else:

                summary[user_id] = {'codes': {code}, 'uses': {code: uses}}
        
        result_before = []
        for user_id in summary:

            total_uses = sum(summary[user_id]['uses'].values())
            for code in summary[user_id]['codes']:

                result_before.append((code, user_id, total_uses))
        
        summary2 = {}
        for invite in invites_after:
            code = invite.code
            name = invite.inviter.id
            uses = invite.uses
            
            if name in summary2:

                summary2[name]['codes'].add(code)
                summary2[name]['uses'][code] = summary2[name]['uses'].get(code, 0) + uses

            else:

                summary2[name] = {'codes': {code}, 'uses': {code: uses}}

        result_after = []
        for name in summary2:

            total_uses = sum(summary2[name]['uses'].values())

            for code in summary2[name]['codes']:

                result_after.append((code, name, total_uses))

        for entry_after in result_after:
            
            if entry_after[0] not in result_before:

                await DatabaseUpdates.manage_leaderboard_invite_list(guild_id = member.guild.id, user_id = entry_after[1], invite_code = entry_after[0], uses = entry_after[2])

            for entry_before in result_before:
                
                if entry_after[1] == entry_before[1] and entry_before[2] < entry_after[2]:

                    await DatabaseUpdates.manage_leaderboard_invite(guild_id = member.guild.id, user_id = entry_before[1], settings = "tracking", interval = "countInvite")
                    await DatabaseUpdates.manage_leaderboard_invite_list(guild_id = member.guild.id, user_id = entry_before[1], invite_code = entry_before[0], uses = entry_after[2])
                    await self.check_expired_invites()
                    return            


    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):

        check = DatabaseCheck.check_leaderboard_settings(guild_id = payload.guild_id, system = "message")
        
        if check:

            if payload.message_id == check[2]:

                await DatabaseUpdates.manage_leaderboard_message(guild_id = payload.guild_id, back_to_none = "daily")

            elif payload.message_id == check[3]:

                await DatabaseUpdates.manage_leaderboard_message(guild_id = payload.guild_id, back_to_none = "weekly")


            elif payload.message_id == check[4]:

                await DatabaseUpdates.manage_leaderboard_message(guild_id = payload.guild_id, back_to_none = "monthly")

            elif payload.message_id == check[5]:

                await DatabaseUpdates.manage_leaderboard_message(guild_id = payload.guild_id, back_to_none = "whole")


        check = DatabaseCheck.check_leaderboard_settings(guild_id = payload.guild_id, system = "invite")

        if check:

            if payload.message_id == check[2]:

                await DatabaseUpdates.manage_leaderboard_invite(guild_id = payload.guild_id, back_to_none = "weekly")

            elif payload.message_id == check[3]:

                await DatabaseUpdates.manage_leaderboard_invite(guild_id = payload.guild_id, back_to_none = "monthly")

            elif payload.message_id == check[4]:

                await DatabaseUpdates.manage_leaderboard_invite(guild_id = payload.guild_id, back_to_none = "quarterly")

            elif payload.message_id == check[5]:

                await DatabaseUpdates.manage_leaderboard_invite(guild_id = payload.guild_id, back_to_none = "whole")


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        for system in ["message", "invite"]:

            check = DatabaseCheck.check_leaderboard_settings(guild_id = channel.guild.id, system = system)

            if check[5] == channel.id:

                await DatabaseRemoveDatas.remove_leaderboard_settings(guild_id = channel.guild.id, system = system)



############################################  Leaderboard system  ###################################


    '''
    Removes the roles from the users after the leaderboard has been updated

    Parameters:
    ------------
        - guild_id 
            The id of the server
        - interval
            Which interval was updated
        - system 
            Which leaderboard has been updated
    '''
    async def remove_leaderboard_roles(self, guild:int, interval:str, system:str):
    
        check_role = DatabaseCheck.check_leaderboard_roles_users(guild_id = guild.id, interval = interval, status = system)
        await DatabaseUpdates.manage_leaderboard_roles_users(guild_id = guild.id, interval = interval, status = system, operation = "remove")
        
        for _, role, user, _, _ in check_role:

            user = await guild.fetch_member(user)
            leaderboard_role = guild.get_role(role)
            await user.remove_roles(leaderboard_role)


    '''
    Creates the leaderboard

    Parameters:
    ------------
        - guild_id
            Id of the server
        - user_list
            Which users should be on the leaderboard
        - interval
            Which leaderboard interval is involved
        - system
            Which leaderboard should be created
    '''
    async def sort_leaderboard(self, user_list, interval, guild_id, system):
    
        guild = self.bot.get_guild(guild_id)
        interval_list = ["", "day", "week", "month", "whole"] if system == "message" else ["", "week", "month", "quarter", "whole"]
        check_roles = DatabaseCheck.check_leaderboard_roles(guild_id = guild_id, interval = interval_list[interval], system = system)
        
        general_role = None
        if check_roles:

            for i in check_roles:

                if i[2] == 0:

                    general_role = guild.get_role(i[1])

        max_lengths = [
            max(len(str(t[i])) for t in user_list)
            for i in range(10)
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
                str(t[2]).ljust(max_lengths[2]) if system == "message" else str(t[6]).ljust(max_lengths[6]),
                str(t[3]).ljust(max_lengths[3]) if system == "message" else str(t[7]).ljust(max_lengths[7]),
                str(t[4]).ljust(max_lengths[4]) if system == "message" else str(t[8]).ljust(max_lengths[8]),
                str(t[5]).ljust(max_lengths[5]) if system == "message" else str(t[9]).ljust(max_lengths[9])
            )
            for i, t in enumerate(user_list)
        ]
        
        await self.remove_leaderboard_roles(guild=guild, interval=interval_list[interval], system=system)
        
        leaderboard, count = [], 0
        for i in range(min(len(user_list), 15)):
            
            if check_roles and i != None:
                
                role = DatabaseCheck.check_leaderboard_roles(guild_id = guild_id, position = i + 1, system = system)

                if general_role != None and count < 1:
                    
                    await users[i].add_roles(general_role)
                    await DatabaseUpdates.manage_leaderboard_roles_users(guild_id = guild_id, user_id = users[i].id, role_id = general_role.id, operation = "add", status = system, interval = interval_list[interval])
                    count =+ 1

                if role != None:

                    leaderboard_role = guild.get_role(role[1])
                    await users[i].add_roles(leaderboard_role)
                    await DatabaseUpdates.manage_leaderboard_roles_users(guild_id = guild_id, user_id = users[i].id, role_id = role[1], operation = "add", status = system, interval = interval_list[interval])
                
            num_str = str(i + 1)
            if len(num_str) == 1:
                num_str = f" #{num_str}  "
            elif len(num_str) == 2:
                num_str = f" #{num_str} "
            
            leaderboard.append(f"`{num_str}` `{padded_tuples[i][0]}` `{'messages' if system == 'message' else 'invitations'} {padded_tuples[i][interval]}`\n")
            
        return "".join(leaderboard)


    @tasks.loop(hours=1)
    async def edit_leaderboard_invite(self):

        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:
            leaderboard_settings = DatabaseCheck.check_leaderboard_settings(guild_id=guild.id, system="invite")

            if leaderboard_settings and leaderboard_settings[1] == 1:

                message_ids = [
                    ("1_week_old", leaderboard_settings[2]),
                    ("1_month_old", leaderboard_settings[3]),
                    ("1_quarter_old", leaderboard_settings[4]),
                    ("whole", leaderboard_settings[5])
                ]
                
                if leaderboard_settings[6] is not None:

                    current_date = datetime.now(timezone.utc)
                    channel = self.bot.get_channel(leaderboard_settings[6])

                    for message_name, message_id in message_ids:

                        if message_id is not None:

                            message = await channel.fetch_message(message_id)
                            message_age = message.edited_at if message.edited_at is not None else message.created_at

                            if message_name == "whole" and (current_date - message_age) > timedelta(days=1):

                                await self.update_whole_leaderboard_invite(guild_id=guild.id, message=message)

                            if message_name == "1_week_old" and (current_date - message_age) > timedelta(days=1):

                                await self.update_weekly_leaderboard_invite(guild_id=guild.id, message=message)

                            if message_name == "1_month_old" and (current_date - message_age) > timedelta(weeks=1):

                                await self.update_monthly_leaderboard_invite(guild_id=guild.id, message=message)

                            if message_name == "1_quarter_old" and (current_date - message_age) > timedelta(days=30):

                                await self.update_quarterly_leaderboard_invite(guild_id=guild.id, message=message)

        else:

            return
        

    async def update_whole_leaderboard_invite(self, guild_id:int, message:discord.Message):

        user_list = DatabaseCheck.check_leaderboard(guild_id=guild_id, interval=3, system = "invite")
        users = await self.sort_leaderboard(user_list=user_list, interval=4, guild_id=guild_id, system="invite")

        emb = discord.Embed(description=f"""## Whole invite leaderboard
            The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=1)).timestamp())}>

            {users}""", color=bot_colour)
        await message.edit(embed=emb, view=ShowLeaderboardGivenRoles())


    async def update_weekly_leaderboard_invite(self, guild_id:int, message:discord.Message):

        user_list = DatabaseCheck.check_leaderboard(guild_id=guild_id, interval=0, system = "invite")
        users = await self.sort_leaderboard(user_list=user_list, interval=1, guild_id=guild_id, system="invite")

        emb = discord.Embed(description=f"""## Weekly invite leaderboard
            {Emojis.dot_emoji} These are the users who have invited the most users in the period from <t:{int((datetime.now() - timedelta(weeks=1)).timestamp())}> to <t:{int((datetime.now()).timestamp())}>

            {users}
            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(weeks=1)).timestamp())}>""", color=bot_colour)
        await message.edit(embed=emb, view=ShowLeaderboardGivenRoles())
        await DatabaseUpdates.manage_leaderboard_invite(guild_id=guild_id, back_to_none="weekly", settings="tracking")


    async def update_monthly_leaderboard_invite(self, guild_id:int, message:discord.Message):

        user_list = DatabaseCheck.check_leaderboard(guild_id=guild_id, interval=1, system = "invite")
        users = await self.sort_leaderboard(user_list=user_list, interval=2, guild_id=guild_id, system="invite")

        emb = discord.Embed(description=f"""## Monthly invite leaderboard
            {Emojis.dot_emoji} These are the users who have invited the most users in the period from <t:{int((datetime.now() - timedelta(days=30)).timestamp())}> to <t:{int((datetime.now()).timestamp())}>

            {users}
            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=30)).timestamp())}>""", color=bot_colour)
        await message.edit(embed=emb, view=ShowLeaderboardGivenRoles())
        await DatabaseUpdates.manage_leaderboard_invite(guild_id=guild_id, back_to_none="monthly", settings="tracking")


    async def update_quarterly_leaderboard_invite(self, guild_id:int, message:discord.Message):

        user_list = DatabaseCheck.check_leaderboard(guild_id=guild_id, interval=2, system = "invite")
        users = await self.sort_leaderboard(user_list=user_list, interval=3, guild_id=guild_id, system="invite")

        emb = discord.Embed(description=f"""## Quarterly invite leaderboard (90 days)
            {Emojis.dot_emoji} These are the users who have invited the most users in the period from <t:{int((datetime.now() - timedelta(days=80)).timestamp())}> to <t:{int((datetime.now()).timestamp())}>

            {users}
            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=90)).timestamp())}>""", color=bot_colour)
        await message.edit(embed=emb, view=ShowLeaderboardGivenRoles())
        await DatabaseUpdates.manage_leaderboard_invite(guild_id=guild_id, back_to_none="quarterly", settings="tracking")


    @tasks.loop(hours=1)
    async def edit_leaderboard_message(self):

        await self.bot.wait_until_ready()
        
        for guild in self.bot.guilds:
            
            leaderboard_settings = DatabaseCheck.check_leaderboard_settings(guild_id=guild.id, system="message")

            if leaderboard_settings:

                if leaderboard_settings and leaderboard_settings[1] == 1:

                    message_ids = [
                        ("1_day_old", leaderboard_settings[2]),
                        ("1_week_old", leaderboard_settings[3]),
                        ("1_month_old", leaderboard_settings[4]),
                        ("whole", leaderboard_settings[5])
                    ]
                    
                    if leaderboard_settings[6] is not None:

                        current_date = datetime.now(timezone.utc)
                        channel = self.bot.get_channel(leaderboard_settings[6])

                        for message_name, message_id in message_ids:

                            if message_id is not None:

                                message = await channel.fetch_message(message_id)
                                message_age = message.edited_at if message.edited_at is not None else message.created_at

                                if message_name == "whole" and (current_date - message_age) > timedelta(days=1):

                                    await self.update_whole_leaderboard_message(guild_id=guild.id, message=message)

                                if message_name == "1_day_old" and (current_date - message_age) > timedelta(days=1):

                                    await self.update_daily_leaderboard_message(guild_id=guild.id, message=message)

                                if message_name == "1_week_old" and (current_date - message_age) > timedelta(weeks=1):

                                    await self.update_weekly_leaderboard_message(guild_id=guild.id, message=message)

                                if message_name == "1_month_old" and (current_date - message_age) > timedelta(days=30):

                                    await self.update_monthly_leaderboard_message(guild_id=guild.id, message=message)

            else:
    
                return


    async def update_whole_leaderboard_message(self, guild_id:int, message:discord.Message):

        user_list = DatabaseCheck.check_leaderboard(guild_id=guild_id, interval=3, system = "message")
        users = await self.sort_leaderboard(user_list=user_list, interval=4, guild_id=guild_id, system="message")

        emb = discord.Embed(description=f"""## Whole message leaderboard
            The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=1)).timestamp())}>

            {users}""", color=bot_colour)
        await message.edit(embed=emb, view=ShowLeaderboardGivenRoles())


    async def update_daily_leaderboard_message(self, guild_id:int, message:discord.Message):

        user_list = DatabaseCheck.check_leaderboard(guild_id=guild_id, interval=0, system = "message")
        users = await self.sort_leaderboard(user_list=user_list, interval=1, guild_id=guild_id, system="message")

        emb = discord.Embed(description=f"""## Daily message leaderboard
            {Emojis.dot_emoji} These are the users who have written the most messages in the period from <t:{int((datetime.now() - timedelta(days=1)).timestamp())}> to <t:{int((datetime.now()).timestamp())}>

            {users}
            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=30)).timestamp())}>""", color=bot_colour)
        await message.edit(embed=emb, view=ShowLeaderboardGivenRoles())
        await DatabaseUpdates.manage_leaderboard_message(guild_id=guild_id, back_to_none="daily", settings="tracking")


    async def update_weekly_leaderboard_message(self, guild_id:int, message:discord.Message):

        user_list = DatabaseCheck.check_leaderboard(guild_id=guild_id, interval=1, system = "message")
        users = await self.sort_leaderboard(user_list=user_list, interval=2, guild_id=guild_id, system="message")

        emb = discord.Embed(description=f"""## Weekly message leaderboard
            {Emojis.dot_emoji} These are the users who have written the most messages in the period from <t:{int((datetime.now() - timedelta(weeks=1)).timestamp())}> to <t:{int((datetime.now()).timestamp())}>

            {users}
            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=30)).timestamp())}>""", color=bot_colour)
        await message.edit(embed=emb, view=ShowLeaderboardGivenRoles())
        await DatabaseUpdates.manage_leaderboard_message(guild_id=guild_id, back_to_none="weekly", settings="tracking")


    async def update_monthly_leaderboard_message(self, guild_id:int, message:discord.Message):

        user_list = DatabaseCheck.check_leaderboard(guild_id=guild_id, interval=2, system = "message")
        users = await self.sort_leaderboard(user_list=user_list, interval=3, guild_id=guild_id, system="message")

        emb = discord.Embed(description=f"""## Monthly message leaderboard (30 days)
            {Emojis.dot_emoji} These are the users who have written the most messages in the period from <t:{int((datetime.now() - timedelta(days=30)).timestamp())}> to <t:{int((datetime.now()).timestamp())}>

            {users}
            {Emojis.dot_emoji} The leaderboard will next be updated on <t:{int((datetime.now() + timedelta(days=30)).timestamp())}>""", color=bot_colour)
        await message.edit(embed=emb, view=ShowLeaderboardGivenRoles())
        await DatabaseUpdates.manage_leaderboard_message(guild_id=guild_id, back_to_none="monthly", settings="tracking")

    
def setup(bot):
    bot.add_cog(LeaderboardSystem(bot))



#######################################  Leaderboard system interactions  ###################################


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

                    await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=5, settings=system), view=ContinueSettingLeaderboard())

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
                
                if (all(option in value_check and value_check[option] is not None for option in select.values) and
                    len(select.values) == sum(1 for key, value in value_check.items() if value is not None)):

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
                    await interaction.response.edit_message(embed=emb, view=OverwriteInterval(intervals=select.values))

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
                            description=f"""## The number of messages is saved for {interval_text_message[i][0]}.
                            {Emojis.dot_emoji} This message will be edited on <t:{int((datetime.now() + timedelta(days=interval_text_message[i][1])).timestamp())}> and will then act as a leaderboard and show who has written the most messages on the server""", color=bot_colour)
                        message = await channel.send(embed=emb)
                        
                        await DatabaseUpdates.manage_leaderboard_message(guild_id = interaction.guild.id, settings = i, message_id = message.id)

                for i in [value for value in ["daily", "weekly", "monthly"] if value not in check_list]:

                    await DatabaseUpdates.manage_leaderboard_message(guild_id = interaction.guild.id, back_to_none = i)

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=6, settings=select.values, settings2=option_list, settings3=channel.mention), view=None)

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
                
                if (all(option in value_check and value_check[option] is not None for option in select.values) and
                    len(select.values) == sum(1 for key, value in value_check.items() if value is not None)): 

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
                    await interaction.response.edit_message(embed=emb, view=OverwriteInterval(intervals=select.values))

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
                            description=f"""## The number of invitations is saved for {interval_text_invite[i][0]}.
                            {Emojis.dot_emoji} This message will be edited on <t:{int((datetime.now() + timedelta(days=interval_text_invite[i][1])).timestamp())}> and will then act as a leaderboard and show who has invited the most users on the server""", color=bot_colour)
                        message = await channel.send(embed=emb)
                        
                        await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, settings = i, message_id = message.id)

                for i in [value for value in ["weekly", "monthly", "quarterly"] if value not in check_list]:

                    await DatabaseUpdates.manage_leaderboard_invite(guild_id = interaction.guild.id, back_to_none = i)

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
            
            system = 'message' if 'message leaderboard' in interaction.message.embeds[0].description else 'invite'

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

            system = 'message' if 'message leaderboard' in interaction.message.embeds[0].description else 'invite'

            emb = discord.Embed(description=f"""## Set intervals
                {Emojis.dot_emoji} With the lower select menu you can define an interval in which periods the {system} leaderboard should be updated
                {Emojis.dot_emoji} You can also select several intervals, but you only need to select at least one
                {Emojis.help_emoji} As soon as you have selected the intervals, the leaderboards are sent to the channel you have previously set up and then always updated in the corresponding time periods""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=SetInviteleaderboard() if system == "invite" else SetMessageleaderboard())

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class OverwriteInterval(discord.ui.View):

    def __init__(self, intervals):
        self.intervals = intervals
        super().__init__(timeout=None)
        self.add_item(CancelButton(system=None))

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

                for ids in [settings[2], settings[3], settings[4], settings[5]]:

                    if ids != None:

                        old_message = await channel.fetch_message(ids)
                        await old_message.delete()

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
                        list_intervals.append(f"{Emojis.dot_emoji} Daily updated leaderboard\n")
                    if week is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Weekly updated leaderboard\n")
                    if month is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Monthly updated leaderboard\n")

            else:

                for _, _, week, month, quarter, _, _ in check_settings:

                    if week is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Weekly updated leaderboard\n")
                    if month is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Monthly updated leaderboard\n")
                    if quarter is not None:
                        list_intervals.append(f"{Emojis.dot_emoji} Quarterly updated leaderboard\n")

            emb = discord.Embed(
                description=f"""## The current intervals are retained
                {Emojis.dot_emoji} Here you can see an overview of the currently defined intervals
                {"".join(list_intervals)}""",
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



#########################################  Message leaderboard roles  ####################################################
        

'''
Shows which roles have been defined for which leaderboard

Parameters:
------------
    - guid_id
        Id of the server
    - interval
        Which leaderboard interval is involved
    - system
        Which leaderboard is involved
'''
def show_leaderboard_roles(guild_id, interval, system):

    check = DatabaseCheck.check_leaderboard_roles(guild_id = guild_id, interval = interval, system = system)
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
            
            system = "message" if "message leaderboard" in interaction.message.embeds[0].description else "invite"

            if any(x != None for x in [self.role, self.interval, self.settings, self.position, self.delete]):

                check_role = DatabaseCheck.check_leaderboard_roles(guild_id = interaction.guild.id, role_id = self.delete[1], system = system)
                if check_role:
                    await DatabaseRemoveDatas.remove_leaderboard_role(guild_id = interaction.guild.id, role_id = self.delete[1], interval = self.interval, system = system)
                check_positon = DatabaseCheck.check_leaderboard_roles(guild_id = interaction.guild.id, position = self.position, system = system)
                if check_positon:
                    await DatabaseRemoveDatas.remove_leaderboard_role(guild_id = interaction.guild.id, role_id = check_positon[1], interval = self.interval, system = system)

                await DatabaseUpdates.manage_leaderboard_roles(guild_id = interaction.guild.id, role_id = self.role.id, position = self.position, status = system, interval = self.interval)

                emb = discord.Embed(description=f"""## The entry has been overwritten
                    {Emojis.dot_emoji} From now on the role <@&{self.role.id}> is assigned to the {self.position} place, this applies to the {self.interval}{'ly' if self.interval != 'general' else ''} leaderboard
                    {Emojis.dot_emoji} If you want to change the settings of the {system} leaderboard system you can do this with the `set-{system}-leaderboard` command""", color=bot_colour)  
                await interaction.response.edit_message(embed=emb, view=None)

            else:

                await interaction.response.edit_message(embed=GetEmbed.get_embed(embed_index=10, settings="leaderboard role", settings2="to overwrite the role", settings3=f"add-{system}-leaderboard-role"), view=None)

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


class ShowLeaderboardRolesButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label = "show all leaderboard roles",
        style = discord.ButtonStyle.blurple,
        custom_id = "show_leaderboard_roles_button"
    )
    
    async def callback(self, button, interaction:discord.Interaction):
        
        if interaction.user.guild_permissions.administrator:

            interval_text = {
                "message":f"""{Emojis.dot_emoji} Daily leaderboard: Every day, the system checks which users have posted the most messages. The previously counted messages are deleted
                {Emojis.dot_emoji} Weekly leaderboard: Every week, the system checks which users have posted the most messages. The previously counted messages are deleted
                {Emojis.dot_emoji} Monthly leaderboard: Every month, the system checks which users have posted the most messages. The previously counted messages are deleted
                {Emojis.dot_emoji} General leaderboard: This checks which users have written the most messages (updated daily). The previously counted messages are not deleted""",
                
                "invite":f"""{Emojis.dot_emoji} Weekly leaderboard: Every week, the system checks which users have invited the most users. The previously counted invitations are deleted
                {Emojis.dot_emoji} Monthly leaderboard: Every month, the system checks which users have invited the most users. The previously counted invitations are deleted
                {Emojis.dot_emoji} Quarterly leaderboard: Every quarter of a year, the system checks which users have invited the most users. The previously counted invitations are deleted
                {Emojis.dot_emoji} General leaderboard: This checks which users have invited the most users (updated daily). The previously counted invitations are not deleted"""
            }

            emb = discord.Embed(description=f"""## Leaderboard roles
                {Emojis.dot_emoji} With the lower select menu you can see which roles are set for which leaderboard
                {Emojis.dot_emoji} The following leaderboards are available
                
                {interval_text['message' if 'message leaderboard' in interaction.message.embeds[0].description else 'invite']}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=ShowLeaderboardRolesSelectMessage())
        
        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)


class ShowLeaderboardRolesSelectMessage(discord.ui.View):

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

            emb = discord.Embed(description=f"""## Leaderboard roles for the message leaderboard
                {Emojis.dot_emoji} Here you can see an overview of all roles that are listed on the {select.values[0]} leaderboard

                {show_leaderboard_roles(guild_id=interaction.guild.id, interval=select.values[0], system="message")}""", color=bot_colour)
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

        system = "message" if "Messages Leaderboard" in interaction.message.embeds[0].description else "invite"

        intervals = [
            "Whole",
            "Daily" if system == "message" else "Weekly",
            "Weekly" if system == "message" else "Monthly",
            "Monthly" if system == "message" else "Quarterly"
        ]
        
        for key in intervals:

            if key in interaction.message.embeds[0].description:
            
                check_roles = DatabaseCheck.check_leaderboard_roles_users(guild_id = interaction.guild.id, status = system, interval = key.lower())

                user_list, general_role = [], None
                for role in check_roles:
                    
                    check_position = DatabaseCheck.check_leaderboard_roles(guild_id = interaction.guild.id, role_id = role[1], system = system)

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


class ShowLeaderboardRolesSelectInvite(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder = "Choose from which leaderboard you want to see all roles!",
        min_values = 1,
        max_values = 1,
        custom_id = "show_leaderboard_roles",
        options = [
            discord.SelectOption(label="Weekly leaderboard", description="Take a look at which roles are defined for the weekly leaderboard", value="weekly"),
            discord.SelectOption(label="Monthly leaderboard", description="Take a look at which roles are defined for the Monthly leaderboard", value="monthly"),
            discord.SelectOption(label="Quarterly leaderboard", description="Take a look at which roles are defined for the quarterly leaderboard", value="quarterly"),
            discord.SelectOption(label="General leaderboard", description="Take a look at which roles are defined for the Gernal leaderboard", value="general")
        ]
    )

    async def show_leaderboard_roles_select(self, select, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(description=f"""## Leaderboard roles for the invite leaderboard
                {Emojis.dot_emoji} Here you can see an overview of all roles that are listed on the {select.values[0]} leaderboard

                {show_leaderboard_roles(guild_id=interaction.guild.id, interval=select.values[0], system="invite")}""", color=bot_colour)
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)