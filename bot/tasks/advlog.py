import asyncio
import csv
import traceback
import re
import ast
import datetime
from io import StringIO

import aiohttp
import discord

from bot.db.models import PlayerActivities, AdvLogState


async def advlog(client):
    while True:
        try:
            with client.db_session() as session:
                state = session.query(AdvLogState).first()
                if not state:
                    state = AdvLogState(messages=True)
                    session.add(state)
                    session.commit()
                current_state = state.messages
            if not current_state:
                await asyncio.sleep(60)
                continue
            async with aiohttp.ClientSession() as cs:
                for get_clan in client.setting.advlog_clans:
                    clan = get_clan.get('name')
                    clan_name = get_clan.get('name').replace(' ', '%20')
                    clan_list = await retrieve_clan_list(cs, get_clan.get('name'))

                    print(f"Checking for new adventurer's log entries from clanmates at {datetime.datetime.utcnow()}.")

                    channel = client.get_channel(get_clan.get('chat'))
                    banner = f"http://services.runescape.com/m=avatar-rs/{clan_name}/clanmotif.png"

                    with client.db_session() as session:
                        all_activities = session.query(PlayerActivities).filter_by(clan=clan).all()
                        old_activities = {}
                        if all_activities:
                            for act in all_activities:
                                if not max(act.name in member for member in clan_list):
                                    print(f"Removing {act.name} from Adv. Log database.")
                                    session.delete(act)
                                    session.commit()
                                act_list = ast.literal_eval(act.activities)
                                old_activities[act.name] = act_list

                        for player in clan_list[1:]:
                            player = player[0]
                            # Removing non-breaking spaces from the player's name, since they would break the URL
                            # Source: https://stackoverflow.com/a/52254293
                            player_icon_url = ' '.join(player.split()).replace(' ', '%20')
                            icon_url = f"https://secure.runescape.com/m=avatar-rs/{player_icon_url}/chat.png"
                            activities = await retrieve_activities(cs, player)

                            if not session.query(PlayerActivities).filter_by(name=player).first():
                                print(f'Adding {player} to Adv. Log database.')
                                new_player = PlayerActivities(name=player, activities=str(activities), clan=clan)
                                session.add(new_player)
                                session.commit()
                                continue

                            for activity in activities:
                                if activity not in old_activities[player]:
                                    text = activity.get('text')
                                    details = activity.get('details')
                                    try:
                                        text_exp = int(re.findall(r'\d+', text)[0])
                                        details_exp = int(re.findall(r'\d+', text)[0])
                                        text = text.replace(str(text_exp), f"{text_exp:,}")
                                        details = details.replace(str(details_exp), f"{details_exp:,}")
                                    except IndexError:
                                        pass
                                    embed = discord.Embed(title=text, description=details)
                                    embed.set_author(name=player, icon_url=icon_url)
                                    embed.set_thumbnail(url=banner)
                                    embed.set_footer(text=activity.get('date'))
                                    try:
                                        await channel.send(embed=embed)
                                    except Exception as e:
                                        tb = traceback.format_exc()
                                        print(e, tb)

                    print(f"Finished sending adv log data for clan {get_clan.get('name')}")
                print(f"Sent adv. log data at {datetime.datetime.utcnow()}. Sleeping for 10 minutes.")
                await asyncio.sleep(60 * 10)
        except Exception as e:
            print(f'{e}: {traceback.format_exc()}')


async def retrieve_clan_list(cs, clan_name):
    clan = f"http://services.runescape.com/m=clan-hiscores/members_lite.ws?clanName={clan_name.replace(' ', '%20')}"
    async with cs.get(clan) as r:
        clan_csv = await r.text()
        return list(csv.reader(StringIO(clan_csv), delimiter=','))


async def retrieve_activities(cs, player_name):
    player_name = player_name.replace(' ', '%20')
    profile_url = f'https://apps.runescape.com/runemetrics/profile/profile?user={player_name}&activities=20'
    async with cs.get(profile_url) as r:
        if r.status != 200:
            return []
        call = await r.json()
        if call.get('error') == 'PROFILE_PRIVATE':
            return []
        elif call.get('error') == 'NOT_A_MEMBER':
            return []
        else:
            if call.get('activities'):
                return ast.literal_eval(str(call.get('activities')))
            return []
