import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import table

from bot.db.db import engine
from bot.db.models import Team, Player, BotMessage
import bot.db.db as db

import discord

separator = ("_\\" * 15) + "_"
right_arrow = "<:rightarrow:484382334582390784>"


async def manage_team(team_id: int, client):
    with db.Session() as session:
        team = session.query(Team).get(team_id)  # type: Team
        invite_channel = client.get_channel(int(team.invite_channel_id))
        team_channel = client.get_channel(int(team.team_channel_id))
        if not invite_channel or not team_channel:
            return

        try:
            invite_message = await invite_channel.get_message(int(team.invite_message_id))
            team_message = await team_channel.get_message(int(team.team_message_id))
        except discord.errors.NotFound:
            session.delete(team)
            session.commit()
            return

        async for message in invite_channel.history(after=invite_message):
            sent_message = None
            current_players = session.query(Player).filter_by(team=team.id)
            # Validate Team Additions
            if message.content.lower() == f'in {team.team_id}':
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    continue
                if message.author.bot:
                    continue
                try:
                    team_role = int(team.role)
                except TypeError:
                    team_role = None
                except ValueError:
                    team_role = None
                if has_any_role(message.author, team_role) or not team.role:
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
                        f"*(`out {team.team_id}`)*"
                    )
                else:
                    sent_message = await invite_channel.send(
                        f"{message.author.mention} já não estava no time '{team.title}'. "
                        f"({current_players.count()}/{team.size})\n"
                        f"*(`out {team.team_id}`)*"
                    )
            if sent_message:
                message = BotMessage(message_id=sent_message.id, team=team.id)
                session.add(message)
                session.commit()
                embed_description = (
                    f"Marque presença no <#{team.invite_channel_id}>\n"
                    f"Criador: <@{team.author_id}>"
                )
                if team.role:
                    embed_description = f"Requisito: <@&{team.role}>\n{embed_description}"
                team_embed = discord.Embed(
                    title=f"__{team.title}__ - {current_players.count()}/{team.size}",
                    description=embed_description,
                    color=discord.Color.purple()
                )
                footer = (f"Digite '{client.setting.prefix}del {team.team_id}' "
                          f"para excluir o time. (Criador do time ou Admin e acima)")
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


def has_any_role(member: discord.member.Member, *role_ids: int):
    for role_id in role_ids:
        if any(member_role.id == role_id for member_role in member.roles):
            return True
    return False


def plot_table(table_name: str, image_name: str, safe: bool = True):
    # https://stackoverflow.com/questions/35634238/how-to-save-a-pandas-dataframe-table-as-a-png
    df = pd.read_sql(table_name, engine)
    if safe:
        if table_name == 'amigosecreto':
            df = df.drop(['id', 'discord_id', 'giving_to_id', 'giving_to_name', 'receiving'], axis=1)
    fig, ax = plt.subplots(figsize=(12, 2))  # set size frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame
    table(ax, df, loc='upper right', colWidths=[0.17] * len(df.columns))
    # https://stackoverflow.com/questions/11837979/removing-white-space-around-a-saved-image-in-matplotlib
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(f"{image_name}.tmp.png", bbox_inches='tight', pad_inches=0, transparent=True)
