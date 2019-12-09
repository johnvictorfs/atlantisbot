import rs3clans
import discord
from discord.ext import commands
from sqlalchemy.sql.expression import func

from bot.bot_client import Bot
from bot.orm.models import AmigoSecretoPerson, AmigoSecretoState
from bot.utils.tools import has_any_role
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
    async def send_amigo_secreto_messages(self, ctx: Context, dia: str, test: bool):
        with self.bot.db_session() as session:
            query = session.query(AmigoSecretoPerson).filter(AmigoSecretoPerson.giving_to_id.isnot(None)).all()
            if not query:
                return await ctx.send("Não há nenhuma mensagem de Amigo Secreto para enviar.")
            dev = self.bot.get_user(self.bot.setting.developer_id)
            for member in query:
                user = self.bot.get_user(int(member.discord_id))
                if not user:
                    await dev.send(
                        f'Erro ao enviar mensagem do AS para {member.discord_name} ({member.id}). Não existe')
                    continue
                try:
                    giving_to = session.query(AmigoSecretoPerson).get(member.giving_to_id)
                    embed = discord.Embed(
                        title="Olá, seu amigo secreto foi sorteado:",
                        description=f"<@{giving_to.discord_id}> ({giving_to.discord_name})",
                        color=discord.Color.green()
                    )
                    ingame_name = giving_to.ingame_name.replace(' ', '%20')
                    icon_url = f"https://secure.runescape.com/m=avatar-rs/{ingame_name}/chat.png"
                    embed.set_author(name=f"{giving_to.ingame_name}", icon_url=icon_url)
                    embed.set_footer(text=f"Evento: {dia}/12 às 18:00 - Tenha seu presente em mãos até lá!")
                    embed.set_thumbnail(url=self.bot.setting.banner_image)
                    if test:
                        await dev.send(embed=embed)
                        break
                    await user.send(embed=embed)
                    await dev.send(f"Sucesso: {member.id} - <@{member.discord_id}>")
                except Exception as e:
                    await dev.send(f'{e} ao enviar mensagem do Amigo Secreto para {member.discord_name} ({member.id}).')
        return await ctx.send("Todas as mensagens foram enviadas.")

    @commands.is_owner()
    @commands.command()
    async def roll_amigo_secreto(self, ctx: Context):
        with self.bot.db_session() as session:
            query = session.query(AmigoSecretoPerson).order_by(func.random()).all()
            query_count = session.query(AmigoSecretoPerson).count()
            if not query:
                return await ctx.send("Não há nenhuma pessoa cadastrada no Amigo Secreto.")

            if query_count < 2:
                return await ctx.send("Há apenas uma pessoa cadastrada no Amigo Secreto. Deixe ela se presentear.")

            for person in query:
                if not person.giving_to_id:
                    to_give = session.query(AmigoSecretoPerson).filter(
                        AmigoSecretoPerson.receiving.is_(False), AmigoSecretoPerson.id != person.id).first()
                    if not to_give:
                        continue
                    to_give.receiving = True
                    person.giving_to_id = to_give.id
                    person.giving_to_name = to_give.discord_name
                    session.commit()

            left_receiver = session.query(AmigoSecretoPerson).filter(AmigoSecretoPerson.receiving.is_(False)).first()
            left_giver = session.query(AmigoSecretoPerson).filter(AmigoSecretoPerson.giving_to_id.is_(None)).first()

            if (left_giver and not left_receiver) or (not left_giver and left_receiver):
                return await ctx.send("Algo deu errado ao tentar montar o Amigo Secreto. Tente novamente.")

            if left_receiver and left_giver:
                left_receiver.receiving = True
                left_giver.giving_to_id = left_receiver.id
                left_giver.giving_to_name = left_receiver.discord_name
                session.commit()
        return await ctx.send("Amigo secreto montado com sucesso!")

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
                end_date = f"no dia {state.end_date.strftime('%d/%m')}"
            else:
                end_date = "quando os Amigos Secretos forem sorteados!"

            return await ctx.send(
                f"{ctx.author.mention}, você foi cadastrado no Amigo Secreto do Atlantis com sucesso! :)\n"
                f"Uma mensagem será enviada pra você no privado do Discord com o nome do seu Amigo Secreto {end_date}"
            )


def setup(bot):
    bot.add_cog(AmigoSecreto(bot))
