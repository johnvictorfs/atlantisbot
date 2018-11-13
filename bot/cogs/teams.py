import re
import traceback
import asyncio
import json

import discord
from discord.ext import commands

from .utils import separator, has_role


class TeamCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['timesativos', 'times_ativos'])
    async def running_teams(self, ctx):
        if has_role(ctx.author, self.bot.setting.role.get('admin')):
            await ctx.trigger_typing()
            running_teams_embed = discord.Embed(
                title='__Times Ativos__',
                description="",
                color=discord.Color.red()
            )
            with open('pvm_teams.json', 'r') as f:
                teams = json.load(f)
                if not teams.get('teams'):
                    running_teams_embed.add_field(
                        name=separator,
                        value=f"Nenhum time ativo no momento."
                    )
                for team in teams.get('teams'):
                    running_teams_embed.add_field(
                        name=separator,
                        value=f"**Título:** {team['title']}\n"
                              f"**Chat:** <#{team['team_channel_id']}>\n"
                              f"**Criado por:** <@{team['author_id']}>"
                    )
                await ctx.send(embed=running_teams_embed)

    @commands.command(aliases=['newteam', 'createteam', 'novotime', 'time'])
    async def team(self, ctx):
        await ctx.trigger_typing()
        try:
            try:
                await ctx.message.delete()
            except discord.errors.Forbidden:
                return await ctx.send(
                    "Criação de time não pôde ser iniciada. Permissões insuficientes (Excluir mensagens)"
                )
            except discord.errors.NotFound:
                return await ctx.send(
                    "Criação de time não pôde ser iniciada. Erro inesperado."
                )
            cancel_command = f'{self.bot.setting.prefix}cancelar'
            creation_message_content = (
                "Criação de time iniciada por {author}.\n\n"
                "Digite `{cancel}` a qualquer momento para cancelar.\n\n"
                "**Título:** {title}\n"
                "**Tamanho:** {size}\n"
                "**Chat:** {chat}\n"
                "**Requisito:** {requisito}"
            )
            creation_message = await ctx.send(creation_message_content.format(
                author=ctx.author.mention,
                cancel=cancel_command,
                title='',
                size='',
                chat='',
                requisito='',
            ))

            # Só aceitar respostas de quem iniciou o comando
            def check(message):
                return message.author == ctx.author

            # Título do time
            sent_message = await ctx.send(
                f"{ctx.author.mention}, digite o nome do time. (e.g.: Solak 20:00)"
            )
            try:
                team_title_message = await self.bot.wait_for('message', timeout=60.0, check=check)
                try:
                    await sent_message.delete()
                    await team_title_message.delete()
                except discord.errors.NotFound:
                    await ctx.send("Criação de time cancelada. A mensagem do Bot não foi encontrada.")
                    return await creation_message.delete()
                if team_title_message.content.lower() == cancel_command:
                    await creation_message.delete()
                    return await ctx.send("Criação de time cancelada.")
                team_title = team_title_message.content
                await creation_message.edit(
                    content=creation_message_content.format(
                        author=ctx.author.mention,
                        cancel=cancel_command,
                        title=team_title,
                        size='',
                        chat='',
                        requisito='',
                    )
                )
            except asyncio.TimeoutError:
                await creation_message.delete()
                return await ctx.send("Criação de time cancelada. Tempo Esgotado.")

            # Tamanho do time
            sent_message = await ctx.send(
                f"{ctx.author.mention}, digite o tamanho do time. (apenas números)"
            )
            try:
                team_size_message = await self.bot.wait_for('message', timeout=60.0, check=check)
                try:
                    await sent_message.delete()
                    await team_size_message.delete()
                except discord.errors.NotFound:
                    await ctx.send("Criação de time cancelada. A mensagem do Bot não foi encontrada.")
                    return await creation_message.delete()
                if team_size_message.content.lower() == cancel_command:
                    await creation_message.delete()
                    return await ctx.send("Criação de time cancelada.")
                team_size = int(team_size_message.content)
                await creation_message.edit(
                    content=creation_message_content.format(
                        author=ctx.author.mention,
                        cancel=cancel_command,
                        title=team_title,
                        size=team_size,
                        chat='',
                        requisito='',
                    )
                )
            except asyncio.TimeoutError:
                await creation_message.delete()
                return await ctx.send("Criação de time cancelada. Tempo Esgotado.")
            except ValueError:
                await creation_message.delete()
                return await ctx.send(
                    f"Criação de time cancelada. Tamanho de time inválido ({team_size_message.content}).")

            # Chat para aceitar presenças
            sent_message = await ctx.send(
                f"{ctx.author.mention}, digite o chat onde o bot deve aceitar presenças para esse time."
            )
            try:
                chat_presence_message = await self.bot.wait_for('message', timeout=60.0, check=check)
                try:
                    await sent_message.delete()
                    await chat_presence_message.delete()
                except discord.errors.NotFound:
                    await ctx.send("Criação de time cancelada. A mensagem do Bot não foi encontrada.")
                    return await creation_message.delete()
                if chat_presence_message.content.lower() == cancel_command:
                    await creation_message.delete()
                    return await ctx.send("Criação de time cancelada.")
                chat_presence_id = int(re.findall('\d+', chat_presence_message.content)[0])
                await creation_message.edit(
                    content=creation_message_content.format(
                        author=ctx.author.mention,
                        cancel=cancel_command,
                        title=team_title,
                        size=team_size,
                        chat=f"<#{chat_presence_id}>",
                        requisito='',
                    )
                )
            except asyncio.TimeoutError:
                await creation_message.delete()
                return await ctx.send("Criação de time cancelada. Tempo Esgotado.")
            except ValueError:
                await creation_message.delete()
                return await ctx.send(f"Criação de time cancelada. Chat inválido ({chat_presence_message.content}).")
            except IndexError:
                await creation_message.delete()
                return await ctx.send(f"Criação de time cancelada. Chat inválido ({chat_presence_message.content}).")

            # Role requisito (opcional)
            sent_message = await ctx.send(
                f"{ctx.author.mention}, mencione o Role de requisito para o time. (ou 'nenhum' caso nenhum)"
            )
            try:
                role_str = 'Nenhum'
                role_message = await self.bot.wait_for('message', timeout=60.0, check=check)
                try:
                    await role_message.delete()
                    await sent_message.delete()
                except discord.errors.NotFound:
                    await ctx.send("Criação de time cancelada. A mensagem do Bot não foi encontrada.")
                    return await creation_message.delete()
                if role_message.content.lower() == 'nenhum':
                    role_id = None
                elif role_message.content.lower() == cancel_command:
                    await creation_message.delete()
                    return await ctx.send("Criação de time cancelada.")
                else:
                    role_id = int(re.findall('\d+', role_message.content)[0])
                    if not any(role.id == role_id for role in ctx.guild.roles):
                        await creation_message.delete()
                        return await ctx.send(f"Criação de time cancelada. Role inválido ({role_message.content}).")
                    for role in ctx.guild.roles:
                        if role.id == role_id:
                            role_str = str(role)
                await creation_message.edit(
                    content=creation_message_content.format(
                        author=ctx.author.mention,
                        cancel=cancel_command,
                        title=team_title,
                        size=team_size,
                        chat=f"<#{chat_presence_id}>",
                        requisito=role_str
                    )
                )

            except asyncio.TimeoutError:
                await creation_message.delete()
                return await ctx.send("Criação de time cancelada. Tempo Esgotado.")
            except ValueError:
                await creation_message.delete()
                return await ctx.send(f"Criação de time cancelada. Role inválido ({role_message.content}).")
            except IndexError:
                await creation_message.delete()
                return await ctx.send(f"Criação de time cancelada. Role inválido ({role_message.content}).")

            invite_channel = self.bot.get_channel(chat_presence_id)
            try:
                with open('pvm_teams.json', 'r') as f:
                    current_teams = json.load(f)
                get_teams = current_teams['teams']
                current_id = max([_['id'] for _ in get_teams])
            except FileNotFoundError:
                current_teams = {
                    "teams": []
                }
                current_id = 0
            except json.decoder.JSONDecodeError:
                current_teams = {
                    "teams": []
                }
                current_id = 0
            except TypeError:
                current_teams = {
                    "teams": []
                }
                current_id = 0
            except ValueError:
                current_teams = {
                    "teams": []
                }
                current_id = 0
            team_id = current_id + 1
            requisito = ''
            description = f'Marque presença no <#{chat_presence_id}>\nCriador: <@{ctx.author.id}>'
            if role_id:
                requisito = f'\nRequisito: <@&{role_id}>\n'
                description = f'Requisito: <@&{role_id}>\n{description}'

            invite_embed = discord.Embed(
                title=f"Marque presença para '{team_title}' ({team_size} pessoas)",
                description=f"{separator}\n\n"
                            f"{requisito}"
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
                      f"para excluir o time. (Criador do time ou Mod+)")
            team_embed.set_footer(
                text=footer
            )
            try:
                invite_embed_message = await invite_channel.send(embed=invite_embed)
                team_embed_message = await ctx.channel.send(embed=team_embed)
            except AttributeError:
                await creation_message.delete()
                return await ctx.send(f"Criação de time cancelada. Chat inválido ({chat_presence_message.content}).")
            except discord.errors.HTTPException:
                await creation_message.delete()
                return await ctx.send(
                    f"Criação de time cancelada. "
                    f"Não foi possível enviar uma mensagem para o canal '<#{chat_presence_id}>'"
                )
            created_team = {
                'id': team_id,
                'title': team_title,
                'size': team_size,
                'role': role_id,
                'author_id': ctx.author.id,
                'invite_channel_id': invite_channel.id,
                'invite_message_id': invite_embed_message.id,
                'team_channel_id': ctx.channel.id,
                'team_message_id': team_embed_message.id,
                'players': [],
                'bot_messages': []
            }
            with open('pvm_teams.json', 'r') as f:
                current_teams = json.load(f)
            current_teams['teams'].append(created_team)
            with open('pvm_teams.json', 'w') as f:
                json.dump(current_teams, f, indent=2)
            await creation_message.delete()
        except discord.errors.NotFound:
            return await ctx.send(f"Criação de time cancelada. A mensagem do Bot não foi encontrada.")
        except Exception as e:
            await ctx.send(
                "Erro inesperado :(\n"
                "Os logs desse erro foram enviados para um Dev. Tente novamente."
            )
            dev = self.bot.get_user(self.bot.setting.developer_id)
            tb = traceback.format_exc()
            return await dev.send(f"{e}: {tb}")


def setup(bot):
    bot.add_cog(TeamCommands(bot))
