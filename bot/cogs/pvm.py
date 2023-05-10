from discord.ext import commands

from bot.bot_client import Bot


class PvMTools(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def apply_pvm(self, _ctx, aliases=["pvm"]):
        pass


async def setup(bot):
    await bot.add_cog(PvMTools(bot))
