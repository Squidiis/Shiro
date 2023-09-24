from Import_file import *
from typing import Union
from check import *

            


#############################################  Reset Buttons economy system  #######################################################


class ResetEconomyStatsButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.blurple, row=1, custom_id="yes_button_stats")
    async def reset_stats_button_economy_yes(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id
            DatabaseRemoveDatas._remove_economy_system_stats(guild_id=guild_id)

            emb = discord.Embed(title=f"Du hast alle stats des economy systems zurückgesetzt {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.arrow_emoji} Alle user datein wurden gelöscht jeder user hat jetzt wieder 0 coins.
                Es werden wieder bei aktivitäht neue enträge erstellt, wenn sie das nicht möchten stellen sie das economy system aus {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)


    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, row=1, custom_id="no_button_stats")
    async def reset_stats_button_economy_no(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Der vorgang wurde erfolgreich abgebrochen {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Das resetten der stats wurde erfolgreich abgebrochen.
                Alle user behalten Ihre stats im economy system.""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)



class ResetBlacklistEconomyButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.blurple, row=1, custom_id="reset_economy_blacklist")
    async def reset_economy_blacklist(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:
            guild_id = interaction.guild.id

            DatabaseUpdates.manage_blacklist(guild_id=guild_id, operation="remove", table="economy")
            emb = discord.Embed(title=f"Die blacklist wurde geresetet {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.arrow_emoji} alle Channel, User, Rollen und Kategorien wurden von der Blacklist entfernt.
                Wenn du wieder Dinge auf die Blacklist setzten möchtest kannst du die Befehle wie zuvor nutzen {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)


    @discord.ui.button(label="No", style=discord.ButtonStyle.blurple, row=1, custom_id="no_reset_economy_blacklist")
    async def no_reset_economy_blacklist(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            emb = discord.Embed(title=f"Der vorgang wurde erfolgreich abgebrochen {Emojis.succesfully_emoji}", 
                description=f"""{Emojis.dot_emoji} Das resetten der blacklist wurde erfolgreich abgebrochen.
                Alle Channels, Rollen, Kategorien und User sind weiterhin auf der blacklist gelistet.
                {Emojis.dot_emoji} Wenn du einzelne elemente von der blacklist steichen möchtest kannst du sie mit den Remove commands streichen lassen {Emojis.exclamation_mark_emoji}""", color=bot_colour)
            await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb)

            
    @discord.ui.button(label="Shows all elements of the blacklist", style=discord.ButtonStyle.blurple, row=2, custom_id="show_economy_blacklist")
    async def show_economy_blacklist(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id
            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=guild_id)
            
            channel, category, role, user = blacklist[0], blacklist[1], blacklist[2], blacklist[3] 

            emb = discord.Embed(title=f"Hier siehst du alle Elemente die auf der Blacklist stehen {Emojis.exclamation_mark_emoji}", 
                description=f"""Hier sind alle Elemente aufgelistet die auf der Blacklist stehen.""", color=bot_colour)
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
    async def economy_system_settings(self, select, interaction:discord.Interaction):
        
        guild_id = interaction.guild.id

        if "cancel" in select.values:
            
            emb = discord.Embed(title="Die einstellung wurde abbgebrochen")
            await interaction.response.send_message(embed=emb, view=None)

        else:

            parameter = []
            _insert_parameter = []
            
            for values in select.values:
                
                if values == "message":
                    parameter.append(f"{Emojis.dot_emoji} message\n")
                    _insert_parameter.append("on_message")

                if values == "work":
                    parameter.append(f"{Emojis.dot_emoji} work\n")
                    _insert_parameter.append("on_work")

                if values == "voice":
                    parameter.append(f"{Emojis.dot_emoji} voice\n")
                    _insert_parameter.append("on_voice")

                if "on_voice" in _insert_parameter and "on_work" in _insert_parameter and "on_message" in _insert_parameter:
                    insert_parameter = "on_all"
                else:
                    insert_parameter = ", ".join(_insert_parameter)

                all_parameter = "".join(parameter)
           
            DatabaseUpdates._update_status_economy(status=insert_parameter, guild_id=guild_id)
                
            emb = discord.Embed(title=f"Das Economy system ist jetzt eingestellt {Emojis.succesfully_emoji}", 
                description=f"""Das Economy system reagiert ab jetzt auf:
                {all_parameter}
                Wenn du diese einstellungen ändern möchtest führen sie diesen command noch einmal aus
                """, color=bot_colour)
            await interaction.response.send_message(embed=emb, ephemeral=True, view=None) 

                
    @discord.ui.button(label="Click my for Help", style=discord.ButtonStyle.green, custom_id="help_button", emoji=Emojis.help_emoji)
    async def help_button_economy_system(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id

            infos = DatabaseCheck.check_economy_settings(guild_id=guild_id)
            
            if infos == None:

                DatabaseUpdates._create_bot_settings(guild_id=guild_id)
                status = "Das economy system ist aktiv und reagiert auf Nachtichten"

            else:

                parameter = []
                if "on_all" in infos[1]:
                    parameter.append(f"{Emojis.dot_emoji} Alles auf Nachrichten, Voice time und Work commands")
                else:
                    if "on_message" in infos[1]:
                        parameter.append(f"{Emojis.dot_emoji} Das schicken von Nachrichten")
                    if "on_voice" in infos[1]:
                        parameter.append(f"{Emojis.dot_emoji} Die zeit die ein user in einen Voice channel vergringt")
                    if "on_work" in infos[1]:
                        parameter.append(f'{Emojis.dot_emoji} Das nutzen von Work Commands')
                    if "off" in infos[1]:
                        parameter.append(f"{Emojis.dot_emoji} Nichts da es deaktiveirt wurde")

                status = f"\n".join(parameter)
            help_embed = discord.Embed(title=f"Hilfe zum einstellen des Economy systems {Emojis.help_emoji}", 
                description=f"""
                Das Economy system ist ein system bei denen akktivitäten mit coins belohnt werden dabei kann man auswählen was belohnt wird: 

                {Emojis.dot_emoji} Nachrichten.
                {Emojis.dot_emoji} Voice zeit.
                {Emojis.dot_emoji} Benutzen von den Fun work commands.

                Es ist auch möglich alles auzuwählen.
                Du kann auch ein Individuelles Genre wählen.
                Auch ist es möglich seine coins im shop auszugeben {Emojis.dollar_animation_emoji},
                für mehr informatinen dazu kannst du unten auf die Knöpfe drücken""", color=bot_colour)
            help_embed.add_field(name=f"Status {Emojis.settings_emoji}", value=f"Das economy system belohnt:\n{status}", inline= False)
            help_embed.add_field(name="Was bringt das economy system", 
                value="Es soll bei der steigerung der server aktivität und beim wacksen deiner Community Helfen", inline=True)
            help_embed.add_field(name="Steuerung", 
                value=f"""Du kannst alles mit dem bot oder vom Dashbourd aus steuern und vieles custom anpassen.
                Mit den Button kannst du das Economy system aus/anschalten""", inline=True)
            help_embed.set_footer(icon_url=bot.user.avatar ,text="This message is only visible to you")
            await interaction.response.send_message(embeds=[help_embed], ephemeral=True)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)

    
    @discord.ui.button(label="On/Off economy system", style=discord.ButtonStyle.blurple, custom_id="on_off_system")
    async def on_off_button_economy_system_callback(self, button, interaction:discord.Interaction):

        if interaction.user.guild_permissions.administrator:

            guild_id = interaction.guild.id

            check_status = DatabaseCheck.check_economy_settings(guild_id=guild_id)

            if check_status == None:

                emb = discord.Embed(title=f"Es wurde kein eintrag gefunden {Emojis.fail_emoji}", 
                    description=f"""Es wurde kein eintrag gefunden deshalb wurde einer für dein server erstellt. 
                    {Emojis.dot_emoji} Das Economy system wurde auch gleich automatisch eingeschalten.
                    {Emojis.dot_emoji} Wenn du es deaktivieren möchtest benutzen sie diesen command einfach noch einmal""", color=error_red)
                await interaction.response.edit_message(embed=emb)

            else:

                status, new_status, opposite_status = "", "", ""

                if "on_message"  in check_status[1] or "on_voice"  in check_status[1] or "on_work"  in check_status[1] or "on_all" in check_status[1]:

                    new_status, status = "Eingeschalten", "off"
                    opposite_status = "Ausgeschalten"

                elif check_status[1] == "off":

                    new_status, status = "Ausgeschalten", "on_all"
                    opposite_status = "Eingeschalten"

                DatabaseUpdates._update_status_economy(guild_id=guild_id, status=status)

                emb = discord.Embed(title=f"Das economy system wurde {new_status}", 
                    description=f"""Sie haben das Economy system erfolgreich {new_status}.
                    {Emojis.dot_emoji} Wenn sie das economy system wieder {opposite_status} wollen benutzen sie diesen command einfach noch einmal {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                await interaction.response.edit_message(embed=emb, view=None)

        else:

            await interaction.response.send_message(embed=no_permissions_emb, ephemeral=True, view=None)



            
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
    async def on_message(self, message:discord.Message):

        if self.get_ratelimit(message):
            return

        if message.author.bot:
            return

        if message.content.startswith("?"):
            return

        economy_settings = DatabaseStatusCheck._economy_system_status(guild_id=message.guild.id, text="check")
        
        if economy_settings == False:
            return
        
        elif economy_settings == None:
            DatabaseUpdates._create_bot_settings(guild_id=message.guild.id)
            return
        
        else:

            # checks the blacklist
            blacklist_check = DatabaseStatusCheck._economy_system_blacklist_check(guild_id=message.guild.id, message_check=message)

            if blacklist_check != True:

                user_stats = DatabaseCheck.check_economy_system_stats(guild_id=message.guild.id, user=message.author.id)
                
                if user_stats:

                    money = self.coin_message()

                    money_count = user_stats[2]

                    new_money_count = money_count + money
                    print("money")

                    DatabaseUpdates._update_user_money_economy(guild_id=message.guild.id, user_id=message.author.id, money=new_money_count)

                else:

                    DatabaseUpdates._insert_user_stats_economy(guild_id=message.guild.id, user_id=message.author.id, user_name=message.guild.name)

    
    @commands.slash_command(name="economy-system-settings", description="Stellen sie das economy system ein!")
    @commands.has_permissions(administrator=True)
    async def economy_system_settings(self, ctx:commands.Context):

        check_settings = DatabaseCheck.check_economy_settings(guild_id=ctx.guild.id)
        
        settings_list = []

        if check_settings[1] != "off":
            status = "**off**"
            settings = f"{Emojis.arrow_emoji} Nichts denn es ist nicht aktiv!"
        else:
            status = "**on**"

            if "on_all" in check_settings:

                settings = f"""Alles darunter zählt: {Emojis.dot_emoji} messages\n{Emojis.dot_emoji} Work commands\n{Emojis.dot_emoji} voice time"""

            else:

                settings_list.append("message\n") if check_settings[1] == "on_message" else None
                settings_list.append("work commands\n") if check_settings[1] == "on_work" else None
                settings_list.append("voice time\n") if check_settings[1] == "on_voice" else None
                settings_list.append("mini games\n") if check_settings[1] == "on_mini_games" else None
        
            settings = f"{Emojis.dot_emoji} ".join(settings_list)

        emb = discord.Embed(title="Hir kannst du das economy system einstellen", 
            description=f"""Mit dem on/off button kannst du das economy system aus oder an schalten.
            Mit dem Help button kannst du dir alles erklären lassen wir das economy system funktioniert.""", color=bot_colour)
        emb.add_field(name="Festlegung der Parameter", value=f"Mit dem Select menü kannst du auswählen wie man Punkte verdient", inline=False)
        emb.add_field(name=f"{Emojis.help_emoji} Aktueller status:", value=f"""{status} es reagiert auf:
        {settings}""", inline=False)
        await ctx.respond(embed=emb, view=EconomySystemSettings())

    
    @commands.slash_command(name="show-economy-settings")
    async def show_economy_settings(self, ctx:commands.Context):

        check_settings = DatabaseCheck.check_economy_settings(guild_id=ctx.guild.id)
        
        settings_list = []

        if check_settings[1] != "off":
            status = "**off**"
            settings = f"{Emojis.arrow_emoji} Nichts denn es ist nicht aktiv!"
        else:
            status = "**on**"

            if "on_all" in check_settings:

                settings = f"""Alles darunter zählt: {Emojis.dot_emoji} messages\n{Emojis.dot_emoji} Work commands\n{Emojis.dot_emoji} voice time"""

            else:

                settings_list.append("message\n") if check_settings[1] == "on_message" else None
                settings_list.append("work commands\n") if check_settings[1] == "on_work" else None
                settings_list.append("voice time\n") if check_settings[1] == "on_voice" else None
                settings_list.append("mini games\n") if check_settings[1] == "on_mini_games" else None
        
            settings = f"{Emojis.dot_emoji} ".join(settings_list)

        emb = discord.Embed(title=f"Hier siehst du alle einstellungen des Economy systems {Emojis.settings_emoji}", 
            description=f"""{Emojis.dot_emoji} Wenn du die einstellugen ändern möchtest benutze den {economy_settings} command!""", color=bot_colour)
        emb.add_field(name="Status:", value=f"Der status des Economy systems ist {status}", inline=False)
        emb.add_field(name="Einstellungen:", value=f"Das economy system reagiert auf:\n{settings}", inline=False)
        await ctx.respond(embed=emb)





#####################################  Blacklist Settings  ##########################################################################


    @commands.slash_command(name="add-channel-economy-blacklist", description="Schliese einen Channel vom economy system aus!")
    @commands.has_permissions(administrator=True)
    async def add_channel_economy_blacklist(self, ctx:commands.Context, channel:Option(Union[discord.VoiceChannel, discord.TextChannel], 
        description="Wählen sie ein channel aus der auf die blacklist gesetzt werden soll!")):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, channel_id=channel.id, table="economy")

        if blacklist:
            
            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"Dieser channel ist bereits auf der economy system Blacklist {Emojis.fail_emoji}", 
                description=f"""Auf der economy system Blacklist befinden sich folgende channels:\n
                {blacklist[0]}
                Wenn du channels von der Blacklist entfernen möchtest führen sie diesen command aus: 
                {remove_blacklist_economy_channel}""", color=error_red)
            await ctx.respond(embed=emb)

        else:

            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", guild_name=ctx.guild.name, channel_id=channel.id, table="economy")

            emb = discord.Embed(title=f"Dieser Channel wurde erfolgreich auf die economy system Blacklist gesetzt {Emojis.succesfully_emoji}", 
                description=f"""Der channel: <#{channel.id}> wurde erfolgreich auf die economy system Blacklist gesetzt. 
                Wenn du in wieder entfernen möchtest benutze diesen command: 
                {remove_blacklist_economy_channel}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-channel-economy-blacklist", description="Entferne einen Channel von der Economy system blacklist!")
    @commands.has_permissions(administrator=True)
    async def remove_channel_economy_blacklist(self, ctx:commands.Context, channel:Option(Union[discord.VoiceChannel, discord.TextChannel])):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, channel=channel.id, table="economy")

        if blacklist:

            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove",channel_id=channel.id, table="economy")

            emb = discord.Embed(title=f"Der channel wurde von der economy system Blacklist entfernt {Emojis.succesfully_emoji}", 
                description=f"""Der channel wurde erfolgreich von der economy system Blacklist entfernt wenn du in wieder hinzugügen möchtest benutze den: {add_blacklist_economy_channel} command.
                Wenn du sehen willst was noch auf der Blacklist steht dann benutze den: {show_blacklist_economy}""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"Dieser Channel ist nicht auf der economy system Blacklist {Emojis.fail_emoji}", 
                description=f"""Der Channel: <#{channel.id}> ist nicht auf der economy system Blacklist. 
                Die folgenden channels sind auf der Blacklist:\n
                {blacklist[0]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="add-category-economy-blacklist", description="Schliese eine Kategorie von economy system aus!")
    @commands.has_permissions(administrator=True)
    async def add_category_economy_blacklist(self, ctx:commands.Context, category:Option(discord.CategoryChannel)):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, category=category.id, table="economy")

        if blacklist:
            
            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=ctx.guild.id)
                
            emb = discord.Embed(title=f"Diese Category ist bereits auf der economy system Blacklist {Emojis.fail_emoji}", 
                description=f"""Auf der economy system Blacklist befinden sich folgende categories:\n
                {blacklist[1]}
                Wenn du categories von der blacklist entfernen möchtest führen sie diesen command aus: 
                {remove_blacklist_economy_category}""", color=error_red)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", guild_name=ctx.guild.name, category_id=category.id, table="economy")

            emb = discord.Embed(title=f"Diese Category wurde erfolgreich auf die economy system Blacklist gesetzt {Emojis.succesfully_emoji}", 
                description=f"""Die Category: <#{category.id}> wurde erfolgreich auf die economy system Blacklist gesetzt. 
                Wenn du sie wieder entfernen möchtest benutze diesen command: 
                {remove_blacklist_economy_category}""", color=bot_colour)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name="remove-category-economyblacklist", description="Entfernt eine category von der economy system blacklist!")
    @commands.has_permissions(administrator=True)
    async def remove_category_economy_blacklist(self, ctx:commands.Context, category:Option(discord.CategoryChannel)):

        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, category=category.id, table="economy")

        if blacklist:

            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", category_id=category.id, table="economy")

            emb = discord.Embed(title=f"Die Category wurde von der economy system blacklist entfernt {Emojis.succesfully_emoji}", 
                description=f"""Die Kategorie wurde erfolgreich von der economy system blacklist entfernt wenn du sie wieder hinzugügen möchtest benutze den: {add_blacklist_economy_category} command.
                Wenn du sehen willst was noch auf der Blacklist steht dann benutze den: {show_blacklist_economy} comamnd""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"Diese Kategorie ist nicht auf der economy system Blacklist {Emojis.fail_emoji}", 
                description=f"""Die Kategorie: <#{category.id}> ist nicht auf der economy system Blacklist. 
                Die folgenden Kategorien sind auf der Blacklist:\n
                {blacklist[1]}""", color=error_red)
            await ctx.respond(embed=emb)

    
    @commands.slash_command(name="add-role-economy-blacklist")
    @commands.has_permissions(administrator=True)
    async def add_role_economy_blacklist(self, ctx:commands.Context, role:Option(discord.Role, description="Wähle eine rolle aus die du vom economy system auschlisen möchtest")):
        
        blacklist = DatabaseCheck.check_blacklist(guild_id=ctx.guild.id, role=role.id, table="economy")

        if blacklist:
            
            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"Diese rolle ist bereits auf der economy system Blacklist {Emojis.fail_emoji}", 
                description=f"""Auf der economy system blacklist befinden sich folgende rollen:\n
                {blacklist[2]}
                Wenn du rollen von der blacklist entfernen möchtest führen sie diesen command aus: 
                {remove_blacklist_economy_role}""", color=error_red)
            await ctx.respond(embed=emb)

        else:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", guild_name=ctx.guild.name, role_id=role.id, table="economy")

            emb = discord.Embed(title=f"Diese rolle wurde erfolgreich auf die economy system Blacklist gesetzt {Emojis.succesfully_emoji}", 
                description=f"""Die rolle: <@&{role.id}> wurde erfolgreich auf die economy system Blacklist gesetzt. 
                Wenn du sie wieder entfernen möchtest benutze diesen command: 
                {remove_blacklist_economy_role}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-role-economy-blacklist")
    @commands.has_permissions(administrator=True)
    async def remove_role_economy_blacklist(self, ctx:commands.Context, role:Option(discord.Role)):
        
        blacklist = DatabaseCheck.check_blacklist(guild=ctx.guild.id, role=role.id, table="economy")

        if blacklist:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", role_id=role.id, table="economy")

            emb = discord.Embed(title=f"Die rolle wurde von der economy system blacklist entfernt {Emojis.succesfully_emoji}", 
                description=f"""Die Rolle wurde erfolgreich von der economy system blacklist entfernt wenn du sie wieder hinzugügen möchtest benutze den: {add_blacklist_economy_role} command.
                Wenn du sehen willst was noch auf der Blacklist steht dann benutze den: {show_blacklist_economy} comamnd""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"Diese Rolle ist nicht auf der economy system Blacklist {Emojis.fail_emoji}", 
                description=f"""Die Rolle: <@&{role.id}> ist nicht auf der economy system Blacklist. 
                Die folgenden Rollen sind auf der Blacklist:\n
                {blacklist[2]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="add-user-economy-blacklist")
    @commands.has_permissions(administrator=True)
    async def add_user_economy_blacklist(self, ctx:commands.Context, user:Option(discord.Member)):

        blacklist = DatabaseCheck.check_blacklist(guild=ctx.guild.id, user=user.id, table="economy")

        if user.bot:
            await ctx.respond(embed=user_bot_emb, view=None)

        else:

            if blacklist:
                
                blacklist = ShowBlacklist._show_blacklist_economy(guild_id=ctx.guild.id)

                emb = discord.Embed(title=f"Dieser user ist bereits auf der economy system Blacklist {Emojis.fail_emoji}", 
                    description=f"""Auf der economy system blacklist befinden sich folgende users:
                    {blacklist[3]}
                    Wenn du users von der blacklist entfernen möchtest führen sie diesen command aus: 
                    {remove_blacklist_economy_user}""", color=error_red)
                await ctx.respond(embed=emb)

            else:
                
                DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="add", guild_name=ctx.guild.name, user_id=user.id, table="economy")

                emb = discord.Embed(title=f"Dieser user wurde erfolgreich auf die economy system Blacklist gesetzt {Emojis.succesfully_emoji}", 
                    description=f"""Der user: <@{user.id}> wurde erfolgreich auf die economy system Blacklist gesetzt. 
                    Wenn du ihn wieder entfernen möchtest benutze diesen command: 
                    {remove_blacklist_economy_user}""", color=bot_colour)
                await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-user-economy-blacklist", description="Streiche einen user von der blacklist!")
    @commands.has_permissions(administrator=True)
    async def remove_user_economy_blacklist(self, ctx:commands.Context, user:Option(discord.Member, description="Wähle einen User den du von der blacklist steichen möchtest!")):

        blacklist = DatabaseCheck.check_blacklist(guild=ctx.guild.id, user=user.id, table="economy")

        if blacklist:
            
            DatabaseUpdates.manage_blacklist(guild_id=ctx.guild.id, operation="remove", user_id=user.id, table="economy")

            emb = discord.Embed(title=f"Der user wurde von der economy system blacklist entfernt {Emojis.succesfully_emoji}", 
                description=f"""Der user wurde erfolgreich von der economy system blacklist entfernt wenn du ihn wieder hinzugügen möchtest benutze den: {add_blacklist_economy_user} command.
                Wenn du sehen willst was noch auf der Blacklist steht dann benutze den: {show_blacklist_economy} comamnd""", color=bot_colour)
            await ctx.respond(embed=emb)

        else:

            blacklist = ShowBlacklist._show_blacklist_economy(guild_id=ctx.guild.id)

            emb = discord.Embed(title=f"Dieser user ist nicht auf der economy system Blacklist {Emojis.fail_emoji}", 
                description=f"""Der user: <@{user.id}> ist nicht auf der economy system Blacklist. 
                Die folgenden users sind auf der Blacklist:\n
                {blacklist[3]}""", color=error_red)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="reset-economy-blacklist", description="Setze die gesammte blacklist zurück!")
    @commands.has_permissions(administrator=True)
    async def reset_economy_blacklist(self, ctx:commands.Context):
        
        blacklist = DatabaseCheck.check_blacklist(guild=ctx.guild.id, table="economy")

        if blacklist:

            emb = discord.Embed(title="Bist du dir sicher das du alles von der economy system Blacklist streichen möchtest?", 
                description=f"""{Emojis.help_emoji} Mit den Buttuns kannst du deine Entscheidung bestätigen!
                {Emojis.dot_emoji} Wenn du auf den **Yes button** drückst werden alle Channels, Kategorien, Users und Rollen entgültig von der economy system Blacklist gestrichen.
                {Emojis.dot_emoji} Wenn du auf den **No button** drückst wird der vorgang abgebrochen.
                {Emojis.dot_emoji} Der **Shows all elements button** zeigt dir was gerade alles auf der economy system Blacklist steht.""", color=bot_colour)
            await ctx.respond(embed=emb, view=ResetBlacklistEconomyButton())
        
        else:

            emb = discord.Embed(title=f"Es befindet sich nichts auf der economy system Blacklist {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} Die economy system blacklist konnte nicht zurück gesetzt werden da auf Ihr nichts gespeichert ist.
                {Emojis.dot_emoji} Wenn sie etwas auf die Blacklist setzen möchten benutzen sie einen dieser Commands:
                
                {Emojis.arrow_emoji} {add_blacklist_economy_channel}
                {Emojis.arrow_emoji} {add_blacklist_economy_category}
                {Emojis.arrow_emoji} {add_blacklist_economy_role}
                {Emojis.arrow_emoji} {add_blacklist_economy_user}""", color=bot_colour)
            await ctx.respond(embed=emb)


    @commands.slash_command(name="show-economy-blacklist", description="Lass dir alles was auf der Blacklist steht anzeigen!")
    async def show_economy_blacklist(self, ctx:commands.Context):

        blacklist = ShowBlacklist._show_blacklist_economy(guild_id=ctx.guild.id)
        channel, category, role, user = blacklist[0], blacklist[1], blacklist[2], blacklist[3] 

        emb = discord.Embed(title=f"Hier siehst du die Gesamte economy system Blacklist", 
            description=f"""Hier siehst du alles was sich auf der economy system Blacklist befindet:{Emojis.exclamation_mark_emoji}
            """, color=bot_colour)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Channels on the Blacklist", value=f"{channel}", inline=False)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Categories on the Blacklist", value=f"{category}", inline=False)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Roles on the Blacklist", value=f"{role}", inline=False)
        emb.add_field(name=f"{Emojis.arrow_emoji} All Users on the Blacklist", value=f"{user}", inline=False)
        await ctx.respond(embed=emb)



#####################################################  User Settings economy system  ##################################################


    @commands.slash_command(name="give-money")
    @commands.has_permissions(administrator=True)
    async def give_money(self, ctx:commands.Context, user:Option(discord.Member), money:Option(int, description="gebe eine menge an coins an die übertragen werden sollen!")):

        if user.bot:
            await ctx.respond(embed=user_bot_emb, view=None)

        else:

            check_user = DatabaseCheck.check_economy_system_stats(guild_id=ctx.guild.id, user=user.id)

            if check_user:
                
                new_coins = check_user[2] + money

                DatabaseUpdates._update_user_money_economy(guild_id=ctx.guild.id, user_id=user.id, money=new_coins)

                emb = discord.Embed(title=f"Du hast {user.name} erfolgreich die coins übergeben {Emojis.succesfully_emoji}", 
                    description=f"""{Emojis.dot_emoji} Du hast dem user: <@{user.id}> erfolgreich {money} coins übertagen {Emojis.dollar_animation_emoji}.
                    {Emojis.dot_emoji} <@{user.id}> hat ab jetzt {new_coins} coins.
                    {Emojis.dot_emoji} Wenn du diesen <@{user.id}> seine Coins wieder entfernen möchtest kannst du den\n{remove_money} command nutzen {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_economy(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)
                
                emb = discord.Embed(title=f"Der angegebene user wurde nicht gefunden {Emojis.fail_emoji}", 
                    description=f"""{Emojis.dot_emoji} Der user konnte nicht gefunden werden deshalb wurde der user: <@{user.id}> nachrtäglich hinzugefügt.
                    {Emojis.dot_emoji} Der user wurde hinzugefügt und startet mit 0 coins.""", color=error_red)
                await ctx.respond(embed=emb)


    @commands.slash_command(name="remove-money")
    @commands.has_permissions(administrator=True)
    async def remove_money(self, ctx:commands.Context, user:Option(discord.Member), money:(Option(int, description="gibt eine menge an coins an die entfernt werden sollen!"))):

        if user.bot:
            await ctx.respond(embed=user_bot_emb, view=None)

        else:

            check_user = DatabaseCheck.check_economy_system_stats(guild_id=ctx.guild.id, user=user.id)

            if check_user:

                if check_user[2] < money:

                    emb = discord.Embed(title=f"Der user hat nicht so viel geld {Emojis.fail_emoji}", 
                        description=f"""Der user hat nicht genug geld.
                        {Emojis.dot_emoji} Der user: <@{user.id}> hat nur {check_user[2]} coins!
                        {Emojis.dot_emoji} Wenn du diesen User coins entfernen willst der wert den du entfernen willst kleiner oder gleich mit dem Kontostand des users sein {Emojis.exclamation_mark_emoji}""", color=error_red)
                    await ctx.respond(embed=emb)

                else:

                    emb = discord.Embed(title=f"Du hast diesen user erfolgreich den angegebenen betrag abgebucht {Emojis.succesfully_emoji}", 
                        description=f"""{Emojis.dot_emoji} Du hast den user: <@{user.id}> erfolgreich {money} coin abgebucht {Emojis.dollar_animation_emoji}.
                        {Emojis.dot_emoji} Wenn du diesen user wieder coins geben möchtest benutze den:\n{give_money} command {Emojis.exclamation_mark_emoji}""", color=bot_colour)
                    await ctx.respond(embed=emb)

            else:

                DatabaseUpdates._insert_user_stats_economy(guild_id=ctx.guild.id, user_id=user.id, user_name=user.name)

                emb = discord.Embed(title=f"Der angegebene user wurd nicht gefunden {Emojis.fail_emoji}",
                    description=f"""{Emojis.dot_emoji} Der user konnte nicht gefunden werden deshalb wurde der user: <@{user.id}> nachrtäglich hinzugefügt.
                    {Emojis.dot_emoji} Der user wurde hinzugefügt und startet mit 0 coins.""", color=error_red)
                await ctx.respond(embed=emb)


    @commands.slash_command(name="reset-economy-stats")
    async def reset_economy_stats(self, ctx:commands.Context):

        check_user_stats = DatabaseCheck.check_economy_system_stats(guild_id=ctx.guild.id)

        if check_user_stats:

            emb = discord.Embed(title=f"Bist du dir sicher das du alle stats des economy systems zurücksetzen möchtest?", 
                description=f"""{Emojis.help_emoji} Mit den Buttuns kannst du deine Entscheidung bestätigen!
                {Emojis.dot_emoji} Wenn du auf den **Yes button** drückst werden alle user stats gelöscht.
                {Emojis.dot_emoji} Wenn du auf den **No button** drückst wird der vorgang abgebrochen.""", color=bot_colour)
            await ctx.respond(embed=emb, view=ResetEconomyStatsButton())

        else:

            emb = discord.Embed(title=f"Es wurden keine daten zu diesen Server gefunden {Emojis.fail_emoji}", 
                description=f"""{Emojis.dot_emoji} Es wurden keine Daten zu diesen Server gefunden,
                deshalb konnte nichts gelöscht werden. 
                {Emojis.help_emoji} Daten werden automatisch erstellt sobald nachrichten gesendet werden und das economy system eingeschaltet ist.""", color=error_red)
            await ctx.respond(embed=emb)

    
    @commands.slash_command()
    async def show_points(self, ctx:commands.Context, user:Option(discord.User, description="Wähle einen user dessen werte du ansehen möchtest!")):

        check_stats = DatabaseCheck.check_economy_system_stats(guild_id=ctx.guild.id, user=user.id)

        emb = discord.Embed(title=f"Hier siehst du alle werte von {user.name} im economy system {Emojis.dollar_animation_emoji}", 
            description=f"""{Emojis.dot_emoji} Hiest sihst du alle werte aufgelistet:
            Gesammelte coins: {check_stats[2]}""")
        await ctx.respond(embed=emb)
    


def setup(bot): 
    bot.add_cog(EconomySystem(bot))
   
