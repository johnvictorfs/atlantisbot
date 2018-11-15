import datetime

import discord


class WelcomeMessage:

    def __init__(self, bot):
        self.bot = bot

    async def on_member_join(self, member):
        print(f'> {member} joined the server {member.guild} at {member.joined_at}')
        for name in self.bot.setting.not_allowed_in_name:
            if name in member.name:
                print(f"Kicked {member} for having a not allowed string '{name}' in in username at "
                      f"{datetime.datetime.today()}.")
                await member.kick(reason="Automated Kick: Server invite in username.")
                return await member.send(f"Você foi expulso do servidor por ter uma string não permitida no seu nome. "
                                         f"({name}) Caso deseja entrar no servidor, por favor a remova.")
        tags_do_server = self.bot.setting.chat.get('tags_do_server')
        visitantes = self.bot.setting.chat.get('visitantes')
        discord_bots = self.bot.setting.chat.get('discord_bots')
        links_uteis = self.bot.setting.chat.get('links_uteis')
        raids = self.bot.setting.chat.get('raids')
        pvmemes = self.bot.setting.chat.get('pvmemes')

        welcome_embed = discord.Embed(
            title=f"{member.name}, Bem vindo ao Discord do Atlantis!",
            description="",
            color=discord.Color.blue()
        )

        welcome_embed.add_field(
            name="Você recebeu o cargo de `convidado`",
            value=f"Caso seja um membro do Atlantis, digite `{self.bot.setting.prefix}membro` no canal {visitantes}",
            inline=False
        )

        welcome_embed.add_field(
            name=f"**Veja alguns chats do Servidor:**",
            value=f"⯈ {tags_do_server} para info sobre os Roles do server\n"
                  f"⯈ {links_uteis} para links úteis gerais (principalmente PvM)\n"
                  f"\n"
                  f"⯈ {pvmemes} para conversas gerais ou notificar trips de PvM\n"
                  f"⯈ {raids} para aplicar para os Raids do Clã (Membros apenas)\n"
                  f"\n"
                  f"⯈ {discord_bots} para comandos de Bots\n",
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
            text=f"Digite {self.bot.setting.prefix}atlbot para ver os meus comandos!")
        return await member.send(embed=welcome_embed)


def setup(bot):
    bot.add_cog(WelcomeMessage(bot))
