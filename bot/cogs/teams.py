import re
import asyncio

import discord
from discord.ext import commands
from sqlalchemy import cast, Integer

from bot.bot_client import Bot
from bot.utils.tools import separator
from bot.utils.teams import delete_team, update_team_message
from bot.orm.models import Team, Player


async def is_team_owner(ctx: commands.Context):
    """Checks if the command caller is the team's owner or not, team_id has to be the first argument of the command"""
    with ctx.bot.db_session() as session:
        team_id = re.findall(r"(?:\S+\s+)(\S+)", ctx.message.content)
        if not team_id:
            raise commands.MissingRequiredArgument(ctx.command)
        team_id = team_id[0]
        team: Team = session.query(Team).filter_by(team_id=team_id).first()
        if not team:
            await ctx.send(f"Time com ID {team_id} não existe.")
            return False
        if not int(team.author_id) == ctx.author.id:
            await ctx.send(f"Você precisa ser o criador desse Time para fazer isso.")
            return False
        return True


async def is_in_team(ctx: commands.Context):
    """Checks if the command caller is in the team or not, team_id has to be the first argument of the command"""
    with ctx.bot.db_session() as session:
        team_id = re.findall(r"(?:\S+\s+)(\S+)", ctx.message.content)
        if not team_id:
            raise commands.MissingRequiredArgument(ctx.command)
        team_id = team_id[0]
        team: Team = session.query(Team).filter_by(team_id=team_id).first()
        if not team:
            await ctx.send(f"Time com ID {team_id} não existe.")
            return False
        in_team = session.query(Player).filter_by(team=team.id, player_id=str(ctx.author.id)).first()
        if not in_team:
            await ctx.send(f"Você precisa estar no Time para fazer isso.")
            return False
        return True


class Teams(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(aliases=['teamrole', 'tr', 'setrole', 'sr'])
    async def team_role(self, ctx: commands.Context, team_id: str, to_add: discord.Member, *, role: str):
        with self.bot.db_session() as session:
            team: Team = session.query(Team).filter_by(team_id=team_id).first()
            if not team:
                return await ctx.send(f"Time com ID {team_id} não existe.")
            team_channel = self.bot.get_channel(int(team.team_channel_id))
            if not ctx.author.permissions_in(team_channel).manage_channels:
                raise commands.MissingPermissions(['manage_messages'])
            player = session.query(Player).filter_by(player_id=str(to_add.id), team=str(team.id)).first()
            if not player:
                return await ctx.send(f"{ctx.author.mention}, esse jogador não está no time de ID {team_id}.")
            player.role = role
            team_channel: discord.TextChannel = self.bot.get_channel(int(team.team_channel_id))
            team_message: discord.Message = await team_channel.fetch_message(int(team.team_message_id))
            await update_team_message(team_message, team, self.bot.setting.prefix, session)
            team_url = team_message.jump_url
            msg = f"Role de {to_add.mention} no time **[{team.title}]({team_url})** foi alterado para '{role}'"
            embed = discord.Embed(title='', description=msg, color=discord.Color.green())
            return await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.check(is_in_team)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(aliases=['tagall'])
    async def tag_all(self, ctx: commands.Context, team_id: str, *, message: str = None):
        with self.bot.db_session() as session:
            team: Team = session.query(Team).filter_by(team_id=team_id).first()
            players = session.query(Player).filter_by(team=team.id, substitute=False)
            if not players:
                return await ctx.send(f"O time '{team.title}' está vazio.")
            text = f"Menção enviada por: {ctx.author.mention}\n"
            for player in players:
                text = f"{text} <@{player.player_id}>"
            if message:
                text = f"{text}\n{message}"
            await ctx.message.delete()
            return await ctx.send(text)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(manage_messages=True, embed_links=True)
    @commands.guild_only()
    @commands.command(aliases=['del'])
    async def delteam(self, ctx: commands.Context, team_id: str):
        with self.bot.db_session() as session:
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                pass
            team: Team = session.query(Team).filter_by(team_id=team_id).first()
            if not team:
                return await ctx.send(f"ID inválida: {team_id}")
            if int(team.author_id) != ctx.author.id:
                if not ctx.author.permissions_in(ctx.channel).manage_roles:
                    raise commands.MissingPermissions(['manage_roles'])
            if int(team.team_channel_id) != ctx.channel.id:
                return await ctx.send('Você só pode deletar um time no canal que ele foi criado.')
            await delete_team(session, team, self.bot)
            await ctx.author.send(f"Time '{team.title}' excluído com sucesso.")

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(manage_messages=True, embed_links=True, read_message_history=True)
    @commands.guild_only()
    @commands.command(aliases=['newteam', 'createteam', 'novotime', 'time'])
    async def team(self, ctx: commands.Context):
        await ctx.message.delete()

        cancel_command = f'{self.bot.setting.prefix}cancelar'
        orange = discord.Color.orange()

        embed = discord.Embed(title="Criação de Time", description=f"", color=orange)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.bot.setting.banner_image)
        team_message: discord.Message = await ctx.send(embed=embed)

        def author_check(message):
            if ctx.channel != message.channel:
                return False
            return message.author == ctx.author

        def size_check(message):
            if ctx.channel != message.channel:
                return False
            if message.author != ctx.author:
                return False
            try:
                size = int(message.content)
                return size > 0
            except ValueError:
                return False

        def limit_check(message):
            if ctx.channel != message.channel:
                return False
            if message.author != ctx.author:
                return False
            try:
                _limit = int(message.content)
                return _limit >= 0
            except ValueError:
                return False

        def chat_check(message):
            if ctx.channel != message.channel:
                return False
            if message.author != ctx.author:
                return False
            _chat_id = re.search(r'\d+', message.content)
            if not _chat_id:
                return False
            try:
                _chat_id = _chat_id.group()
                _chat_id = int(_chat_id)
            except ValueError:
                return False
            channel = self.bot.get_channel(_chat_id)
            if not channel:
                return False
            return True

        def role_check(message):
            if ctx.channel != message.channel:
                return False
            if message.author != ctx.author:
                return False
            if message.content.lower() == 'nenhum':
                return True
            _role_id = re.search(r'\d+', message.content)
            if not _role_id:
                return False
            _role_id = int(_role_id.group())
            if not any(role.id == _role_id for role in ctx.guild.roles):
                return False
            return True

        fields = [
            {
                'name': 'title',
                'pt_name': 'Título',
                'check': author_check,
                'value': None,
                'message': f"{ctx.author.mention}, digite o nome do time. (e.g.: Solak 20:00)"
            },
            {
                'name': 'size',
                'pt_name': 'Tamanho',
                'check': size_check,
                'value': None,
                'message': f"{ctx.author.mention}, digite o tamanho do time. (apenas números maiores que 0)"
            },
            {
                'name': 'chat',
                'pt_name': 'Chat',
                'check': chat_check,
                'value': None,
                'message': f"{ctx.author.mention}, digite o chat onde o bot deve aceitar presenças para esse time."
            },
            {
                'name': 'role',
                'pt_name': 'Requisito',
                'check': role_check,
                'value': None,
                'message': f"{ctx.author.mention}, mencione o Role de requisito para o time. (ou 'nenhum')"
            },
            {
                'name': 'role_secondary',
                'pt_name': 'Requisito Secundário',
                'check': role_check,
                'value': None,
                'message': f"{ctx.author.mention}, mencione o Role secundário de requisito para o time. (ou 'nenhum')"
            },
            {
                'name': 'secondary_limit',
                'pt_name': 'Limite Secundário',
                'check': limit_check,
                'value': None,
                'message': (f"{ctx.author.mention}, qual o limite para o número de pessoas no Time que tenham apenas"
                            f" o cargo secundário? (0 para sem limite)")
            }
        ]

        has_requirement = False
        has_secondary_requirement = False

        for field in fields:
            if field['name'] == 'role_secondary' and not has_requirement:
                continue
            if field['name'] == 'secondary_limit' and not has_secondary_requirement:
                continue

            sent_message = await ctx.send(field['message'])
            try:
                answer: discord.Message = await self.bot.wait_for('message', timeout=60.0, check=field['check'])
            except asyncio.TimeoutError:
                await sent_message.delete()
                return await ctx.send("Criação de Time Cancelada. Tempo Esgotado.")

            await answer.delete()
            await sent_message.delete()

            if answer.content.lower() == cancel_command:
                await team_message.delete()
                return await ctx.send("Criação de Time Cancelada.")

            if field['name'] == 'chat':
                chat_id = re.search(r'\d+', answer.content).group()
                field['value'] = self.bot.get_channel(int(chat_id))
            else:
                field['value'] = answer.content

            if type(field['value']) == str and field['value'].lower() == 'nenhum':
                field['value'] = None
            elif field['name'] == 'role' or field['name'] == 'role_secondary':
                field['value'] = re.search(r'\d+', answer.content).group()
            elif field['name'] == 'secondary_limit':
                if field['value']:
                    field['value'] = int(field['value'])

            embed.add_field(name=field['pt_name'], value=answer.content)
            await team_message.edit(embed=embed)

            if field['name'] == 'role' and field['value']:
                has_requirement = True
            if field['name'] == 'role_secondary' and field['value']:
                has_secondary_requirement = True

        team_title = fields[0]['value']
        team_size = fields[1]['value']
        team_chat = fields[2]['value']
        team_role = fields[3]['value']
        team_secondary = fields[4]['value']
        team_secondary_limit = fields[5]['value']

        description = f'Marque presença no {team_chat.mention}\nCriador: <@{ctx.author.id}>'

        requisito = ""
        requisito2 = ""

        if has_requirement:
            requisito = f"Requisito: <@&{team_role}>\n"

        if has_secondary_requirement:
            limit = "" if not team_secondary_limit else f"(Limite: {team_secondary_limit})"
            requisito2 = f"Requisito Secundário: <@&{team_secondary}> {limit}\n\n"

        description = f"{requisito}{requisito2}{description}"

        team_id = str(self.current_id() + 1)
        invite_embed = discord.Embed(
            title=f"Marque presença para '{team_title}' ({team_size} pessoas)",
            description=f"{separator}\n\n"
            f"{requisito}"
            f"{requisito2}"
            f"Time: {ctx.channel.mention}\n"
            f"Criador: <@{ctx.author.id}>\n\n"
            f"`in {team_id}`: Marcar presença\n"
            f"`out {team_id}`: Retirar presença"
        )
        team_embed = discord.Embed(
            title=f"__{team_title}__ - 0/{team_size}",
            description=description,
            color=discord.Color.purple()
        )
        footer = (f"Digite '{self.bot.setting.prefix}del {team_id}' "
                  f"para excluir o time. (Criador do time ou Admin e acima)")
        team_embed.set_footer(text=footer)

        try:
            invite_embed_message = await team_chat.send(embed=invite_embed)
            team_embed_message = await ctx.channel.send(embed=team_embed)
        except discord.errors.HTTPException:
            return await ctx.send(
                f"Criação de time cancelada. "
                f"Não foi possível enviar uma mensagem para o canal '{team_chat}'"
            )

        created_team = {
            'team_id': team_id,
            'title': team_title,
            'size': team_size,
            'role': team_role,
            'role_secondary': team_secondary,
            'author_id': ctx.author.id,
            'invite_channel_id': team_chat.id,
            'invite_message_id': invite_embed_message.id,
            'team_channel_id': ctx.channel.id,
            'team_message_id': team_embed_message.id,
            'secondary_limit': team_secondary_limit
        }

        await team_message.delete()

        self.save_team(team=created_team)

    @commands.is_owner()
    @commands.command()
    async def potato(self, ctx: commands.Context):
        """Test Command"""

        # RuntimeWarning: coroutine 'check' was never awaited
        # if potato_check is a coroutine
        def potato_check(message: discord.Message):
            if message.content != 'potato':
                # await ctx.send(f"Hey, you need to say potato, not {message.content}", delete_after=3)
                return False
            return True

        await ctx.send("Send potato")
        answer: discord.Message = await self.bot.wait_for('message', timeout=60.0, check=potato_check)
        await ctx.send(answer.content)

    def save_team(self, team: dict):
        with self.bot.db_session() as session:
            role = None
            if team.get('role'):
                role = str(team.get('role'))

            role_secondary = None
            if team.get('role_secondary'):
                role_secondary = str(team.get('role_secondary'))

            team = Team(
                team_id=team.get('team_id'),
                title=team.get('title'),
                size=team.get('size'),
                role=role,
                role_secondary=role_secondary,
                author_id=str(team.get('author_id')),
                invite_channel_id=str(team.get('invite_channel_id')),
                invite_message_id=str(team.get('invite_message_id')),
                team_channel_id=str(team.get('team_channel_id')),
                team_message_id=str(team.get('team_message_id')),
                secondary_limit=team.get('secondary_limit')
            )
            session.add(team)
            session.commit()

    def current_id(self) -> int:
        with self.bot.db_session() as session:
            try:
                # Achar a team_id mais alta e retornar ela
                current_id = int(session.query(Team).filter(Team.team_id != 'raids').order_by(
                    cast(Team.team_id, Integer).desc()).first().team_id)
            except (AttributeError, ValueError):
                return 0
        return current_id


def setup(bot):
    bot.add_cog(Teams(bot))
