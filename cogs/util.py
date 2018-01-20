from discord.ext import commands
import discord

class Util:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, hidden=True)
    async def role(self, ctx):
        """ Give yourself some color"""
        # Validate subcommand usage
        if ctx.invoked_subcommand is None:
            await self.bot.say(self.print_ih("help"))
        return

    @role.command(pass_context=True)
    async def add(self, ctx, role_name: str, hex_color: str):
        """ Gives author a role with given name and color"""
        member = ctx.message.author
        server = ctx.message.server

        decimal_color = int(hex_color, 16) # Convert from Hex to Decimal
        new_role = await self.bot.create_role(server, name=role_name, colour=discord.Colour(decimal_color), position=0)
        await self.bot.add_roles(member, new_role)

    @role.command(pass_context=True)
    async def remove(self, ctx, role_name: str):
        """ Removes a role from the author"""
        member = ctx.message.author
        server = ctx.message.server

        try:
            role = discord.utils.get(server.roles, name=role_name)
            await self.bot.remove_roles(member, role)
        except Exception:
            pass

def setup(bot):
    bot.add_cog(Util(bot))