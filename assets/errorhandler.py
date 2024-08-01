from utils import *

f = Emojis.fail_emoji
class error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error): # Slash Commands

        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(colour=error_red, title=f"Missing authorizations",
                                  description=f"{f} | You do not have authorization to use this command.")
            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        if isinstance(error, commands.TooManyArguments):
            embed = discord.Embed(colour=error_red, title=f"Too many arguments",
                                  description=f"{f} | You have entered too many arguments.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(colour=error_red, title=f"Command Deactivated",
                                  description=f"{f} | This command is currently deactivated.")
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if isinstance(error, commands.MissingAnyRole):
            embed = discord.Embed(colour=error_red, title=f"Missing role",
                                  description=f"{f} | You need a specific role for this.")
            await ctx.respond(embed=embed, ephemeral=True)
            return


        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): # Noramele Commands
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(colour=error_red, title=f"Missing authorizations",
                                  description=f"{f} | You do not have authorization to use this command.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.TooManyArguments):
            embed = discord.Embed(colour=error_red, title=f"Too many arguments",
                                  description=f"{f} | You have entered too many arguments.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(colour=error_red, title=f"Command Deactivated",
                                  description=f"{f} | This command is currently deactivated.")
            await ctx.reply(embed=embed)
            return

        if isinstance(error, commands.MissingAnyRole):
            embed = discord.Embed(colour=error_red, title=f"Missing role",
                                  description=f"{f} | You need a specific role for this.")
            await ctx.reply(embed=embed)
            return

def setup(bot):
    bot.add_cog(error(bot))