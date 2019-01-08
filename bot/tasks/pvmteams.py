import asyncio
import traceback

from bot.utils.tools import manage_team
from bot.db.models import Team
import bot.db.db as db


async def team_maker(client):
    print("Starting Team Maker task.")
    while True:
        with db.Session() as session:
            running_teams = session.query(Team).all()
            if running_teams:
                for team in running_teams:
                    try:
                        await manage_team(team_id=team.id, client=client)
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        tb = traceback.format_exc()
                        await client.send_logs(e, tb)
        await asyncio.sleep(1)
