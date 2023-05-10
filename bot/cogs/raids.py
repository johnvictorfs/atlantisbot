import datetime
import traceback
import sys

from discord.ext import tasks, commands
import discord
import asyncio

from bot.bot_client import Bot
from bot.utils.teams import delete_team
from bot.utils.tools import separator
from bot.utils.context import Context

from atlantisbot_api.models import RaidsState, Team


def time_till_raids(start_date) -> int:
    """Calculates the time between now and the next raids in seconds, assuming raids occur every 2 days"""
    now = datetime.datetime.utcnow()
    difference = start_date - now
    if (now - start_date).days % 2 == 0:
        # Add a day to the difference in case it has been an even number of days between start_date and now
        return difference.seconds + (24 * 60 * 60)
    return difference.seconds


class RaidsTasks(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.update_next_raids.start()
        self.raids_teams.start()

    def cog_unload(self):
        self.update_next_raids.cancel()
        self.raids_teams.cancel()

    # noinspection PyCallingNonCallable
    @tasks.loop(seconds=15)
    async def raids_teams(self) -> None:
        """Starts a Raids Team every 2 days 1 hour before midnight UTC (RuneScape's Reset Time)"""

        if "testraid" in sys.argv:
            try:
                await self.start_raids_team()
                await asyncio.sleep(60 * 10)
            except Exception as e:
                tb = traceback.format_exc()
                await self.bot.send_logs(e, tb)
        else:
            seconds_till_raids = time_till_raids(self.bot.setting.raids_start_date)
            raids_diff = datetime.timedelta(seconds=seconds_till_raids)
            print(
                f"Next Raids in: {raids_diff.days} "
                f"Days, {raids_diff.seconds // 3600} "
                f"Hours, {(raids_diff.seconds // 60) % 60} "
                f"Minutes"
            )
            await asyncio.sleep(seconds_till_raids)
            if self.raids_notifications():
                try:
                    await self.start_raids_team()
                except Exception as e:
                    tb = traceback.format_exc()
                    await self.bot.send_logs(e, tb)

    @raids_teams.before_loop
    async def before_raids_teams(self):
        await self.bot.wait_until_ready()

    # noinspection PyCallingNonCallable
    @tasks.loop(seconds=30)
    async def update_next_raids(self) -> None:
        """Updates the message with the time until the next raids in the #raids channel"""

        await self.bot.wait_until_ready()

        if self.bot.setting.mode == "dev":
            return

        try:
            seconds_till_raids = time_till_raids(self.bot.setting.raids_start_date)
            raids_diff = datetime.timedelta(seconds=seconds_till_raids)
            days = raids_diff.days
            hours = raids_diff.seconds // 3600
            minutes = (raids_diff.seconds // 60) % 60

            msg_url = "https://discordapp.com/channels/321012107942428673/393104367471034369/666257577256026123"

            # Check if Raids notifications are currently active or not
            state = RaidsState.object()
            raids_active = state.notifications

            text = (
                f"Próxima notificação de Raids em: **{days} Dia{'s' if days > 1 else ''}, "
                f"{hours} Hora{'s' if hours > 1 else ''} e "
                f"{minutes} Minuto{'s' if minutes > 1 else ''}**.\n\n"
                f"• [Clique aqui para saber como participar]({msg_url})"
            )

            if not raids_active:
                text = (
                    f"• **Notificações de Raids estão atualmente desabilitadas.**"
                    f"\n\n• [Clique aqui para saber como participar]({msg_url})"
                )

            embed = discord.Embed(
                title="", description=text, color=discord.Color.blue()
            )

            channel: discord.TextChannel = self.bot.get_channel(
                self.bot.setting.chat.get("raids")
            )

            state = RaidsState.object()

            if state:
                if state.time_to_next_message:
                    message_id = int(state.time_to_next_message)
                else:
                    sent = await channel.send(content=None, embed=embed)
                    state.time_to_next_message = str(sent.id)
                    message_id = sent.id
                    state.save()
            try:
                message: discord.Message = await channel.fetch_message(message_id)
                await message.edit(content=None, embed=embed)
            except discord.errors.NotFound:
                sent = await channel.send(content=None, embed=embed)
                state.time_to_next_message = str(sent.id)
                state.save()
            await asyncio.sleep(1)
        except Exception as e:
            tb = traceback.format_exc()
            await self.bot.send_logs(e, tb)

    @update_next_raids.before_loop
    async def before_update_next_raids(self):
        await self.bot.wait_until_ready()

    @staticmethod
    def raids_notifications() -> bool:
        """Checks if raids notifications are turned on or off in the bot settings"""
        state = RaidsState.object()
        return state.notifications

    async def start_raids_team(self) -> None:
        """Starts a Raids Team, the owner of the team is the Bot itself"""
        old_team = Team.objects.filter(team_id="raids").first()
        if old_team:
            await delete_team(old_team, self.bot)

        if self.bot.setting.mode == "prod":
            invite_channel_id = self.bot.setting.chat.get("raids_chat")
            team_channel_id = self.bot.setting.chat.get("raids")
        else:
            invite_channel_id = 505240135390986262
            team_channel_id = 505240114662998027

        invite_channel = self.bot.get_channel(invite_channel_id)
        team_channel = self.bot.get_channel(team_channel_id)

        presence = f"Marque presença no <#{invite_channel_id}>\nCriador: {self.bot.user.mention}"
        description = f"Requisito: <@&{self.bot.setting.role.get('raids')}>\n{presence}"
        invite_embed = discord.Embed(
            title="Marque presença para 'Raids' (10 pessoas)",
            description=f"{separator}\n\n"
            f"Requisito: <@&{self.bot.setting.role.get('raids')}>\n"
            f"Time: {team_channel.mention}\n"
            f"Criador: {self.bot.user.mention}\n\n"
            f"`in raids`: Marcar presença\n"
            f"`out raids`: Retirar presença",
        )
        team_embed = discord.Embed(
            title="__Raids__ - 0/10",
            description=description,
            color=discord.Color.purple(),
        )
        footer = (
            f"Digite '{self.bot.setting.prefix}del raids' "
            f"para excluir o time. (Criador do time ou Admin e acima)"
        )
        team_embed.set_footer(text=footer)

        raids_role = f"<@&{self.bot.setting.role.get('raids')}>"
        await team_channel.send(
            content=raids_role, embed=self.raids_embed(), delete_after=60 * 90
        )
        team_message = await team_channel.send(embed=team_embed, delete_after=60 * 90)
        invite_message = await invite_channel.send(embed=invite_embed)

        raids_team = Team(
            team_id="raids",
            title="Raids",
            size=10,
            role=self.bot.setting.role.get("raids"),
            author_id=str(self.bot.user.id),
            invite_channel_id=str(invite_channel_id),
            invite_message_id=str(invite_message.id),
            team_channel_id=str(team_channel_id),
            team_message_id=str(team_message.id),
        )
        raids_team.save()

    def raids_embed(self) -> discord.Embed:
        clan_name = self.bot.setting.clan_name.replace(" ", "%20")
        clan_banner_url = (
            f"http://services.runescape.com/m=avatar-rs/{clan_name}/clanmotif.png"
        )
        raids_notif_embed = discord.Embed(
            title="**Raids**", color=discord.Colour.dark_blue()
        )
        raids_notif_embed.set_thumbnail(url=clan_banner_url)

        raids_notif_embed.add_field(
            name="Marque presença para os Raids de 21:00",
            value=f"<#{self.bot.setting.chat.get('raids_chat')}>\n"
            f"\n"
            f"É obrigatório ter a tag <@&376410304277512192>\n    - Leia os tópicos fixos para saber como obter\n"
            f"\n"
            f"Não mande mensagens desnecessárias no <#{self.bot.setting.chat.get('raids_chat')}>\n"
            f"\n"
            f"Esteja online no jogo no mundo 75 até 20:50 em ponto.\n"
            f"- Risco de remoção do time caso contrário. Não cause atrasos",
            inline=False,
        )
        return raids_notif_embed

    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=["startraids"])
    async def start_raids(self, ctx: Context) -> None:
        await ctx.send(f"Iniciando time de Raids... (mode={self.bot.setting.mode})")
        await self.start_raids_team()
        await ctx.author.send("Time de Raids iniciado com sucesso.")

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    @commands.command()
    async def resend_raids(self, ctx: Context) -> None:
        """
        Re-sends the "Next Raids Notification in (...)" message to the #raids Channel, so it becomes the newest message.
        """
        await ctx.message.delete()

        channel: discord.TextChannel = self.bot.get_channel(
            self.bot.setting.chat.get("raids")
        )
        sent: discord.Message = await channel.send("Próxima notificação de Raids em:")

        state = RaidsState.object()

        if state.time_to_next_message:
            message = await channel.fetch_message(int(state.time_to_next_message))
            if message:
                await message.delete()

        state.time_to_next_message = str(sent.id)
        state.save()

        await ctx.author.send(
            "Mensagem da próxima notificação de Raids reenviada com sucesso."
        )


def setup(bot):
    bot.add_cog(RaidsTasks(bot))
