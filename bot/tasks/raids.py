import datetime
import traceback
import sys

import asyncio

from bot.utils.tools import start_raids_team
from bot.db.models import RaidsState
import bot.db.db as db


async def raids_task(client):
    print("Starting Raids notifications task.")
    while True:
        if 'testraid' not in sys.argv:
            if not day_to_send(start_date=client.setting.raids_start_date):
                await asyncio.sleep(1)
                continue
            if not is_time_to_send(time_to_send=client.setting.raids_time_utc):
                await asyncio.sleep(1)
                continue
            if not raids_notifications():
                await asyncio.sleep(60)
                continue
        try:
            await start_raids_team(client=client)
            await asyncio.sleep(60 * 10)
        except Exception as e:
            tb = traceback.format_exc()
            await client.send_logs(e, tb)


def raids_notifications():
    with db.Session() as session:
        state = session.query(RaidsState).first()
        if not state:
            state = RaidsState(notifications=True)
            session.add(state)
            session.commit()
        return state.notifications


def day_to_send(start_date):
    today = datetime.datetime.utcnow().date()
    check_day = (today - start_date).days % 2
    if check_day == 0:
        return True
    return False


def is_time_to_send(time_to_send):
    date = str(datetime.datetime.utcnow().time())
    time = date[0:7]
    if time == time_to_send[0:7]:
        return True
    return False
