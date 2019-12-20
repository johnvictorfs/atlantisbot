import discord
from discord.ext import commands

from datetime import timedelta

from bot.bot_client import Bot
from bot.orm.models import AmigoSecretoPerson, AmigoSecretoState, User
from bot.utils.tools import has_any_role, format_and_convert_date
from bot.utils.checks import is_authenticated
from bot.utils.context import Context


class AmigoSecreto(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def toggle_amigo_secreto(self, ctx: Context):
        with self.bot.db_session() as session:
            state = session.query(AmigoSecretoState).first()
            if not state:
                state = AmigoSecretoState(activated=True)
                session.add(state)
                session.commit()
                session.close()
                return await ctx.send("Amigo Secreto do Atlantis agora está ativo.")
            state.activated = not state.activated
            session.commit()
            await ctx.send(f"O Amigo Secreto do Atlantis agora está {'ativo' if state.activated else 'desativado'}.")

    @commands.is_owner()
    @commands.command()
    async def inscritos_amigo_secreto(self, ctx: Context):
        with self.bot.db_session() as session:
            embed = discord.Embed(
                title="Inscritos no Amigo Secreto",
                description="Evento dia: 21/12",
                color=discord.Color.green()
            )
            for member in session.query(AmigoSecretoPerson).all():
                embed.add_field(
                    name=member.ingame_name,
                    value=f"<@{member.discord_id}> ({member.discord_name})",
                    inline=False
                )
            embed.set_thumbnail(url=self.bot.setting.banner_image)
        return await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def clear_amigo_secreto(self, ctx: Context):
        with self.bot.db_session() as session:
            deleted = session.query(AmigoSecretoPerson).delete()
            session.commit()
            await ctx.send(f"{deleted} linhas deletadas com sucesso.")

    @commands.is_owner()
    @commands.command()
    async def null_amigo_secreto(self, ctx: Context):
        with self.bot.db_session() as session:
            query = session.query(AmigoSecretoPerson).all()
            for member in query:
                member.giving_to_id = None
                member.giving_to_name = None
                member.receiving = False
            session.commit()
            return await ctx.send("Reinicializado Amigo Secreto com sucesso.")

    @commands.is_owner()
    @commands.command()
    async def send_amigo_secreto_messages(self, ctx: Context, test: bool = True):
        with self.bot.db_session() as session:
            query = session.query(AmigoSecretoPerson).filter(AmigoSecretoPerson.giving_to_user_id.isnot(None)).all()

            if not query:
                return await ctx.send("Não há nenhuma mensagem de Amigo Secreto para enviar.")

            dev = self.bot.get_user(self.bot.setting.developer_id)

            if test:
                await dev.send('Enviando Mensagens do Amigo Secreto em Modo de Teste')
            else:
                confirmation = await ctx.prompt('Enviando Mensagens do Amigo Secreto em Modo de Produção, continuar?')
                if not confirmation:
                    return await dev.send('Cancelado envio de Mensagens do Amigo Secreto')

            member: AmigoSecretoPerson
            for member in query:
                giving_user: User = session.query(User).get(member.user_id)
                await dev.send(f'Tentando enviar mensagem do AS para {giving_user.discord_name} ({giving_user.id}).')

                assert giving_user.discord_id is not None
                user = self.bot.get_user(int(giving_user.discord_id))

                if not giving_user or not user and not test:
                    await dev.send(
                        f'Erro ao enviar mensagem do AS para {giving_user.discord_name} ({giving_user.id}). Não existe')
                    continue
                try:
                    giving_to = session.query(AmigoSecretoPerson).filter_by(user_id=member.giving_to_user_id).first()
                    giving_to_user: User = session.query(User).get(giving_to.user_id)

                    runeclan = f'http://runeclan.com/user/{giving_to_user.ingame_name.replace(" ", "+")}'

                    description = (
                        f"<@{giving_to_user.discord_id}> ({giving_to_user.discord_name})\n[RuneClan]({runeclan})\n\n"
                        f"Acredita que seu Amigo Secreto possa ter mudado de nome recentemente e ainda não atualizou aqui? "
                        f"Adicione-o no jogo como Amigo, e o nome que será mostrado irá ser o nome dele atualizado!"
                    )

                    embed = discord.Embed(
                        title="Olá, seu amigo secreto foi sorteado:",
                        description=description,
                        color=discord.Color.green()
                    )

                    ingame_name = giving_to_user.ingame_name.replace(' ', '%20')
                    icon_url = f"https://secure.runescape.com/m=avatar-rs/{ingame_name}/chat.png"
                    embed.set_author(name=f"{giving_to_user.ingame_name}", icon_url=icon_url)

                    state: AmigoSecretoState = session.query(AmigoSecretoState).first()

                    assert state.end_date is not None

                    embed.set_footer(
                        text=f"Evento: {format_and_convert_date(state.end_date)} - Tenha seu presente em mãos até lá!"
                    )
                    embed.set_thumbnail(url=self.bot.setting.banner_image)

                    if test:
                        await dev.send(embed=embed)
                    else:
                        await user.send(embed=embed)
                    await dev.send(f"Sucesso: {member.id} - <@{giving_user.discord_id}> ({giving_user.id})")
                except Exception as e:
                    await dev.send(f'{e} ao enviar mensagem do Amigo Secreto para {giving_user.discord_name} ({giving_user.id}).')

        return await ctx.send("Todas as mensagens foram enviadas.")

    @commands.is_owner()
    @commands.command()
    async def check_amigo_secreto(self, ctx: Context):
        with self.bot.db_session() as session:
            state = session.query(AmigoSecretoState).first()
            if not state:
                state = AmigoSecretoState(activated=False)
                session.add(state)
                session.commit()
            current_state = state.activated
            if not current_state:
                return await ctx.send("O Amigo Secreto do Atlantis não está ativo.")
        return await ctx.send("O Amigo Secreto do Atlantis está ativo.")

    @commands.check(is_authenticated)
    @commands.command(aliases=['amigosecreto', 'amigo'])
    async def amigo_secreto(self, ctx: Context):
        dev = self.bot.get_user(self.bot.setting.developer_id)
        await dev.send(f'{ctx.author} está se inscrevendo no amigo secreto.')

        with self.bot.db_session() as session:
            state = session.query(AmigoSecretoState).first()

            if not state:
                state = AmigoSecretoState(activated=False)
                session.add(state)
                session.commit()

            if not state.activated:
                return await ctx.send(f"{ctx.author.mention}, o Amigo Secreto do Atlantis ainda não está ativo.")

            session.expunge(state)

        user = ctx.get_user()

        if not user:
            raise Exception('Varíavel \'user\' é None')

        atlantis = self.bot.get_guild(self.bot.setting.server_id)
        member = atlantis.get_member(ctx.author.id)

        if not member:
            return await ctx.send(
                f"{ctx.author.mention}, é necessário estar no Servidor do Atlantis "
                f"para participar do Amigo Secreto\nhttps://discord.me/atlantis"
            )

        allowed_role_list = ['membro', 'mod_trial', 'mod', 'mod+', 'admin']
        allowed_roles = [self.bot.setting.role.get(role) for role in allowed_role_list]

        if not has_any_role(member, *allowed_roles):
            return await ctx.send(
                f"{ctx.author.mention}, você precisa ser um Membro do Clã para participar do Amigo Secreto."
            )

        with self.bot.db_session() as session:
            exists = session.query(AmigoSecretoPerson).filter_by(user_id=user.id).first()

            if exists:
                session.close()
                await ctx.send(f"{ctx.author.mention}, você já está cadastrado no Amigo Secreto!")
                return await dev.send(f'{ctx.author}: Inscrição cancelada. Já está no Amigo Secreto.')

            session.add(AmigoSecretoPerson(user_id=user.id))
            session.commit()

            await dev.send(
                f'{ctx.author} foi cadastrado no Amigo Secreto com sucesso ({user})'
            )

            if state.end_date:
                minus_two_days = state.end_date - timedelta(days=2)
                end_date = f"no dia {minus_two_days.strftime('%d/%m')}"
            else:
                end_date = "quando os Amigos Secretos forem sorteados!"

            return await ctx.send(
                f"{ctx.author.mention}, você foi cadastrado no Amigo Secreto do Atlantis com sucesso! :)\n"
                f"Uma mensagem será enviada pra você no privado do Discord com o nome do seu Amigo Secreto {end_date}"
            )


def setup(bot):
    bot.add_cog(AmigoSecreto(bot))
