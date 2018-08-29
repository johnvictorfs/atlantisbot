# Local imports
import definesettings as setting


class WelcomeMessage:

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def on_member_join(member):
        message = setting.MESSAGES["welcome_message"]
        tags_do_server = setting.MESSAGES["chat"]["tags_do_server"]
        visitantes = setting.MESSAGES["chat"]["visitantes"]
        discord_bots = setting.MESSAGES["chat"]["discord_bots"]
        links_pvm = setting.MESSAGES["chat"]["links_pvm"]
        raids = setting.MESSAGES["chat"]["raids"]
        pvmemes = setting.MESSAGES["chat"]["pvmemes"]
        ouvidoria = setting.MESSAGES["link"]["atlantis_ouvidoria"]
        right_e = setting.MESSAGES["emoji"]["arrow_emoji"]

        await member.send(message.format(
            str(member),
            tags_do_server,
            visitantes,
            discord_bots,
            tags_do_server,
            links_pvm,
            raids,
            pvmemes,
            ouvidoria,
            right_emoji=right_e
        ))

        meus_comandos = (f"{right_e} **Meus comandos:** (Você pode os enviar por aqui)"
                         "\n\n"
                         f"{right_e} `{setting.PREFIX}claninfo` `nome de jogador` - Informações de Clã sobre um jogador"
                         f"\n\n"
                         f"{right_e} `{setting.PREFIX}role` - Aplicar para o role de Membro no servidor, caso seja"
                         f" um membro do Clã."
                         f"\n\n"
                         f"{right_e} `{setting.PREFIX}raids` - Aplicar para o role de Raids no servidor, caso"
                         f" queira participar dos Raids do Clã (Membros apenas).")

        await member.send(meus_comandos)

        print(f'> {member} joined {member.guild} at {member.joined_at}')


def setup(bot):
    bot.add_cog(WelcomeMessage(bot))
