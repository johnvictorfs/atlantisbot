import traceback

import discord
import rs3clans
from discord.ext import commands

from bot.bot_client import Bot
from bot.utils.tools import has_any_role


class Member(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    # @commands.dm_only()
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # @commands.command(aliases=['role'])
    # async def membro(self, ctx: commands.Context):
    #     atlantis: discord.Guild = self.bot.get_guild(self.bot.setting.server_id)
    #     member: discord.Member = atlantis.get_member(ctx.author.id)

    #     if not member:
    #         return await ctx.send(
    #             f"{ctx.author.mention}, é necessário estar no Servidor do Atlantis "
    #             f"para usar esse comando\nhttps://discord.me/atlantis"
    #         )
    #     # if not has_any_role(member, self.bot.setting.role.get('convidado')):
    #     #     return await ctx.send("Fool! Você já é um Membro!")

    #     def check(message):
    #         return message.author == ctx.author

    #     await ctx.send(f"{ctx.author.mention}, por favor me diga o seu nome no jogo.")

    #     ingame_name = await self.bot.wait_for('message', timeout=2.0, check=check)

    #     await ctx.trigger_typing()
    #     player = rs3clans.Player(ingame_name.content)
    #     if not player.exists:
    #         return await ctx.send(f"{ctx.author.mention}, o jogador '{player.name}' não existe.")
    #     elif player.clan != self.bot.setting.clan_name:
    #         return await ctx.send(f"{ctx.author.mention}, o jogador '{player.name}' não é um membro do Clã Atlantis.")
    #     return await ctx.send(".")


def setup(bot):
    bot.add_cog(Member(bot))
