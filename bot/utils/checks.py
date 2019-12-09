from bot.orm.models import User
from bot.orm.db import db_session
from bot.utils.context import Context


async def is_authenticated(ctx: Context):
    """
    Checks if the user running the command is authenticated or not
    """
    with db_session() as session:
        user: User = session.query(User).filter_by(discord_id=str(ctx.author.id)).first()
        if not user or user.disabled:
            await ctx.send(
                f'Você precisa estar autenticado para usar esse comando. Autentique-se enviando o comando'
                f'**`!membro`** para mim aqui: {ctx.bot.user.mention}'
            )
            return False
        if user.warning_date:
            await ctx.send(
                f'Você não pode usar esse comando atualmente por ter recebido um Aviso para '
                f'se re-autenticar, já que mudou de nome recentemente, ou saiu do clã.\n\n'
                f'Você pode se re-autenticar enviando o comando **`!membro`** para mim aqui: {ctx.bot.user.mention}'
            )
            return False
    return True
