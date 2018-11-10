import discord

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


def get_general_embed(role, prefix, chat):
    general_embed = discord.Embed(
        title="Tags Gerais",
        description="",
        color=discord.Colour.dark_blue())
    general_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('eventos')}>\n"
              f" Notificações de Eventos Gerais do Clã",
        inline=False)
    general_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('admin')}>\n"
              f"Administração do Discord, não diretamente relacionado com Ranks do jogo",
        inline=False)
    general_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('mod')}>\n"
              f" Administradores+ do Clã, moderadores do Discord",
        inline=False)
    general_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('bot')}>\n"
              f" Bots",
        inline=False)
    general_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('membro')}>\n"
              f" Dado para membros do Clã. Caso seja um digite `{prefix}membro` no chat"
              f" <#{chat.get('discord_bots')}>",
        inline=False)
    general_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('convidado')}>\n"
              f" Dado para todos que entram no servidor, ver acima caso seja um Membro do Clã",
        inline=False)
    general_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('fortnight')}>\n"
              f" Notificações para jogos de Fortnite")
    general_embed.add_field(
        name="Tags de Doação para o Clã:",
        value=f"<@&{role.get('doador')}> *(20m)* \n"
              f" <@&{role.get('filantropo')}> *(50m)* \n"
              f" <@&{role.get('tio_patinhas')}> *(100m)* \n"
              f" <@&{role.get('lannister')}> *(200m)* \n"
              f" <@&{role.get('smaug')}> *(350m)* \n"
              f" `Título Personalizado` *(500m)*\n"
              f"Mais info: <http://rsatlantis.com/maiores-doadores>",
        inline=False)
    general_embed.set_footer(
        text="Para receber ou remover as Tags livres, use as reações na mensagem abaixo.")
    return general_embed


def get_pvm_embed(role, chat):
    teacher_tags = (f"<@&{role.get('raids_teacher')}> | <@&{role.get('aod_teacher')}> | "
                    f"<@&{role.get('vorago_teacher')}> | <@&{role.get('solak_teacher')}>")
    dpm_tags = f"<@&{role.get('100k_dpm')}> -> <@&{role.get('180k_dpm')}>"
    pvm_embed = discord.Embed(
        title="Tags de PvM",
        description="",
        color=discord.Color.dark_red())
    pvm_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('pvmemos')}>\n"
              f" Notificação de qualquer tipo de Evento/Trip PvM",
        inline=False)
    pvm_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('vorago')}>\n"
              f" Notificações de trips de Vorago",
        inline=False)
    pvm_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('rots')}>\n"
              f" Notificações de trips de Rots",
        inline=False)
    pvm_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('elite_dungeon')}>\n"
              f" Notificações de trips de Elite Dungeons 1 ou 2",
        inline=False)
    pvm_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('solak')}>\n"
              f" Notificações de trips de Solak - Aplique aqui <#{chat.get('solak')}>",
        inline=False)
    pvm_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('aod')}>\n"
              f" Notificações de trips de AoD - Aplique aqui <#{chat.get('aod')}>"
    )
    pvm_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('raids')}>\n"
              f" Notificações de Raids do Clã - Aplique aqui <#{chat.get('raids')}>",
        inline=False)
    pvm_embed.add_field(
        name=line_break,
        value=f"<@&{role.get('durzag')}>\n"
              f" Notificação de eventos de Beastmaster Durzag do Clã",
        inline=False)
    pvm_embed.add_field(
        name=line_break,
        value=f"{teacher_tags}\n"
              f" Dado pra proeficientes em bosses, tague eles para perguntas sobre pvm! :)",
        inline=False)
    pvm_embed.add_field(
        name=line_break,
        value=f"{dpm_tags}\n"
              f" Ganho por fazer uma determinada quantidade de DPM em gemas de desafio, "
              f"veja: https://i.imgur.com/oY29HL7.png",
        inline=False)
    pvm_embed.set_footer(text="Para receber ou remover as Tags livres, use as reações na mensagem abaixo.")
    return pvm_embed


def get_reactions_embed(role):
    reactions_embed = discord.Embed(
        title="Obter Tags",
        description="Use as reações abaixo para receber ou remover as respectivas tags.",
        color=discord.Colour.dark_blue())
    reactions_embed.add_field(
        name=reaction.get('durzag'),
        value=f"<@&{role.get('durzag')}>",
        inline=True)
    reactions_embed.add_field(
        name=reaction.get('fortnite'),
        value=f"<@&{role.get('fortnight')}>",
        inline=True)
    reactions_embed.add_field(
        name=reaction.get('vorago'),
        value=f"<@&{role.get('vorago')}>",
        inline=True)
    reactions_embed.add_field(
        name=reaction.get('rots'),
        value=f"<@&{role.get('rots')}>",
        inline=True)
    reactions_embed.add_field(
        name=reaction.get('elite_dungeons'),
        value=f"<@&{role.get('elite_dungeon')}>",
        inline=True)
    reactions_embed.add_field(
        name=reaction.get('eventos'),
        value=f"<@&{role.get('eventos')}>",
        inline=True)
    reactions_embed.add_field(
        name=reaction.get('pvmemos'),
        value=f"<@&{role.get('pvmemos')}>",
        inline=True)
    return reactions_embed
