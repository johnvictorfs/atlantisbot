import asyncio
from bs4 import BeautifulSoup
import aiohttp


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


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(daily_stock())
