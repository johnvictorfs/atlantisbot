import asyncio
import traceback

import discord

from .cogs.utils import has_role, separator
from .cogs.db.models import Team, BotMessage, Player
from .cogs.db.db import Session


async def team_maker(client):
    print("Starting team maker task.")
    session = Session()
    while True:
        running_teams = session.query(Team).all()
        if not running_teams:
            await asyncio.sleep(1)
            continue
        try:
            for team in running_teams:
                try:
                    team_channel = client.get_channel(int(team.team_channel_id))
                    invite_channel = client.get_channel(int(team.invite_channel_id))
                except discord.errors.Forbidden:
                    session.delete(team)
                    session.commit()
                    continue
                try:
                    team_message = await team_channel.get_message(int(team.team_message_id))
                except discord.errors.NotFound:
                    session.delete(team)
                    session.commit()
                    continue
                except discord.errors.Forbidden:
                    session.delete(team)
                    session.commit()
                    continue
                try:
                    invite_message = await invite_channel.get_message(int(team.invite_message_id))
                except discord.errors.NotFound:
                    session.delete(team)
                    session.commit()
                    continue
                async for message in invite_channel.history(after=invite_message):
                    sent_message = None
                    current_players = session.query(Player).filter_by(team=team.id)
                    # Validate Team Additions
                    if message.content.lower() == f'in {team.team_id}':
                        await message.delete()
                        if message.author.bot:
                            continue
                        try:
                            team_role = int(team.role)
                        except TypeError:
                            team_role = None
                        except ValueError:
                            team_role = None
                        if has_role(message.author, team_role) or team.role is None:
                            if message.author.id not in [int(player.player_id) for player in current_players]:
                                if current_players.count() < team.size:
                                    added_player = Player(player_id=str(message.author.id), team=team.id)
                                    session.add(added_player)
                                    session.commit()
                                    sent_message = await invite_channel.send(
                                        f"{message.author.mention} foi adicionado ao time '{team.title}' "
                                        f"({current_players.count()}/{team.size})\n"
                                        f"*(`in {team.team_id}`)*"
                                    )
                                else:
                                    sent_message = await invite_channel.send(
                                        f"{message.author.mention}, o time '{team.title}' já está cheio. "
                                        f"({current_players.count()}/{team.size})\n"
                                        f"*(`in {team.team_id}`)*"
                                    )
                            else:
                                sent_message = await invite_channel.send(
                                    f"{message.author.mention} já está no time '{team.title}'. "
                                    f"({current_players.count()}/{team.size})\n"
                                    f"*(`in {team.team_id}`)*"
                                )
                        else:
                            no_perm_embed = discord.Embed(
                                title=f"__Permissões insuficientes__",
                                description=f"{message.author.mention}, você precisa ter o cargo <@&{team.role}> "
                                            f"para entrar no Time '{team.title}' "
                                            f"({current_players.count()}/{team.size})\n"
                                            f"(*`in {team.team_id}`*)",
                                color=discord.Color.dark_red()
                            )
                            sent_message = await invite_channel.send(embed=no_perm_embed)
                    # Validate Team Opt-outs
                    elif message.content.lower() == f'out {team.team_id}':
                        await message.delete()
                        if message.author.bot:
                            continue
                        if message.author.id in [int(player.player_id) for player in current_players]:
                            session.query(Player).filter_by(player_id=str(message.author.id), team=team.id).delete()
                            session.commit()
                            sent_message = await invite_channel.send(
                                f"{message.author.mention} foi removido do time '{team.title}' "
                                f"({current_players.count()}/{team.size})\n"
                                f"*(`in {team.team_id}`)*"
                            )
                        else:
                            sent_message = await invite_channel.send(
                                f"{message.author.mention} já não estava no time '{team.title}'. "
                                f"({current_players.count()}/{team.size})\n"
                                f"*(`in {team.team_id}`)*"
                            )
                    if sent_message:
                        message = BotMessage(message_id=sent_message.id, team=team.id)
                        session.add(message)
                        session.commit()
                        embed_description = (
                            f"Marque presença no <#{team.invite_channel_id}>\n"
                            f"Criador: <@{team.author_id}>")
                        if team.role:
                            embed_description = (
                                f"Requisito: <@&{team.role}>\n"
                                f"{embed_description}")
                        team_embed = discord.Embed(
                            title=f"__{team.title}__ - {current_players.count()}/{team.size}",
                            description=embed_description,
                            color=discord.Color.purple()
                        )
                        footer = (f"Digite '{client.setting.prefix}del {team.team_id}' "
                                  f"para excluir o time. (Criador do time ou Mod/Mod+/Admin)")
                        team_embed.set_footer(
                            text=footer
                        )
                        players = session.query(Player).filter_by(team=team.id)
                        index = 0
                        if players:
                            for player in players:
                                team_embed.add_field(
                                    name=separator,
                                    value=f"{index + 1}- <@{player.player_id}>",
                                    inline=False
                                )
                                index += 1
                        try:
                            await team_message.edit(embed=team_embed)
                        except discord.errors.NotFound:
                            session.delete(team)
                            session.commit()
        except Exception as e:
            tb = traceback.format_exc()
            await client.send_logs(e, tb)
        await asyncio.sleep(1)
