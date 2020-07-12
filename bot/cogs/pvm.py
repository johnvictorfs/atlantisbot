from discord.ext import commands

from bot.bot_client import Bot


class PvMTools(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def apply_pvm(aliases=['pvm']):
        pass


def setup(bot):
    bot.add_cog(PvMTools(bot))
