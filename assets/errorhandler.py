from ultils.py import *

f = "Emoji"
class error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error): # Slash Commands

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(colour=error_red, title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Ihnen fehlen Berechtigungen zur Verwendung dieses Befehls.")
            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        if isinstance(error, commands.TooManyArguments):
            embed = discord.Embed(colour=error_red, title=f"Zu viele Argumente",
                                  description=f"{f} | Sie haben zu viele Argumente vorgebracht.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(colour=error_red, title=f"Befehl Deaktiviert",
                                  description=f"{f} | Dieser Befehl ist derzeit deaktiviert.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.MissingAnyRole):
            embed = discord.Embed(colour=error_red, title=f"Fehlende Rolle",
                                  description=f"{f} | Dafür benötigen Sie eine bestimmte Rolle.")
            await ctx.respond(embed=embed, ephemeral=True)
            return


        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): # Noramele Commands
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(colour=error_red, title=f"Fehlende Berechtigungen",
                                  description=f"{f} | Ihnen fehlen Berechtigungen zur Verwendung dieses Befehls.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.TooManyArguments):
            embed = discord.Embed(colour=error_red, title=f"Zu viele Argumente",
                                  description=f"{f} | Sie haben zu viele Argumente vorgebracht.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(colour=error_red, title=f"Befehl Deaktiviert",
                                  description=f"{f} | Dieser Befehl ist derzeit deaktiviert.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.MissingAnyRole):
            embed = discord.Embed(colour=error_red, title=f"Fehlende Rolle",
                                  description=f"{f} | Dafür benötigen Sie eine bestimmte Rolle.")
            await ctx.reply(embed=embed)
            return

def setup(bot):
    bot.add_cog(error(bot))