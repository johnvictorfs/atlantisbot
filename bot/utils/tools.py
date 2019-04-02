import asyncio
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import table

from bot.orm.db import engine
from bot.orm.models import Team, Player, BotMessage

import discord

separator = ("_\\" * 15) + "_"
right_arrow = "<:rightarrow:484382334582390784>"


class TeamNotFoundError(Exception):
    pass


class WrongChannelError(Exception):
    pass


def has_any_role(member: discord.member.Member, *role_ids: int):
    for role_id in role_ids:
        if any(member_role.id == role_id for member_role in member.roles):
            return True
    return False


def raids_embed(setting):
    clan_name = setting.clan_name.replace(' ', '%20')
    clan_banner_url = f"http://services.runescape.com/m=avatar-rs/{clan_name}/clanmotif.png"
    raids_notif_embed = discord.Embed(title="**Raids**", color=discord.Colour.dark_blue())
    raids_notif_embed.set_thumbnail(url=clan_banner_url)

    raids_notif_embed.add_field(
        name="Marque presença para os Raids de 21:00",
        value=f"<#{setting.chat.get('raids_chat')}>\n"
        f"\n"
        f"É obrigatório ter a tag <@&376410304277512192>\n    - Leia os tópicos fixos para saber como obter\n"
        f"\n"
        f"Não mande mensagens desnecessárias no <#{setting.chat.get('raids_chat')}>\n"
        f"\n"
        f"Não marque presença mais de uma vez\n"
        f"\n"
        f"Esteja online no jogo no mundo 75 até 20:50 em ponto.\n"
        f"- Risco de remoção do time caso contrário. Não cause atrasos",
        inline=False
    )
    return raids_notif_embed


async def manage_team(team_id: str, client, message: discord.Message, mode: str):
    """
    mode: can be 'join' or 'leave'
    """
    with client.db_session() as session:
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
        if mode == 'join':
            team_role = None
            if team.role:
                team_role = int(team.role)
            secondary_team_role = None
            if team.role_secondary:
                secondary_team_role = int(team.role_secondary)
            if has_any_role(message.author, team_role, secondary_team_role) or not team.role:
                if message.author.id not in [int(player.player_id) for player in current_players]:
                    if current_players.count() < team.size:
                        added_player = Player(player_id=str(message.author.id), team=team.id)
                        session.add(added_player)
                        session.commit()
                        sent_message = await invite_channel.send(
                            f"{message.author.mention} entrou no time '{team.title}' "
                            f"({current_players.count()}/{team.size})\n"
                            f"*(`in {team.team_id}`)*"
                        )
                    else:
                        added_player = Player(player_id=str(message.author.id), team=team.id, substitute=True)
                        session.add(added_player)
                        session.commit()

                        sent_message = await invite_channel.send(
                            f"{message.author.mention} entrou no time '{team.title}' ***como substituto*** "
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
                description = f"{message.author.mention}, você precisa ter o cargo <@&{team.role}>"
                if team.role_secondary:
                    description = f"{description} ou o cargo <@&{team.role_secondary}>"
                description = (f"{description} para entrar no Time '{team.title}' "
                               f"({current_players.count()}/{team.size})\n"
                               f"(*`in {team.team_id}`*)")
                no_perm_embed = discord.Embed(
                    title=f"__Permissões insuficientes__",
                    description=description,
                    color=discord.Color.dark_red()
                )
                sent_message = await invite_channel.send(embed=no_perm_embed)
        elif mode == 'leave':
            if message.author.id in [int(player.player_id) for player in current_players]:
                sent_message = await invite_channel.send(
                    f"{message.author.mention} saiu do time '{team.title}' "
                    f"({current_players.count() - 1}/{team.size})\n"
                    f"*(`out {team.team_id}`)*"
                )
                # Check for substitutes, but discarding the person who sent the message to leave in the first place
                substitute = session.query(Player).filter(
                    Player.substitute == True,
                    Player.player_id != str(message.author.id),
                    Player.team == team.id
                ).first()

                # Checks if the person leaving the team was already a substitute or not
                is_substitute = session.query(Player).filter_by(
                    player_id=str(message.author.id), team=team.id
                ).first().substitute
                # If the person leaving is not a substitute and there is one available, then
                # make that substitute not be a substitute anymore
                if substitute and not is_substitute:
                    substitute.substitute = False
                    session.commit()
                    sent_message2 = await invite_channel.send(
                        f"<@{substitute.player_id}> não é mais um substituto do time '{team.title}' "
                        f"({current_players.count() - 1}/{team.size})"
                    )
                    bot_message = BotMessage(message_id=sent_message2.id, team=team.id)
                    session.add(bot_message)
                    session.commit()
                session.query(Player).filter_by(player_id=str(message.author.id), team=team.id).delete()
                session.commit()
            else:
                sent_message = await invite_channel.send(
                    f"{message.author.mention} já não estava no time '{team.title}'. "
                    f"({current_players.count()}/{team.size})\n"
                    f"*(`out {team.team_id}`)*"
                )
        else:
            return
        message = BotMessage(message_id=sent_message.id, team=team.id)
        session.add(message)
        session.commit()
        embed_description = (
            f"Marque presença no <#{team.invite_channel_id}>\n"
            f"Criador: <@{team.author_id}>"
        )

        requisito = ""
        requisito2 = ""
        if team.role:
            requisito = f"Requisito: <@&{team.role}>\n"
        if team.role_secondary:
            requisito2 = f"Requisito Secundário: <@&{team.role_secondary}>\n\n"

        embed_description = f"{requisito}{requisito2}{embed_description}"

        team_embed = discord.Embed(
            title=f"__{team.title}__ - {current_players.count()}/{team.size}",
            description=embed_description,
            color=discord.Color.purple()
        )
        footer = (f"Digite '{client.setting.prefix}del {team.team_id}' "
                  f"para excluir o time. (Criador do time ou Admin e acima)")

        team_embed.set_footer(text=footer)

        players = session.query(Player).filter_by(team=team.id)
        index = 0
        if players:
            for player in players:
                if not player.substitute:
                    team_embed.add_field(
                        name=separator,
                        value=f"{index + 1}- <@{player.player_id}>",
                        inline=False
                    )
                    index += 1
        if players:
            for player in players:
                if player.substitute:
                    team_embed.add_field(
                        name=separator,
                        value=f"{index + 1}- <@{player.player_id}> ***(Substituto)***",
                        inline=False
                    )
                    index += 1
        try:
            await team_message.edit(embed=team_embed)
        except discord.errors.NotFound:
            session.delete(team)
            session.commit()


async def start_raids_team(client):
    with client.db_session() as session:
        old_team = session.query(Team).filter_by(team_id='raids').first()
        if old_team:
            await delete_team(session, old_team, client)
    if client.setting.mode == 'prod':
        invite_channel_id = client.setting.chat.get('raids_chat')
        team_channel_id = client.setting.chat.get('raids')
    else:
        invite_channel_id = 505240135390986262
        team_channel_id = 505240114662998027

    invite_channel = client.get_channel(invite_channel_id)
    team_channel = client.get_channel(team_channel_id)

    presence = f'Marque presença no <#{invite_channel_id}>\nCriador: {client.user.mention}'
    description = f"Requisito: <@&{client.setting.role.get('raids')}>\n{presence}"
    invite_embed = discord.Embed(
        title=f"Marque presença para 'Raids' (10 pessoas)",
        description=f"{separator}\n\n"
        f"Requisito: <@&{client.setting.role.get('raids')}>\n"
        f"Time: {team_channel.mention}\n"
        f"Criador: {client.user.mention}\n\n"
        f"`in raids`: Marcar presença\n"
        f"`out raids`: Retirar presença"
    )
    team_embed = discord.Embed(
        title=f"__Raids__ - 0/10",
        description=description,
        color=discord.Color.purple()
    )
    footer = (f"Digite '{client.setting.prefix}del raids' "
              f"para excluir o time. (Criador do time ou Admin e acima)")
    team_embed.set_footer(text=footer)

    await team_channel.send(
        content=f"<@&{client.setting.role.get('raids')}>",
        embed=raids_embed(client.setting),
        delete_after=60 * 90
    )
    team_message = await team_channel.send(embed=team_embed, delete_after=60 * 90)
    invite_message = await invite_channel.send(embed=invite_embed)

    raids_team = Team(
        team_id='raids',
        title='Raids',
        size=10,
        role=client.setting.role.get('raids'),
        author_id=str(client.user.id),
        invite_channel_id=str(invite_channel_id),
        invite_message_id=str(invite_message.id),
        team_channel_id=str(team_channel_id),
        team_message_id=str(team_message.id)
    )
    with client.db_session() as session:
        session.add(raids_team)
        session.commit()
    await asyncio.sleep(60 * 30)


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
