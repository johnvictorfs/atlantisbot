import datetime

from discord.ext import commands
import discord

from .models import Session, RaidsState, Team, PlayerActivities, AdvLogState
from .utils import separator


class Owner:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['admin'])
    async def admin_commands(self, ctx):
        clan_banner = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{self.bot.setting.clan_name}/clanmotif.png"

        embed = discord.Embed(
            title="__Comandos Admin__",
            description="",
            color=discord.Color.blue()
        )
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
            url="http://rsatlantis.com/images/logo.png"
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['timesativos', 'times_ativos'])
    async def running_teams(self, ctx):
        running_teams_embed = discord.Embed(
            title='__Times Ativos__',
            description="",
            color=discord.Color.red()
        )
        session = Session()
        teams = session.query(Team).all()
        if not teams:
            running_teams_embed.add_field(
                name=separator,
                value=f"Nenhum time ativo no momento."
            )
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
    async def check_raids(self, ctx):
        notifications = self.raids_notifications()
        return await ctx.send(f"Notificações de Raids estão {'habilitadas' if notifications else 'desabilitadas'}.")

    @commands.command()
    async def toggle_raids(self, ctx):
        toggle = self.toggle_raids_notifications()
        return await ctx.send(f"Notificações de Raids agora estão {'habilitadas' if toggle else 'desabilitadas'}.")

    @commands.command()
    async def check_advlog(self, ctx):
        messages = self.advlog_messages()
        return await ctx.send(f"Mensagens do Adv log estão {'habilitadas' if messages else 'desabilitadas'}.")

    @commands.command()
    async def toggle_advlog(self, ctx):
        toggle = self.toggle_advlog_messages()
        return await ctx.send(f"Mensagens do Adv log agora estão {'habilitadas' if toggle else 'desabilitadas'}.")

    @commands.command()
    async def status(self, ctx):
        session = Session()
        team_count = session.query(Team).count()
        advlog_count = session.query(PlayerActivities).count()
        session.close()
        embed = discord.Embed(
            title="",
            description="",
            color=discord.Color.blue()
        )
        embed.set_footer(
            text=f"Uptime: {datetime.datetime.utcnow() - self.bot.start_time}"
        )
        embed.set_thumbnail(
            url="http://rsatlantis.com/images/logo.png"
        )
        embed.add_field(
            name="Times ativos",
            value=team_count
        )
        embed.add_field(
            name="Adv Log Entries",
            value=advlog_count
        )
        embed.add_field(
            name="Notificações de Raids",
            value=f"{'Habilitadas' if self.raids_notifications() else 'Desabilitadas'}",
        )
        embed.add_field(
            name="Mensagens de Adv Log",
            value=f"{'Habilitadas' if self.advlog_messages() else 'Desabilitadas'}"
        )

        return await ctx.send(embed=embed)

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
