from discord.ext import commands

from bot.orm.models import User
from bot.orm.db import db_session


async def is_authenticated(ctx: commands.Context):
    """
    Checks if the user running the command is authenticated or not
    """
    with db_session() as session:
        user: User = session.query(User).filter_by(discord_id=str(ctx.author.id))
        if not user:
            await ctx.send(
                f'Você precisa estar autenticado para usar esse comando. Autentique-se enviando o comando'
                f'**`!membro`** para mim aqui: {ctx.bot.user.mention}'
            )
            return False
    return True
