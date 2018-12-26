import datetime
import sys

import discord
import asyncio

from bot.utils.tools import separator

from bot.db.models import RaidsState, Team
import bot.db.db as db


def raids_embed(setting):
    clan_name = setting.clan_name.replace(' ', '%20')
    clan_banner_url = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{clan_name}/clanmotif.png"
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


async def raids_task(client):
    print("Starting Raids notifications task.")
    while True:
        if 'testraid' not in sys.argv:
            if not day_to_send(client.setting.raids_start_date):
                continue
            if not time_to_send(client.setting.raids_time_utc):
                continue
            if not raids_notifications():
                await asyncio.sleep(60)
                continue

        with db.Session() as session:
            old_team = session.query(Team).filter_by(team_id='raids').first()
            if old_team:
                session.delete(old_team)
                session.commit()
        if client.setting.mode == 'prod':
            invite_channel_id = client.setting.chat.get('raids_chat')
            team_channel_id = client.setting.chat.get('raids')
        else:
            invite_channel_id = 505240135390986262
            team_channel_id = 505240114662998027

        invite_channel = client.get_channel(invite_channel_id)
        team_channel = client.get_channel(team_channel_id)

        if not invite_channel or not team_channel:
            dev = client.get_user(client.setting.developer_id)
            await dev.send(f'Erro ao pegar canais para o time de Raids'
                           f'\n- Invite: {invite_channel}'
                           f'\n- Team: {team_channel}')
            continue

        presence = f'Marque presença no <#{invite_channel_id}>\nCriador: {client.user.mention}'
        description = f"Requisito: <@&{client.setting.role.get('raids')}>\n{presence}"

        invite_embed = discord.Embed(
            title=f"Marque presença para 'Raids' (10 pessoas)",
            description=f"{separator}\n\n"
            f"<@&{client.setting.role.get('raids')}>"
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
        with db.Session() as session:
            session.add(raids_team)
            session.commit()
        await asyncio.sleep(60 * 30)


def raids_notifications():
    with db.Session() as session:
        state = session.query(RaidsState).first()
        if not state:
            state = RaidsState(notifications=True)
            session.add(state)
            session.commit()
        return state.notifications


def day_to_send(start_day):
    today = datetime.datetime.utcnow().date()
    check_day = (today - start_day).days % 2
    if check_day == 0:
        return True
    return False


def time_to_send(to_send):
    date = str(datetime.datetime.utcnow().time())
    time = date[0:7]
    if time == to_send[0:7]:
        return True
    return False
