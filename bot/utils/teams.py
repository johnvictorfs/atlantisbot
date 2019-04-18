import traceback

import discord

from bot.orm.models import Team, Player, BotMessage
from bot.utils.tools import has_any_role, separator


class TeamNotFoundError(Exception):
    pass


class WrongChannelError(Exception):
    pass


def secondary_full(team: Team, session) -> (int, bool):
    """Checks if a team has hit its limit for number of players that only have its secondary role requirement"""
    secondary_count = session.query(Player).filter_by(team=team.id, secondary=True).count()
    if not team.secondary_limit:
        # If the team does not have a secondary role limit, then it can't ever reach that
        return False
    return secondary_count, (secondary_count >= team.secondary_limit)


def add_to_team(author: discord.Member, team: Team, substitute: bool, secondary: bool, session) -> None:
    """Adds a Player to a Team"""
    added_player = Player(player_id=str(author.id), team=team.id, substitute=substitute, secondary=secondary)
    session.add(added_player)
    session.commit()


def first_substitute(team: Team, session, exclude: int) -> Player or None:
    return session.query(Player).filter(
        Player.substitute == True,
        Player.player_id != str(exclude),
        Player.team == team.id
    ).first()


def remove_from_team(player_id: int, team: Team, session) -> None:
    session.query(Player).filter_by(player_id=str(player_id), team=team.id).delete()
    session.commit()


def team_count(team: Team, session) -> int:
    return session.query(Player).filter_by(team=team.id).count()


async def update_team_message(message: discord.Message, team: Team, prefix: str, session) -> None:
    embed_description = f"Marque presença no <#{team.invite_channel_id}>\n Criador: <@{team.author_id}>"
    requisito = ""
    requisito2 = ""
    if team.role:
        requisito = f"Requisito: <@&{team.role}>\n"
    if team.role_secondary:
        count = session.query(Player).filter_by(team=team.id, secondary=True).count()
        limit = "" if not team.secondary_limit else f"({count}/{team.secondary_limit})"
        requisito2 = f"Requisito Secundário: <@&{team.role_secondary}> {limit}\n\n"

    embed_description = f"{requisito}{requisito2}{embed_description}"

    team_embed = discord.Embed(
        title=f"__{team.title}__ - {team_count(team, session)}/{team.size}",
        description=embed_description,
        color=discord.Color.purple()
    )
    footer = f"Digite '{prefix}del {team.team_id}' para excluir o time. (Criador do time ou Admin e acima)"
    team_embed.set_footer(text=footer)

    players = session.query(Player).filter_by(team=team.id)
    index = 0
    if players:
        for player in players:
            if not player.substitute:
                player_role = f"({player.role})" if player.role else ""
                player_value = f"{index + 1}- <@{player.player_id}> {player_role} {'***(Secundário)***' if player.secondary else ''}"
                team_embed.add_field(
                    name=separator,
                    value=player_value,
                    inline=False
                )
                index += 1
    if players:
        for player in players:
            if player.substitute:
                player_role = f"({player.role})" if player.role else ""
                player_value = f"- <@{player.player_id}> {player_role} ***(Substituto)*** {'***(Secundário)***' if player.secondary else ''}"
                team_embed.add_field(
                    name=separator,
                    value=player_value,
                    inline=False
                )
    await message.edit(embed=team_embed)


async def manage_team(team_id: str, client, message: discord.Message, mode: str) -> None:
    """
    Manages a join or leave for a Team

    mode: can be 'join' or 'leave'
    """
    with client.db_session() as session:
        try:
            team: Team = session.query(Team).filter_by(team_id=team_id).first()
            if not team:
                raise TeamNotFoundError
            if int(team.invite_channel_id) != message.channel.id:
                raise WrongChannelError
            await message.delete()
            current_players = session.query(Player).filter_by(team=team.id)
            invite_channel: discord.TextChannel = client.get_channel(int(team.invite_channel_id))
            team_channel: discord.TextChannel = client.get_channel(int(team.team_channel_id))
            if not invite_channel or not team_channel:
                return await delete_team(session, team, client)
            try:
                team_message = await team_channel.fetch_message(int(team.team_message_id))
            except discord.errors.NotFound:
                return await delete_team(session, team, client)

            text = ''
            no_perm_embed = None

            if mode == 'join':
                team_role = None if not team.role else int(team.role)
                secondary_team_role = None if not team.role_secondary else int(team.role_secondary)

                has_main = has_any_role(message.author, team_role)  # Has main role requirement
                has_secondary = has_any_role(message.author, secondary_team_role)  # Has secondary role requirement
                has_any = has_any_role(message.author, team_role, secondary_team_role)  # Has either or both
                # Has only secondary requirement
                is_secondary = True if (has_secondary and not has_main) else False

                if is_secondary:
                    is_team_full = secondary_full(team, session)[1]
                else:
                    is_team_full = is_full(team, session)

                if in_team(message.author.id, team, session):
                    text = 'já está no time'
                elif has_any:
                    add_to_team(message.author, team, substitute=is_team_full, secondary=is_secondary, session=session)
                    text = 'foi adicionado ***como substituto*** ao time' if is_team_full else 'foi adicionado ao time'
                else:
                    description = f"{message.author.mention}, você precisa ter o cargo <@&{team.role}>"
                    if team.role_secondary:
                        description = f"{description} ou o cargo <@&{team.role_secondary}>"
                    description = (f"{description} para entrar no Time '{team.title}' "
                                   f"({current_players.count()}/{team.size})\n"
                                   f"(*`{message.content}`*)")
                    no_perm_embed = discord.Embed(
                        title=f"__Permissões insuficientes__",
                        description=description,
                        color=discord.Color.dark_red()
                    )

            elif mode == 'leave':
                if in_team(message.author.id, team, session):
                    text = 'saiu do time'
                    substitute: Player = first_substitute(team, session, message.author.id)
                    is_substitute = session.query(Player).filter_by(
                        player_id=str(message.author.id), team=team.id
                    ).first().substitute
                    # If the person leaving is not a substitute and there is one available, then
                    # make that substitute not be a substitute anymore
                    if substitute and not is_substitute:
                        if substitute.secondary and secondary_full(team, session)[1]:
                            pass
                        else:
                            substitute.substitute = False
                            session.commit()
                            _text = (f"<@{substitute.player_id}> não é mais um substituto do time "
                                     f"**[{team.title}]({team_message.jump_url})** "
                                     f"({current_players.count() - 1}/{team.size})")
                            embed = discord.Embed(title='', description=_text, color=discord.Color.green())
                            msg = await invite_channel.send(content=f"<@{substitute.player_id}>", embed=embed)
                            session.add(BotMessage(message_id=msg.id, team=team.id))
                    remove_from_team(message.author.id, team, session)
                else:
                    text = 'já estava no time'
            if no_perm_embed:
                sent_message = await invite_channel.send(embed=no_perm_embed)
            else:
                _text = (f"{message.author.mention} {text} **[{team.title}]({team_message.jump_url})** "
                         f"({current_players.count()}/{team.size})\n\n *`({message.content})`*")
                if mode == 'leave':
                    embed_color = discord.Color.red()
                else:
                    embed_color = discord.Color.green()
                embed = discord.Embed(title='', description=_text, color=embed_color)
                sent_message = await invite_channel.send(embed=embed)

            session.add(BotMessage(message_id=sent_message.id, team=team.id))
            session.commit()

            try:
                await update_team_message(team_message, team, client.setting.prefix, session)
            except discord.errors.NotFound:
                session.delete(team)
                session.commit()

        except TeamNotFoundError:
            raise TeamNotFoundError
            return
        except WrongChannelError:
            raise WrongChannelError
            return
        except Exception as e:
            await client.send_logs(e, traceback.format_exc())


def is_full(team: Team, session) -> bool:
    """Verifies if a team is full or not"""
    count = session.query(Player).filter_by(team=team.id).count()
    return count >= team.size


def in_team(author_id: int, team: Team, session):
    """Checks if a player is in a team"""
    current_players = session.query(Player).filter_by(team=team.id)
    return author_id in [int(player.player_id) for player in current_players]


async def delete_team(session, team: Team, client):
    try:
        team_channel = client.get_channel(int(team.team_channel_id))
        invite_channel = client.get_channel(int(team.invite_channel_id))
    except Exception:
        session.delete(team)
        session.commit()
        return
    try:
        team_message = await team_channel.fetch_message(int(team.team_message_id))
        await team_message.delete()
    except Exception:
        pass
    try:
        invite_message = await invite_channel.fetch_message(int(team.invite_message_id))
        await invite_message.delete()
    except Exception:
        pass
    try:
        messages_to_delete = []
        qs = session.query(BotMessage).filter_by(team=team.id)
        if qs:
            for message in qs:
                to_delete = await invite_channel.fetch_message(message.message_id)
                messages_to_delete.append(to_delete)
            await invite_channel.delete_messages(messages_to_delete)
    except Exception:
        pass
    session.delete(team)
    session.commit()
