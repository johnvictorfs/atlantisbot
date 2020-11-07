from rs3clans import Clan
from typing import Optional

from aioify import aioify
import matplotlib.pyplot as plt
from pandas.plotting import table
from pytz import timezone, utc
import pandas as pd
import discord

from datetime import datetime

separator = ("_\\" * 15) + "_"
right_arrow = "<:rightarrow:484382334582390784>"


def get_clan_sync(name: str, **kwargs) -> Clan:
    return Clan(name, **kwargs)


get_clan_async = aioify(get_clan_sync)


def has_any_role(member: discord.member.Member, *role_ids: Optional[int]):
    for role_id in role_ids:
        if any(member_role.id == role_id for member_role in member.roles):
            return True
    return False


def format_and_convert_date(date: datetime) -> str:
    """
    Convert UTC Datetime to Brazil Time and format it into a nicer string
    """
    tz = timezone('America/Sao_Paulo')
    return date.replace(tzinfo=utc).astimezone(tz).strftime('%d/%m/%y - %H:%M')


def divide_list(items: list, every: int = 5):
    """
    Divide a list into different lists every n items
    """
    lista_de_listas = []
    contador_de_indice = 0

    for a, i in zip(items, range(len(items))):
        if i % every == 0:
            lista_de_listas.append([x for x in items[contador_de_indice: contador_de_indice + every]])
            contador_de_indice += every

    lista_de_listas.append(items[contador_de_indice:])

    if lista_de_listas[-1] == []:
        lista_de_listas.pop(-1)

    return lista_de_listas
