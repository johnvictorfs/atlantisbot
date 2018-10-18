# Standard lib imports
import datetime

# Non-standard imports
import discord

# Local imports
import definesettings as setting


class WelcomeMessage:

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def on_member_join(member):
        print(f"{member} joined the server at {datetime.datetime.today()}")
        if 'discord.gg' in member.name or 'discord.me' in member.name:
            print(f"Banned {member} for having a server invite in username at {datetime.datetime.today()}.")
            await member.send("Olá, não permitimos usuários com convites para qualquer Servidor de Discord em seu nome para evitar Bots de Spam.\nCaso deseja entrar no nosso servidor, por favor retire o convite de seu usuário.")
            await member.kick(reason="Automated Kick: Server invite in username.")
            return
        print('passed')
        tags_do_server = setting.MESSAGES["chat"]["tags_do_server"]
        visitantes = setting.MESSAGES["chat"]["visitantes"]
        discord_bots = setting.MESSAGES["chat"]["discord_bots"]
        links_pvm = setting.MESSAGES["chat"]["links_pvm"]
        raids = setting.MESSAGES["chat"]["raids"]
        pvmemes = setting.MESSAGES["chat"]["pvmemes"]

        welcome_embed = discord.Embed(
            title=f"{member.name}, Bem vindo ao Discord do Atlantis!",
            description="",
            color=discord.Color.blue()
        )

        welcome_embed.add_field(
            name="Você recebeu o cargo de `convidado`",
            value=f"Caso seja um membro do Atlantis, digite `{setting.PREFIX}membro` no canal {visitantes}",
            inline=False
        )

        welcome_embed.add_field(
            name=f"**Veja alguns chats do Servidor:**",
            value=f"⯈ {tags_do_server} para info sobre os Roles do server\n"
                  f"⯈ {links_pvm} para informações úteis sobre PvM\n"
                  f"⯈ {pvmemes} para conversas gerais ou notificar trips de PvM\n"
                  f"⯈ {discord_bots} para comandos de Bots\n"
                  f"⯈ {raids} para aplicar para os Raids do Clã (Membros apenas)\n",
            inline=False
        )

        welcome_embed.add_field(
            name="Convite para esse discord",
            value="<https://discord.me/atlantis>",
            inline=False
        )

        welcome_embed.add_field(
            name=f"Alguma reclamação/elogio/outro? Fale conosco!",
            value=f"<http://tiny.cc/atlantisouvidoria>"
        )

        welcome_embed.set_footer(
            text=f"Digite {setting.PREFIX}atlcommands para ver os meus comandos!")

        await member.send(embed=welcome_embed)

        print(f'> {member} joined {member.guild} at {member.joined_at}')
        print("    - Answer sent.")


def setup(bot):
    bot.add_cog(WelcomeMessage(bot))
