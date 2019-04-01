import traceback

import asyncio
import aiohttp


async def update_all_clans():
    base_url = 'https://nriver.pythonanywhere.com'
    print('Starting Update Clans task')
    while True:
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f'{base_url}/clan/update-all/') as r:
                    if r.status != 200:
                        print(f'Erro ao atualizar clãs: {r.status}')
                    else:
                        print(f'Exp dos Clãs atualizada com sucesso.')
            await asyncio.sleep(60 * 5)
        except Exception as e:
            print(f'{e}: {traceback.format_exc()}')
