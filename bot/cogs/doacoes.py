from quantiphy import Quantity
from discord.ext import commands
import discord

from bot.utils.api import ApiService
from bot.bot_client import Bot
from bot.utils.context import Context


class DoacoesManager(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        self.doacoesApi = ApiService(
            self.bot.setting.rsatlantis['API_URL'],
            'discord/doacoes',
            self.bot.setting.rsatlantis['API_TOKEN']
        )

        self.doacoesGoalsApi = ApiService(
            self.bot.setting.rsatlantis['API_URL'],
            'discord/doacoes_goals',
            self.bot.setting.rsatlantis['API_TOKEN']
        )

    @staticmethod
    def money_value(value: str) -> int:
        return int(Quantity(value.replace('m', 'M')))

    @commands.command('doacoes_list')
    async def doacoes_list(self, ctx: Context):
        data = await self.doacoesApi.get_all()
        await ctx.send(str(data))

    @commands.has_permissions(manage_channels=True)
    @commands.command('donation', aliases=['doacao', 'doação', 'doar'])
    async def create_donation(self, ctx: Context, quantidade: str, *, nome: str):
        if 'b' in quantidade.lower():
            return await ctx.send("Magnitute 'b' ainda não é suportada, utilize 'm' ou 'k' no lugar.")

        quantidade_int = self.money_value(quantidade)

        await self.doacoesApi.create({
            'doador_name': nome,
            'ammount': quantidade_int
        })

        await ctx.send(f"Doação de <:coins:573305319661240340> {quantidade_int:,} de '{nome}' confirmada com sucesso.")

    @commands.command('goal')
    async def donation_goal(self, ctx: Context):
        goals = await self.doacoesGoalsApi.get_all()
        doacoes = await self.doacoesApi.get_all()

        total = sum(doacao['ammount'] for doacao in doacoes)

        active = [goal for goal in goals if goal['active']]

        if not active:
            return await ctx.send("Não há nenhum objetivo de Doações ativo atualmente.")

        goal = active[0]

        description = (
            f"**Objetivo:** <:coins:573305319661240340> {goal['goal']:,}\n"
            f"**Arrecadado:** <:coins:573305319661240340> {total:,}\n"
            f"**Restante:** <:coins:573305319661240340> {goal['goal'] - total:,} "
        )

        embed = discord.Embed(
            title=goal['name'],
            description=description,
            color=discord.Color.blue()
        )

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DoacoesManager(bot))
