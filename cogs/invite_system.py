from utils import *


class InviteSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    
    #@commands.Cog.listener()
    #async def on_member_join(member):
    #    if not member.bot:
    #        guild = member.guild
    #        invites = await guild.invites()
            #for invite in invites:
                #if invite.uses > 0:
                    # Speichere die Einladung in der Datenbank
                    # cursor.execute("INSERT INTO invites (inviter_id, invitee_id) VALUES (%s, %s)", (invite.inviter.id, member.id))
                    # db.commit()

    @commands.slash_command(name = "show-invites")
    async def show_invites(self, ctx:discord.ApplicationContext, user:Option(discord.Member)):

        if user is None:

            total_invites = 0
            for invite in await ctx.guild.invites():
                if invite.inviter == ctx.author:
                    total_invites += invite.uses

            emb = discord.Embed(description=f"""## Anzahl an eingeladenen Mitgliedern {ctx.author.name}
                {Emojis.dot_emoji} {f'Du hast {total_invites} user' if total_invites != 0 else 'Du hast noch keine anderen user'} auf den Server {ctx.guild.name} eingeladen.
                {Emojis.help_emoji} Die einladungen werden nur dann gezählt wenn du den einladungs link erstellt hast!""", color=bot_colour)
            
            await ctx.respond(embed=emb)
        else:

            total_invites = 0
            for invite in await ctx.guild.invites():
                if invite.inviter == user:
                    total_invites += invite.uses
            await ctx.respond(f"{user.mention} hat {total_invites} Mitglied{'er' if total_invites != 1 else ''} auf den Server eingeladen.")


    @commands.Cog.listener()
    async def on_member_join(member):

        Image.open()
        print(member)

def setup(bot):
    bot.add_cog(InviteSystem(bot))

