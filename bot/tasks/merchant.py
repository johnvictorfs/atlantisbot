import datetime
import json

import discord
import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def daily_stock():
    async with aiohttp.ClientSession() as cs:
        async with cs.get('https://runescape.wiki/w/Template:Travelling_Merchant') as r:
            source = await r.text()
            soup = BeautifulSoup(source, 'lxml')
            table = soup.find('table', attrs={'class': 'wikitable align-center-1 align-center-4'})
            items = []
            for row in table.find_all('tr'):
                item = row.find_all('td')
                try:
                    item_dict = {
                        "name": item[1].text,
                        "price": item[2].text,
                        "quantity": item[3].text,
                        "description": item[4].text
                    }
                    items.append(item_dict)
                except IndexError:
                    pass
            return items


def time_till_midnight():
    """https://stackoverflow.com/a/45986036"""
    dt = datetime.datetime.now()
    return ((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)


def translate_item(item: dict):
    with open('bot/merchant.json') as f:
        file = json.load(f)
    if file['stock'].get(item.get('name')):
        if file['stock'].get(item.get('name')).get('name'):
            return {
                "name": file['stock'].get(item.get('name')).get('name'),
                "price": item['price'],
                "quantity": item['quantity'],
                "description": file['stock'].get(item.get('name')).get('description')
            }
    return item


async def update_merchant_stock(client):
    if client.setting.mode == 'dev':
        return
    while True:
        stock = await daily_stock()
        embed = discord.Embed(
            title="Estoque de Hoje",
            description=f"",
            color=discord.Colour.dark_red(),
            url=f"https://runescape.wiki/w/Travelling_Merchant's_Shop"
        )
        for item in stock:
            item = translate_item(item)
            embed.add_field(
                name=f"{item['name']}\n- {item['price']} (Quantidade: {item['quantity']})",
                value=f"{item['description']}\n",
                inline=False
            )
        embed.set_footer(text="Imagens para os produtos em breve...")
        channel: discord.TextChannel = client.get_channel(560980279360094208)
        message: discord.Message = await channel.fetch_message(562120346979794944)
        await message.edit(content=None, embed=embed)
        await asyncio.sleep(time_till_midnight())
        await channel.send('<@&560997610954162198>', delete_after=600)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(daily_stock())
