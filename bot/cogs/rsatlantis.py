# Non-Standard lib imports
import discord
from discord.ext import commands
import requests

# Standard lib imports
import json


def check_role(ctx, *roles):
    for role in roles:
        if role in str(ctx.message.author.roles):
            return True
    return False


class RsAtlantisCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['atlantisrs', 'Rsatlantis', 'RSatlantis', 'RSATLANTIS'])
    async def rsatlantis(self, ctx):
        if check_role(ctx, 'Admin'):
            pass


def setup(bot):
    bot.add_cog(RsAtlantisCommands(bot))
