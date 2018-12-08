import traceback
import datetime

import discord
from discord.ext import commands


class CommandErrorHandler:

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def __global_check(ctx: commands.Context):
        """This runs at the start of every command"""
        await ctx.trigger_typing()
        time = datetime.datetime.utcnow()
        print(f"'{ctx.command}' ran by '{ctx.author}' as '{ctx.invoked_with}' at {time}. with '{ctx.message.content}'")
        return True

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        prefix = self.bot.setting.prefix
        arguments_error = [
            commands.MissingRequiredArgument,
            commands.BadArgument,
            commands.TooManyArguments,
        ]
        command = None
        arguments = None
        if any([isinstance(error, arg_error) for arg_error in arguments_error]):
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
            try:
                await ctx.send(embed=embed)
            except discord.errors.Forbidden:
                await ctx.send("Erro. Permissões insuficientes para enviar um Embed.")
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("Esse comando está desabilitado.")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("Esse comando não pode ser usado em mensagens privadas.")
        elif isinstance(error, commands.NotOwner):
            await ctx.send("Você não pode usar isso.")
        elif isinstance(error, commands.MissingPermissions):
            permissions = [f"***{perm.title().replace('_', ' ')}***" for perm in error.missing_perms]
            await ctx.send(f"Você precisa das seguintes permissões para fazer isso: {', '.join(permissions)}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"Ei! Você já usou este comando recentemente. "
                f"Espere mais {error.retry_after:.1f}s para usar novamente"
            )
        elif isinstance(error, commands.BotMissingPermissions):
            permissions = [f"***{perm.title().replace('_', ' ')}***" for perm in error.missing_perms]
            await ctx.send(f"Eu preciso das seguintes permissões para fazer isso: {', '.join(permissions)}")
        elif isinstance(error, commands.errors.CheckFailure):
            await ctx.send(f"Você não tem permissão para fazer isso.")
        else:
            tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            await self.bot.send_logs(error, tb, ctx)
            await ctx.send(f"Erro inesperado. Os logs desse erro foram enviados para um Dev.")


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
