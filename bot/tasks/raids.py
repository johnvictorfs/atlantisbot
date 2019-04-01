import datetime
import traceback
import sys

import asyncio
import discord

from bot.utils.tools import start_raids_team
from bot.orm.models import RaidsState


async def raids_task(client) -> None:
    print("Starting Raids Notifications task.")
    while True:
        if 'testraid' in sys.argv:
            try:
                await start_raids_team(client=client)
                await asyncio.sleep(60 * 10)
            except Exception as e:
                tb = traceback.format_exc()
                await client.send_logs(e, tb)
        else:
            seconds_till_raids = time_till_raids(client.setting.raids_start_date)
            raids_diff = datetime.timedelta(seconds=seconds_till_raids)
            print(f'Next Raids in: {raids_diff.days} '
                  f'Days, {raids_diff.seconds//3600} '
                  f'Hours, {(raids_diff.seconds//60)%60} '
                  f'Minutes')
            await asyncio.sleep(seconds_till_raids)
            if not raids_notifications(client):
                await asyncio.sleep(60)
                continue
            try:
                await start_raids_team(client=client)
            except Exception as e:
                tb = traceback.format_exc()
                await client.send_logs(e, tb)
            finally:
                await asyncio.sleep(60)


async def update_next_raids(client) -> None:
    """Updates the message with the time until the next raids in the #raids channel"""
    while True:
        seconds_till_raids = time_till_raids(client.setting.raids_start_date)
        raids_diff = datetime.timedelta(seconds=seconds_till_raids)
        days = raids_diff.days
        hours = raids_diff.seconds // 3600
        minutes = (raids_diff.seconds // 60) % 60

        text = f"Próxima notificação de Raids em: {days} Dias, {hours} Horas, {minutes} Minutos."
        channel: discord.TextChannel = client.get_channel(client.setting.chat.get('raids'))
        await channel.send(text)
        await asyncio.sleep(60)


def raids_notifications(client) -> bool:
    """Checks if raids notifications are turned on or off in the bot settings"""
    with client.db_session() as session:
        state = session.query(RaidsState).first()
        if not state:
            state = RaidsState(notifications=True)
            session.add(state)
            session.commit()
        return state.notifications


def time_till_raids(start_date):
    """Calculates the time between now and the next raids, assuming raids occur every 2 days"""
    now = datetime.datetime.utcnow()
    difference = start_date - now
    if (now - start_date).days % 2 == 0:
        # Add a day to the difference in case it has been an even number of days between start_date and now
        return difference.seconds + (24 * 60 * 60)
    return difference.seconds
