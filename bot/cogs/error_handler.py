import datetime
import logging
from concurrent.futures._base import TimeoutError

import sentry_sdk
import discord
from discord.ext import commands

from bot.bot_client import Bot
from bot.utils.context import Context


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger("commands")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename="commands.log", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        )

        if not self.logger.handlers:
            # Prevent multiple handlers sending duplicate messages
            self.logger.addHandler(handler)

    async def bot_check(self, ctx: Context):
        """This runs at the start of every command"""
        await ctx.typing()
        time = datetime.datetime.utcnow().strftime("%d/%m/%y - %H:%M")
        msg = f"'{ctx.command}' ran by '{ctx.author}' as '{ctx.invoked_with}' at {time}. with '{ctx.message.content}'"
        self.logger.info(msg)
        return True

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandError):
        if hasattr(ctx.command, "on_error"):
            # Don't try to handle the error if the command has a local handler
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
                color=discord.Colour.red(),
            )
            for param, param_type in ctx.command.clean_params.items():
                try:
                    default_name = param_type.default.__name__
                except AttributeError:
                    default_name = param_type.default
                default = (
                    f"(Opcional, Padrão: {default_name})"
                    if default_name != "_empty"
                    else "(Obrigatório)"
                )

                p_type = param_type.annotation.__name__

                if p_type == "str":
                    p_type = "Texto"
                elif p_type == "bool":
                    p_type = "[True, False]"
                elif p_type == "Member":
                    p_type = "Membro"
                elif p_type == "int":
                    p_type = "Número"

                embed.add_field(
                    name=param, value=f"**Tipo:** *{p_type}*\n*{default}*", inline=False
                )
            try:
                await ctx.send(embed=embed)
            except discord.errors.Forbidden:
                await ctx.send("Erro. Permissões insuficientes para enviar um Embed.")
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.DisabledCommand):
            pass
            # await ctx.send("Esse comando está desabilitado.")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("Esse comando não pode ser usado em mensagens privadas.")
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(
                f"Esse comando só pode ser usado em Mensagens Privadas.\n"
                f"Fale comigo aqui: {self.bot.user.mention}"
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.send("Você não pode usar isso.")
        elif isinstance(error, commands.MissingPermissions):
            permissions = [
                f"***{perm.title().replace('_', ' ')}***"
                for perm in error.missing_perms
            ]
            await ctx.send(
                f"Você precisa das seguintes permissões para fazer isso: {', '.join(permissions)}"
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"Ei! Você já usou este comando recentemente. "
                f"Espere mais {error.retry_after:.1f}s para usar novamente"
            )
        elif isinstance(error, commands.BotMissingPermissions):
            permissions = [
                f"***{perm.title().replace('_', ' ')}***"
                for perm in error.missing_perms
            ]
            await ctx.send(
                f"Eu preciso das seguintes permissões para fazer isso: {', '.join(permissions)}"
            )
        elif isinstance(error, commands.errors.CheckFailure):
            pass
        elif isinstance(error, commands.errors.CommandInvokeError) and isinstance(
            error.original, TimeoutError
        ):
            await ctx.send("Ação cancelada. Tempo esgotado.")
        else:
            await ctx.send(
                "Erro inesperado. Os logs desse erro foram enviados para um Dev e em breve será arrumado."
            )

            sentry_sdk.set_user(
                {
                    "id": ctx.author and ctx.author.id,
                    "username": str(ctx.author) if ctx.author else None,
                }
            )

            sentry_sdk.set_context(
                "discord",
                {
                    "guild": ctx.guild,
                    "channel": ctx.channel
                    and (hasattr(ctx.channel, "name") or None)
                    and ctx.channel,
                    "message": ctx.message and ctx.message.content,
                    "message_id": ctx.message and ctx.message.id,
                    "cog": ctx.cog and ctx.cog.qualified_name,
                    "command": ctx.command and ctx.command.name,
                },
            )

            sentry_sdk.capture_exception(error)


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
