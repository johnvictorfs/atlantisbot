import re
import traceback
import asyncio
import json

import discord
from discord.ext import commands

from .utils import separator


class TeamCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['newteam', 'createteam', 'novotime', 'time'])
    async def team(self, ctx):
        try:
            try:
                await ctx.message.delete()
            except discord.errors.Forbidden:
                return await ctx.send(
                    "Criação de time não pôde ser iniciada. Permissões insuficientes (Excluir mensagens)"
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
            description = f'Marque presença no <#{chat_presence_id}>'
            if role_id:
                requisito = f'\nRequisito: <@&{role_id}>'
                description = f'Requisito: <@&{role_id}>\n{description}'

            invite_embed = discord.Embed(
                title=f"Marque presença para '{team_title}' ({team_size} pessoas)",
                description=f"{separator}\nTime: {ctx.channel.mention}{requisito}\n\n"
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
                'author_id': ctx.author.id,
                'invite_channel_id': invite_channel.id,
                'invite_message_id': invite_embed_message.id,
                'team_channel_id': ctx.channel.id,
                'team_message_id': team_embed_message.id,
                'title': team_title,
                'size': team_size,
                'presence_chat_id': chat_presence_id,
                'role': role_id,
                'players': [],
                'bot_messages': []
            }
            current_teams['teams'].append(created_team)
            with open('pvm_teams.json', 'w') as f:
                json.dump(current_teams, f, indent=2)
            await creation_message.delete()
        except Exception as e:
            tb = traceback.format_exc()
            await ctx.send(e)
            await ctx.send(tb)
            return await ctx.send("<@148175892596785152>")


def setup(bot):
    bot.add_cog(TeamCommands(bot))
