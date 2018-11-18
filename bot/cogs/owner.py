import os

from discord.ext import commands

from .models import Session, RaidsState


class Owner:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def check_raids(self, ctx):
        session = Session()
        state = session.query(RaidsState).first()
        if not state:
            state = RaidsState(notifications=True)
            session.add(state)
            session.commit()
        if state.notifications:
            await ctx.send("Notificações de Raids estão habilitadas.")
        else:
            await ctx.send("Notificações de Raids estão desabilitadas.")
        session.close()

    @commands.command()
    async def toggle_raids(self, ctx):
        session = Session()
        state = session.query(RaidsState).first()
        if not state:
            state = RaidsState(notifications=True)
            session.add(state)
            session.commit()
        state.notifications = not state.notifications
        if state.notifications:
            await ctx.send("Notificações de Raids agora estão habilitadas.")
        else:
            await ctx.send("Notificações de Raids agora estão desabilitadas.")
        session.commit()
        session.close()


def setup(bot):
    bot.add_cog(Owner(bot))
