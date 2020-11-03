from atlantisbot_api.models import DiscordUser
import discord

from bot.utils.context import Context


async def is_admin(ctx: Context):
    atlantis: discord.Guild = ctx.bot.get_guild(ctx.setting.server_id)
    member: discord.Member = atlantis.get_member(ctx.author.id)

    admin_roles = ['coord_discord', 'org_discord', 'adm_discord']
    roles = [atlantis.get_role(ctx.setting.admin_roles().get(role)) for role in admin_roles]

    has_admin = any(role in member.roles for role in roles)
    ctx.bot.logger.info(f'[Check is_admin] {member} -> {has_admin}')

    return has_admin


async def is_authenticated(ctx: Context):
    """
    Checks if the user running the command is authenticated or not
    """
    user = DiscordUser.objects.filter(discord_id=str(ctx.author.id)).first()

    if not user or user.disabled:
        await ctx.send(
            f'Você precisa estar autenticado para usar esse comando. Autentique-se enviando o comando'
            f'**`!membro`** para mim aqui: {ctx.bot.user.mention}'
        )
        ctx.bot.logger.info(f'[Check is_authenticated] {user} -> Disabled or non-existent')
        return False
    if user.warning_date:
        await ctx.send(
            f'Você não pode usar esse comando atualmente por ter recebido um Aviso para '
            f'se re-autenticar, já que mudou de nome recentemente, ou saiu do clã.\n\n'
            f'Você pode se re-autenticar enviando o comando **`!membro`** para mim aqui: {ctx.bot.user.mention}'
        )
        ctx.bot.logger.info(f'[Check is_authenticated] {user} -> Warning date')
        return False

    ctx.bot.logger.info(f'[Check is_authenticated] {user} -> True')
    return True
