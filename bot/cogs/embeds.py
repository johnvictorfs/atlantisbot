# Non-Standard lib imports
import discord

# Local imports
from bot import definesettings as setting

role = {
    'pvmemos': '<@&338221796748820502>',
    'vorago': '<@&386575400064516097>',
    'raids': '<@&376410304277512192>',
    'durzag': '<@&488121068834258954>',
    'raids_teacher': '<@&346107622853836801>',
    'aod_teacher': '<@&346107676448522240>',
    'rots_teacher': '<@&346107686888407043>',
    'vorago_teacher': '<@&346107810670706699>',
    '100k_dpm': '<@&348857911084187648>',
    '180k_dpm': '<@&488125956679270410>',
    'eventos': '<@&409734099800948736>',
    'admin': '<@&321015469341540352>',
    'mod': '<@&321015489583251467>',
    'bot': '<@&324359293304438787>',
    'membro': '<@&321015529059909674>',
    'convidado': '<@&321015669883797506>',
    'doador': '<@&475407948839911424>',
    'filantropo': '<@&475409267751518228>',
    'tio_patinhas': '<@&475409581481263104>',
    'fortnigth': '<@&494634882643787776>',
    'rots': '<@&497821982264655873>',
    'elite_dungeon': '<@&497550738768134183>'
}

reaction = {
    'vorago': '<:vorago:428678603476172810>',
    'pvmemos': '<:pvmemos:428679267228975105>',
    'eventos': '<:eventos:428679384954568706>',
    'durzag': '<:durzag:488178236774154240>',
    'fortnite': '<:fortnite:497821209413550109>',
    'rots': '<:rots:497822431378145291>',
    'elite_dungeons': '<:elitedungeons:497824706687139841>'
}

line_break = "-"

teacher_tags = f"{role['raids_teacher']} | {role['aod_teacher']} | {role['rots_teacher']} | {role['vorago_teacher']}"
dpm_tags = f"{role['100k_dpm']} -> {role['180k_dpm']}"

bots_mention = "<#321012588924370945>"
raids_mention = "<#393104367471034369>"
durzag_mention = "<#488112229430984704>"


def get_general_embed():
    general_embed = discord.Embed(title="Tags Gerais",
                                  description="",
                                  color=discord.Colour.dark_blue())
    general_embed.add_field(name=line_break,
                            value=f"{role['eventos']}\n"
                                  f" Notificações de Eventos Gerais do Clã",
                            inline=False)
    general_embed.add_field(name=line_break,
                            value=f"{role['admin']}\n"
                                  f" Maior rank da Administração do Discord, geralmente Fiscais+",
                            inline=False)
    general_embed.add_field(name=line_break,
                            value=f"{role['mod']}\n"
                                  f" Administradores+ do Clã, moderadores do Discord",
                            inline=False)
    general_embed.add_field(name=line_break,
                            value=f"{role['bot']}\n"
                                  f" Bots",
                            inline=False)
    general_embed.add_field(name=line_break,
                            value=f"{role['membro']}\n"
                                  f" Dado para membros do Clã. Caso seja um digite `{setting.PREFIX}membro` no chat"
                                  f" {bots_mention}",
                            inline=False)
    general_embed.add_field(name=line_break,
                            value=f"{role['convidado']}\n"
                                  f" Dado para todos que entram no servidor, ver acima caso seja um Membro do Clã",
                            inline=False)
    general_embed.add_field(name=line_break,
                            value=f"{role['fortnigth']}\n"
                                  f" Notificações para jogos de Fortnite")
    general_embed.add_field(name="Tags de Doação para o Clã:",
                            value=f"{role['doador']} *(20m)* \n"
                                  f" {role['filantropo']} *(50m)* \n"
                                  f" {role['tio_patinhas']} *(100m)* \n"
                                  f" `Título Personalizado` *(500m)*\n"
                                  f"Mais info: <http://rsatlantis.com/maiores-doadores>",
                            inline=False)
    general_embed.set_footer(text="Para receber ou remover as Tags livres, use as reações na mensagem abaixo.")
    return general_embed


def get_pvm_embed():
    pvm_embed = discord.Embed(title="Tags de PvM",
                              description="",
                              color=discord.Color.dark_red())
    pvm_embed.add_field(name=line_break,
                        value=f"{role['pvmemos']}\n"
                              f" Notificação de qualquer tipo de Evento/Trip PvM",
                        inline=False)
    pvm_embed.add_field(name=line_break,
                        value=f"{role['vorago']}\n"
                              f" Notificações de trips de Vorago",
                        inline=False)
    pvm_embed.add_field(name=line_break,
                        value=f"{role['rots']}\n"
                              f" Notificações de trips de Rots",
                        inline=False)
    pvm_embed.add_field(name=line_break,
                        value=f"{role['elite_dungeon']}\n"
                              f" Notificações de trips de Elite Dungeons 1 ou 2",
                        inline=False)
    pvm_embed.add_field(name=line_break,
                        value=f"{role['raids']}\n"
                              f" Notificações de Raids do Clã - Aplique aqui {raids_mention}",
                        inline=False)
    pvm_embed.add_field(name=line_break,
                        value=f"{role['durzag']}\n"
                              f" Notificação de eventos de Beastmaster Durzag do Clã - {durzag_mention}",
                        inline=False)
    pvm_embed.add_field(name=line_break,
                        value=f"{teacher_tags}\n"
                              f" Dado pra proeficientes em bosses, tague eles para perguntas sobre pvm! :)",
                        inline=False)
    pvm_embed.add_field(name=line_break,
                        value=f"{dpm_tags}\n"
                              f" Ganho por fazer uma determinada quantidade de DPM em gemas de desafio, "
                              f"veja: https://i.imgur.com/oY29HL7.png",
                        inline=False)
    pvm_embed.set_footer(text="Para receber ou remover as Tags livres, use as reações na mensagem abaixo.")
    return pvm_embed


def get_reactions_embed():
    reactions_embed = discord.Embed(title="Obter Tags",
                                    description="Use as reações abaixo para receber ou remover as respectivas tags.",
                                    color=discord.Colour.dark_blue())
    reactions_embed.add_field(name=reaction['vorago'],
                              value=role['vorago'],
                              inline=True)
    reactions_embed.add_field(name=reaction['pvmemos'],
                              value=role['pvmemos'],
                              inline=True)
    reactions_embed.add_field(name=f"\n{reaction['eventos']}",
                              value=role['eventos'],
                              inline=True)
    reactions_embed.add_field(name=reaction['durzag'],
                              value=role['durzag'],
                              inline=True)
    reactions_embed.add_field(name=reaction['rots'],
                              value=role['rots'],
                              inline=True)
    reactions_embed.add_field(name=reaction['fortnite'],
                              value=role['fortnigth'],
                              inline=True)
    return reactions_embed
