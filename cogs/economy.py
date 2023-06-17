from Import_file import *
from typing import Union
from check import *

            


#############################################  Reset Buttons economy system  #######################################################


class ResetEconomyStatsButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.blurple, row=1, custom_id="yes_button_stats")
    async def reset_stats_button_economy_yes(self, button, interaction, ):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id
            DatabaseRemoveDatas._remove_economy_system_stats(guild_id=guild_id)

            emb = discord.Embed(title=f"Du hast alle stats des economy systems zurückgesetzt {succesfully_emoji}", 
                description=f"""{arrow_emoji} Alle user datein wurden gelöscht jeder user hat jetzt wieder 0 coins.
                Es werden wieder bei aktivitäht neue enträge erstellt, wenn sie das nicht möchten stellen sie das economy system aus {exclamation_mark_emoji}""", color=shiro_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)


    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, row=1, custom_id="no_button_stats")
    async def reset_stats_button_economy_no(self, button, interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Der vorgang wurde erfolgreich abgebrochen {succesfully_emoji}", 
                description=f"""{dot_emoji} Das resetten der stats wurde erfolgreich abgebrochen.
                Alle user behalten Ihre stats im economy system.""", color=shiro_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)



class ResetBlacklistEconomyButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.blurple, row=1, custom_id="yes_button_blacklist")
    async def reset_blacklist_button_economy_yes(self, button, interaction, ):

        if interaction.user.guild_permissions.administrator:
            guild_id = interaction.guild.id

            DatabaseRemoveDatas._remove_economy_system_blacklist(guild_id=guild_id)
            emb = discord.Embed(title=f"Die blacklist wurde geresetet {succesfully_emoji}", 
                description=f"""{arrow_emoji} alle Channel, User, Rollen und Kategorien wurden von der Blacklist entfernt.
                Wenn du wieder Dinge auf die Blacklist setzten möchtest kannst du die Befehle wie zuvor nutzen {exclamation_mark_emoji}""", color=shiro_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)


    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, row=1, custom_id="no_button_blacklist")
    async def reset_blacklist_button_economy_no(self, button, interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Der vorgang wurde erfolgreich abgebrochen {succesfully_emoji}", 
                description=f"""{dot_emoji} Das resetten der blacklist wurde erfolgreich abgebrochen.
                Alle Channels, Rollen, Kategorien und User sind weiterhin auf der blacklist gelistet.
                {dot_emoji} Wenn du einzelne elemente von der blacklist steichen möchtest kannst du sie mit den Remove commands streichen lassen {exclamation_mark_emoji}""", color=shiro_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)

            
    @discord.ui.button(label="Shows all elements of the blacklist", style=discord.ButtonStyle.blurple, row=2, custom_id="show_blacklist_button_economy")
    async def show_blacklist_button_economy(self, button, interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id
            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)
            
            channel, category, role, user = blacklist[0], blacklist[1], blacklist[2], blacklist[3] 

            emb = discord.Embed(title=f"Hier siehst du alle Elemente die auf der Blacklist stehen {exclamation_mark_emoji}", 
                description=f"""Hier sind alle Elemente aufgelistet die auf der Blacklist stehen.""", color=shiro_colour)
            emb.add_field(name="Channels:", value=f"{channel}", inline=False)
            emb.add_field(name="Categories:", value=f"{category}", inline=False)
            emb.add_field(name="Rolles", value=f"{role}", inline=False)
            emb.add_field(name="Users", value=f"{user}", inline=False)
            emb.set_footer(icon_url=bot.user.avatar ,text="This message is only visible to you")
            await interaction.response.send_message(embed=emb, view=None, ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)



class EconomySystemBigHelp(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="More Information", style=discord.ButtonStyle.gray, custom_id="more_help_ecnomy")
    async def economy_system_more_help_button_callback(self, button, interaction):

        guild_id = interaction.guild.id

        emb = discord.Embed(title="All informationen zum Economy system")





##############################################  Economy System Settings  ##############################################


class EconomySystemSettings(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    # Erweitern 
    @discord.ui.select(placeholder="Wähle die Parameter aus die du haben möchten", min_values=1, max_values=4, custom_id="interaction:dropdown_system_control", options = [

        discord.SelectOption(label="Messages", description="Hier werden nachrichten mit coins belohnt", value="message"),
        discord.SelectOption(label="Work", description="Hier kann man mit einen Command arbeiten um coins zu bekomemn", value="work"),
        discord.SelectOption(label="Voice", description="Hier werden alle aktivitäten in voice channels belohnt", value="voice"),
        discord.SelectOption(label="Abbrechen", description="Hier brichst du die einrichtung ab", value="cancel")     
    ])
    async def economy_system_control_callback(self, select, interaction: discord.Interaction):
        
        guild_id = interaction.guild.id

        if "cancel" in select.values:
            
            emb = discord.Embed(title="Die einstellung wurde abbgebrochen")
            await interaction.response.send_message(embed=emb, view=None)

        else:

            parameter = []
            _insert_parameter = []
            
            for values in select.values:
                
                if values == "message":
                    parameter.append(f"{dot_emoji} message\n")
                    _insert_parameter.append("on_message")

                if values == "work":
                    parameter.append(f"{dot_emoji} work\n")
                    _insert_parameter.append("on_work")

                if values == "voice":
                    parameter.append(f"{dot_emoji} voice\n")
                    _insert_parameter.append("on_voice")

                if "on_voice" in _insert_parameter and "on_work" in _insert_parameter and "on_message" in _insert_parameter:
                    insert_parameter = "on_all"
                else:
                    insert_parameter = ", ".join(_insert_parameter)

                all_parameter = "".join(parameter)
           
            DatabaseUpdates._update_status_economy(status=insert_parameter, guild_id=guild_id)
                
            emb = discord.Embed(title=f"Das Economy system ist jetzt eingestellt {succesfully_emoji}", 
                description=f"""Das Economy system reagiert ab jetzt auf:
                {all_parameter}
                Wenn du diese einstellungen ändern möchtest führen sie diesen command noch einmal aus
                """, color=shiro_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True, view=None) 

                
    @discord.ui.button(label="Click my for Help", style=discord.ButtonStyle.green, custom_id="help_button", emoji=help_emoji)
    async def help_button_economy_system_callback(self, button, interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id

            infos = DatabaseCheck.check_bot_settings(guild=guild_id)
            
            if infos == None:

                DatabaseUpdates._create_bot_settings(guild_id=guild_id)
                status = "Das economy system ist aktiv und reagiert auf Nachtichten"

            else:

                parameter = []
                if "on_all" in infos[4]:
                    parameter.append(f"{dot_emoji} Alles auf Nachrichten, Voice time und Work commands")
                else:
                    if "on_message" in infos[4]:
                        parameter.append(f"{dot_emoji} Das schicken von Nachrichten")
                    if "on_voice" in infos[4]:
                        parameter.append(f"{dot_emoji} Die zeit die ein user in einen Voice channel vergringt")
                    if "on_work" in infos[4]:
                        parameter.append(f'{dot_emoji} Das nutzen von Work Commands')
                    if "off" in infos[4]:
                        parameter.append(f"{dot_emoji} Nichts da es deaktiveirt wurde")

                status = f"\n".join(parameter)
            help_embed = discord.Embed(title=f"Hilfe zum einstellen des Economy systems {help_emoji}", 
                description=f"""
                Das Economy system ist ein system bei denen akktivitäten mit coins belohnt werden dabei kann man auswählen was belohnt wird: 

                {dot_emoji} Nachrichten.
                {dot_emoji} Voice zeit.
                {dot_emoji} Benutzen von den Fun work commands.

                Es ist auch möglich alles auzuwählen.
                Du kann auch ein Individuelles Genre wählen.
                Auch ist es möglich seine coins im shop auszugeben {dollar_animation_emoji},
                für mehr informatinen dazu kannst du unten auf die Knöpfe drücken""", color=shiro_colour)
            help_embed.add_field(name=f"Status {settings_emoji}", value=f"Das economy system belohnt:\n{status}", inline= False)
            help_embed.add_field(name="Was bringt das economy system", 
                value="Es soll bei der steigerung der server aktivität und beim wacksen deiner Community Helfen", inline=True)
            help_embed.add_field(name="Steuerung", 
                value=f"""Du kannst alles mit dem bot oder vom Dashbourd aus steuern und vieles custom anpassen.
                Mit den Button kannst du das Economy system aus/anschalten""", inline=True)
            help_embed.set_footer(icon_url=bot.user.avatar ,text="This message is only visible to you")
            await interaction.response.send_message(embeds=[help_embed], ephemeral=True)

        else:

            await interaction.send_message(embed=no_permissions_emb, ephemeral=True, view=None)

    
    @discord.ui.button(label="On/Off economy system", style=discord.ButtonStyle.blurple, custom_id="on_off_system")
    async def on_off_button_economy_system_callback(self, button, interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id

            check_status = DatabaseCheck.check_bot_settings(guild=guild_id)

            if check_status == None:

                emb = discord.Embed(title=f"Es wurde kein eintrag gefunden {fail_emoji}", 
                    description=f"""Es wurde kein eintrag gefunden deshalb wurde einer für dein server erstellt. 
                    {dot_emoji} Das Economy system wurde auch gleich automatisch eingeschalten.
                    {dot_emoji} Wenn du es deaktivieren möchtest benutzen sie diesen command einfach noch einmal""", color=error_red)
                await interaction.response.edit_message(embed=emb)

            else:

                status, new_status, opposite_status = "", "", ""

                if "on_message"  in check_status[4] or "on_voice"  in check_status[4] or "on_work"  in check_status[4] or "on_all" in check_status[4]:

                    new_status, status = "Eingeschalten", "off"
                    opposite_status = "Ausgeschalten"

                elif check_status[4] == "off":

                    new_status, status = "Ausgeschalten", "on_all"
                    opposite_status = "Eingeschalten"

                DatabaseUpdates._update_status_economy(guild_id=guild_id, status=status)

                emb = discord.Embed(title=f"Das economy system wurde {new_status}", 
                    description=f"""Sie haben das Economy system erfolgreich {new_status}.
                    {dot_emoji} Wenn sie das economy system wieder {opposite_status} wollen benutzen sie diesen command einfach noch einmal {exclamation_mark_emoji}""", color=shiro_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



            
class EconomySystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cd = commands.CooldownMapping.from_cooldown(1, 10.0, commands.BucketType.member)

    def get_ratelimit(self, message: discord.Message):
        bucket = self.cd.get_bucket(message)
        return bucket.update_rate_limit()

    def coin_message(self):
        coins = 5
        return coins

    @commands.Cog.listener()
    async def on_message(self, message):

        if self.get_ratelimit(message):
            return

        if message.author.bot:
            return

        if message.content.startswith("?"):
            return

        # user infos
        guild_id = message.guild.id
        user_id = message.author.id
        guild_name = message.guild.name
        user_name = message.author.name

        economy_system_status = DatabaseStatusCheck._economy_system_status(guild_id=guild_id)
        if economy_system_status == True:
            return
        elif economy_system_status == None:
            DatabaseUpdates._create_bot_settings(guild_id=guild_id)
        else:

            # checks the blacklist
            blacklist_check = DatabaseStatusCheck._economy_system_blacklist_check(guild_id=guild_id, message_check=message)

            if blacklist_check != True:

                user_stats = DatabaseCheck.check_economy_system_stats(guild=guild_id, user=user_id)
                
                if user_stats:

                    money = self.coin_message()

                    money_count = user_stats[2]

                    new_money_count = money_count + money
                    print("money")

                    DatabaseUpdates._update_user_money_economy(guild_id=guild_id, user_id=user_id, money=new_money_count)

                else:

                    DatabaseUpdates._insert_user_stats_economy(guild_id=guild_id, user_id=user_id, user_name=user_name)

    
    @commands.slash_command(name="economy-system-settings", description="Stellen sie das economy system ein!")
    @commands.has_permissions(administrator=True)
    async def economy_system_settings(self, ctx):

        guild_id = ctx.guild.id
        check_settings = DatabaseCheck.check_bot_settings(guild=guild_id)
        
        settings_list = []

        if check_settings[4] != "off":
            status = "**off**"
            settings = f"{arrow_emoji} Nichts denn es ist nicht aktiv!"
        else:
            status = "**on**"

            if "on_all" in check_settings:

                settings = f"""Alles darunter zählt: {dot_emoji} messages\n{dot_emoji} Work commands\n{dot_emoji} voice time"""

            else:

                settings_list.append("message\n") if check_settings[4] == "on_message" else None
                settings_list.append("work commands\n") if check_settings[4] == "on_work" else None
                settings_list.append("voice time\n") if check_settings[4] == "on_voice" else None
                settings_list.append("mini games\n") if check_settings[4] == "on_mini_games" else None
        
            settings = f"{dot_emoji} ".join(settings_list)

        emb = discord.Embed(title="Hir kannst du das economy system einstellen", 
            description=f"""Mit dem on/off button kannst du das economy system aus oder an schalten.
            Mit dem Help button kannst du dir alles erklären lassen wir das economy system funktioniert.""", color=shiro_colour)
        emb.add_field(name="Festlegung der Parameter", value=f"Mit dem Select menü kannst du auswählen wie man Punkte verdient", inline=False)
        emb.add_field(name=f"{help_emoji} Aktueller status:", value=f"""{status} es reagiert auf:
        {settings}""", inline=False)
        await ctx.respond(embed=emb, view=EconomySystemSettings())

    
    @commands.slash_command(name="show-economy-settings")
    async def show_economy_settings(self, ctx):

        guild_id = ctx.guild.id
        check_settings = DatabaseCheck.check_bot_settings(guild=guild_id)
        
        settings_list = []

        if check_settings[4] != "off":
            status = "**off**"
            settings = f"{arrow_emoji} Nichts denn es ist nicht aktiv!"
        else:
            status = "**on**"

            if "on_all" in check_settings:

                settings = f"""Alles darunter zählt: {dot_emoji} messages\n{dot_emoji} Work commands\n{dot_emoji} voice time"""

            else:

                settings_list.append("message\n") if check_settings[4] == "on_message" else None
                settings_list.append("work commands\n") if check_settings[4] == "on_work" else None
                settings_list.append("voice time\n") if check_settings[4] == "on_voice" else None
                settings_list.append("mini games\n") if check_settings[4] == "on_mini_games" else None
        
            settings = f"{dot_emoji} ".join(settings_list)

        emb = discord.Embed(title=f"Hier siehst du alle einstellungen des Economy systems {settings_emoji}", 
            description=f"""{dot_emoji} Wenn du die einstellugen ändern möchtest benutze den {economy_settings} command!""", color=shiro_colour)
        emb.add_field(name="Status:", value=f"Der status des Economy systems ist {status}", inline=False)
        emb.add_field(name="Einstellungen:", value=f"Das economy system reagiert auf:\n{settings}", inline=False)
        await ctx.respond(embed=emb)



#####################################  Blacklist Settings  ##########################################################################


    @commands.slash_command(name="add-channel-economy-blacklist", description="Schliese einen Channel vom economy system aus!")
    @commands.has_permissions(administrator=True)
    async def add_channel_economy_blacklist(self, ctx, channel:Option(Union[discord.VoiceChannel, discord.TextChannel], 
        description="Wählen sie ein channel aus der auf die blacklist gesetzt werden soll!")):

        channel_id = channel.id
        guild_id = ctx.guild.id
        guild_name = ctx.guild.name

        blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, channel=channel_id)

        if blacklist:
            
            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)

            emb = discord.Embed(title=f"Dieser channel ist bereits auf der economy system Blacklist {fail_emoji}", 
                description=f"""Auf der economy system Blacklist befinden sich folgende channels:\n
                {blacklist[0]}
                Wenn du channels von der Blacklist entfernen möchtest führen sie diesen command aus: 
                {remove_blacklist_economy_channel}""", color=error_red)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.set_on_blacklist(guild_id=guild_id, guild_name=guild_name, channel_id=channel_id, table="economy")

            emb = discord.Embed(title=f"Dieser Channel wurde erfolgreich auf die economy system Blacklist gesetzt {succesfully_emoji}", 
                description=f"""Der channel: <#{channel_id}> wurde erfolgreich auf die economy system Blacklist gesetzt. 
                Wenn du in wieder entfernen möchtest benutze diesen command: 
                {remove_blacklist_economy_channel}""", color=shiro_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-channel-economy-blacklist", description="Entferne einen Channel von der Economy system blacklist!")
    @commands.has_permissions(administrator=True)
    async def remove_channel_economy_blacklist(self, ctx, channel:Option(Union[discord.VoiceChannel, discord.TextChannel])):

        channel_id = channel.id
        guild_id = ctx.guild.id

        blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, channel=channel_id)

        if blacklist:

            DatabaseRemoveDatas._remove_economy_system_blacklist(guild_id=guild_id, channel_id=channel_id)

            emb = discord.Embed(title=f"Der channel wurde von der economy system Blacklist entfernt {succesfully_emoji}", 
                description=f"""Der channel wurde erfolgreich von der economy system Blacklist entfernt wenn du in wieder hinzugügen möchtest benutze den: {add_blacklist_economy_channel} command.
                Wenn du sehen willst was noch auf der Blacklist steht dann benutze den: {show_blacklist_economy}""", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)

            emb = discord.Embed(title=f"Dieser Channel ist nicht auf der economy system Blacklist {fail_emoji}", 
                description=f"""Der Channel: <#{channel_id}> ist nicht auf der economy system Blacklist. 
                Die folgenden channels sind auf der Blacklist:\n
                {blacklist[0]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="add-category-economy-blacklist", description="Schliese eine Kategorie von economy system aus!")
    @commands.has_permissions(administrator=True)
    async def add_category_economy_blacklist(self, ctx, category:Option(discord.CategoryChannel)):

        guild_id = ctx.guild.id
        category_id = category.id
        guild_name = ctx.guild.name

        blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, category=category_id)

        if blacklist:
            
            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)
                
            emb = discord.Embed(title=f"Diese Category ist bereits auf der economy system Blacklist {fail_emoji}", 
                description=f"""Auf der economy system Blacklist befinden sich folgende categories:\n
                {blacklist[1]}
                Wenn du categories von der blacklist entfernen möchtest führen sie diesen command aus: 
                {remove_blacklist_economy_category}""", color=error_red)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates.set_on_blacklist(guild_id=guild_id, guild_name=guild_name, category_id=category_id, table="economy")

            emb = discord.Embed(title=f"Diese Category wurde erfolgreich auf die economy system Blacklist gesetzt {succesfully_emoji}", 
                description=f"""Die Category: <#{category_id}> wurde erfolgreich auf die economy system Blacklist gesetzt. 
                Wenn du sie wieder entfernen möchtest benutze diesen command: 
                {remove_blacklist_economy_category}""", color=shiro_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name="remove-category-economyblacklist", description="Entfernt eine category von der economy system blacklist!")
    @commands.has_permissions(administrator=True)
    async def remove_category_economy_blacklist(self, ctx, category:Option(discord.CategoryChannel)):

        guild_id = ctx.guild.id
        category_id = category.id

        blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, category=category_id)

        if blacklist:

            DatabaseRemoveDatas._remove_economy_system_blacklist(guild_id=guild_id, category_id=category_id)

            emb = discord.Embed(title=f"Die Category wurde von der economy system blacklist entfernt {succesfully_emoji}", 
                description=f"""Die Kategorie wurde erfolgreich von der economy system blacklist entfernt wenn du sie wieder hinzugügen möchtest benutze den: {add_blacklist_economy_category} command.
                Wenn du sehen willst was noch auf der Blacklist steht dann benutze den: {show_blacklist_economy} comamnd""", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)

            emb = discord.Embed(title=f"Diese Kategorie ist nicht auf der economy system Blacklist {fail_emoji}", 
                description=f"""Die Kategorie: <#{category_id}> ist nicht auf der economy system Blacklist. 
                Die folgenden Kategorien sind auf der Blacklist:\n
                {blacklist[1]}""", color=error_red)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name="add-role-economy-blacklist")
    @commands.has_permissions(administrator=True)
    async def add_role_economy_blacklist(self, ctx, role:Option(discord.Role, description="Wähle eine rolle aus die du vom economy system auschlisen möchtest")):

        guild_id = ctx.guild.id
        role_id = role.id
        guild_name = ctx.guild.name
        
        blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, role=role_id)

        if blacklist:
            
            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)

            emb = discord.Embed(title=f"Diese rolle ist bereits auf der economy system Blacklist {fail_emoji}", 
                description=f"""Auf der economy system blacklist befinden sich folgende rollen:\n
                {blacklist[2]}
                Wenn du rollen von der blacklist entfernen möchtest führen sie diesen command aus: 
                {remove_blacklist_economy_role}""", color=error_red)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates.set_on_blacklist(guild_id=guild_id, guild_name=guild_name, role_id=role_id, table="economy")

            emb = discord.Embed(title=f"Diese rolle wurde erfolgreich auf die economy system Blacklist gesetzt {succesfully_emoji}", 
                description=f"""Die rolle: <@&{role_id}> wurde erfolgreich auf die economy system Blacklist gesetzt. 
                Wenn du sie wieder entfernen möchtest benutze diesen command: 
                {remove_blacklist_economy_role}""", color=shiro_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-role-economy-blacklist")
    @commands.has_permissions(administrator=True)
    async def remove_role_economy_blacklist(self, ctx, role:Option(discord.Role)):

        guild_id = ctx.guild.id
        role_id = role.id
        
        blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, role=role_id)

        if blacklist:
            
            DatabaseRemoveDatas._remove_economy_system_blacklist(guild_id=guild_id, role_id=role_id)

            emb = discord.Embed(title=f"Die rolle wurde von der economy system blacklist entfernt {succesfully_emoji}", 
                description=f"""Die Rolle wurde erfolgreich von der economy system blacklist entfernt wenn du sie wieder hinzugügen möchtest benutze den: {add_blacklist_economy_role} command.
                Wenn du sehen willst was noch auf der Blacklist steht dann benutze den: {show_blacklist_economy} comamnd""", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)

            emb = discord.Embed(title=f"Diese Rolle ist nicht auf der economy system Blacklist {fail_emoji}", 
                description=f"""Die Rolle: <@&{role_id}> ist nicht auf der economy system Blacklist. 
                Die folgenden Rollen sind auf der Blacklist:\n
                {blacklist[2]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="add-user-economy-blacklist")
    @commands.has_permissions(administrator=True)
    async def add_user_economy_blacklist(self, ctx, user:Option(discord.Member)):

        guild_id = ctx.guild.id
        user_id = user.id
        guild_name = ctx.guild.name
        
        blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, user=user_id)

        if user.bot:
            await ctx.respond(embed=user_bot_emb, view=None)

        else:

            if blacklist:
                
                blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)

                emb = discord.Embed(title=f"Dieser user ist bereits auf der economy system Blacklist {fail_emoji}", 
                    description=f"""Auf der economy system blacklist befinden sich folgende users:
                    {blacklist[3]}
                    Wenn du users von der blacklist entfernen möchtest führen sie diesen command aus: 
                    {remove_blacklist_economy_user}""", color=error_red)
                await ctx.respond(embed=emb)

            else:
                
                DatabaseUpdates.set_on_blacklist(guild_id=guild_id, guild_name=guild_name, user_id=user_id, table="economy")

                emb = discord.Embed(title=f"Dieser user wurde erfolgreich auf die economy system Blacklist gesetzt {succesfully_emoji}", 
                    description=f"""Der user: <@{user_id}> wurde erfolgreich auf die economy system Blacklist gesetzt. 
                    Wenn du ihn wieder entfernen möchtest benutze diesen command: 
                    {remove_blacklist_economy_user}""", color=shiro_colour)
                await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-user-economy-blacklist", description="Streiche einen user von der blacklist!")
    @commands.has_permissions(administrator=True)
    async def remove_user_economy_blacklist(self, ctx, user:Option(discord.Member, description="Wähle einen User den du von der blacklist steichen möchtest!")):

        guild_id = ctx.guild.id 
        user_id = user.id

        blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id, user=user_id)

        if blacklist:
            
            DatabaseRemoveDatas._remove_economy_system_blacklist(guild_id=guild_id, user_id=user_id)

            emb = discord.Embed(title=f"Der user wurde von der economy system blacklist entfernt {succesfully_emoji}", 
                description=f"""Der user wurde erfolgreich von der economy system blacklist entfernt wenn du ihn wieder hinzugügen möchtest benutze den: {add_blacklist_economy_user} command.
                Wenn du sehen willst was noch auf der Blacklist steht dann benutze den: {show_blacklist_economy} comamnd""", color=shiro_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)

            emb = discord.Embed(title=f"Dieser user ist nicht auf der economy system Blacklist {fail_emoji}", 
                description=f"""Der user: <@{user_id}> ist nicht auf der economy system Blacklist. 
                Die folgenden users sind auf der Blacklist:\n
                {blacklist[3]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="reset-economy-blacklist", description="Setze die gesammte blacklist zurück!")
    @commands.has_permissions(administrator=True)
    async def reset_economy_blacklist(self, ctx):
        
        guild_id = ctx.guild.id
        blacklist = DatabaseCheck.check_economy_system_blacklist(guild=guild_id)

        if blacklist:

            emb = discord.Embed(title="Bist du dir sicher das du alles von der economy system Blacklist streichen möchtest?", 
                description=f"""{help_emoji} Mit den Buttuns kannst du deine Entscheidung bestätigen!
                {dot_emoji} Wenn du auf den **Yes button** drückst werden alle Channels, Kategorien, Users und Rollen entgültig von der economy system Blacklist gestrichen.
                {dot_emoji} Wenn du auf den **No button** drückst wird der vorgang abgebrochen.
                {dot_emoji} Der **Shows all elements button** zeigt dir was gerade alles auf der economy system Blacklist steht.""", color=shiro_colour)
            await ctx.respond(embed=emb, view=ResetBlacklistEconomyButton())
        
        else:

            emb = discord.Embed(title=f"Es befindet sich nichts auf der economy system Blacklist {fail_emoji}", 
                description=f"""{dot_emoji} Die economy system blacklist konnte nicht zurück gesetzt werden da auf Ihr nichts gespeichert ist.
                {dot_emoji} Wenn sie etwas auf die Blacklist setzen möchten benutzen sie einen dieser Commands:
                
                {arrow_emoji} {add_blacklist_economy_channel}
                {arrow_emoji} {add_blacklist_economy_category}
                {arrow_emoji} {add_blacklist_economy_role}
                {arrow_emoji} {add_blacklist_economy_user}""", color=shiro_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="show-economy-blacklist", description="Lass dir alles was auf der Blacklist steht anzeigen!")
    async def show_economy_blacklist(self, ctx):

        guild_id = ctx.guild.id

        blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)
        channel, category, role, user = blacklist[0], blacklist[1], blacklist[2], blacklist[3] 

        emb = discord.Embed(title=f"Hier siehst du die Gesamte economy system Blacklist", 
            description=f"""Hier siehst du alles was sich auf der economy system Blacklist befindet:{exclamation_mark_emoji}
            """, color=shiro_colour)
        emb.add_field(name=f"{arrow_emoji} All Channels on the Blacklist", value=f"{channel}", inline=False)
        emb.add_field(name=f"{arrow_emoji} All Categories on the Blacklist", value=f"{category}", inline=False)
        emb.add_field(name=f"{arrow_emoji} All Roles on the Blacklist", value=f"{role}", inline=False)
        emb.add_field(name=f"{arrow_emoji} All Users on the Blacklist", value=f"{user}", inline=False)
        await ctx.respond(embed=emb)



#####################################################  User Settings economy system  ##################################################


    @commands.slash_command(name="give-money")
    @commands.has_permissions(administrator=True)
    async def give_money(self, ctx, user:Option(discord.Member), money:Option(int), ):

        guild_id = ctx.guild.id
        user_id = user.id
        user_name = user.name

        if user.bot:
            await ctx.respond(embed=user_bot_emb, view=None)

        else:

            check_user = DatabaseCheck.check_economy_system_stats(guild=guild_id, user=user_id)

            if check_user:
                
                new_coins = check_user[2] + money

                DatabaseUpdates._update_user_money_economy(guild_id=guild_id, user_id=user_id, money=new_coins)

                emb = discord.Embed(title=f"Du hast {user_name} erfolgreich die coins übergeben {succesfully_emoji}", 
                    description=f"""{dot_emoji} Du hast dem user: <@{user_id}> erfolgreich {money} coins übertagen {dollar_animation_emoji}.
                    {dot_emoji} <@{user_id}> hat ab jetzt {new_coins} coins.
                    {dot_emoji} Wenn du diesen <@{user_id}> seine Coins wieder entfernen möchtest kannst du den\n{remove_money} command nutzen {exclamation_mark_emoji}""", color=shiro_colour)
                await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_economy(guild_id=guild_id, user_id=user_id, user_name=user_name)
                
                emb = discord.Embed(title=f"Der angegebene user wurde nicht gefunden {fail_emoji}", 
                    description=f"""{dot_emoji} Der user konnte nicht gefunden werden deshalb wurde der user: <@{user_id}> nachrtäglich hinzugefügt.
                    {dot_emoji} Der user wurde hinzugefügt und startet mit 0 coins.""", color=error_red)
                await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-money")
    @commands.has_permissions(administrator=True)
    async def remove_money(self, ctx, user:Option(discord.Member), money:(Option(int))):

        guild_id = ctx.guild.id
        user_id = user.id
        user_name = user.name

        if user.bot:
            await ctx.respond(embed=user_bot_emb, view=None)

        else:

            check_user = DatabaseCheck.check_economy_system_stats(guild=guild_id, user=user_id)

            if check_user:

                if check_user[2] < money:

                    emb = discord.Embed(title=f"Der user hat nicht so viel geld {fail_emoji}", 
                        description=f"""Der user hat nicht genug geld.
                        {dot_emoji} Der user: <@{user_id}> hat nur {check_user[2]} coins!
                        {dot_emoji} Wenn du diesen User coins entfernen willst der wert den du entfernen willst kleiner oder gleich mit dem Kontostand des users sein {exclamation_mark_emoji}""", color=error_red)
                    await ctx.respond(embed=emb)

                else:

                    emb = discord.Embed(title=f"Du hast diesen user erfolgreich den angegebenen betrag abgebucht {succesfully_emoji}", 
                        description=f"""{dot_emoji} Du hast den user: <@{user_id}> erfolgreich {money} coin abgebucht {dollar_animation_emoji}.
                        {dot_emoji} Wenn du diesen user wieder coins geben möchtest benutze den:\n{give_money} command {exclamation_mark_emoji}""", color=shiro_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_economy(guild_id=guild_id, user_id=user_id, user_name=user_name)

                emb = discord.Embed(title=f"Der angegebene user wurd nicht gefunden {fail_emoji}",
                    description=f"""{dot_emoji} Der user konnte nicht gefunden werden deshalb wurde der user: <@{user_id}> nachrtäglich hinzugefügt.
                    {dot_emoji} Der user wurde hinzugefügt und startet mit 0 coins.""", color=error_red)
                await ctx.respond(embed=emb)


    @commands.slash_command(name="reset-economy-stats")
    async def reset_economy_stats(self, ctx):
        
        guild_id = ctx.guild.id
        check_user_stats = DatabaseCheck.check_economy_system_stats(guild=guild_id)

        if check_user_stats:

            emb = discord.Embed(title=f"Bist du dir sicher das du alle stats des economy systems zurücksetzen möchtest?", 
                description=f"""{help_emoji} Mit den Buttuns kannst du deine Entscheidung bestätigen!
                {dot_emoji} Wenn du auf den **Yes button** drückst werden alle user stats gelöscht.
                {dot_emoji} Wenn du auf den **No button** drückst wird der vorgang abgebrochen.""", color=shiro_colour)
            await ctx.respond(embed=emb, view=ResetEconomyStatsButton())

        else:

            emb = discord.Embed(title=f"Es wurden keine daten zu diesen Server gefunden {fail_emoji}", 
                description=f"""{dot_emoji} Es wurden keine Daten zu diesen Server gefunden,
                deshalb konnte nichts gelöscht werden. 
                {help_emoji} Daten werden automatisch erstellt sobald nachrichten gesendet werden und das economy system eingeschaltet ist.""", color=error_red)
            await ctx.respond(embed=emb)

    
    @commands.slash_command()
    async def show_points(self, ctx, user:Option(discord.User, description="Wähle einen user dessen werte du ansehen möchtest!")):

        check_stats = DatabaseCheck.check_economy_system_stats(guild=ctx.guild.id, user=user.id)

        emb = discord.Embed(title=f"Hier siehst du alle werte von {user.name} im economy system {dollar_animation_emoji}", 
            description=f"""{dot_emoji} Hiest sihst du alle werte aufgelistet:
            Gesammelte coins: {check_stats[2]}""")
    

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="server-shop")
    async def server_shop(self, ctx):

        emb = discord.Embed(title=f"Hier siehst du den Shop von {ctx.guild.name}")
        await ctx.respond(embed=emb)



def setup(bot): 
    bot.add_cog(EconomySystem(bot))
   
