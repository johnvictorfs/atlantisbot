import traceback
import datetime
import json

from discord.ext import commands
from bs4 import BeautifulSoup
import discord
import asyncio
import aiohttp

from bot.bot_client import Bot


class Merchant(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        self.update_merchant_task = self.bot.loop.create_task(self.update_merchant_stock())

    def cog_unload(self):
        self.update_merchant_task.cancel()

    @staticmethod
    def today_str() -> str:
        today = datetime.datetime.utcnow()
        return f"{today.day} {today.strftime('%B')} {today.year}"

    async def daily_stock(self) -> list:
        full_stock = await self.future_stock()
        today = self.today_str()
        item = full_stock.get(today)
        if not item:
            await self.bot.send_logs(full_stock, f'KeyError: {today}')
            return []
        return [self.get_item(item[f'slot_{letter}']) for letter in ['a', 'b', 'c']]

    @staticmethod
    def get_item(name: str):
        with open('bot/merchant.json') as f:
            merchant_file = json.load(f)
        return merchant_file['stock'][name.replace(u'\xa0', u' ')]

    @staticmethod
    async def future_stock() -> dict:
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://runescape.wiki/w/Travelling_Merchant%27s_Shop/Future') as r:
                source = await r.text()
                soup = BeautifulSoup(source, 'lxml')
                table = soup.find('table', attrs={'class': 'wikitable sticky-header'})
                items = {}
                for row in table.find_all('tr'):
                    item = row.find_all('td')
                    try:
                        items[item[0].text] = {
                            "slot_a": item[1].text,
                            "slot_b": item[2].text,
                            "slot_c": item[3].text
                        }
                    except IndexError:
                        pass
                return items

    @staticmethod
    def time_till_midnight() -> int:
        """
        Returns the time till midnight in seconds
        https://stackoverflow.com/a/45986036
        """
        dt = datetime.datetime.utcnow()
        return ((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)

    async def merchant_embed(self):
        embed = discord.Embed(
            title=f"Estoque de Hoje ({self.today_str()})",
            description=f"",
            color=discord.Colour.dark_red(),
            url=f"https://runescape.wiki/w/Travelling_Merchant's_Shop"
        )
        stock = await self.daily_stock()
        for item in stock:
            embed.add_field(
                name=f"{item['emoji']} {item['name']} ({item['quantity']})\n- {item['price']}",
                value=f"{item['description']}\n",
                inline=False
            )
        return embed

    async def update_merchant_stock(self):
        await self.bot.wait_until_ready()

        if self.bot.setting.mode == 'dev':
            return

        while True:
            try:
                channel: discord.TextChannel = self.bot.get_channel(self.bot.setting.chat.get('merchant_call'))
                message: discord.Message = await channel.fetch_message(562120346979794944)
                embed = await self.merchant_embed()
                await message.edit(content=None, embed=embed)
                await asyncio.sleep(self.time_till_midnight() + 30)
                await channel.send('<@&560997610954162198>', delete_after=600)
            except Exception as e:
                tb = traceback.format_exc()
                print(e, tb)
                await self.bot.send_logs(e, tb)


def setup(bot):
    bot.add_cog(Merchant(bot))
