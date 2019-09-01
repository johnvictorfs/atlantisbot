import traceback
import datetime
import logging
import json

from discord.ext import commands, tasks
import asyncio
import discord
import aiohttp
import re

from bot.bot_client import Bot
from bot.orm.models import User


async def get_user_data(username: str, cs: aiohttp.ClientSession):
    url = "http://services.runescape.com/m=website-data/"
    player_url = url + "playerDetails.ws?names=%5B%22{}%22%5D&callback=jQuery000000000000000_0000000000&_=0"

    async with cs.get(player_url.format(username.replace(' ', '%20'))) as r:
        # Check clan of player
        content = await r.text()
        return parse_user(content)


def parse_user(content: str) -> dict or None:
    parsed = re.search(r'{"isSuffix":.*,"name":.*,"title":.*}', content)
    if not parsed:
        print(content)
        return None
    parsed = parsed.group()
    info_dict = json.loads(parsed)
    info_dict['is_suffix'] = info_dict.pop('isSuffix')

    return info_dict


class UserAuthentication(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.debugging = False

        if self.bot.setting.mode == 'prod' or self.debugging:
            self.check_users.start()

    def cog_unload(self):
        if self.bot.setting.mode == 'prod' or self.debugging:
            self.check_users.cancel()

    @tasks.loop(hours=1)
    async def check_users(self):
        """
        Check users that have changed names or left the clan since last authentication
        """
        atlantis = self.bot.get_guild(self.bot.setting.server_id)
        membro = atlantis.get_role(self.bot.setting.role.get('membro'))
        convidado = atlantis.get_role(self.bot.setting.role.get('convidado'))

        try:
            async with aiohttp.ClientSession() as cs:
                with self.bot.db_session() as session:
                    users = session.query(User).all()
                    for user in users:
                        user: User
                        user_data = await get_user_data(user.ingame_name, cs)
                        if not user_data:
                            # Sometimes call to RS3's API fail and a 404 html page is returned instead (...?)
                            continue
                        if not self.debugging and user_data['clan'] == self.bot.setting.clan_name:
                            # Don't do anything if player in in clan
                            continue
                        now = datetime.datetime.utcnow()
                        member: discord.Member = atlantis.get_member(int(user.discord_id))
                        if not member:
                            # Exclude from DB if user left the discord
                            session.delete(user)
                            continue

                        if user.warning_date:
                            # Only remove role if warning message was send 7 days before this check
                            if (now - user.warning_date).days >= 7:
                                session.delete(user)
                                await member.remove_roles(membro)
                                await member.add_roles(convidado)
                                await member.send(
                                    f"Olá {member.mention}! Há 7 dias, você trocou de nome ou saiu do Atlantis. "
                                    f"Como, até o momento, você não voltou a se registrar como membro do clã "
                                    f"autenticado ao Discord, seu cargo de `Membro` foi removido.\n\n"
                                    f"Caso ainda seja membro da comunidade, **autentique-se novamente "
                                    f"já!** O cargo de `Membro` é essencial para uma ampla participação "
                                    f"nas atividades do Atlantis.\n\n"
                                    f"Para se autenticar novamente, utilize o comando **`!membro`** aqui!\n\n"
                                )
                        else:
                            await member.send(
                                f"Olá {member.mention}!\n"
                                f"Parece que você trocou o seu nome no jogo ou saiu do Clã! Desse modo, "
                                f"seu cargo de `Membro` deverá ser re-avaliada.\n\n"
                                f"**Caso tenha apenas mudado de nome**, será necessário se autenticar novamente "
                                f"no Discord do clã para continuar a ter acesso aos canais e vantagens do cargo de "
                                f"`Membro`. Torna-se válido ressaltar que o cargo é de fundamental importância para "
                                f"participação em muitas atividades do Atlantis.\n\n"
                                f"A partir de agora, você tem até **7 dias para se autenticar novamente** e "
                                f"registrar-se como Membro do Atlantis! Após este período, o cargo de `Membro` será "
                                f"removido até atualização de seu status.\n\n"
                                f"Caso tenha deixado a comunidade, o cargo só poderá ser reavido mediante um eventual "
                                f"reingresso no clã.\n\n"
                                f"Para se autenticar novamente, utilize o comando **`!membro`** aqui!"
                            )
                            user.warning_date = now
                            session.commit()
        except Exception as e:
            await asyncio.sleep(30)
            logging.error(f'{e}: {traceback.format_exc()}')


def setup(bot):
    bot.add_cog(UserAuthentication(bot))
