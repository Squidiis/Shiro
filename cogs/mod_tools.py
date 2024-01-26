
from import_file import *
import calendar



class ModeratorCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



##################################  Anti-link system  #########################################


    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):

        if message.author.bot:
            return

        else:

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
            
                    if "discord.gg/" in message.content:
                        await message.delete()
                        rule_violation = True

                # Is triggered when there is a link in the message, images and videos are ignored (when triggered, the message is deleted)
                elif check_settings[3] == 1:
            
                    if "https://" in message.content and not message.attachments:

                        await message.delete()
                        rule_violation = True

                # Is triggered when there is a link in the message (when triggered, the message is deleted)
                elif check_settings[3] == 2:

                    if "https://" in message.content or message.attachments:

                        await message.delete()
                        rule_violation = True

                elif check_settings[3] == 3:
                    return
                
                if rule_violation == True:

                    await channel.send(embed=emb, delete_after=5)
                    await message.author.timeout_for(timedelta(minutes = check_settings[4]))


    @commands.slash_command(name = "set-anti-link", description = "Set the anti-link system the way you want it!")
    @commands.has_permissions(administrator = True)
    async def set_anti_link(self, ctx:discord.ApplicationContext,
        settings:Option(str, required = True,
            description="Choose how the anti-link system should behave!",
            choices = [
                discord.OptionChoice(name = "All messages with a discord invitation link will be deleted", value="0"),
                discord.OptionChoice(name = "All messages with a link will be deleted exceptions: images, videos (discord links will be deleted)", value="1"),
                discord.OptionChoice(name = "All messages with a link will be deleted this also includes pictures and videos", value="2"),
                discord.OptionChoice(name = "Deactivate anti-link system! (no messages are deleted)", value="3")]), 
        timeout:Option(int, max_value = 60, required = True, 
            description="Choose how long the user who violates the anti link system should be timed out! (Optional)", 
            choices = [0, 5, 10, 20, 30, 40, 50, 60])):

        DatabaseUpdates.update_bot_settings(guild_id=ctx.guild.id, anti_link=int(settings), anti_link_timeout=timeout)

        # Text passages for the embed
        settings_text = {
            "0":"All messages that contain a discord invitation link.",
            "1":"All messages with a link, pictures and videos will not be deleted (discord invitation links will be deleted)",
            "2":"All messages with a link will be deleted this also includes pictures and videoso",
            "3":"Nothing because the anti-link system is deactivated"}

        emb = discord.Embed(title=f"{Emojis.settings_emoji} The anti-link system was set up", 
            description=f"""{Emojis.dot_emoji} The anti-link system will now delete the following messages:
            `{settings_text[settings]}`
            {f'{Emojis.dot_emoji} Users who still send links will receive a timeout of **{timeout}** minutes' if settings != '3' else ''}""", color=bot_colour)
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


    @commands.slash_command(name = 'timeout', description = "Send a user to timeout!")
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


    @commands.slash_command(name = 'remove-timeout', description = "Cancel the timeout of a user!")
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


    @commands.slash_command(name = "clear", description = "Delete messages in the channel!")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, quantity:Option(int, description = "How many messages do you want to delete?", required = True)):
        await ctx.defer()
        z = await ctx.channel.purge(limit = quantity)
        await ctx.send(f"I have deleted {len(z)} messages.")


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
        embed.add_field(name='💬 Channels', value=f'Text [{len(ctx.guild.text_channels)}], Voice [{len(ctx.guild.voice_channels)}], \nCategories [{len(ctx.guild.categories)}], \nThreads [{len(ctx.guild.threads)}], Stage [{len(ctx.guild.stage_channels)}]', inline=False)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_author(name=str(ctx.author.name), icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)


    # Anti ghost ping system
    @commands.Cog.listener()
    async def on_message_delete(self, message:discord.Message):

        check_settings = DatabaseCheck.check_bot_settings(guild_id=message.guild.id)

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


    @commands.slash_command(name = "ghost-ping-settings", description = "Schalte das ghost ping system ein oder aus!")
    async def ghost_ping_settings(self, ctx:commands.Context):

        # If the database contains 0, the system is deactivated; if it contains 1, it is activated
        check_settings = DatabaseCheck.check_bot_settings(guild_id=ctx.guild.id)

        emb = discord.Embed(title=f"{Emojis.settings_emoji} Here you can set the anti ghost ping system ", 
            description=f"""{Emojis.dot_emoji} Currently the anti ghost ping system is {'**enabled**' if check_settings[2] == 0 else '**disabled**'}
            {Emojis.dot_emoji} If you want it to {'**turn it on**' if check_settings[2] == 0 else '**turn it off**'} press the lower button""", color=bot_colour)
        await ctx.respond(embed=emb, view=GhostPingButtons())


    @commands.slash_command()
    async def userinfo(ctx:discord.ApplicationContext, member:Option(discord.Member, description="Select a user from whom you want to view the user infos!")):
        member = ctx.author if not member else member

        unix_join_time = calendar.timegm(member.joined_at.utctimetuple())
        unix_create_time = calendar.timegm(member.created_at.utctimetuple())

        badge = ""
        if member.public_flags.bug_hunter:
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

        user_banner = await bot.fetch_user(member.id)

        if user_banner.banner is not None:
            if member.avatar is not None:
                embed = discord.Embed(colour=member.color,
                                    timestamp=datetime.utcnow(),
                                    description=f"[User Avatar]({member.avatar.url}) | [User Banner]({user_banner.banner.url})")
                embed.set_image(url=f"{user_banner.banner.url}")
                embed.set_thumbnail(url=f'{member.display_avatar.url}')
            else:
                embed = discord.Embed(colour=member.color,
                                    timestamp=datetime.utcnow(),
                                    description=f"[User Banner]({user_banner.banner.url})")
                embed.set_image(url=f"{user_banner.banner.url}")
        elif member.avatar is not None:
            embed = discord.Embed(colour=member.color,
                                    timestamp=datetime.utcnow(),
                                    description=f"[User Avatar]({member.avatar.url})")
            embed.set_thumbnail(url=f'{member.display_avatar.url}')
        else:
            embed = discord.Embed(colour=member.color,
                                    timestamp=datetime.utcnow())

        embed.set_author(name=f"Userinfo")

        embed.add_field(name="Name:",
                        value=f"`{member} (Bot)`" if member.bot else f"`{member}`",
                        inline=True)
        embed.add_field(name=f"Mention:",
                        value=member.mention,
                        inline=True)
        embed.add_field(name="Nick:",
                        value=f"`{member.nick}`" if member.nick else "Nicht gesetzt",
                        inline=True)
        embed.add_field(name="ID:",
                        value=f"`{member.id}`",
                        inline=True)

        if member.status == discord.Status.online:
            if member.is_on_mobile():
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

        await ctx.reply(embed=embed)
            

def setup(bot):
    bot.add_cog(ModeratorCommands(bot))



class GhostPingButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Turn off / on the Ghost ping system", style=discord.ButtonStyle.blurple, custom_id="turn_off_on", row=1)
    async def on_off_ghost_ping(self, button, interaction:discord.Interaction):

        check_settings = DatabaseCheck.check_bot_settings(guild_id=interaction.guild.id)
        DatabaseUpdates.update_bot_settings(guild_id=interaction.guild.id, ghost_ping=1 if check_settings[2] == 0 else 0)

        emb = discord.Embed(title=f"{Emojis.help_emoji} You have successfully switched the ghost ping system {'**off**' if check_settings[2] != 0 else '**on**'}", 
            description=f"""{Emojis.dot_emoji} The anti ghost ping system is now {'**disabled**.' if check_settings[2] != 0 else f'''**enabled**.
            {Emojis.dot_emoji} From now on a message is always sent when a user marks someone and deletes this message.'''}""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label="Cancel from setting ghost ping system", style=discord.ButtonStyle.blurple, custom_id="cancel_ghost_ping", row=2)
    async def cancel_ghost_ping_settings(self, button, interaction:discord.Interaction):

        emb = discord.Embed(title=f"{Emojis.help_emoji} The setting of the anti ghost ping system was canceled", 
            description=f"""{Emojis.dot_emoji} The setting was successfully canceled but you can change the settings at any time.""", color=bot_colour)
        await interaction.response.edit_message(embed=emb, view=None)