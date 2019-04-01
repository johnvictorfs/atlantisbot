from discord.ext import commands


class RsAtlantisCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['atlantisrs'])
    async def rsatlantis(self, ctx: commands.Context):
        pass


def setup(bot):
    bot.add_cog(RsAtlantisCommands(bot))
