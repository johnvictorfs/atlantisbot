from discord.ext import commands

from .utils import has_role


class RsAtlantisCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['atlantisrs'])
    async def rsatlantis(self, ctx):
        if has_role(ctx.author, self.bot.setting.role.get('admin')):
            pass


def setup(bot):
    bot.add_cog(RsAtlantisCommands(bot))
