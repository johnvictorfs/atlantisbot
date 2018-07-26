# Non-Standard lib imports
import rs3clans
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
        user_exp = rs3clans.get_user_clan_exp(username, user_clan)
        await ctx.send(f"Your clan is {user_clan} and your exp in it is {user_exp:,}")


def setup(bot):
    bot.add_cog(ClanCommands(bot))
