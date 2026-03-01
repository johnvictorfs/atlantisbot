import asyncio
import os
import io
import re
import sys
import datetime
import inspect
import traceback
import textwrap
import subprocess
from typing import Set, List, Tuple
from contextlib import redirect_stdout
from sentry_sdk import capture_exception

import discord
from discord import app_commands
from discord.ext import commands
from atlantisbot_api.models import (
    AmigoSecretoState,
    RaidsState,
    AmigoSecretoPerson,
    Team,
    PlayerActivities,
    AdvLogState,
    DisabledCommand,
)

from bot.bot_client import Bot
from bot.utils.tools import separator, has_any_role
from bot.utils.context import Context
from bot.utils.checks import is_pedim_or_nriver


class SpamConfirmView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id
        self.confirmed: bool | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id

    @discord.ui.button(label="Sim, enviar para todos", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        self.stop()
        await interaction.response.edit_message(content="Cancelado.", view=None)


class Admin(commands.Cog):
    _GIT_PULL_REGEX = re.compile(r"\s*(?P<filename>.+?)\s*\|\s*[0-9]+\s*[+-]+")

    def __init__(self, bot: Bot):
        self.bot = bot
        self._last_result = None
        self.sessions: Set[int] = set()

    async def cog_check(self, ctx: Context):
        """
        Checks if the User running the command is either an Admin or the Bot's Owner
        """
        roles = ["coord_discord", "org_discord", "adm_discord"]
        roles_ = [self.bot.setting.role.get(role) for role in roles]
        is_owner = await self.bot.is_owner(ctx.author)
        return is_owner or has_any_role(ctx.author, *roles_)

    @commands.is_owner()
    @commands.command()
    async def load(self, ctx: Context, *, module: str):
        """Loads a module."""
        try:
            self.bot.load_extension(f"bot.cogs.{module}")
            return await ctx.send(f"Extensão {module} iniciada com sucesso.")
        except ModuleNotFoundError:
            return await ctx.send(f"Extensão {module} não existe.")
        except Exception as e:
            return await ctx.send(
                f"Erro ao iniciar extensão {module}:\n {type(e).__name__} : {e}"
            )

    @commands.group(name="reload", hidden=True, invoke_without_command=True)
    async def _reload(self, ctx: Context, *, module: str):
        """Reloads a module."""
        try:
            self.bot.reload_extension(f"bot.cogs.{module}")
            return await ctx.send(f"Extensão {module} reiniciada com sucesso.")
        except ModuleNotFoundError:
            return await ctx.send(f"Extensão {module} não existe.")
        except Exception as e:
            return await ctx.send(
                f"Erro ao reiniciar extensão {module}:\n {type(e).__name__} : {e}"
            )

    @commands.is_owner()
    @_reload.command(name="all", hidden=True)
    async def _reload_all(self, ctx: Context):
        """Reloads all modules, while pulling from git."""
        try:
            async with ctx.typing():
                stdout, stderr = await self.run_process("git pull")

            # progress and stuff is redirected to stderr in git pull
            # however, things like "fast forward" and files
            # along with the text "already up-to-date" are in stdout

            if stdout:
                self.bot.logger.info(f"[Reload all] Stdout: {stdout}")
            if stderr:
                self.bot.logger.info(f"[Reload all] Stderr: {stderr}")
                await ctx.send(f"Erro ao atualizar:\n{stderr}")

            if stdout.startswith("Already up to date."):
                return await ctx.send(
                    "Não há mudanças para serem atualizadas da origin."
                )

            modules = self.find_modules_from_git(stdout)

            self.bot.logger.info(f"[Reload all] Modules: {modules}")

            if not modules:
                return await ctx.send("Não há nenhuma cog a ser atualizada.")

            mods_text = "\n".join(
                f"{index}. `{module}`"
                for index, (_, module) in enumerate(modules, start=1)
            )
            prompt_text = (
                f"Isso vai atualizar as seguinte cogs, tem certeza?\n{mods_text}"
            )

            confirm = await ctx.prompt(prompt_text)
            if not confirm:
                return await ctx.send("Abortando.")

            statuses = []
            for is_submodule, module in modules:
                if is_submodule:
                    try:
                        try:
                            await self.bot.reload_extension(module)
                        except commands.ExtensionNotLoaded:
                            await self.bot.load_extension(module)
                    except Exception:
                        statuses.append((ctx.tick(False), module))
                    else:
                        statuses.append((ctx.tick(True), module))
                else:
                    try:
                        await self.reload_or_load_extension(module)
                    except commands.ExtensionError:
                        statuses.append((ctx.tick(False), module))
                    else:
                        statuses.append((ctx.tick(True), module))

            await ctx.send(
                "\n".join(f"{status} `{module}`" for status, module in statuses)
            )
        except Exception as e:
            capture_exception(e)

    async def reload_or_load_extension(self, module: str):
        try:
            await self.bot.reload_extension(module)
        except commands.ExtensionNotLoaded:
            await self.bot.load_extension(module)

    def find_modules_from_git(self, output: str) -> List[Tuple[bool, str]]:
        files = self._GIT_PULL_REGEX.findall(output)
        ret = []
        for file in files:
            root, ext = os.path.splitext(file)
            if ext != ".py":
                continue

            if root.startswith("bot/cogs/"):
                ret.append((root.count("/") - 1, root.replace("/", ".")))

        ret.sort(reverse=True)
        return ret

    async def run_process(self, command):
        try:
            process = await asyncio.create_subprocess_shell(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    @commands.is_owner()
    @commands.command()
    async def restart(self, ctx: Context):
        await ctx.author.send("Reiniciando bot...")
        if self.bot.setting.mode == "dev":
            os.execv(sys.executable, ["python3"] + sys.argv)

        with open("restart_atl_bot.log", "w+") as f:
            f.write("1")

        await self.bot.close()
        sys.exit(0)

    @commands.is_owner()
    @commands.command(aliases=["reloadall"])
    async def reload_all_cogs(self, ctx: Context):
        """Reloads all cogs"""
        err = await self.bot.reload_all_extensions()
        if err:
            return await ctx.send(
                "Houve algum erro reiniciando extensões. Verificar os Logs do bot."
            )
        return await ctx.send("Todas as extensões foram reiniciadas com sucesso.")

    @commands.is_owner()
    @commands.command()
    async def disable(self, ctx: Context, command_name: str):
        """Disables a command"""
        command = self.bot.get_command(command_name)
        if not command:
            return await ctx.send(f"O comando {command_name} não existe.")
        if not command.enabled:
            return await ctx.send(f"O comando {command_name} já está desabilitado.")

        command.enabled = False
        disabled_command = DisabledCommand(name=command_name)
        disabled_command.save()
        return await ctx.send(f"Comando {command_name} desabilitado com sucesso.")

    @commands.is_owner()
    @commands.command()
    async def enable(self, ctx: Context, command_name: str):
        """Enables a command"""
        command = self.bot.get_command(command_name)
        if not command:
            return await ctx.send(f"O comando {command_name} não existe.")
        if command.enabled:
            return await ctx.send(f"O comando {command_name} já está habilitado.")

        disabled_command = DisabledCommand.objects.filter(name=command_name).first()
        disabled_command.delete()
        command.enabled = True
        return await ctx.send(f"Comando {command_name} habilitado com sucesso.")

    @staticmethod
    def cleanup_code(content: str) -> str:
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True, name="eval")
    async def _eval(self, ctx, *, body: str):
        """
        https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py#L216-L261
        Evaluates code in a message
        """

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except Exception:
                pass

            if ret is None:
                if value:
                    await ctx.send(f"```py\n{value}\n```")
            else:
                self._last_result = ret
                await ctx.send(f"```py\n{value}{ret}\n```")

    @staticmethod
    def get_syntax_error(e):
        if e.text is None:
            return f"```py\n{e.__class__.__name__}: {e}\n```"
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def repl(self, ctx):
        """Launches an interactive REPL session."""
        variables = {
            "ctx": ctx,
            "bot": self.bot,
            "message": ctx.message,
            "guild": ctx.guild,
            "channel": ctx.channel,
            "author": ctx.author,
            "_": None,
        }

        if ctx.channel.id in self.sessions:
            await ctx.send(
                "Already running a REPL session in this channel. Exit it with `quit`."
            )
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send("Enter code to execute or evaluate. `exit()` or `quit` to exit.")

        def check(m):
            return (
                m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id
                and m.content.startswith("`")
            )

        while True:
            try:
                response = await self.bot.wait_for(
                    "message", check=check, timeout=10.0 * 60.0
                )
            except asyncio.TimeoutError:
                await ctx.send("Exiting REPL session.")
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in ("quit", "exit", "exit()"):
                await ctx.send("Exiting.")
                self.sessions.remove(ctx.channel.id)
                return
            code = None
            executor = exec
            if cleaned.count("\n") == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, "<repl session>", "eval")
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, "<repl session>", "exec")
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue

            variables["message"] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception:
                value = stdout.getvalue()
                fmt = f"```py\n{value}{traceback.format_exc()}\n```"
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f"```py\n{value}{result}\n```"
                    variables["_"] = result
                elif value:
                    fmt = f"```py\n{value}\n```"

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await ctx.send("Content too big to be printed.")
                    else:
                        await ctx.send(fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await ctx.send(f"Unexpected error: `{e}`")

    @commands.command(aliases=["admin"])
    async def admin_commands(self, ctx: Context):
        clan_banner = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{self.bot.setting.clan_name}/clanmotif.png"

        embed = discord.Embed(
            title="__Comandos Admin__", description="", color=discord.Color.blue()
        )
        prefix = self.bot.setting.prefix

        embed.add_field(
            name=f"{prefix}times",
            value="Ver informações sobre os times ativos no momento",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}check_raids",
            value="Verificar se notificações de Raids estão habilitadas ou não",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}toggle_raids",
            value="Desativar/Ativar notificações de Raids",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}check_advlog",
            value="Verificar se mensagens do Adv. Log estão habilitadas ou não",
            inline=False,
        )
        embed.add_field(
            name=f"{prefix}toggle_advlog",
            value="Desativar/Ativar mensagens do Adv. Log",
            inline=False,
        )
        embed.set_author(icon_url=clan_banner, name="AtlantisBot")
        embed.set_thumbnail(url=self.bot.setting.banner_image)
        await ctx.send(embed=embed)

    @commands.command(aliases=["times", "times_ativos"])
    async def running_teams(self, ctx: Context):
        running_teams_embed = discord.Embed(
            title="__Times Ativos__", description="", color=discord.Color.red()
        )

        teams = Team.objects.all()
        if not teams:
            running_teams_embed.add_field(
                name=separator, value="Nenhum time ativo no momento."
            )
        for team in teams:
            running_teams_embed.add_field(
                name=separator,
                value=f"**Título:** {team.title}\n"
                f"**PK:** {team.id}\n"
                f"**Team ID:** {team.team_id}\n"
                f"**Chat:** <#{team.team_channel_id}>\n"
                f"**Criado por:** <@{team.author_id}>\n"
                f"**Criado em:** {team.created_date}",
            )
        await ctx.send(embed=running_teams_embed)

    @commands.command()
    async def check_raids(self, ctx: Context):
        notifications = self.raids_notifications()
        return await ctx.send(
            f"Notificações de Raids estão {'habilitadas' if notifications else 'desabilitadas'}."
        )

    @commands.command()
    async def toggle_raids(self, ctx: Context):
        toggle = self.toggle_raids_notifications()
        return await ctx.send(
            f"Notificações de Raids agora estão {'habilitadas' if toggle else 'desabilitadas'}."
        )

    @commands.command()
    async def check_advlog(self, ctx: Context):
        messages = self.advlog_messages()
        return await ctx.send(
            f"Mensagens do Adv log estão {'habilitadas' if messages else 'desabilitadas'}."
        )

    @commands.command()
    async def toggle_advlog(self, ctx: Context):
        toggle = self.toggle_advlog_messages()
        return await ctx.send(
            f"Mensagens do Adv log agora estão {'habilitadas' if toggle else 'desabilitadas'}."
        )

    @commands.command()
    async def status(self, ctx: Context):
        team_count = Team.objects.count()
        advlog_count = PlayerActivities.objects.count()
        amigosecreto_count = AmigoSecretoPerson.objects.all().count()
        raids_notif = (
            f"{'Habilitadas' if self.raids_notifications() else 'Desabilitadas'}"
        )
        advlog = f"{'Habilitadas' if self.advlog_messages() else 'Desabilitadas'}"
        amigo_secreto = f"{'Ativo' if self.secret_santa() else 'Inativo'}"
        embed = discord.Embed(title="", description="", color=discord.Color.blue())

        embed.set_footer(
            text=f"Uptime: {datetime.datetime.utcnow() - self.bot.start_time}"
        )

        embed.set_thumbnail(url=self.bot.setting.banner_image)

        embed.add_field(name="Times ativos", value=team_count)
        embed.add_field(name="Adv Log Entries", value=advlog_count)
        embed.add_field(name="Notificações de Raids", value=raids_notif)
        embed.add_field(name="Mensagens de Adv Log", value=advlog)
        embed.add_field(name="Amigo Secreto", value=amigo_secreto)
        embed.add_field(name="Amigo Secreto Entries", value=amigosecreto_count)
        return await ctx.send(embed=embed)

    @staticmethod
    def secret_santa() -> bool:
        return AmigoSecretoState.object().activated

    @staticmethod
    def raids_notifications() -> bool:
        return RaidsState.object().notifications

    @staticmethod
    def toggle_raids_notifications() -> bool:
        current = RaidsState.object()
        current.toggle()

        return current.notifications

    @staticmethod
    def advlog_messages() -> bool:
        state = AdvLogState.object()
        return state.active

    @staticmethod
    def toggle_advlog_messages():
        state = AdvLogState.object()

        state.active = not state.active
        state.save()
        return state.active

    @commands.is_owner()
    @commands.command(hidden=True)
    async def sync(self, ctx: Context):
        """Syncs slash commands to Discord."""
        await self.bot.tree.sync()
        await ctx.send("Slash commands sincronizados com sucesso.")

    @app_commands.check(is_pedim_or_nriver)
    @app_commands.command(name="atl-spam", description="Envia uma mensagem no privado para todos os membros do servidor")
    async def atl_spam(
        self,
        interaction: discord.Interaction,
        message: str,
        image1: discord.Attachment | None = None,
        image2: discord.Attachment | None = None,
        image3: discord.Attachment | None = None,
        image4: discord.Attachment | None = None,
        image5: discord.Attachment | None = None,
    ):
        attachments = [a for a in [image1, image2, image3, image4, image5] if a is not None]
        images_data: list[tuple[bytes, str]] = [(await a.read(), a.filename) for a in attachments]

        def make_files() -> list[discord.File]:
            return [discord.File(io.BytesIO(data), filename=name) for data, name in images_data]

        try:
            send_kwargs = {"files": make_files()} if images_data else {}
            await interaction.user.send(f"**[TESTE - Pré-visualização da mensagem]**\n\n{message}", **send_kwargs)
        except discord.Forbidden:
            return await interaction.response.send_message(
                "Não foi possível enviar uma mensagem de teste para você. Verifique se suas DMs estão abertas.",
                ephemeral=True,
            )

        view = SpamConfirmView(interaction.user.id)
        await interaction.response.send_message(
            "Mensagem de teste enviada no seu privado. Deseja enviá-la para **todos os membros** do servidor?",
            view=view,
            ephemeral=True,
        )

        await view.wait()

        if not view.confirmed:
            if view.confirmed is None:
                await interaction.edit_original_response(content="Tempo esgotado. Envio cancelado.", view=None)
            return

        guild = self.bot.get_guild(self.bot.setting.server_id)
        if not guild:
            return await interaction.edit_original_response(content="Servidor não encontrado.", view=None)

        await interaction.edit_original_response(content="Enviando mensagens...", view=None)

        sent = []
        errs = []
        for m in guild.members:
            if m.bot:
                continue
            try:
                send_kwargs = {"files": make_files()} if images_data else {}
                await m.send(message, **send_kwargs)
                sent.append(m.id)
            except Exception as e:
                await interaction.user.send(f"Erro {m.id} {m.name}: {e}")
                errs.append(m.id)

        await interaction.user.send(f"Concluído. Enviado: {len(sent)}. Erros: {len(errs)}.")
        await interaction.edit_original_response(
            content=f"Concluído! Enviado para {len(sent)} membros. Erros: {len(errs)}.",
            view=None,
        )

    @atl_spam.error
    async def atl_spam_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Admin(bot))
