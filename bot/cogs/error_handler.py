# Non-Standard lib imports
from discord.ext import commands

# Local imports
import definesettings as setting

PREFIX = setting.PREFIX


class CommandErrorHandler:

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'clan_user_info':
                if setting.LANGUAGE == 'Portuguese':
                    return await ctx.send(f"**Uso do comando `{PREFIX}claninfo` | `{PREFIX}clanexp`:**\n"
                                          f"\n{PREFIX}claninfo `<nome de jogador>`")
                else:
                    return await ctx.send(f"**Usage of command `{PREFIX}claninfo` | `{PREFIX}clanexp`:**\n"
                                          f"\n{PREFIX}claninfo `<player name>`")


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))