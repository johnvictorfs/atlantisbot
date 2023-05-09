from typing import Union, Tuple
import traceback

from django.db.models import Q
from atlantisbot_api.models import DiscordUser, Team, Player, BotMessage
import discord

from bot.utils.tools import has_any_role, separator


class TeamNotFoundError(Exception):
    pass


class WrongChannelError(Exception):
    pass


def secondary_full(team: Team) -> Tuple[int, bool]:
    """Checks if a team has hit its limit for number of players that only have its secondary role requirement"""
    secondary_count = team.players.filter(secondary=True).count()
    if not team.secondary_limit:
        # If the team does not have a secondary role limit, then it can't ever reach that
        return 0, False
    return secondary_count, (secondary_count >= team.secondary_limit)


def add_to_team(
    author: discord.Member, team: Team, substitute: bool, secondary: bool
) -> None:
    """Adds a Player to a Team"""
    added_player = Player(
        player_id=str(author.id), team=team, substitute=substitute, secondary=secondary
    )
    added_player.save()


def first_substitute(team: Team, exclude: int) -> Union[Player, None]:
    return team.players.filter(~Q(player_id=str(exclude)), substitute=True).first()


def remove_from_team(player_id: int, team: Team) -> None:
    team.players.filter(player_id=str(player_id)).delete()


def team_count(team: Team) -> int:
    return team.players.count()


async def update_team_message(
    message: discord.Message, team: Team, prefix: str
) -> None:
    embed_description = (
        f"Marque presença no <#{team.invite_channel_id}>\n Criador: <@{team.author_id}>"
    )
    requisito = ""
    requisito2 = ""
    if team.role:
        requisito = f"Requisito: <@&{team.role}>\n"
    if team.role_secondary:
        count = team.players.filter(secondary=True).count()
        limit = "" if not team.secondary_limit else f"({count}/{team.secondary_limit})"
        requisito2 = f"Requisito Secundário: <@&{team.role_secondary}> {limit}\n\n"

    embed_description = f"{requisito}{requisito2}{embed_description}"

    team_embed = discord.Embed(
        title=f"__{team.title}__ - {team_count(team)}/{team.size}",
        description=embed_description,
        color=discord.Color.purple(),
    )
    footer = f"Digite '{prefix}del {team.team_id}' para excluir o time. (Criador do time ou Admin e acima)"
    team_embed.set_footer(text=footer)

    index = 0
    for player in team.players.all():
        if not player.substitute:
            user = DiscordUser.objects.filter(discord_id=player.player_id).first()

            player_role = f"({player.role})" if player.role else ""

            if user:
                player_ingame = f"({user.ingame_name})"
            else:
                player_ingame = ""

            player_value = (
                f"{index + 1}- <@{player.player_id}> {player_role} {player_ingame}"
                f"{'***(Secundário)***' if player.secondary else ''}"
            )
            team_embed.add_field(name=separator, value=player_value, inline=False)
            index += 1
    for player in team.players.all():
        if player.substitute:
            user_ = DiscordUser.objects.filter(discord_id=player.player_id).first()

            if user_:
                player_ingame = f"({user_.ingame_name})"
            else:
                player_ingame = ""

            player_role = f"({player.role})" if player.role else ""
            player_value = (
                f"- <@{player.player_id}> {player_role} {player_ingame} ***(Substituto)*** "
                f"{'***(Secundário)***' if player.secondary else ''}"
            )
            team_embed.add_field(name=separator, value=player_value, inline=False)
    await message.edit(embed=team_embed)


async def manage_team(
    team_id: str, client, message: discord.Message, mode: str
) -> None:
    """
    Manages a join or leave for a Team

    mode: can be 'join' or 'leave'
    """
    try:
        team = Team.objects.filter(team_id=team_id).first()
        if not team:
            raise TeamNotFoundError
        if int(team.invite_channel_id or 0) != message.channel.id:
            raise WrongChannelError
        await message.delete()

        current_players = team.players
        substitutes = team.players.filter(substitute=True)
        invite_channel: discord.TextChannel = client.get_channel(
            int(team.invite_channel_id or 0)
        )
        team_channel: discord.TextChannel = client.get_channel(
            int(team.team_channel_id or 0)
        )
        if not invite_channel or not team_channel:
            return await delete_team(team, client)
        try:
            team_message = await team_channel.fetch_message(
                int(team.team_message_id or 0)
            )
        except discord.errors.NotFound:
            return await delete_team(team, client)

        text = ""
        no_perm_embed = None

        if mode == "join":
            team_role = None if not team.role else int(team.role)
            secondary_team_role = (
                None if not team.role_secondary else int(team.role_secondary)
            )

            has_main = has_any_role(
                message.author, team_role
            )  # Has main role requirement
            has_secondary = has_any_role(
                message.author, secondary_team_role
            )  # Has secondary role requirement
            has_any = has_any_role(
                message.author, team_role, secondary_team_role
            )  # Has either or both
            # Has only secondary requirement
            is_secondary = True if (has_secondary and not has_main) else False

            if is_secondary:
                _, is_team_full = secondary_full(team)
            else:
                is_team_full = is_full(team)

            if in_team(message.author.id, team):
                text = "já está no time"
            elif has_any or not team_role:
                add_to_team(
                    message.author,
                    team,
                    substitute=is_team_full,
                    secondary=is_secondary,
                )
                text = (
                    "entrou ***como substituto*** no time"
                    if is_team_full
                    else "entrou no time"
                )
            else:
                description = f"{message.author.mention}, você precisa ter o cargo <@&{team.role}>"
                if team.role_secondary:
                    description = f"{description} ou o cargo <@&{team.role_secondary}>"
                description = (
                    f"{description} para entrar no Time '{team.title}' "
                    f"({current_players.count() - substitutes.count()}/{team.size})\n"
                    f"(*`{message.content}`*)"
                )
                no_perm_embed = discord.Embed(
                    title="__Permissões insuficientes__",
                    description=description,
                    color=discord.Color.dark_red(),
                )

        elif mode == "leave":
            if in_team(message.author.id, team):
                text = "saiu do time"
                substitute: Player = first_substitute(team, message.author.id)
                is_substitute = (
                    team.players.filter(player_id=str(message.author.id))
                    .first()
                    .substitute
                )
                # If the person leaving is not a substitute and there is one available, then
                # make that substitute not be a substitute anymore
                if substitute and not is_substitute:
                    if substitute.secondary and secondary_full(team)[1]:
                        pass
                    else:
                        substitute.substitute = False
                        substitute.save()
                        _text = (
                            f"<@{substitute.player_id}> não é mais um substituto do time "
                            f"**[{team.title}]({team_message.jump_url})** "
                            f"({current_players.count() - substitutes.count() - 1}/{team.size})"
                        )
                        embed = discord.Embed(
                            title="", description=_text, color=discord.Color.green()
                        )
                        msg = await invite_channel.send(
                            content=f"<@{substitute.player_id}>", embed=embed
                        )
                        bot_message = BotMessage(message_id=msg.id, team=team)
                        bot_message.save()
                remove_from_team(message.author.id, team)
            else:
                text = "já não estava no time"
        if no_perm_embed:
            sent_message = await invite_channel.send(embed=no_perm_embed)
        else:
            _text = (
                f"{message.author.mention} {text} **[{team.title}]({team_message.jump_url})** "
                f"({current_players.count() - substitutes.count()}/{team.size})\n\n *`{message.content}`*"
            )
            if mode == "leave":
                embed_color = discord.Color.red()
            else:
                embed_color = discord.Color.green()
            embed = discord.Embed(title="", description=_text, color=embed_color)
            embed.set_author(
                name=message.author.display_name, icon_url=message.author.avatar_url
            )
            sent_message = await invite_channel.send(embed=embed)

        bot_message = BotMessage(message_id=sent_message.id, team=team)
        bot_message.save()

        try:
            await update_team_message(team_message, team, client.setting.prefix)
        except discord.errors.NotFound:
            team.delete()

    except TeamNotFoundError:
        raise TeamNotFoundError
    except WrongChannelError:
        raise WrongChannelError
    except Exception as e:
        await client.send_logs(e, traceback.format_exc())


def is_full(team: Team) -> bool:
    """Verifies if a team is full or not"""
    count = team.players.filter(substitute=False).count()
    return count >= team.size


def in_team(author_id: int, team: Team) -> bool:
    """Checks if a player is in a team"""
    return author_id in [int(player.player_id) for player in team.players.all()]


async def delete_team(team: Team, client) -> None:
    try:
        team_channel = client.get_channel(int(team.team_channel_id or 0))
        invite_channel = client.get_channel(int(team.invite_channel_id or 0))
    except Exception:
        team.delete()
        return
    try:
        team_message = await team_channel.fetch_message(int(team.team_message_id or 0))
        await team_message.delete()
    except Exception:
        pass
    try:
        invite_message = await invite_channel.fetch_message(
            int(team.invite_message_id or 0)
        )
        await invite_message.delete()
    except Exception:
        pass
    try:
        messages_to_delete = []
        for message in BotMessage.objects.filter(team=team):
            to_delete = await invite_channel.fetch_message(message.message_id)
            messages_to_delete.append(to_delete)

        await invite_channel.delete_messages(messages_to_delete)
    except Exception:
        pass
    team.delete()
