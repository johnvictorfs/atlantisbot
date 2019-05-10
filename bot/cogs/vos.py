import asyncio
import discord
from discord.ext import commands

import datetime

from bot.bot_client import Bot
from bot.orm.models import SongOfSerenState


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


class Vos(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.song_of_seren_task = self.bot.loop.create_task(self.song_of_seren())

    def cog_unload(self):
        self.song_of_seren_task.cancel()

    async def song_of_seren(self):
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

        while True:
            now = datetime.datetime.utcnow()
            current_schedule = days.get(now.day)

            if now.month == 5 and current_schedule:
                current_type = current_schedule.get(now.hour)
                if not current_type:
                    current_type = current_schedule.get(now.hour + 1)
                if current_type:
                    channel_id = self.bot.setting.chat.get('vos')
                    channel: discord.TextChannel = self.bot.get_channel(channel_id)
                    if not channel:
                        continue

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

                        if current_type == 'Subsistência':
                            color = discord.Color.from_rgb(139, 69, 19)
                        elif current_type == 'Manuais':
                            color = discord.Color.orange()
                        elif current_type == 'Combate':
                            color = discord.Color.red()
                        else:
                            color = discord.Color.blue()  # Apoio
                        description = f"**Tipo:** {current_type}\n\n**Bônus:**\n{type_bonus.get(current_type)}\n"
                        embed = discord.Embed(title="Canção de Seren Atual", description=description, color=color)
                        nb = '\u200B'
                        embed.add_field(name="1.5x Exp nas Habilidades Abaixo: ", value=nb, inline=False)
                        for skill in skill_types.get(current_type):
                            embed.add_field(name=f"{emoji.get(skill)} {skill}", value=nb, inline=True)
                        embed.set_footer(text="Bõnus marcados com * não funcionam para jogadores do Modo independente")
                        await message.edit(content=None, embed=embed)
            await asyncio.sleep(5)


def setup(bot):
    bot.add_cog(Vos(bot))
