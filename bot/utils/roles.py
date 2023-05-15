from typing import Dict, Optional

import discord

from bot.settings import Settings
from bot.utils.tools import has_any_role


async def check_admin_roles(
    user: discord.Member, settings: Settings, rank: str
) -> None:
    """
    Check which Admin rank the User needs to have (if any), and remove any he has
    but shouldn't have
    """

    role_ranks: Dict[str, int] = {
        "Owner": settings.admin_roles().get("rs_owner"),
        "Deputy Owner": settings.admin_roles().get("rs_deputy_owner"),
        "Overseer": settings.admin_roles().get("rs_overseer"),
        "Coordinator": settings.admin_roles().get("rs_coord"),
        "Organiser": settings.admin_roles().get("rs_org"),
        "Admin": settings.admin_roles().get("rs_admin"),
    }

    discord_rank: Optional[int] = role_ranks.get(rank)

    if has_any_role(user, discord_rank):
        # User already has necessary rank
        return

    log_channel: discord.TextChannel = user.guild.get_channel(697682722503524352)

    embed = discord.Embed(title="Atualização de Rank")
    embed.set_author(name=str(user), icon_url=user.avatar.url)

    role: discord.Role
    for role in user.roles:
        if role.id in role_ranks.values():
            # Remove any Admin roles from user
            await user.remove_roles(role)
            embed.color = discord.Color.dark_red()
            embed.add_field(name="Rank Removido", value=role.mention)
            await log_channel.send(embed=embed)

    # User is not Admin
    if not discord_rank:
        return

    server_rank: discord.Role = user.guild.get_role(discord_rank)

    if server_rank:
        # Give user the necessary rank
        embed.color = discord.Color.green()
        embed.add_field(name="Rank Adicionado", value=server_rank.mention)
        await log_channel.send(embed=embed)
        await user.add_roles(server_rank)
