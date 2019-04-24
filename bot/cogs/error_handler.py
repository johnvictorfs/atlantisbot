import traceback
import datetime
import logging

import discord
from discord.ext import commands

from bot.bot_client import Bot
from bot.cogs.teams import NotTeamOwnerError


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    async def bot_check(self, ctx: commands.Context):
        """This runs at the start of every command"""
        await ctx.trigger_typing()
        time = datetime.datetime.utcnow()
        msg = f"'{ctx.command}' ran by '{ctx.author}' as '{ctx.invoked_with}' at {time}. with '{ctx.message.content}'"
        logging.info(msg)
        print(msg)
        return True

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        # Don't try to handle the error if the command has a local handler
        ctx.command: commands.Command
        if hasattr(ctx.command, 'on_error'):
            return
        arguments_error = [
            commands.MissingRequiredArgument,
            commands.BadArgument,
            commands.TooManyArguments,
        ]
        if any([isinstance(error, arg_error) for arg_error in arguments_error]):
            embed = discord.Embed(
                title=f"Argumentos do comando '{ctx.command}':",
                description="",
                color=discord.Colour.red()
            )
            for param, param_type in ctx.command.clean_params.items():
                try:
                    default_name = param_type.default.__name__
                except AttributeError:
                    default_name = param_type.default
                default = f"(Padrão: {default_name})" if default_name != '_empty' else '(Obrigatório)'

                p_type = param_type.annotation.__name__

                if p_type == 'str':
                    p_type = 'Texto'
                elif p_type == 'bool':
                    p_type = '[True, False]'
                elif p_type == 'Member':
                    p_type = 'Membro'
                elif p_type == 'int':
                    p_type = 'Número'

                embed.add_field(name=param, value=f"**Tipo:** *{p_type}*\n*{default}*", inline=False)
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
            await ctx.send(f"Erro inesperado. Os logs desse erro foram enviados para um Dev e em breve será arrumado.")
            tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            await self.bot.send_logs(error, tb, ctx)


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
