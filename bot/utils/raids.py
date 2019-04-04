import asyncio

import discord

from bot.orm.models import Team
from bot.utils.teams import delete_team
from bot.utils.tools import separator


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