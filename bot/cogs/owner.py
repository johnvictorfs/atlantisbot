import asyncio
import os
import sys
import datetime
import sqlite3

from discord.ext import commands
import discord

from bot.db.models import RaidsState, Team, PlayerActivities, AdvLogState, AmigoSecretoState, AmigoSecretoPerson
from bot.db.db import Session
from bot.utils.tools import separator, plot_table


class Owner:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.is_owner()
    @commands.command()
    async def restart(self, ctx: commands.Context):
        await ctx.send("Restarting bot...")
        if self.bot.setting.mode == 'dev':
            # Heroku will make sure the bot logs back in after getting logged out without needing to do it manually
            os.execv(sys.executable, ['python3'] + sys.argv)
        await self.bot.logout()

    @commands.is_owner()
    @commands.command(aliases=['reload'])
    async def reload_cog(self, ctx: commands.Context, cog: str):
        """Reloads a cog"""
        try:
            self.bot.unload_extension(f'bot.cogs.{cog}')
            self.bot.load_extension(f'bot.cogs.{cog}')
            return await ctx.send(f'Extensão {cog} reiniciada com sucesso.')
        except ModuleNotFoundError:
            return await ctx.send(f"Extensão {cog} não existe.")
        except Exception as e:
            error = f'{cog}:\n {type(e).__name__} : {e}'
            return await ctx.send(f'Erro ao reiniciar extensão {error}')

    @commands.is_owner()
    @commands.command(aliases=['reloadall'])
    async def reload_all_cogs(self, ctx: commands.Context):
        """Reloads all cogs"""
        err1 = await self.bot.unload_all_extensions()
        err2 = await self.bot.load_all_extensions()
        if err1 or err2:
            return await ctx.send('Houve algum erro reiniciando extensões. Verificar os Logs do bot.')
        return await ctx.send('Todas as extensões foram reiniciadas com sucesso.')

    @commands.is_owner()
    @commands.command(aliases=['sendtable'])
    async def send_table(self, ctx: commands.Context, table: str, safe: bool = True):
        if not safe:
            await ctx.send(f"Você tem certeza que deseja enviar uma imagem da tabela '{table}'? (y/N)")

            def check(msg):
                return ctx.author == msg.author

            try:
                message = await self.bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send("Comando cancelado. Tempo expirado.")
            if 'y' not in message.content.lower():
                return await ctx.send("Envio de Tabela cancelada.")
        try:
            plot_table(table, table, safe=safe)
        except IndexError:
            return await ctx.send("Não há nenhuma linha nessa tabela.")
        except sqlite3.OperationalError:
            return await ctx.send("Essa tabela não existe.")
        return await ctx.send(file=discord.File(f'{table}.tmp.png'))

    @commands.command(aliases=['admin'])
    async def admin_commands(self, ctx: commands.Context):
        clan_banner = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{self.bot.setting.clan_name}/clanmotif.png"

        embed = discord.Embed(title="__Comandos Admin__", description="", color=discord.Color.blue())
        embed.add_field(
            name=f"{self.bot.setting.prefix}timesativos",
            value="Ver informações sobre os times ativos no momento",
            inline=False
        )
        embed.add_field(
            name=f"{self.bot.setting.prefix}check_raids",
            value="Verificar se notificações de Raids estão habilitadas ou não",
            inline=False
        )
        embed.add_field(
            name=f"{self.bot.setting.prefix}toggle_raids",
            value="Desativar/Ativar notificações de Raids",
            inline=False
        )
        embed.add_field(
            name=f"{self.bot.setting.prefix}check_advlog",
            value="Verificar se mensagens do Adv. Log estão habilitadas ou não",
            inline=False
        )
        embed.add_field(
            name=f"{self.bot.setting.prefix}toggle_advlog",
            value="Desativar/Ativar mensagens do Adv. Log",
            inline=False
        )
        embed.set_author(
            icon_url=clan_banner,
            name="AtlantisBot"
        )
        embed.set_thumbnail(
            url=self.bot.setting.banner_image
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['timesativos', 'times_ativos'])
    async def running_teams(self, ctx: commands.Context):
        running_teams_embed = discord.Embed(title='__Times Ativos__', description="", color=discord.Color.red())
        session = Session()
        teams = session.query(Team).all()
        if not teams:
            running_teams_embed.add_field(name=separator, value=f"Nenhum time ativo no momento.")
        for team in teams:
            running_teams_embed.add_field(
                name=separator,
                value=f"**Título:** {team.title}\n"
                f"**PK:** {team.id}\n"
                f"**Team ID:** {team.team_id}\n"
                f"**Chat:** <#{team.team_channel_id}>\n"
                f"**Criado por:** <@{team.author_id}>\n"
                f"**Criado em:** {team.created_date}"
            )
        session.close()
        await ctx.send(embed=running_teams_embed)

    @commands.command()
    async def check_raids(self, ctx: commands.Context):
        notifications = self.raids_notifications()
        return await ctx.send(f"Notificações de Raids estão {'habilitadas' if notifications else 'desabilitadas'}.")

    @commands.command()
    async def toggle_raids(self, ctx: commands.Context):
        toggle = self.toggle_raids_notifications()
        return await ctx.send(f"Notificações de Raids agora estão {'habilitadas' if toggle else 'desabilitadas'}.")

    @commands.command()
    async def check_advlog(self, ctx: commands.Context):
        messages = self.advlog_messages()
        return await ctx.send(f"Mensagens do Adv log estão {'habilitadas' if messages else 'desabilitadas'}.")

    @commands.command()
    async def toggle_advlog(self, ctx: commands.Context):
        toggle = self.toggle_advlog_messages()
        return await ctx.send(f"Mensagens do Adv log agora estão {'habilitadas' if toggle else 'desabilitadas'}.")

    @commands.command()
    async def status(self, ctx: commands.Context):
        session = Session()
        team_count = session.query(Team).count()
        advlog_count = session.query(PlayerActivities).count()
        amigosecreto_count = session.query(AmigoSecretoPerson).count()
        raids_notif = f"{'Habilitadas' if self.raids_notifications() else 'Desabilitadas'}"
        advlog = f"{'Habilitadas' if self.advlog_messages() else 'Desabilitadas'}"
        amigo_secreto = f"{'Ativo' if self.secret_santa() else 'Inativo'}"

        session.close()
        embed = discord.Embed(title="", description="", color=discord.Color.blue())

        embed.set_footer(text=f"Uptime: {datetime.datetime.utcnow() - self.bot.start_time}")

        embed.set_thumbnail(url=self.bot.setting.banner_image)

        embed.add_field(name="Times ativos", value=team_count)
        embed.add_field(name="Adv Log Entries", value=advlog_count)
        embed.add_field(name="Notificações de Raids", value=raids_notif)
        embed.add_field(name="Mensagens de Adv Log", value=advlog)
        embed.add_field(name="Amigo Secreto", value=amigo_secreto)
        embed.add_field(name="Amigo Secreto Entries", value=amigosecreto_count)
        return await ctx.send(embed=embed)

    @staticmethod
    def secret_santa():
        session = Session()
        state = session.query(AmigoSecretoState).first()
        if not state:
            state = AmigoSecretoState(activated=False)
            session.add(state)
            session.commit()
        state_ = state.activated
        session.close()
        return state_

    @staticmethod
    def raids_notifications():
        session = Session()
        state = session.query(RaidsState).first()
        if not state:
            state = RaidsState(notifications=True)
            session.add(state)
            session.commit()
        state_ = state.notifications
        session.close()
        return state_

    @staticmethod
    def toggle_raids_notifications():
        session = Session()
        state = session.query(RaidsState).first()
        if not state:
            state = RaidsState(notifications=True)
            session.add(state)
            session.commit()
        state.notifications = not state.notifications
        state_ = state.notifications
        session.commit()
        session.close()
        return state_

    @staticmethod
    def advlog_messages():
        session = Session()
        state = session.query(AdvLogState).first()
        if not state:
            state = AdvLogState(messages=True)
            session.add(state)
            session.commit()
        state_ = state.messages
        session.close()
        return state_

    @staticmethod
    def toggle_advlog_messages():
        session = Session()
        state = session.query(AdvLogState).first()
        if not state:
            state = AdvLogState(messages=True)
            session.add(state)
            session.commit()
        state.messages = not state.messages
        state_ = state.messages
        session.commit()
        session.close()
        return state_


def setup(bot):
    bot.add_cog(Owner(bot))
