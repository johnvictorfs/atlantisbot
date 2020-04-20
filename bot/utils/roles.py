from typing import Dict, Optional

import discord

from bot.settings import Settings
from bot.utils.tools import has_any_role


async def check_admin_roles(user: discord.Member, settings: Settings, rank: str) -> None:
    """
    Check which Admin rank the User needs to have (if any), and remove any he has
    but shouldn't have
    """

    role_ranks: Dict[str, int] = {
        'Owner': settings.admin_roles().get('rs_owner'),
        'Deputy Owner': settings.admin_roles().get('rs_deputy_owner'),
        'Overseer': settings.admin_roles().get('rs_overseer'),
        'Coordinator': settings.admin_roles().get('rs_coord'),
        'Organiser': settings.admin_roles().get('rs_org'),
        'Administrator': settings.admin_roles().get('rs_admin')
    }

    discord_rank: Optional[int] = role_ranks.get(rank)

    if has_any_role(user, discord_rank):
        # User already has necessary rank
        return

    role: discord.Role
    for role in user.roles:
        if role.id in role_ranks.values():
            # Remove any Admin roles from user
            user.remove_roles(role)

    # User is not Admin
    if not discord_rank:
        return

    server_rank: discord.Role = user.guild.get_role(discord_rank)

    if server_rank:
        # Give user the necessary rank
        user.add_roles(server_rank)
