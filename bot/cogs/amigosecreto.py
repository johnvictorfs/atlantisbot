import discord
from discord.ext import commands

from datetime import datetime, timedelta

from bot.bot_client import Bot
from bot.utils.tools import has_any_role, format_and_convert_date
from bot.utils.checks import is_authenticated, is_pedim_or_nriver
from bot.utils.context import Context

from atlantisbot_api.models import AmigoSecretoState, AmigoSecretoPerson
from django.db.models import Q

class AmigoSecreto(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.check(is_pedim_or_nriver)
    @commands.command()
    async def send_amigo_secreto_messages(self, ctx: Context, test: bool = True):
        query = AmigoSecretoPerson.objects.all()

        if not query:
            return await ctx.send(
                "Não há nenhuma mensagem de Amigo Secreto para enviar."
            )

        dev = ctx.author

        if test:
            await dev.send("Enviando Mensagens do Amigo Secreto em Modo de Teste")
        else:
            confirmation = await ctx.prompt(
                "Enviando Mensagens do Amigo Secreto em Modo de Produção, continuar?"
            )
            if not confirmation:
                return await dev.send("Cancelado envio de Mensagens do Amigo Secreto")

        for member in query:
            await dev.send(
                f"Tentando enviar mensagem do AS para {member.user.discord_name} ({member.user.id})."
            )

            assert member.user.discord_id is not None
            user = self.bot.get_user(int(member.user.discord_id))

            if not member.user or not user and not test:
                await dev.send(
                    f"Erro ao enviar mensagem do AS para {member.user.discord_name} ({member.user.id}). Não existe"
                )
                continue
            try:
                runepixels = f'http://runepixels.com/players/{member.giving_to_user.ingame_name.replace(" ", "-")}'

                description = (
                    f"<@{member.giving_to_user.discord_id}> ({member.giving_to_user.discord_name})\n"
                    f"[RunePixels]({runepixels})\n\n"
                    f"Acredita que seu Amigo Secreto possa ter mudado de nome recentemente e ainda não atualizou aqui? "
                    f"Adicione-o no jogo como Amigo, e o nome que será mostrado irá ser o nome dele atualizado!"
                )

                embed = discord.Embed(
                    title="Olá, seu amigo secreto foi sorteado:",
                    description=description,
                    color=discord.Color.green(),
                )

                ingame_name = member.giving_to_user.ingame_name.replace(" ", "%20")
                icon_url = (
                    f"https://secure.runescape.com/m=avatar-rs/{ingame_name}/chat.png"
                )
                embed.set_author(
                    name=f"{member.giving_to_user.ingame_name}", icon_url=icon_url
                )

                state = AmigoSecretoState.objects.first()
                assert state.end_date is not None

                embed.set_footer(
                    text=(
                        f"Evento: {format_and_convert_date(state.end_date)} (Horário de Brasília) "
                        f"- Tenha seu presente em mãos até lá!"
                    )
                )
                embed.set_thumbnail(url=self.bot.setting.banner_image)

                if test:
                    await dev.send(embed=embed)
                else:
                    await user.send(embed=embed)
                await dev.send(
                    f"Sucesso: {member.id} - <@{member.user.discord_id}> ({member.user.id})"
                )
            except Exception as e:
                await dev.send(
                    f"{e} ao enviar mensagem do Amigo Secreto para {member.user.discord_name} ({member.user.id})."
                )

        return await ctx.send("Todas as mensagens foram enviadas.")
    
    @staticmethod
    def clear_secret_santa():
        AmigoSecretoPerson.objects.all().update(receiving=False, giving_to_user=None)

    @staticmethod
    def delete_all_secret_santa():
        AmigoSecretoPerson.objects.all().delete()

    def roll_secret_santa(self):
        exclude: list[int] = []

        person: AmigoSecretoPerson
        for person in AmigoSecretoPerson.objects.filter(giving_to_user=None).all():
            random_recipient = self.random_person_to(person.id, exclude)

            self.bot.logger.info(person.user.ingame_name + ' is giving to ' + random_recipient.user.ingame_name)

            person.giving_to_user = random_recipient.user
            person.save()
            exclude.append(random_recipient.id)

        for person_id in exclude:
            AmigoSecretoPerson.objects.filter(id=person_id).update(receiving=True)

    @staticmethod
    def random_person_to(pk: int, exclude: list[int]) -> AmigoSecretoPerson:
        """
        Get random entry for Secret Santa, excluding people already receiving presents and the person giving himself
        """

        random_person: AmigoSecretoPerson = AmigoSecretoPerson.objects.filter(
            receiving=False
        ).filter(
            Q(receiving=False) & ~Q(id=pk) & ~Q(id__in=exclude)
        ).order_by('?').first()

        random_person.receiving = True
        random_person.save()

        return random_person

    @commands.check(is_pedim_or_nriver)
    @commands.command()
    async def roll_amigo_secreto(self, ctx: Context):
        secret_santa_state: AmigoSecretoState = AmigoSecretoState.object()

        if not secret_santa_state.end_date:
            await ctx.author.send("Data de sorteio não configurada")
            return

        not_receiving = AmigoSecretoPerson.objects.filter(receiving=False).count()

        if not_receiving == 0:
            await ctx.author.send("Nenhuma pessoa sem receber presente, amigo secreto já está montado.")
            return

        attempts = 0
        while True:
            if attempts > 3:
                await ctx.author.send("Muitas tentativas com erro. Contate NRiver.")
                return
            try:
                self.roll_secret_santa()
                break
            except Exception as e:
                self.bot.logger.error(f'Erro ao montar Amigo Secreto: {e}')
                attempts += 1
                await ctx.author.send('Erro ao montar Amigo Secreto, limpando e tentando novamente')
                self.clear_secret_santa()

        not_receiving = AmigoSecretoPerson.objects.filter(receiving=False).count()

        if not_receiving > 0:
            await ctx.author.send(
                f"Erro ao montar Amigo Secreto. Pessoas sem receber: {not_receiving}. "
                "Contate NRiver."
            )
            return

        await ctx.author.send(
            "Amigo Secreto montado com sucesso. Total de pessoas: "
            f"{AmigoSecretoPerson.objects.count()}"
        )

    @commands.check(is_pedim_or_nriver)
    @commands.command()
    async def check_amigo_secreto(self, ctx: Context):
        state = AmigoSecretoState.objects.first()

        total_pessoas = AmigoSecretoPerson.objects.count()

        if not state.activated:
            return await ctx.send("O Amigo Secreto do Atlantis não está ativo.")

        return await ctx.send(f"O Amigo Secreto do Atlantis está ativo. Total de pessoas inscritas: {total_pessoas}")

    @commands.check(is_pedim_or_nriver)
    @commands.command()
    async def deactivate_amigo_secreto(self, ctx: Context):
        state = AmigoSecretoState.objects.first()
        state.activated = False
        state.save()

        return await ctx.send("O Amigo Secreto do Atlantis foi desativado.")
    
    @commands.check(is_pedim_or_nriver)
    @commands.command()
    async def activate_amigo_secreto(self, ctx: Context):
        state = AmigoSecretoState.objects.first()
        state.activated = True
        start_date_brt = await ctx.prompt(
            "Digite a data de inicio do Amigo Secreto (exemplo '20/12/2025 20:00'):"
        )
        end_date_brt = await ctx.prompt(
            "Digite a data de fim do Amigo Secreto (exemplo '30/12/2025 20:00'). "
            "A data do sorteio será 2 dias antes da data final informada:"
        )

        start_date_utc = datetime.strptime(start_date_brt, "%d/%m/%Y %H:%M") - timedelta(hours=3)
        end_date_utc = datetime.strptime(end_date_brt, "%d/%m/%Y %H:%M") - timedelta(hours=3)
        state = AmigoSecretoState.objects.first()
        state.start_date = start_date_utc
        state.end_date = end_date_utc
        state.save()

        return await ctx.send("O Amigo Secreto do Atlantis foi ativado.")
    
    @commands.check(is_pedim_or_nriver)
    @commands.command()
    async def clear_amigo_secreto(self, ctx: Context):
        self.clear_secret_santa()
        total_count = AmigoSecretoPerson.objects.count()
        return await ctx.send(f"O Amigo Secreto do Atlantis foi limpo. Total de pessoas inscritas: {total_count}")
    
    @commands.check(is_pedim_or_nriver)
    @commands.command()
    async def delete_amigo_secreto(self, ctx: Context):
        self.delete_all_secret_santa()
        total_count = AmigoSecretoPerson.objects.count()

        confirmation = await ctx.prompt(
            "Tem absoluta certeza que deseja fazer isso? Isso DELETA TODAS AS INSCRIÇÕES do Amigo Secreto!"
        )
        if not confirmation:
            return await ctx.send("Comando cancelado")

        return await ctx.send(
            "Todas as inscrições do Amigo Secreto do Atlantis foram deletadas. "
            f"Total de pessoas inscritas: {total_count}"
        )

    @commands.check(is_authenticated)
    @commands.command(aliases=["amigosecreto", "amigo"])
    async def amigo_secreto(self, ctx: Context):
        dev = self.bot.get_user(self.bot.setting.developer_id)
        await dev.send(f"{ctx.author} está se inscrevendo no amigo secreto.")

        state = AmigoSecretoState.objects.first()

        if not state.activated:
            return await ctx.send(
                f"{ctx.author.mention}, o Amigo Secreto do Atlantis ainda não está ativo."
            )

        user = ctx.get_user()

        if not user:
            raise Exception("Varíavel 'user' é None")

        atlantis: discord.Guild = self.bot.get_guild(self.bot.setting.server_id)
        member: discord.Member = atlantis.get_member(ctx.author.id)

        if not member:
            return await ctx.send(
                f"{ctx.author.mention}, é necessário estar no Servidor do Atlantis "
                f"para participar do Amigo Secreto\nhttps://discord.me/atlantis"
            )

        allowed_role_list = ["membro", "mod_trial", "mod", "mod+", "admin"]
        allowed_roles = [self.bot.setting.role.get(role) for role in allowed_role_list]

        if not has_any_role(member, *allowed_roles):
            return await ctx.send(
                f"{ctx.author.mention}, você precisa ser um Membro do Clã para participar do Amigo Secreto. "
                "Caso seja um Membro do Clã, utilize o comando `!membro` primeiro e depois tente novamente."
            )

        exists = AmigoSecretoPerson.objects.filter(user__id=user.id).first()

        if exists:
            await ctx.send(
                f"{ctx.author.mention}, você já está cadastrado no Amigo Secreto!"
            )
            return await dev.send(
                f"{ctx.author}: Inscrição cancelada. Já está no Amigo Secreto."
            )

        person = AmigoSecretoPerson(user=user)
        person.save()

        await dev.send(
            f"{ctx.author} foi cadastrado no Amigo Secreto com sucesso ({user})"
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


async def setup(bot):
    await bot.add_cog(AmigoSecreto(bot))
