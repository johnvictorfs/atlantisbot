import discord
from typing import List
from discord.ext import tasks, commands
from PIL import Image

import traceback
import datetime
import re
import os

from bot.bot_client import Bot
from bot.orm.models import SongOfSerenState, VoiceOfSeren


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

    # noinspection PyCallingNonCallable
    @tasks.loop(seconds=5)
    async def song_of_seren(self):
        emoji = {
            'Ataque': '<:attack:499707565949583391>',
            'Defesa': '<:defence:499707566033600513>',
            'Força': '<:strength:499707566406762496>',
            'Constituição': '<:constitution:499707566335459358>',
            'Combate á Distância': '<:ranged:499707566331527168>',
            'Oração': '<:prayer:499707566012497921>',
            'Magia': '<:magic:499707566205566976>',
            'Culinária': '<:cookingskill:499707566167687169>',
            'Corte de Lenha': '<:woodcutting:499707566410956800>',
            'Arco e Flecha': '<:fletching:499707566280933376>',
            'Pesca': '<:fishing:499707566067286018>',
            'Arte do Fogo': '<:firemaking:499707566260224001>',
            'Artesanato': '<:crafting:499707566184726539>',
            'Metalurgia': '<:smithing:499707566335459328>',
            'Mineração': '<:mining:499707566201503768>',
            'Herbologia': '<:herblore:499707566272544778>',
            'Agilidade': '<:agility:499707566192984094>',
            'Roubo': '<:thieving:499707566096646167>',
            'Extermínio': '<:slayer:499707566360625152>',
            'Agricultura': '<:farming:499707566197047306>',
            'Criação de Runas': '<:runecrafting:499707566226669568>',
            'Caça': '<:hunter:499707566197047316>',
            'Construção': '<:constructionskill:499707565949583361>',
            'Evocação': '<:summoning:499707566335459368>',
            'Dungeon': '<:dungeoneering:499707566268612619>',
            'Divinação': '<:divination:499707566348304404>',
            'Invenção': '<:invention:499707566419607552>'
        }

        skill_types = {
            'Combate': [
                'Ataque', 'Força', 'Defesa', 'Combate á Distância',
                'Oração', 'Magia', 'Constituição', 'Evocação'],
            'Subsistência': [
                'Mineração', 'Pesca', 'Corte de Lenha', 'Agricultura', 'Agricultura', 'Caça', 'Divinação'
            ],
            'Manuais': [
                'Herbologia', 'Artesanato', 'Arco e Flecha', 'Metalurgia', 'Culinária',
                'Arte do Fogo', 'Criação de Runas', 'Construção'
            ],
            'Apoio': [
                'Agilidade', 'Roubo', 'Extermínio', 'Dungeon'
            ]
        }

        type_bonus = {
            'Apoio': "• Nenhuma penalidade de EXP ao morrer treinando Dungeon\n"
                     "• Mais saques e chance de receber totens na abertura de cofres\n"
                     "• Todas as tarefas de Extermínio funcionam como se você tivesse fichas VIP",
            'Combate': "• +1 talismã sempre que forem largados\n"
                       "• Custo reduzido de instâncias\n"
                       "• 1 restauração automática de pontos vitais por rodada nas Masmorras de Elite",
            'Subsistência': "• 10% de chance de não esgotar recursos das Ilhas Inexploradas\n"
                            "• Os locais de treinamento mudam de lugar com menos frequência no Salão de Memórias\n"
                            "• 10% mais feijões ao vender itens no Projeto de Obra Rural",
            'Manuais': "• Chance reduzida de queimar comida*\n"
                       "• 2,5% a mais de chance de economizar um ingrediente secundário ao preparar poções*\n"
                       "• Aparecimento mais frequente de nodos e o dobro de recompensas no Runiverso",

        }

        days = {
            10: {
                12: 'Apoio',
                14: 'Manuais',
                16: 'Combate',
                18: 'Subsistência',
                20: 'Apoio',
                22: 'Manuais'
            },
            11: {
                0: 'Subsistência',
                2: 'Apoio',
                4: 'Manuais',
                6: 'Combate',
                8: 'Subsistência',
                10: 'Apoio',
                12: 'Manuais',
                14: 'Combate',
                16: 'Subsistência',
                18: 'Apoio',
                20: 'Manuais',
                22: 'Combate'
            },
            12: {
                0: 'Apoio',
                2: 'Manuais',
                4: 'Combate',
                6: 'Subsistência',
                8: 'Apoio',
                10: 'Manuais',
                12: 'Combate',
                14: 'Subsistência',
                16: 'Apoio',
                18: 'Manuais',
                20: 'Combate',
                22: 'Subsistência'
            },
            13: {
                0: 'Manuais',
                2: 'Combate',
                4: 'Subsistência',
                6: 'Apoio',
                8: 'Manuais',
                10: 'Combate',
            },
        }

        now = datetime.datetime.utcnow()
        current_schedule = days.get(now.day)

        if now.month == 5 and current_schedule:
            current_type = current_schedule.get(now.hour)
            if not current_type:
                current_type = current_schedule.get(now.hour - 1)
            if current_type:
                channel_id = self.bot.setting.chat.get('vos')
                channel: discord.TextChannel = self.bot.get_channel(channel_id)
                if channel:
                    with self.bot.db_session() as session:
                        state: SongOfSerenState = session.query(SongOfSerenState).first()
                        if state:
                            message_id = state.message_id
                        if not state:
                            message = await channel.send('.')
                            message_id = message.id
                            state = SongOfSerenState(activated=True, message_id=message.id)
                            session.add(state)
                            session.commit()

                        message: discord.Message = await channel.fetch_message(int(message_id))
                        content = None
                        if current_type not in message.content:
                            if current_type == 'Combate':
                                content = 'Combate - <@&576415564105515011>'
                            elif current_type == 'Subsistência':
                                content = 'Subsistência - <@&576415463865843712>'
                            elif current_type == 'Apoio':
                                content = 'Apoio - <@&576415360908001310>'
                            elif current_type == 'Manuais':
                                content = 'Manuais - <@&576415565997015040>'
                            if current_type == 'Subsistência':
                                color = discord.Color.from_rgb(139, 69, 19)
                            elif current_type == 'Manuais':
                                color = discord.Color.orange()
                            elif current_type == 'Combate':
                                color = discord.Color.red()
                            else:
                                color = discord.Color.blue()  # Apoio
                            proxima = current_schedule.get(now.hour + 1)
                            if proxima == current_type:
                                proxima = current_schedule.get(now.hour + 2)
                            if not proxima:
                                proxima = current_schedule.get(now.hour + 3)

                            description = (f"**Tipo:** {current_type}\n"
                                           f"**Próxima:** {proxima}\n\n**Bônus:**\n"
                                           f"{type_bonus.get(current_type)}\n")

                            embed = discord.Embed(title="Canção de Seren Atual", description=description, color=color)

                            nb = '\u200B'
                            embed.add_field(name="1.5x Exp nas Habilidades Abaixo: ", value=nb, inline=False)
                            for skill in skill_types.get(current_type):
                                embed.add_field(name=f"{emoji.get(skill)} {skill}", value=nb, inline=True)

                            text = "Bõnus marcados com * não funcionam para jogadores do Modo independente"
                            embed.set_footer(text=text)

                            await message.edit(content=content, embed=embed)

    @staticmethod
    def save_combined(image_names: List[str]) -> (str, str):
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

    def get_voices(self) -> (str, str):
        time_line = self.bot.twitter_api.GetUserTimeline(screen_name='jagexclock')
        for tweet in time_line:
            pattern = r'The Voice of Seren is now active in the (.+?) and (.+?) districts at .+? UTC.'
            match = re.match(pattern, tweet.text)
            if match:
                return match.groups()

    def vos_embed(self, vos_1: str, vos_2: str) -> (discord.Embed, discord.File):
        image_path, image_name = self.save_combined([vos_1, vos_2])

        image_file = discord.File(image_path, filename=image_name)

        url = "https://rs.wiki/vos#Known_effects"
        text = f'A [Voz de Seren]{url} está ativa nos distritos de **{vos_1}** e **{vos_2}**'
        embed = discord.Embed(title="Voz de Seren", description=text, color=discord.Color.blue())
        embed.set_thumbnail(url=f"attachment://{image_name}")

        return embed, image_file

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
                        message: discord.Message = await channel.fetch_message(int(state.message_id))

                        vos_1, vos_2 = self.get_voices()
                        embed, file = self.vos_embed(vos_1, vos_2)

                        print(f"Updating VoS to: {vos_1}, {vos_2}")

                        role_1 = self.bot.setting.role.get(vos_1.lower())
                        role_2 = self.bot.setting.role.get(vos_2.lower())

                        mentions = ''
                        if role_1:
                            mentions += f"<@&{role_1}> "
                        if role_2:
                            mentions += f"<@&{role_2.mention}>"

                        await message.edit(embed=embed)
                        await channel.send(content=mentions, delete_after=5 * 60)

                        state.current_voice_one = vos_1
                        state.current_voice_two = vos_2
                        state.updated = now
                        session.commit()
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

    @commands.command(aliases=['vos'])
    async def voice_of_seren(self, ctx: commands.Context):
        vos_1, vos_2 = self.get_voices()
        embed, file = self.vos_embed(vos_1, vos_2)

        await ctx.send(file=file, embed=embed)


def setup(bot):
    bot.add_cog(Vos(bot))
