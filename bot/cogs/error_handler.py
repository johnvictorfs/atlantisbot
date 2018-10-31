# Standard lib imports
import os

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
            day = None
            if ctx.command.qualified_name == 'set_raids_day':
                day = os.environ.get('RAIDS_DAY', 1)
                if day == 1:
                    day = 'ímpares'
                else:
                    day = 'pares'
                return await ctx.send(f"**Use `{PREFIX}set_raids_day` <par|impar>**\n"
                                      f" - Dias atuais: '{day}'")
            if ctx.command.qualified_name == 'clan_user_info':
                if setting.LANGUAGE == 'Portuguese':
                    return await ctx.send(f"**Uso do comando `{PREFIX}claninfo` | `{PREFIX}clanexp`:**\n"
                                          f"\n{PREFIX}claninfo `<nome de jogador>`")
                else:
                    return await ctx.send(f"**Usage of command `{PREFIX}claninfo` | `{PREFIX}clanexp`:**\n"
                                          f"\n{PREFIX}claninfo `<player name>`")
            if ctx.command.qualified_name == 'running_competitions':
                return await ctx.send(f"**Uso do comando `{PREFIX}comp`:**\n"
                                      f"\n{PREFIX}comp `<número da competição> "
                                      f"<número de jogadores (padrão = 10)>`")
            if ctx.command.qualified_name == 'team':
                return await ctx.send(f"** Uso do comando `{PREFIX}team`:**\n"
                                      f"\n{PREFIX}team `<\"Título do Time\">` `<Tamanho do Time>` `<Roles permitidos>(opcional)`\n\n"
                                      f"*`É necessário que o título do Time esteja contido em aspas (\" \") caso ele contenha espaços`*")


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
