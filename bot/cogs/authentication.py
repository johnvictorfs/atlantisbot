from typing import Union, Dict, Optional, List, Any
import random
import traceback
import datetime
import logging
import base64
import json
import re

from discord.ext import commands, tasks
from django.db.models import Q
from atlantisbot_api.models import DiscordUser, DiscordIngameName
import rs3clans
import asyncio
import discord
import aiohttp

from bot.bot_client import Bot
from bot.cogs.rsworld import grab_world, get_world, random_world, filtered_worlds
from bot.utils.tools import divide_list, get_clan_async
from bot.utils.context import Context
from bot.utils.checks import is_authenticated, is_admin
from bot.utils.roles import check_admin_roles


async def get_user_data(username: str, cs: aiohttp.ClientSession):
    url = "https://services.runescape.com/m=website-data/"
    player_url = (
        url
        + "playerDetails.ws?names=%5B%22{}%22%5D&callback=jQuery000000000000000_0000000000&_=0"
    )

    async with cs.get(player_url.format(username.replace(" ", "%20"))) as r:
        # Check clan of player
        content = await r.text()
        return parse_user(content)


def parse_user(content: str) -> Optional[Dict[str, Union[str, int]]]:
    match = re.search(r'{"isSuffix":.*,"name":.*,"title":.*}', content)
    if not match:
        print(content)
        return None

    parsed = match.group()

    info_dict = json.loads(parsed)
    info_dict["is_suffix"] = info_dict.pop("isSuffix")

    return info_dict


def settings_embed(settings: dict):
    """
    Accepts a dict in the following format and returns a discord Embed accordingly:

    settings = {
        "f2p_worlds": bool,
        "legacy_worlds": bool,
        "language": "pt" | "en" | "fr" | "de"
    }
    """

    embed = discord.Embed(
        title="Configurações de Mundos",
        description=(
            "Olá, para eu poder saber que você é mesmo o jogador que diz ser, "
            "eu vou precisar que você troque para os Mundos do jogo que irei o mostrar, "
            "siga as instruções abaixo para poder ser autenticado e receber o cargo de `Membro` "
            "no Servidor do Atlantis."
        ),
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(
        url="http://services.runescape.com/m=avatar-rs/l=3/a=869/atlantis/clanmotif.png"
    )

    # yes = "✅"
    # no = "❌"
    language = {"pt": "Português-br", "en": "Inglês", "fr": "Francês", "de": "Alemão"}

    # embed.add_field(name=f"Mundos Grátis {yes if settings['f2p_worlds'] else no}", value=separator, inline=False)
    # embed.add_field(name=f"Mundos Legado {yes if settings['legacy_worlds'] else no}", value=separator, inline=False)
    embed.add_field(
        name="Linguagem", value=language[settings["language"]], inline=False
    )
    embed.add_field(
        name="Mundos Restantes", value=settings["worlds_left"], inline=False
    )
    return embed


class UserAuthentication(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.debugging = False
        self.logger = logging.getLogger("authentication")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename="authentication.log", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        )

        self.error_logger = logging.getLogger("check_users_errors")
        self.logger.setLevel(logging.DEBUG)
        error_logger_handler = logging.FileHandler(
            filename="check_users_errors.log", encoding="utf-8"
        )
        error_logger_handler.setFormatter(
            logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        )

        if not self.error_logger.handlers:
            self.error_logger.addHandler(error_logger_handler)

        if not self.logger.handlers:
            # Prevent multiple handlers sending duplicate messages
            self.logger.addHandler(handler)

        if self.bot.setting.mode == "prod" or self.debugging:
            self.check_users.start()

    def cog_unload(self):
        if self.bot.setting.mode == "prod" or self.debugging:
            self.check_users.cancel()

    @commands.check(is_authenticated)
    @commands.command("token", aliases=["auth_token"])
    async def token(self, ctx: Context):
        user = ctx.get_user()

        if not user:
            return

        data = {
            "name": self.bot.setting.authorization["name"],
            "type": self.bot.setting.authorization["type"],
            "data": self.bot.setting.authorization["data"],
            "id": user.id,
            "discord_id": user.discord_id,
            "discord_name": user.discord_name,
            "ingame_name": user.ingame_name,
        }

        token = base64.b64encode(str(data).encode("utf-8")).decode("utf-8")

        description = (
            "Atenção: Nunca compartilhe o seu Token de Autorização com outras pessoas, "
            "ele pode ser utilizado para se passar "
            "por você, em pesquisas, eventos do Clã etc."
        )

        embed = discord.Embed(
            title="Token de Autorização",
            description=description,
            color=discord.Color.dark_red(),
        )

        embed.add_field(name="Clique abaixo para ver o seu Token", value=f"||{token}||")

        await ctx.message.add_reaction("✅")
        return await ctx.author.send(embed=embed)

    @tasks.loop(hours=1)
    async def check_users(self):
        """
        Check users that have changed names or left the clan since last authentication
        """
        if self.bot.setting.mode == "dev":
            return

        self.logger.info("[check_users] Checando autenticação de usuários...")
        atlantis = self.bot.get_guild(self.bot.setting.server_id)
        membro = atlantis.get_role(self.bot.setting.role.get("membro"))
        argus = atlantis.get_role(self.bot.setting.role.get("argus"))
        convidado = atlantis.get_role(self.bot.setting.role.get("convidado"))
        auth_chat = self.bot.setting.chat.get("auth")
        auth_chat = atlantis.get_channel(auth_chat)

        clan: rs3clans.Clan = await get_clan_async(
            self.bot.setting.clan_name, set_exp=False
        )
        argus_clan: rs3clans.Clan = await get_clan_async(
            "Atlantis Argus", set_exp=False
        )

        for user in DiscordUser.objects.all():
            try:
                self.logger.debug(f"[check_users] Checando {user}")

                member: discord.Member = atlantis.get_member(int(user.discord_id))

                if user.disabled:
                    # Fix disabled member roles, if necessary
                    if member:
                        await member.add_roles(convidado)
                        await member.remove_roles(membro, argus)
                    continue

                if not user.ingame_names.exists():
                    # Add curent player's ingame name as a IngameName model if none exist
                    new_ingame_name = DiscordIngameName(
                        name=user.ingame_name, user=user
                    )
                    new_ingame_name.save()

                # Fix member roles if necessary
                if member:
                    if user.clan == "Atlantis Argus":
                        await member.add_roles(membro, argus)
                    else:
                        await member.add_roles(membro)
                    await member.remove_roles(convidado)

                clan_user = None
                if member:
                    clan_user = clan.get_member(user.ingame_name)

                    if not clan_user:
                        clan_user = argus_clan.get_member(user.ingame_name)

                    if clan_user:
                        self.logger.debug(
                            f"[check_users] Checando Admin Roles {clan_user}"
                        )
                        await check_admin_roles(
                            member, self.bot.setting, clan_user.rank
                        )

                if not self.debugging and clan_user and not user.warning_date:
                    self.logger.debug(
                        f"[check_users] Skipping {clan_user}, in clan and no warning date"
                    )
                    # Don't do anything if player in clan
                    continue

                if not member:
                    # Disable user if he left the discord
                    user.disabled = True
                    user.warning_date = None
                    user.save()
                    continue

                if user.warning_date:
                    now = datetime.datetime.now(user.warning_date.tzinfo)

                    difference = (now - user.warning_date).days
                    self.logger.debug(
                        f"[check_users] Difference warning for {user} is {difference} days."
                    )

                    # Only remove role if warning message was send 7 days before this check
                    if difference >= 7:
                        user.disabled = True
                        user.warning_date = None
                        user.save()

                        await member.remove_roles(membro, argus)
                        await member.add_roles(convidado)
                        await member.send(
                            f"Olá {member.mention}! Há 7 dias, você trocou de nome ou saiu do Atlantis. "
                            f"Como, até o momento, você não voltou a se registrar como membro do clã "
                            f"autenticado ao Discord, seu cargo de `Membro` foi removido.\n\n"
                            f"Caso ainda seja membro da comunidade, **autentique-se novamente "
                            f"já!** O cargo de `Membro` é essencial para uma ampla participação "
                            f"nas atividades do Atlantis.\n\n"
                            f"Para se autenticar novamente, utilize o comando **`!membro`** aqui!\n\n"
                            f"Caso queira desabilitar sua autenticação, utiliza o comando **`!unmembro`**"
                        )

                        ingame_names = [
                            ingame_name.name for ingame_name in user.ingame_names.all()
                        ]
                        ingame_names = ", ".join(ingame_names)

                        tag_removida_embed = discord.Embed(
                            title="Teve Tag de Membro Removida",
                            description=f"**ID:** {member.id}\n**Nomes Anteriores:** {ingame_names}",
                            color=discord.Color.dark_red(),
                        )

                        tag_removida_embed.set_author(
                            name=str(member),
                            icon_url=member.avatar and member.avatar.url,
                        )

                        await auth_chat.send(embed=tag_removida_embed)
                else:
                    await member.send(
                        f"Olá {member.mention}!\n"
                        f"Parece que você trocou o seu nome no jogo ou saiu do Clã! Desse modo, "
                        f"seu cargo de `Membro` deverá ser re-avaliada.\n\n"
                        f"**Caso tenha apenas mudado de nome**, será necessário se autenticar novamente "
                        f"no Discord do clã para continuar a ter acesso aos canais e vantagens do cargo de "
                        f"`Membro`. Torna-se válido ressaltar que o cargo é de fundamental importância para "
                        f"participação em muitas atividades do Atlantis.\n\n"
                        f"A partir de agora, você tem até **7 dias para se autenticar novamente** e "
                        f"registrar-se como Membro do Atlantis! Após este período, o cargo de `Membro` será "
                        f"removido até atualização de seu status.\n\n"
                        f"Caso tenha deixado a comunidade, o cargo só poderá ser reavido mediante um eventual "
                        f"reingresso no clã.\n\n"
                        f"Para se autenticar novamente, utilize o comando **`!membro`** aqui!"
                    )

                    ingame_names = [
                        ingame_name.name for ingame_name in user.ingame_names.all()
                    ]
                    ingame_names = ", ".join(ingame_names)

                    warning_embed = discord.Embed(
                        title="Recebeu Warning de 7 dias para re-autenticação",
                        description=f"**ID:** {member.id}\n**Nomes Anteriores:** {ingame_names}",
                        color=discord.Color.red(),
                    )

                    warning_embed.set_author(
                        name=str(member), icon_url=member.avatar and member.avatar.url
                    )

                    await auth_chat.send(embed=warning_embed)
                    user.warning_date = datetime.datetime.utcnow()
                    user.save()
            except Exception as e:
                if "403 Forbidden" in traceback.format_exc():
                    try:
                        user.disabled = True
                        user.warning_date = None
                        user.save()
                    except Exception:
                        pass
                    continue

                await self.bot.send_logs(
                    e,
                    traceback.format_exc(),
                    more_info={"user": str(user), "member": member},
                )
                await asyncio.sleep(30)

    @staticmethod
    async def send_cooldown(ctx):
        await ctx.send("O seu próximo mundo será enviado em 3...", delete_after=1)
        await asyncio.sleep(1)
        await ctx.send("O seu próximo mundo será enviado em 2...", delete_after=1)
        await asyncio.sleep(1)
        await ctx.send("O seu próximo mundo será enviado em 1...", delete_after=1)
        await asyncio.sleep(1)

    @commands.command(aliases=["desmembro", "unmembro"])
    async def un_membro(self, ctx: Context):
        """
        Command to remove a user's authentication
        """
        user = DiscordUser.objects.filter(discord_id=str(ctx.author.id)).first()

        if not user or user.disabled:
            return await ctx.send(
                "Você precisa estar autenticado para poder se desautenticar!!"
            )

        await ctx.send(
            "Tem certeza que deseja remover sua Autenticação do Discord do Atlantis? (Sim/Não)"
        )

        try:
            message = await self.bot.wait_for(
                "message", check=lambda msg: msg.author == ctx.author, timeout=20
            )
        except asyncio.TimeoutError:
            return await ctx.send("Comando cancelado. Tempo esgotado.")

        if message.content.lower() == "sim":
            user.disabled = True
            user.warning_date = None
            user.save()
            atlantis: discord.Guild = self.bot.get_guild(self.bot.setting.server_id)
            auth_chat: discord.TextChannel = atlantis.get_channel(
                self.bot.setting.chat.get("auth")
            )

            member = atlantis.get_member(ctx.author.id)

            if not member:
                invite = "<https://discord.me/atlantis>"
                return await ctx.send(
                    f"Você precisa estar no Discord do Atlantis para fazer isso. {invite}"
                )

            membro = atlantis.get_role(self.bot.setting.role.get("membro"))
            convidado = atlantis.get_role(self.bot.setting.role.get("convidado"))
            await member.remove_roles(membro)
            await member.add_roles(convidado)

            name_list: List[str] = [
                ingame_name.name for ingame_name in user.ingame_names.all()
            ]
            ingame_names = ", ".join(name_list)

            removed_embed = discord.Embed(
                title="Removeu sua autenticação como Membro",
                description=(
                    f"**Username:** {user.ingame_name}\n"
                    f"**ID:** {ctx.author.id}\n"
                    f"**Clã:** {user.clan}\n"
                    f"**Nomes Anteriores:** {ingame_names}"
                ),
                color=discord.Color.red(),
            )

            removed_embed.set_author(
                name=str(ctx.author),
                icon_url=ctx.author.avatar and ctx.author.avatar.url,
            )
            removed_embed.set_footer(
                text=f"• {datetime.datetime.now().strftime('%d/%m/%y - %H:%M')}"
            )

            await auth_chat.send(embed=removed_embed)

            return await ctx.send("Sua autenticação foi removida com sucesso.")
        else:
            return await ctx.send("Remoção de autenticação cancelada.")

    @commands.check(is_admin)
    @commands.command(aliases=["user"])
    async def authenticated_user(self, ctx: Context, *, user_name: str):
        """
        Searches Authenticated User, first by Ingame Name, then by Discord Name, then by Discord Id
        """
        lower_name = user_name.lower()

        query = DiscordUser.objects.filter(
            Q(ingame_name__icontains=lower_name)
            | Q(discord_name__icontains=lower_name)
            | Q(discord_id__icontains=lower_name)
        )

        if query:
            member = query.first()
        else:
            return await ctx.send(f"Nenhum Usuário encontrado para '{user_name}'.")

        if not member:
            # Search User using one of his old names
            ingame_name = DiscordIngameName.objects.get(
                Q(name__icontains=lower_name),
            )

            if ingame_name:
                member = ingame_name.user

        if not member:
            return await ctx.send(
                f"Não existe um usuário autenticado com o usuário in-game ou do Discord '{user_name}'."
            )

        nb_space = "\u200B"

        embed = discord.Embed(
            title="Usuário Autenticado",
            description=nb_space,
            color=discord.Color.green(),
        )

        last_update = member.updated.strftime("%d/%m/%y - %H:%M")

        warning_date = "N/A"
        if member.warning_date:
            warning_date = member.warning_date.strftime("%d/%m/%y - %H:%M")

        disabled = "Sim" if member.disabled else "Não"

        name_list = [ingame_name.name for ingame_name in member.ingame_names.all()]
        ingame_names = ", ".join(name_list) if name_list else "Nenhum"

        clan = rs3clans.Clan(member.clan)
        player = clan.get_member(member.ingame_name)

        embed.add_field(name="Nome In-game", value=member.ingame_name)
        embed.add_field(name="Clã", value=member.clan)
        embed.add_field(name="Desabilitado?", value=disabled)
        embed.add_field(name="Nome Discord", value=member.discord_name)
        embed.add_field(name="ID Discord", value=member.discord_id)
        embed.add_field(name="ID Database", value=member.id)
        embed.add_field(name="Último update", value=last_update)
        embed.add_field(name="Data de Warning", value=warning_date)

        if player:
            player_rank = (
                f'{self.bot.setting.clan_settings[player.rank]["Translation"]} '
                f'{self.bot.setting.clan_settings[player.rank]["Emoji"]}'
            )
            embed.add_field(name="Exp no Clã", value=f"{player.exp:,}")
            embed.add_field(name="Rank no Clã", value=player_rank)
        else:
            embed.add_field(name="No Clã?", value="Não")

        embed.add_field(
            name="Nomes In-Game Anteriores", value=ingame_names, inline=False
        )

        embed.set_author(
            name="RunePixels",
            url=f"https://runepixels.com/players/{member.ingame_name.replace(' ', '-')}",
        )

        await ctx.author.send(embed=embed)
        await ctx.message.add_reaction("✅")

    @commands.check(is_admin)
    @commands.command(aliases=["membros"])
    async def authenticated_users(self, ctx: Context):
        not_disabled_count = DiscordUser.objects.filter(disabled=False).count()
        disabled_count = DiscordUser.objects.filter(disabled=True).count()

        members = list(DiscordUser.objects.all())

        if not members:
            return await ctx.send("Não há nenhum Membro Autenticado no momento")

        members = divide_list(members, 30)

        for member_list in members:
            embed = discord.Embed(
                title=f"Membros Autenticados\nHabilitados: {not_disabled_count}\nDesabilitados: {disabled_count}",
                description="-",
                color=discord.Color.green(),
            )

            for user in member_list:
                disabled = "Sim" if user.disabled else "Não"

                embed.add_field(
                    name="\u200B",
                    value=(
                        f"**In-game:** {user.ingame_name}\n**Discord:** {user.discord_name}\n"
                        f"**Desabilitado:** {disabled}"
                    ),
                )

            await ctx.author.send(embed=embed)
        await ctx.message.add_reaction("✅")

    @commands.is_owner()
    @commands.command()
    async def snap(self, ctx: Context):
        """
        Remover a Tag de Membro de todo Usuário não-autenticado do Servidor
        """
        atlantis: discord.Guild = self.bot.get_guild(self.bot.setting.server_id)
        membro: discord.Role = atlantis.get_role(self.bot.setting.role.get("membro"))
        convidado: discord.Role = atlantis.get_role(
            self.bot.setting.role.get("convidado")
        )

        removed_count = 0

        member: discord.Member
        for member in atlantis.members:
            discord_user: discord.User = member._user

            user = DiscordUser.objects.filter(discord_id=str(discord_user.id)).first()

            if not user or user.disabled:
                role: discord.Role
                for role in member.roles:
                    if role.id == membro.id:
                        text = (
                            f"Olá {member.mention}! O Atlantis está em processo de automação, a que "
                            f"possibilitará uma série de "
                            f"melhorias na estrutura do clã, a incluir nosso super novo sistema de ranks "
                            f"(Em elaboração, aguarde por mais detalhes)\n\n"
                            f"Como você não se autenticou como **Membro** no novo sistema, sua tag foi retirada,"
                            f" visto que o prazo de 30 dias para autenticação chegou ao fim. "
                            f"Mas não se preocupe! Obter a tag novamente é super rápido, automático e possibilitará"
                            f" que você acesse cada vez mais os benefícios vigentes e futuros de nossa comunidade."
                            f"\n\nPara se autenticar, basta enviar a mensagem **`!membro`** para mim! O processo "
                            f"todo dura menos de 2 minutos, e só deve ser refeito caso você altere seu nome ou saia"
                            f" do clã."
                        )
                        embed = discord.Embed(
                            title="Fim do Prazo de Graça para Reautenticação",
                            description=text,
                            color=discord.Color.red(),
                        )
                        embed.set_thumbnail(
                            url="http://services.runescape.com/m=avatar-rs/l=3/a=869/atlantis/clanmotif.png"
                        )

                        dev = self.bot.get_user(self.bot.setting.developer_id)

                        try:
                            removed_count += 1
                            await member.add_roles(convidado)
                            await member.remove_roles(membro)
                            await member.send(embed=embed)
                            await dev.send(f"Mensagem enviada para {member}.")
                        except Exception as e:
                            await dev.send(
                                f"Erro ao enviar mensagem para {member}. {e}"
                            )

        embed = discord.Embed(
            color=discord.Color.red(),
            title=f"{removed_count} membros removidos... Balanced, as all things should be.",
        )
        embed.set_image(
            url=(
                "https://cdn3.movieweb.com/i/article/lBzyCahFfuBqwD8hG4i72GO5PaeJ9i/"
                "798:50/Infinity-War-Decimation-Thanos-Scientific-Real-Life-Effects.jpg"
            )
        )
        await ctx.send(embed=embed)

    @staticmethod
    def feedback_embed() -> discord.Embed:
        return discord.Embed(
            title="Feedback",
            description=(
                "O que achou do nosso processo de Autenticação para Membro do Servidor? "
                "Teve algum Problema? Tem alguma sugestão?\n\n"
                "Responda enviando uma mensagem aqui, "
                "seu Feedback é importante para nós!"
            ),
            color=discord.Color.blue(),
        )

    @staticmethod
    def timeout_feedback_embed() -> discord.Embed:
        return discord.Embed(
            title="Feedback",
            description=(
                "Olá, parece que você não conseguiu alterar de Mundo a tempo. "
                "Você teve algum Problema?\n\n"
                "Responda enviando uma mensagem aqui, "
                "seu Feedback é importante para nós!"
            ),
            color=discord.Color.blue(),
        )

    @commands.dm_only()
    @commands.cooldown(60, 0, commands.BucketType.user)
    @commands.command(aliases=["role", "membro"])
    async def aplicar_role(self, ctx: Context):
        self.logger.info(f"[{ctx.author}] Autenticação iniciada.")

        user: Optional[DiscordUser] = None
        atlantis = self.bot.get_guild(self.bot.setting.server_id)
        member: discord.Member = atlantis.get_member(ctx.author.id)

        if not member:
            self.logger.info(
                f"[{ctx.author}] Autenticação finalizada. Não está no servidor."
            )
            invite = "<https://discord.me/atlantis>"

            return await ctx.send(
                f"Você precisa estar no Discord do Atlantis para se autenticar {invite}"
            )

        membro: discord.Role = atlantis.get_role(self.bot.setting.role.get("membro"))
        argus: discord.Role = atlantis.get_role(self.bot.setting.role.get("argus"))
        convidado: discord.Role = atlantis.get_role(
            self.bot.setting.role.get("convidado")
        )

        user = DiscordUser.objects.filter(discord_id=str(ctx.author.id)).first()

        if user and not user.warning_date and not user.disabled:
            role: discord.Role
            for role in member.roles:
                if role.id == membro.id:
                    self.logger.info(f"[{ctx.author}] Não é um convidado.")
                    return await ctx.send(
                        "Fool! Você não é um Convidado! Não é necessário se autenticar."
                    )

            async with aiohttp.ClientSession() as cs:
                user_data = await get_user_data(user.ingame_name, cs)

                if not user_data:
                    self.logger.info(
                        f"[{ctx.author}] Erro acessando API do RuneScape. ({user})"
                    )
                    return await ctx.send(
                        "Houve um erro ao tentar acessar seus dados do RuneScape. "
                        "Tente novamente mais tarde."
                    )

                if user_data.get("clan") in self.bot.setting.clan_names:
                    if user_data.get("clan") == "Atlantis Argus":
                        await member.add_roles(membro, argus)
                    else:
                        await member.add_roles(membro)

                    await member.remove_roles(convidado)
                    self.logger.info(
                        f"[{ctx.author}] Já está autenticado, corrigindo dados. ({user})"
                    )
                    return await ctx.send(
                        "Você já está autenticado! Seus dados foram corrigidos. "
                        "Você agora é um Membro do clã autenticado no Discord."
                    )

        def check(message: discord.Message):
            return message.author == ctx.author

        await ctx.send(f"{ctx.author.mention}, por favor me diga o seu nome no jogo.")

        try:
            ingame_name = await self.bot.wait_for("message", timeout=180.0, check=check)
        except asyncio.TimeoutError:
            self.logger.info(
                f"[{ctx.author}] Autenticação cancelada por Timeout (ingame_name)."
            )
            return await ctx.send(
                f"{ctx.author.mention}, autenticação cancelada. Tempo Esgotado."
            )

        if len(ingame_name.content.strip()) > 12:
            return await ctx.send("Nome Inválido. Tamanho muito grande.")

        # Já existe outro usuário cadastrado com esse username in-game
        user_ingame = DiscordUser.objects.filter(
            ~Q(discord_id=str(ctx.author.id)), ingame_name__iexact=ingame_name.content
        ).first()

        if user_ingame:
            self.logger.info(
                f"[{ctx.author}] já existe usuário in-game autenticado com esse nome. ({user_ingame})"
            )
            return await ctx.send(
                "Já existe um Usuário do Discord autenticado com esse nome do jogo.\n"
                "Caso seja mesmo o Dono dessa conta e acredite que outra pessoa tenha se cadastrado "
                "com o seu nome por favor me contate aqui: <@148175892596785152>."
            )

        async with aiohttp.ClientSession() as cs:
            user_data = await get_user_data(ingame_name.content, cs)
            if not user_data:
                self.logger.info(
                    f"[{ctx.author}] Erro acessando API do RuneScape. ({ingame_name.content})"
                )
                return await ctx.send(
                    "Houve um erro ao tentar acessar a API do RuneScape. Tente novamente mais tarde."
                )

        re_auth = False
        if user and user.ingame_name:
            re_auth = True

        settings: Dict[str, Any] = {}
        worlds_done = []

        if self.bot.setting.mode == "prod" or True:
            with open("bot/data/worlds.json") as f:
                worlds = json.load(f)

            if user_data.get("clan") not in self.bot.setting.clan_names:
                self.logger.info(
                    f"[{ctx.author}] Jogador não existe ou não é Membro. ({user_data})"
                )
                return await ctx.send(
                    f"{ctx.author.mention}, o jogador '{user_data.get('name')}' "
                    f"não existe ou não é um membro do Clã Atlantis."
                )

            player_world = await grab_world(
                user_data["name"], user_data["clan"], self.bot.setting.clans
            )

            if player_world == "Offline" or not player_world:
                self.logger.info(f"[{ctx.author}] Jogador offline. ({user_data})")
                image_file = discord.File(
                    "images/privacy_rs.png", filename="privacy_rs.png"
                )

                return await ctx.send(
                    f"{ctx.author.mention}, autenticação Cancelada. Você precisa estar Online.\n"
                    f"Verifique suas configurações de privacidade no jogo. Caso já esteja, e ainda "
                    f"está recebendo essa mensagem, tente entrar no Lobby do jogo, e em seguida em um mundo novamente.",
                    file=image_file,
                )

            player_world = get_world(worlds, player_world)
            if not player_world:
                self.logger.error(f"[{ctx.author}] Player world is None. ({user_data})")
                return await ctx.send(
                    "Você não pode se autenticar em um mundo instanciado "
                    "(Fortaleza, Minigames etc.) por favor vá para um mundo normal para se autenticar."
                )

            worlds_requirement = random.randint(2, 3)
            if re_auth:
                worlds_requirement = 2

            settings = {
                "f2p_worlds": player_world["f2p"],
                "legacy_worlds": player_world["legacy"],
                "language": player_world["language"],
                "worlds_left": worlds_requirement,
                "failed_tries": 0,
            }

            def confirm_check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "✅"

            settings_message = await ctx.send(embed=settings_embed(settings))
            confirm_message = await ctx.send(
                "Reaja nessa mensagem quando estiver pronto."
            )
            await confirm_message.add_reaction("✅")
            try:
                await self.bot.wait_for(
                    "reaction_add", timeout=180, check=confirm_check
                )
            except asyncio.TimeoutError:
                self.logger.info(
                    f"[{ctx.author}] Autenticação cancelada por Timeout. ({user_data})"
                )
                return await ctx.send(
                    f"{ctx.author.mention}, autenticação cancelada. Tempo Esgotado."
                )
            await confirm_message.delete()
            await self.send_cooldown(ctx)

            # Filter worlds based on user settings
            world_list = filtered_worlds(worlds, **settings)
            last_world = player_world

            while settings["worlds_left"] > 0:
                # Update settings message
                await settings_message.edit(embed=settings_embed(settings))

                while True:
                    # Don't allow same world 2 times in a row
                    world = random_world(world_list)
                    if world == last_world:
                        continue
                    break

                last_world = world

                message: discord.Message = await ctx.send(
                    f"{ctx.author.mention}, troque para o **Mundo {world['world']}**. "
                    f"Reaja na mensagem quando estiver nele."
                )

                await message.add_reaction("✅")

                try:
                    await self.bot.wait_for(
                        "reaction_add", timeout=160, check=confirm_check
                    )
                except asyncio.TimeoutError:
                    self.logger.info(
                        f"[{ctx.author}] Autenticação cancelada por Timeout. (mundo) ({settings}) ({user_data})"
                    )
                    dev = self.bot.get_user(self.bot.setting.developer_id)
                    await dev.send(
                        f"{ctx.author} não conseguiu se autenticar por Timeout.\n\n"
                        f"```python\n{settings}\n```\n"
                        f"```python\n{user_data}\n```"
                    )
                    await ctx.send(
                        f"{ctx.author.mention}, autenticação cancelada. Tempo Esgotado."
                    )

                    await ctx.send(embed=self.timeout_feedback_embed())

                    try:
                        feedback_message: discord.Message = await self.bot.wait_for(
                            "message",
                            check=lambda msg: msg.author == ctx.author,
                            timeout=60 * 20,
                        )

                        if feedback_message.content:
                            auth_feedback: discord.TextChannel = self.bot.get_channel(
                                self.bot.setting.chat.get("auth_feedback")
                            )

                            feedback_embed = discord.Embed(
                                title="Feedback de Autenticação (Timeout em troca de Mundo)",
                                description=feedback_message.content,
                                color=discord.Color.red(),
                            )
                            feedback_embed.set_author(
                                name=str(ctx.author),
                                icon_url=ctx.author.avatar and ctx.author.avatar.url,
                            )

                            await auth_feedback.send(embed=feedback_embed)

                            await ctx.send(
                                "Seu Feedback foi recebido com sucesso, muito obrigado!"
                            )
                    except asyncio.TimeoutError:
                        pass
                    return

                wait_message = await ctx.send("Aguarde um momento...")
                await asyncio.sleep(1)
                player_world = await grab_world(
                    user_data["name"], user_data["clan"], self.bot.setting.clans
                )
                if player_world == "Offline":
                    # Check again in 3 seconds in case player was offline
                    # He might have a slow connection, or the clan's webpage
                    # is taking a while to update
                    await asyncio.sleep(3)
                    player_world = await grab_world(
                        user_data["name"], user_data["clan"], self.bot.setting.clans
                    )
                await wait_message.delete()

                if world["world"] == player_world:
                    settings["worlds_left"] -= 1
                    worlds_done.append(player_world)
                    wl = settings["worlds_left"]
                    plural_1 = "m" if wl > 1 else ""
                    plural_2 = "s" if wl > 1 else ""
                    second_part = (
                        f"Falta{plural_1} {settings['worlds_left']} mundo{plural_2}."
                        if wl != 0
                        else ""
                    )

                    await ctx.send(
                        f"**Mundo {world['world']}** verificado com sucesso. {second_part}"
                    )
                else:
                    settings["failed_tries"] += 1

                    await ctx.send(
                        f"Mundo incorreto ({player_world}). Tente novamente."
                    )

                    if settings["failed_tries"] == 3:
                        self.logger.info(
                            f"[{ctx.author}] Autenticação cancelada. Muitas tentativas. ({user_data}) {settings}"
                        )
                        return await ctx.send(
                            "Autenticação cancelada. Muitas tentativas incorretas."
                        )

                await message.delete()

                if settings["worlds_left"] == 0:
                    break

            await settings_message.delete()

        self.logger.info(
            f"[{ctx.author}] Autenticação feita com sucesso. ({user_data}) {settings}"
        )

        if user_data.get("clan") == "Atlantis Argus":
            await member.add_roles(membro, argus)
        else:
            await member.add_roles(membro)
        await member.remove_roles(convidado)

        auth_chat = atlantis.get_channel(self.bot.setting.chat.get("auth"))

        if user:
            user.warning_date = None
            user.disabled = False
            user.ingame_name = user_data["name"]
            user.discord_name = str(ctx.author)
            user.clan = user_data.get("clan")
            user.save()

            auth_embed = discord.Embed(
                title="Autenticação Finalizada",
                description=(
                    f"{ctx.author.mention}, você é novamente um Membro no Discord do Atlantis!\n\n"
                    f"***Nota:*** Caso saia do Clã ou troque de nome, iremos o notificar da necessidade de refazer "
                    f"o  processo de Autenticação, e caso não o faça em até 7 dias, removeremos o seu cargo "
                    f"de Membro."
                ),
                color=discord.Color.green(),
            )

            await ctx.send(embed=auth_embed)

            ingame_names = [ingame_name.name for ingame_name in user.ingame_names.all()]
            nomes_anteriores = ", ".join(ingame_names)

            confirm_embed = discord.Embed(
                title="Se re-autenticou como Membro",
                description=(
                    f"**Username:** {user_data['name']}\n"
                    f"**ID:** {ctx.author.id}\n"
                    f"**Clã:** {user_data.get('clan')}\n"
                    f"**Mundos:** {', '.join([str(world) for world in worlds_done])}\n"
                    f"**Nomes Anteriores:** {nomes_anteriores}"
                ),
                color=discord.Color.blue(),
            )

            confirm_embed.set_author(
                name=str(ctx.author),
                icon_url=ctx.author.avatar and ctx.author.avatar.url,
            )
            confirm_embed.set_footer(
                text=f"• {datetime.datetime.now().strftime('%d/%m/%y - %H:%M')}"
            )

            await auth_chat.send(embed=confirm_embed)
        else:
            user = DiscordUser(
                ingame_name=user_data["name"],
                discord_id=str(ctx.author.id),
                discord_name=str(ctx.author),
                clan=user_data["clan"],
            )
            user.save()

            auth_embed = discord.Embed(
                title="Autenticação Finalizada",
                description=(
                    f"{ctx.author.mention}, você agora é um Membro no Discord do Atlantis!\n\n"
                    f"***Nota:*** Caso saia do Clã ou troque de nome, iremos o notificar da necessidade de refazer "
                    f"o  processo de Autenticação, e caso não o faça em até 7 dias, removeremos o seu cargo "
                    f"de Membro."
                ),
                color=discord.Color.green(),
            )

            whatsapp_embed = discord.Embed(
                title="Grupos de WhatsApp do Clã",
                color=discord.Color.green(),
                description=(
                    "Agora que você já se autenticou no Discord, que tal entrar nos grupos do Whatsapp?\n\n"
                    "Temos dois grupos: um apenas para assuntos do jogo e outro liberado "
                    "para conversas gerais - desde que respeitosas.\n\n"
                    "Entre no link abaixo, diga seu nickname e confirme sua identidade com "
                    "um print dessa tela de autenticação:\n"
                    f"<{self.bot.setting.whatsapp_url}>\n\n"
                    "Quer saber mais detalhes sobre os grupos? Acesse <#579680045157711872>"
                ),
            )

            whatsapp_embed.set_thumbnail(
                url="https://cdn3.iconfinder.com/data/icons/social-media-chamfered-corner/154/whatsapp-512.png"
            )

            await ctx.send(embed=auth_embed)
            await ctx.send(embed=whatsapp_embed)

            ingame_names = [ingame_name.name for ingame_name in user.ingame_names.all()]
            nomes_anteriores = ", ".join(ingame_names)

            confirm_embed = discord.Embed(
                title="Se autenticou como Membro",
                description=(
                    f"**Username:** {user_data['name']}\n"
                    f"**ID**: {ctx.author.id}\n"
                    f"**Clã**: {user_data.get('clan')}\n"
                    f"**Mundos:** {', '.join([str(world) for world in worlds_done])}\n"
                    f"**Nomes Anteriores:** {nomes_anteriores}"
                ),
                color=discord.Color.green(),
            )

            confirm_embed.set_author(
                name=str(ctx.author),
                icon_url=ctx.author.avatar and ctx.author.avatar.url,
            )
            confirm_embed.set_footer(
                text=f"• {datetime.datetime.now().strftime('%d/%m/%y - %H:%M')}"
            )

            await auth_chat.send(embed=confirm_embed)

        self.logger.info(f"[{ctx.author}] Autenticação finalizada.")

        await ctx.send(embed=self.feedback_embed())

        try:
            auth_feedback_message: discord.Message = await self.bot.wait_for(
                "message",
                check=lambda msg: msg.author == ctx.author
                and msg.channel == ctx.channel,
                timeout=60 * 20,
            )

            if auth_feedback_message.content:
                auth_feedback: discord.TextChannel = self.bot.get_channel(
                    self.bot.setting.chat.get("auth_feedback")
                )

                feedback_embed = discord.Embed(
                    title="Feedback de Autenticação",
                    description=auth_feedback_message.content,
                    color=discord.Color.blue(),
                )

                feedback_embed.set_author(
                    name=str(ctx.author), icon_url=ctx.author.avatar and ctx.author.avatar.url
                )

                await auth_feedback.send(embed=feedback_embed)

                if "curiosidade aleatória" in auth_feedback_message.content.lower():
                    await ctx.send("🧐 Good to know.")

                await ctx.send("Seu Feedback foi recebido com sucesso, muito obrigado!")
        except asyncio.TimeoutError:
            pass


async def setup(bot):
    await bot.add_cog(UserAuthentication(bot))
