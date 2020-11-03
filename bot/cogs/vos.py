import asyncio
import discord
from typing import List, Tuple, Optional, Sequence, AnyStr
from discord.ext import tasks, commands
from PIL import Image

import traceback
import datetime
import re
import os

from bot.bot_client import Bot
from bot.orm.models import VoiceOfSeren
from bot.utils.context import Context


# TODO: Acabar essas descrições https://rs.wiki/vos#Known_effects
vos_description = {
    "Amlodd": "• +20% Exp Base de Evocação ao fazer Algibeiras e Pergaminhos\n"
              "• Trocar uma algibeira por pergaminhos agora retorna 12 ao invés de 10\n"
              "• +20% Exp Base de Divinação ao converter [Núcleos de Sombra](https://rs.wiki/Shadow_cores)\n"
              "• Chance de [Crônicas](https://rs.wiki/Chronicle_fragment) aparecerem ao matar Sombras em Amlodd",
    "Cadarn": "• Ao derrotar um [Arqueiro](https://rs.wiki/Cadarn_ranger) ou [Mago](https://rs.wiki/w/Cadarn_magus) "
              "Cadarn, 200 Exp em Combate á Distância ou Magia é ganho, respectivamente\n",
    "Crwys": "• +20% Exp Base em Corte de Lenha ao cortar "
}


class Vos(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        if self.bot.setting.mode == 'prod':
            self.song_of_seren.start()
            self.update_vos.start()

    def cog_unload(self):
        if self.bot.setting.mode == 'prod':
            self.song_of_seren.cancel()
            self.update_vos.cancel()

    @staticmethod
    def save_combined(image_names: List[str]) -> Tuple[str, str]:
        """
        Saves two images combined horizontally and then returns the path for said image

        https://stackoverflow.com/a/30228308
        """
        images = [Image.open(f'images/vos/{image}.png') for image in image_names]
        widths, heights = zip(*(i.size for i in images))

        separation = 15

        new_image = Image.new('RGBA', (sum(widths) + separation, max(heights)))

        x_offset = 0
        for image in images:
            new_image.paste(image, (x_offset, 0))
            x_offset += image.size[0] + separation

        file_name = '-'.join(image_names).replace('.png', '') + '.png'

        path = os.path.join('/tmp', file_name)

        new_image.save(path, 'PNG')

        return path, file_name

    def get_voices(self) -> Optional[Sequence[AnyStr]]:
        time_line = self.bot.twitter_api.GetUserTimeline(screen_name='jagexclock')

        for tweet in time_line:
            pattern = r'The Voice of Seren is now active in the (.+?) and (.+?) districts at .+? UTC.'
            match = re.match(pattern, tweet.text)
            if match:
                return match.groups()

        return None

    def vos_embed(self, vos_1: str, vos_2: str) -> Tuple[discord.Embed, discord.File]:
        image_path, image_name = self.save_combined([vos_1, vos_2])

        image_file = discord.File(image_path, filename=image_name)

        url = "https://rs.wiki/vos#Known_effects"
        text = f'A [Voz de Seren]({url}) está ativa nos distritos de **{vos_1}** e **{vos_2}**'
        embed = discord.Embed(title="Voz de Seren", description=text, color=discord.Color.blue())
        embed.set_thumbnail(url=f"attachment://{image_name}")

        return embed, image_file

    @commands.command()
    async def vos_update(self, ctx: Context):
        with self.bot.db_session() as session:
            state: VoiceOfSeren = session.query(VoiceOfSeren).first()
            channel: discord.TextChannel = self.bot.get_channel(self.bot.setting.chat.get('vos'))
            if state:
                voices = self.get_voices()
                if voices:
                    vos_1, vos_2 = voices

                    if vos_1 != state.current_voice_one and vos_2 != state.current_voice_two:
                        try:
                            message: discord.Message = await channel.fetch_message(int(state.message_id))
                        except discord.errors.NotFound:
                            message = None
                        await ctx.send(f"Updated VoS to: {vos_1}, {vos_2}")
                        await self.change_vos(vos_1, vos_2, message, channel, state)
            else:
                voices = self.get_voices()
                if voices:
                    vos_1, vos_2 = voices

                    print(f"Set VoS to: {vos_1}, {vos_2}")
                    await ctx.send(f"Set VoS to: {vos_1}, {vos_2}")

                    role_1 = self.bot.setting.role.get(vos_1.lower())
                    role_2 = self.bot.setting.role.get(vos_2.lower())

                    mentions = ''
                    if role_1:
                        mentions += f"<@&{role_1}> "
                    if role_2:
                        mentions += f"<@&{role_2.mention}>"

                    embed, file = self.vos_embed(vos_1, vos_2)
                    vos_message: discord.Message = await channel.send(file=file, embed=embed, content="")
                    await channel.send(content=mentions, delete_after=5 * 60)
                    state = VoiceOfSeren(current_voice_one=vos_1, current_voice_two=vos_2, message_id=str(vos_message.id))
                    session.add(state)
                    session.commit()

    async def change_vos(
        self, vos_1: str, vos_2: str, message: discord.Message, channel: discord.TextChannel, state: VoiceOfSeren
    ):
        with self.bot.db_session() as session:
            embed, file = self.vos_embed(vos_1, vos_2)
            now = datetime.datetime.utcnow()

            print(f"Updating VoS to: {vos_1}, {vos_2}")

            role_1 = self.bot.setting.role.get(vos_1.lower())
            role_2 = self.bot.setting.role.get(vos_2.lower())

            mentions = ''
            if role_1:
                mentions += f"<@&{role_1}> "
            if role_2:
                mentions += f"<@&{role_2}>"

            if message:
                try:
                    await message.delete()
                except Exception:
                    pass

            new_message: discord.Message = await channel.send(embed=embed, file=file, content=mentions)

            state.current_voice_one = vos_1
            state.current_voice_two = vos_2
            state.updated = now
            state.message_id = str(new_message.id)
            session.commit()

    # noinspection PyCallingNonCallable
    @tasks.loop(seconds=5)
    async def update_vos(self):
        try:
            with self.bot.db_session() as session:
                state: VoiceOfSeren = session.query(VoiceOfSeren).first()
                channel: discord.TextChannel = self.bot.get_channel(self.bot.setting.chat.get('vos'))

                if state:
                    now = datetime.datetime.utcnow()

                    if state.updated.hour != now.hour or state.updated.day != now.day:
                        vos_1, vos_2 = self.get_voices()
                        if vos_1 != state.current_voice_one and vos_2 != state.current_voice_two:
                            try:
                                message: discord.Message = await channel.fetch_message(int(state.message_id))
                            except discord.errors.NotFound:
                                message = None
                            await self.change_vos(vos_1, vos_2, message, channel, state)
                else:
                    vos_1, vos_2 = self.get_voices()

                    print(f"Set VoS to: {vos_1}, {vos_2}")

                    role_1 = self.bot.setting.role.get(vos_1.lower())
                    role_2 = self.bot.setting.role.get(vos_2.lower())

                    mentions = ''
                    if role_1:
                        mentions += f"<@&{role_1}> "
                    if role_2:
                        mentions += f"<@&{role_2.mention}>"

                    embed, file = self.vos_embed(vos_1, vos_2)
                    message: discord.Message = await channel.send(file=file, embed=embed, content="")
                    await channel.send(content=mentions, delete_after=5 * 60)
                    state = VoiceOfSeren(current_voice_one=vos_1, current_voice_two=vos_2, message_id=str(message.id))
                    session.add(state)
                    session.commit()
        except Exception as e:
            tb = traceback.format_exc()
            await self.bot.send_logs(e, tb)
            await asyncio.sleep(40)

    @commands.command(aliases=['vos'])
    async def voice_of_seren(self, ctx: Context):
        voices = self.get_voices()

        if voices:
            vos_1, vos_2 = voices
            embed, file = self.vos_embed(vos_1, vos_2)

            await ctx.send(file=file, embed=embed)
        else:
            return await ctx.send('Erro ao pegar dados da Voz de Seren. Tente novamente mais tarde.')


def setup(bot):
    bot.add_cog(Vos(bot))
