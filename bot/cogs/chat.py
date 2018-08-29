# Non-Standard lib imports
from discord.ext import commands


class ChatCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['role'])
    async def aplicar_role(self, ctx):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'aplicar_role'.")

        await ctx.send()

    @commands.command(aliases=['aplicar', 'raids'])
    async def aplicar_raids(self, ctx):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'aplicar_raids'.")

        await ctx.send()


def setup(bot):
    bot.add_cog(ChatCommands(bot))
