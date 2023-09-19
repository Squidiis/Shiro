
from Import_file import *
import aiofiles
import calendar



class moderator_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        
        guild=bot.get_guild(977958841385902092)

        member=message.author
        if message.author.bot:
            return

        else:

            if message.author.guild_permissions.administrator:
                return
            
            else:

                if 'discord.gg/' in message.content:
                    await message.delete()
                    modembed = discord.Embed(title=f'Hey {message.author.name}!', description='Please do not send invitation links!', colour=bot_colour)
                    modembed.set_author(name=f'{message.author.name}', icon_url = guild.icon.url)
                    msg = await message.channel.send(embed=modembed, delete_after=5)
                    reason = "Send invitation link"
                    await member.timeout(until=timedelta(minutes=5), reason = reason)
                    embed = discord.Embed(title=f"{member} You get a 5 minute time out", description=f"Grund: {reason}")
                    await member.send(embed=embed)

        if message.author.bot:
            return
    


    @commands.slash_command(name = "ban", description = "Bans a member!")
    @commands.has_permissions(ban_members = True, administrator = True)
    async def ban_slash(self, ctx, member: Option(discord.Member, description = "Who do you want to ban?"), reason: Option(str, description = "Why?", required = False)):
        if member.id == ctx.author.id:
            await ctx.respond("**BRUH! You can't banish yourself!")
        elif member.guild_permissions.administrator:
            await ctx.respond("**You can't ban an admin!** :rolling_eyes:")
        else:
            if reason == None:
                reason = f"**No reason was given by {ctx.author}!**"
            embed=discord.Embed(title=f"{member} you have been banned from your server name!", description=f"Reason: `{reason}`", color=0x0094ff)
            await member.send(embed=embed)
            await member.ban(reason = reason)
            await ctx.respond(f"**<@{ctx.author.id}>, <@{member.id}> was successfully banned from the server!** `{reason}`")



    @commands.slash_command(name = "kick", description = "Kicks a member!")
    @commands.has_permissions(kick_members = True, administrator = True)
    async def kick_slash(self, ctx, member: Option(discord.Member, description = "Who do you want to kick?"), reason: Option(str, description = "Why?", required = False)):
        if member.id == ctx.author.id: 
            await ctx.respond("**BRUH! You can't kick yourself!")
        elif member.guild_permissions.administrator:
            await ctx.respond("**You can't kick an admin!** :rolling_eyes:")
        else:
            if reason == None:
                reason = f"**No reason was given by {ctx.author}!**"
            embed=discord.Embed(title=f"{member} you have been kicked from your server name!", description=f"Reason: `{reason}`", color=0x0094ff)
            await member.send(embed=embed)
            await member.kick(reason = reason)
            await ctx.respond(f"**<@{ctx.author.id}>, <@{member.id}> was successfully kicked from the server!\n\nReason:** `{reason}`")



    @commands.slash_command(name = "unban", description = "Unbanned a member")
    @commands.has_permissions(ban_members = True)
    async def unban_slash(self, ctx, id: Option(discord.Member, description = "The user ID of the member you want to unban.", required = True)):
        await ctx.defer()
        member = await bot.get_or_fetch_user(id)
        await ctx.guild.unban(member)
        await ctx.respond(f"**I have unbanned {member.mention}.**")



    @commands.slash_command(name = 'mute', description = "Mutes a member!")
    @commands.has_permissions(moderate_members = True)
    async def mute_slash(self, ctx, member: Option(discord.Member, required = True), reason: Option(str, required = False), days: Option(int, max_value = 27, default = 0, required = False), hours: Option(int, default = 0, required = False), minutes: Option(int, default = 0, required = False), seconds: Option(int, default = 0, required = False)): #setting each value with a default value of 0 reduces a lot of the code
        if member.id == ctx.author.id:
            await ctx.respond("**You can't mute yourself!**")
            return
        if member.guild_permissions.moderate_members:
            await ctx.respond("**You can't mute an admin!**")
            return
        duration = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)
        if duration >= timedelta(days = 28):
            await ctx.respond("**I can't mute anyone for more than 28 days!**", ephemeral = True) 
            return
        if reason == None:
            await member.timeout_for(duration)
            await ctx.respond(f"**<@{member.id}> was muted for** `{days}` **days,** `{hours}` **hours,** `{minutes}` **minutes, and** `{seconds}` **seconds by <@{ctx.author.id}>! Reason:** `No reason was given!`")
            embed=discord.Embed(title=f"{member} you have been muted on your server name!", description=f"Follow the rules! Please do not send any more links!\nDuration: {days} days, {hours} hours, {minutes} minutes and {seconds} seconds\nReason: `No reason was given!`", color=0x0094ff)
            await member.send(embed=embed)
        else:
            await member.timeout_for(duration, reason = reason)
            await ctx.respond(f"**<@{member.id}> has been muted for** `{days}` **days,** `{hours}` **hours,** `{minutes}` **minutes, and** `{seconds}` **seconds by <@{ctx.author.id}>! Reason:**`{reason}`")
            embed=discord.Embed(title=f"{member} you have been released on your server name again!", description=f"Follow the rules! Please do not send any more links!\nDuration: {days} days, {hours} hours, {minutes} minutes and {seconds} seconds\nReason: `{reason}!`", color=0x0094ff)
            await member.send(embed=embed)



    @commands.slash_command(name = 'unmute', description = "unmute a Member!")
    @commands.has_permissions(moderate_members = True)
    async def unmute_slash(self, ctx, member: Option(discord.Member, required = True), reason: Option(str, required = False)):
        if reason == None:
            await member.remove_timeout()
            await ctx.respond(f"**<@{member.id}> was Released by <@{ctx.author.id}>.**")
            embed=discord.Embed(title=f"{member} you have been released again!", description="Stick to the rules! Please do not send any more links!", color=0x0094ff)
            await member.send(embed=embed)
        else:
            await member.remove_timeout(reason = reason)
            await ctx.respond(f"**<@{member.id}> was released by <@{ctx.author.id}>. Reason:** `{reason}`")
            embed=discord.Embed(title=f"{member} you have been released again!", description="Stick to the rules! Please do not send any more links!", color=0x0094ff)
            await member.send(embed=embed)



    @commands.slash_command(name = "clear", description = "Delete messages in the channel!")
    @commands.has_permissions(manage_messages=True)
    async def clear_slash(self, ctx, wieviele: Option(int , description = "How many messages do you want to delete?", required = True)):
        await ctx.defer()
        z = await ctx.channel.purge(limit = wieviele)
        await ctx.send(f"I have deleted {len(z)}.")



    @commands.slash_command(name = "server-info", description="Server info!")
    async def serverinfo_slash(self, ctx):

        embed = discord.Embed(title=f"{ctx.guild.name} Info", description="Information of this Server", color=discord.Colour.blue())
        embed.add_field(name='🆔Server ID', value=f"{ctx.guild.id}")
        embed.add_field(name='📆Created On', value=ctx.guild.created_at.strftime("%b %d %Y"))
        embed.add_field(name='👑Owner', value=f"{ctx.guild.owner.mention}")
        embed.add_field(name='👥Members', value=f'{ctx.guild.member_count} Members')
        embed.add_field(name='🌎Region', value=f'{ctx.guild.preferred_locale}')
        #embed.add_field(name='💬 Text Channels', value=f'{len(ctx.guild.text_channels)}', inline=True)
        #embed.add_field(name='💬 Voice Channels', value=f'{len(ctx.guild.voice_channels)} Voice', inline=True)
        #embed.add_field(name='💬 Categories', value=f'{len(ctx.guild.categories)} Categories', inline=True)
        #embed.add_field(name='💬 Threads', value=f'{len(ctx.guild.threads)}', inline=True)
        #embed.add_field(name='💬 Stage Channels', value=f'{len(ctx.guild.stage_channels)}', inline=True)
        embed.add_field(name='🌎Roles', value=f'{len(ctx.guild.roles)}')
        embed.add_field(name='🌎Boosts', value=f'{len(ctx.guild.premium_subscribers)}')
        embed.add_field(name='💬 Channels', value=f'Text [{len(ctx.guild.text_channels)}], Voice [{len(ctx.guild.voice_channels)}], \nCategories [{len(ctx.guild.categories)}], \nThreads [{len(ctx.guild.threads)}], Stage [{len(ctx.guild.stage_channels)}]', inline=False)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_footer(text="⭐ • Squidi")
        embed.set_author(name=str(ctx.author.name), icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)



    @commands.slash_command(name = "user-info", description = "Shows you information about individual users!")
    async def userinfo_slash(self ,ctx ,user: Option(discord.Member)):
        if user is None:
            user = ctx.author      
        date_format = "%a, %d %b %Y %I:%M %p"
        embed = discord.Embed(color=0xdfa3ff, description=user.mention)
        embed.set_author(name=str(user), icon_url=user.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Joined", value=user.joined_at.strftime(date_format))
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        embed.add_field(name="Registered", value=user.created_at.strftime(date_format))
        embed.add_field(name="Join position", value=str(members.index(user)+1))
        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            embed.add_field(name="Roles [{}]".format(len(user.roles)-1), value=role_string, inline=False)
        perms_to_show = [
        'administrator', 'manage_messages', 'manage_roles', 'manage_channels',
        'manage_messages', 'manage_webhooks', 'manage_nicknames', 'manage_emojis',
        'manage_emojis_and_stickers', 'kick_members', 'ban_members', 'mention_everyone']
        perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[0] in perms_to_show])
        embed.add_field(name="Guild permissions", value=perm_string, inline=False)
        embed.set_footer(text='ID: ' + str(user.id))
        return await ctx.respond(embed=embed)



    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.mentions != 0:
            if len(message.mentions) < 3:
                for m in message.mentions:
                    if m == message.author or m.bot:
                        pass
                    else:
                        embed=discord.Embed(title=f":ghost: | Ghost ping", description=f"**{m}** you were ghostping from {message.author.mention}.\n \n**message:** {message.content}", color=0xffb375)
                        await message.channel.send(embed=embed)
            else:
                embed=discord.Embed(title=f":ghost: | Ghost ping", description=f"**{len(message.mentions)} User** have been ghostpinged.\n \n**message by {message.author.mention}:** {message.content}", color=0xffb375)
                await message.channel.send(embed=embed)

    

    @commands.slash_command()
    async def userinfo(ctx, member:Option(discord.Member, description="Select a user from whom you want to view the user infos!")):
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

        



class AutoReaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild:
            if message.guild.id == 865899808183287848:
                categorys = [996846958536835203, 927683692695027772, 998934946708205598, 930157270275350598, 897544467266011177, 873622071484252200, 927668688239353926]
                if message.channel.category_id in categorys:
                    if len(message.attachments) > 0 or message.content.startswith("https://"):
                        await message.add_reaction("❤")
        else:
            return


def setup(bot):
    bot.add_cog(AutoReaction(bot))
    bot.add_cog(moderator_commands(bot))

