import traceback

from discord.ext import commands
import asyncio
import aiohttp

from bot.bot_client import Bot


class RsAtlantis(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        if self.bot.setting.mode == 'prod':
            self.update_clans_task = self.bot.loop.create_task(self.update_all_clans())

    def cog_unload(self):
        if self.bot.setting.mode == 'prod':
            self.update_clans_task.cancel()

    @staticmethod
    async def update_all_clans():
        base_url = 'https://nriver.pythonanywhere.com'
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


def setup(bot):
    bot.add_cog(RsAtlantis(bot))
