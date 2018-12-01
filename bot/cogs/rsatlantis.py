from discord.ext import commands


class RsAtlantisCommands:

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['atlantisrs'])
    async def rsatlantis(self, ctx):
        pass


def setup(bot):
    bot.add_cog(RsAtlantisCommands(bot))
