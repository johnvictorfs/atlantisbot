# Non-Standard lib imports
import rs3clans as rs3
import discord
from discord.ext import commands

# Local imports
import getclan


class ClanCommands:

    def __init__(self, bot):
        self.bot = bot

    # def on_member_join(self, member):
    #     print(f'{member.nick} joined {member.guild} at {member.joined_at}')

    @commands.command(aliases=['claninfo', 'clanexp'])
    async def clan_user_exp(self, ctx, *, username):
        user_clan = getclan.get_user_clan(username)
        user_info = rs3.get_user_info(username, user_clan)
        user_rank = user_info[1]
        user_exp = int(user_info[2])
        await ctx.send(f"Your clan is {user_clan} and your exp in it is {user_exp:,} your rank is {user_rank}.")


def setup(bot):
    bot.add_cog(ClanCommands(bot))
