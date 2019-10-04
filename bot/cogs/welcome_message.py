from discord.ext import commands
import discord
import aiohttp

from bot.bot_client import Bot
from bot.cogs.authentication import get_user_data
from bot.orm.models import User


class WelcomeMessage(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        if ctx.author.id == self.bot.setting.developer_id:
            return True
        if self.bot.setting.mode == 'dev':
            return False
        return True

    @commands.command(aliases=['testwelcome'])
    async def test_welcome_message(self, ctx: commands.Context):
        await ctx.author.send(embed=self.welcome_embed(ctx.author))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"'{member}' joined the server '{member.guild}' at {member.joined_at}")
        if member.guild.id != self.bot.setting.guild_id:
            print('Not sending welcome message. Not in main guild.')
            return
        if self.bot.setting.mode == 'dev':
            print("Development mode is on. Not sending welcome message.")
            return
        membro: discord.Role = member.guild.get_role(self.bot.setting.role.get('membro'))
        convidado: discord.Role = member.guild.get_role(self.bot.setting.role.get('convidado'))

        with self.bot.db_session() as session:
            user = session.query(User).filter_by(discord_id=str(member.id)).first()
            if user:
                async with aiohttp.ClientSession() as cs:
                    user_data = await get_user_data(user.ingame_name, cs)
                if user_data.get('clan') == self.bot.setting.clan_name:
                    await member.add_roles(membro)
                    await member.remove_roles(convidado)

        for name in self.bot.setting.not_allowed_in_name:
            if name in member.name.lower():
                print(f"Kicked {member} for having a not allowed string '{name}' in username.")
                try:
                    await member.send(f"Você foi expulso do servidor por ter um nome não permitida em seu usuário. "
                                      f"({name}) Caso deseje entrar no servidor, por favor a remova.")
                except Exception:
                    print(f"No permission to send private message to {member.name}")
                return await member.kick(reason=f"Kick automático. String não permitida no usuário. ({name})")
        return await member.send(embed=self.welcome_embed(member))

    def welcome_embed(self, member):
        tags_do_server = self.bot.setting.chat.get('tags_do_server')
        geral = self.bot.setting.chat.get('geral')
        discord_bots = self.bot.setting.chat.get('discord_bots')
        links_uteis = self.bot.setting.chat.get('links_uteis')
        raids = self.bot.setting.chat.get('raids')
        aod = self.bot.setting.chat.get('aod')
        solak = self.bot.setting.chat.get('solak')
        pvmemes = self.bot.setting.chat.get('pvmemes')

        prefix = self.bot.setting.prefix

        welcome_embed = discord.Embed(
            title=f"{member.name}, Bem vindo ao Discord do Atlantis!",
            description="",
            color=discord.Color.blue()
        )

        welcome_embed.set_thumbnail(
            url=self.bot.setting.banner_image
        )

        welcome_embed.add_field(
            name="Você recebeu o cargo de `convidado`",
            value=f"Caso seja um **membro do Clã**, digite **`{prefix}membro`** aqui",
            inline=False
        )

        welcome_embed.add_field(
            name=f"**Conheça alguns chats do Servidor:**",
            value=f"⯈ <#{tags_do_server}> para info sobre os Roles do servidor\n"
                  f"⯈ <#{links_uteis}> para links úteis gerais (principalmente PvM)\n"
                  f"\n"
                  f"⯈ <#{geral}> para conversas gerais (Membros)"
                  f"\n"
                  f"⯈ <#{pvmemes}> para conversas assuntos de PvM\n"
                  f"⯈ <#{raids}> para aplicar para os Raids do Clã (Membros)\n"
                  f"⯈ <#{aod}> para aplicar para os times de AoD do Clã (Membros)\n"
                  f"⯈ <#{solak}> para aplicar para os times de Solak do Clã (Membros)\n"
                  f"\n"
                  f"⯈ <#{discord_bots}> para comandos de Bots\n",
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
            text=f"Digite {prefix}atlbot para ver os meus comandos!")
        return welcome_embed


def setup(bot):
    bot.add_cog(WelcomeMessage(bot))
