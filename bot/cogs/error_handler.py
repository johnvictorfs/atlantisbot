import discord
from discord.ext import commands


class CommandErrorHandler:

    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        prefix = self.bot.setting.prefix
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            footer = None
            if ctx.command.qualified_name == 'clan_user_info':
                command = "claninfo"
                arguments = f"`<nome de jogador>`"
            if ctx.command.qualified_name == 'running_competitions':
                command = "comp"
                arguments = f"`<número da competição>` `(número de jogadores|10)`"
            if ctx.command.qualified_name == 'team':
                command = "team"
                arguments = f"<\"Título\"> `<Tamanho>` `(Chat para presenças|Chat atual) (Role Requisito)`"
                footer = "É necessário que o título do Time esteja contido em aspas (\" \") caso ele contenha espaços"
            if ctx.command.qualified_name == 'delteam':
                command = "del"
                arguments = f"<ID do Time (número)>"
            embed = discord.Embed(
                title=f"Uso do comando '{command}'",
                description=f"`<argumento>` : Obrigatório\n`(argumento|padrão)` : Opcional\n\n"
                            f"{prefix}{command} {arguments}\n",
                color=discord.Colour.blue()
            )
            if footer:
                embed.set_footer(
                    text=footer
                )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
