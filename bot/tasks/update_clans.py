import asyncio
import aiohttp


async def update_all_clans():
    base_url = 'https://nriver.pythonanywhere.com'
    while True:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'{base_url}/clan/update-all/') as r:
                if r.status != 200:
                    print(f'Erro ao atualizar clãs: {r.status}')
                else:
                    print(f'Exp dos Clãs atualizada com sucesso.')
        await asyncio.sleep(60 * 5)
