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
            setting.PREFIX,
            right_emoji=right_e
        ))

        print(f'> {member} joined {member.guild} at {member.joined_at}')
        print("    - Answer sent.")


def setup(bot):
    bot.add_cog(WelcomeMessage(bot))
