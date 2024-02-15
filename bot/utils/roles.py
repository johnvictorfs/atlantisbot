from typing import Dict, Optional

import discord

from bot.settings import Settings
from bot.utils.tools import has_any_role


async def check_exp_roles(user: discord.Member, exp: int) -> None:
    exp_roles = {
        5_000_000_000: 1207332361759363082,
        4_000_000_000: 1207332431779069952,
        3_000_000_000: 1207332484560326706,
        2_000_000_000: 1207332535236034591,
        1_000_000_000: 1207332728828076085,
        500_000_000: 1207332769303363584,
    }

    highest_role_id = None
    for exp_needed, role_id in exp_roles.items():
        if exp >= exp_needed:
            highest_role_id = role_id
            break

    if highest_role_id:
        highest_role = user.guild.get_role(highest_role_id)
        if highest_role and highest_role not in user.roles:
            await user.add_roles(highest_role)

    # Remove all other exp roles the user might have, except the highest one they qualify for
    exp_role_ids = set(exp_roles.values())
    roles_to_remove = [
        user.guild.get_role(role_id)
        for role_id in exp_role_ids
        if role_id != highest_role_id and user.guild.get_role(role_id) in user.roles
    ]

    if roles_to_remove:
        await user.remove_roles(*roles_to_remove)


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
        "General": settings.admin_roles().get("rs_general"),
    }

    discord_rank: Optional[int] = role_ranks.get(rank)

    if has_any_role(user, discord_rank):
        # User already has necessary rank
        return

    log_channel = user.guild.get_channel(697682722503524352)

    embed = discord.Embed(title="Atualização de Rank")
    embed.set_author(name=str(user), icon_url=user.avatar and user.avatar.url)

    role: discord.Role
    for role in user.roles:
        if role.id in role_ranks.values():
            # Remove any Admin roles from user
            await user.remove_roles(role)
            embed.colour = discord.Color.red()
            embed.add_field(name="Rank Removido", value=role.mention)
            await log_channel.send(embed=embed)

    # User is not Admin
    if not discord_rank:
        return

    server_rank: discord.Role = user.guild.get_role(discord_rank)

    if server_rank:
        # Give user the necessary rank
        embed.colour = discord.Color.green()
        embed.add_field(name="Rank Adicionado", value=server_rank.mention)
        await log_channel.send(embed=embed)
        await user.add_roles(server_rank)
