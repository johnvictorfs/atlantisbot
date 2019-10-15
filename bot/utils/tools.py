import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import table

from bot.orm.db import engine

import discord

separator = ("_\\" * 15) + "_"
right_arrow = "<:rightarrow:484382334582390784>"


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
