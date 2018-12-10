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
from bot.db.db import Session


async def advlog(client):
    while True:
        session = Session()
        state = session.query(AdvLogState).first()
        if not state:
            state = AdvLogState(messages=True)
            session.add(state)
            session.commit()
        current_state = state.messages
        session.close()
        if not current_state:
            await asyncio.sleep(60)
            continue
        clans = [
            {
                'name': 'Iron Atlantis',
                'chat': 521499765696102420
            },
            {
                'name': client.setting.clan_name,
                'chat': client.setting.chat.get('adv_log')
            }
        ]
        for get_clan in clans:
            async with aiohttp.ClientSession() as cs:
                clan = f"http://services.runescape.com/m=clan-hiscores/members_lite.ws?clanName={get_clan.get('name')}"
                async with cs.get(clan) as r:
                    clan_csv = await r.text()
                    clan_list = list(csv.reader(StringIO(clan_csv), delimiter=','))
                new_activities = {}
                success = 0
                profile_private = 0
                not_member = 0
                print(
                    f"Started checking for new adventurer's log entries from clanmates at {datetime.datetime.utcnow()}.")
                for player in clan_list[1:]:
                    player = player[0]
                    profile_url = f'https://apps.runescape.com/runemetrics/profile/profile?user={player}&activities=20'
                    async with cs.get(profile_url) as r:
                        call = await r.json()
                        if call.get('error') == 'PROFILE_PRIVATE':
                            new_activities[player] = []
                            profile_private += 1
                        elif call.get('error') == 'NOT_A_MEMBER':
                            new_activities[player] = []
                            not_member += 1
                        else:
                            if call.get('activities'):
                                # TODO: Since this list can't be .reversed(), sort the dictionaries inside them by date
                                new_activities[player] = ast.literal_eval(str(call.get('activities')))
                                success += 1
                print(f"Finished grabbing adv log data for clan {get_clan.get('name')}. Success: {success} "
                      f"- Private Profile: {profile_private} "
                      f"- Not a Member: {not_member}")
                session = Session()
                all_activities = session.query(PlayerActivities).all()
                old_activities = {}
                if all_activities:
                    for act in all_activities:
                        act_list = ast.literal_eval(act.activities)
                        old_activities[act.name] = act_list
                new_keys = set(new_activities) - set(old_activities)
                difference = {}
                for key, item in new_activities.items():
                    if key not in new_keys:
                        diff_items = []
                        if item:
                            if old_activities.get(key):
                                diff_items = [act for act in item if act not in old_activities.get(key)]
                            else:
                                diff_items = [act for act in item]
                        difference[key] = diff_items
                difference.update({k: new_activities[k] for k in new_keys})
                for key, item in new_activities.items():
                    old_player = session.query(PlayerActivities).filter_by(name=key).first()
                    if old_player:
                        old_player.activities = str(item)
                    else:
                        new_player = PlayerActivities(name=key, activities=str(item))
                        session.add(new_player)
                    session.commit()
                session.close()
                channel = client.get_channel(get_clan.get('chat'))
                banner = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{get_clan.get('name')}/clanmotif.png"
                for player, activities in difference.items():
                    player_name = player.replace(' ', '%20')
                    icon_url = f"https://secure.runescape.com/m=avatar-rs/{player_name}/chat.png"
                    if activities:
                        for activity in activities[::-1]:
                            text = activity.get('text')
                            details = activity.get('details')
                            try:
                                text_exp = int(re.findall('\d+', text)[0])
                                details_exp = int(re.findall('\d+', text)[0])
                                text = text.replace(str(text_exp), f"{text_exp:,}")
                                details = details.replace(str(details_exp), f"{details_exp:,}")
                            except IndexError:
                                pass
                            embed = discord.Embed(
                                title=text,
                                description=details
                            )
                            embed.set_author(
                                name=player,
                                icon_url=icon_url
                            )
                            embed.set_thumbnail(url=banner)
                            embed.set_footer(text=activity.get('date'))
                            try:
                                await channel.send(embed=embed)
                            except Exception as e:
                                tb = traceback.format_exc()
                                print(e, tb)
        print(f"Sent adv. log data at {datetime.datetime.utcnow()}. Sleeping for 10 minutes.")
        await asyncio.sleep(60 * 10)
