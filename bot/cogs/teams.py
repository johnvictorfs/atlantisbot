import re
import asyncio

import discord
from discord.ext import commands

from bot.utils.tools import separator
from bot.db.models import Team, BotMessage
import bot.db.db as db


class TeamCommands:
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5)
    @commands.bot_has_permissions(manage_messages=True, embed_links=True)
    @commands.guild_only()
    @commands.command(aliases=['del'])
    async def delteam(self, ctx: commands.Context, pk: str):
        with db.Session() as session:
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                pass
            team: Team = session.query(Team).filter_by(team_id=pk).first()
            if not team:
                return await ctx.send(f"ID inválida: {pk}")
            if int(team.author_id) != ctx.author.id:
                if not ctx.author.permissions_in(ctx.channel).manage_channels:
                    raise commands.MissingPermissions(['manage_channels'])
            if int(team.team_channel_id) != ctx.channel.id:
                return await ctx.send('Você só pode deletar um time no canal que ele foi criado.')
            invite_channel = None
            try:
                team_channel = self.bot.get_channel(int(team.team_channel_id))
                team_message = await team_channel.get_message(int(team.team_message_id))
                await team_message.delete()
            except Exception:
                pass
            try:
                invite_channel = self.bot.get_channel(int(team.invite_channel_id))
                invite_message = await invite_channel.get_message(int(team.invite_message_id))
                await invite_message.delete()
            except Exception:
                pass
            try:
                messages_to_delete = []
                for message in session.query(BotMessage).filter_by(team=team.id):
                    to_delete = await invite_channel.get_message(message.message_id)
                    messages_to_delete.append(to_delete)
                await invite_channel.delete_messages(messages_to_delete)
            except Exception:
                pass
            try:
                session.query(BotMessage).filter_by(team=team.id).delete()
            except Exception:
                pass
            session.delete(team)
            session.commit()
            await ctx.author.send(f"Time '{team.title}' excluído com sucesso.")

    @commands.cooldown(1, 10)
    @commands.bot_has_permissions(manage_messages=True, embed_links=True, read_message_history=True)
    @commands.guild_only()
    @commands.command(aliases=['newteam', 'createteam', 'novotime', 'time'])
    async def team(self, ctx: commands.Context):
        creation_message = None
        try:
            await ctx.message.delete()
            cancel_command = f'{self.bot.setting.prefix}cancelar'
            creation_message_content = (
                "Criação de time iniciada por {author}.\n\n"
                "Digite `{cancel}` a qualquer momento para cancelar.\n\n"
                "**Título:** {title}\n"
                "**Tamanho:** {size}\n"
                "**Chat:** {chat}\n"
                "**Requisito:** {requisito}\n"
                "**Requisito Secundário:** {requisito_secundario}"
            )
            creation_message = await ctx.send(creation_message_content.format(
                author=ctx.author.mention,
                cancel=cancel_command,
                title='',
                size='',
                chat='',
                requisito='',
                requisito_secundario=''
            ))

            # Only accept answers from the the message author and in the same channel the commands was invoked
            def check(message):
                if ctx.channel != message.channel:
                    return False
                return message.author == ctx.author

            # Team Title
            sent_message = await ctx.send(
                f"{ctx.author.mention}, digite o nome do time. (e.g.: Solak 20:00)"
            )
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
                    requisito_secundario=''
                )
            )
            # Tamanho do time
            sent_message = await ctx.send(
                f"{ctx.author.mention}, digite o tamanho do time. (apenas números)"
            )
            team_size_message = await self.bot.wait_for('message', timeout=60.0, check=check)
            try:
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
                        requisito_secundario=''
                    )
                )
            except ValueError:
                await creation_message.delete()
                return await ctx.send(
                    f"Criação de time cancelada. Tamanho de time inválido ({team_size_message.content})."
                )

            # Chat para aceitar presenças
            sent_message = await ctx.send(
                f"{ctx.author.mention}, digite o chat onde o bot deve aceitar presenças para esse time."
            )
            chat_presence_message = await self.bot.wait_for('message', timeout=60.0, check=check)
            try:
                try:
                    await sent_message.delete()
                    await chat_presence_message.delete()
                except discord.errors.NotFound:
                    await ctx.send("Criação de time cancelada. A mensagem do Bot não foi encontrada.")
                    return await creation_message.delete()
                if chat_presence_message.content.lower() == cancel_command:
                    await creation_message.delete()
                    return await ctx.send("Criação de time cancelada.")
                chat_presence_id = int(re.findall(r'\d+', chat_presence_message.content)[0])
                await creation_message.edit(
                    content=creation_message_content.format(
                        author=ctx.author.mention,
                        cancel=cancel_command,
                        title=team_title,
                        size=team_size,
                        chat=f"<#{chat_presence_id}>",
                        requisito='',
                        requisito_secundario=''
                    )
                )
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
            role_str = 'Nenhum'
            role_message = await self.bot.wait_for('message', timeout=60.0, check=check)
            try:
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
                    role_id = int(re.findall(r'\d+', role_message.content)[0])
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
                        requisito=role_str,
                        requisito_secundario=''
                    )
                )
            except ValueError:
                await creation_message.delete()
                return await ctx.send(f"Criação de time cancelada. Role inválido ({role_message.content}).")
            except IndexError:
                await creation_message.delete()
                return await ctx.send(f"Criação de time cancelada. Role inválido ({role_message.content}).")

            role_id2 = None
            if role_id:
                # Role requisito secundário (opcional)
                sent_message = await ctx.send(
                    f"{ctx.author.mention}, mencione o Role secundário de requisito para o time. (ou 'nenhum' caso nenhum)"
                )
                role_str2 = 'Nenhum'
                role_message2 = await self.bot.wait_for('message', timeout=60.0, check=check)

                try:
                    try:
                        await role_message2.delete()
                        await sent_message.delete()
                    except discord.errors.NotFound:
                        await ctx.send("Criação de time cancelada. A mensagem do Bot não foi encontrada.")
                        return await creation_message.delete()
                    if role_message2.content.lower() == 'nenhum':
                        role_id2 = None
                    elif role_message2.content.lower() == cancel_command:
                        await creation_message.delete()
                        return await ctx.send("Criação de time cancelada.")
                    else:
                        role_id2 = int(re.findall(r'\d+', role_message2.content)[0])
                        if not any(role.id == role_id2 for role in ctx.guild.roles):
                            await creation_message.delete()
                            return await ctx.send(
                                f"Criação de time cancelada. Role inválido ({role_message2.content}).")
                        for role in ctx.guild.roles:
                            if role.id == role_id2:
                                role_str2 = str(role)
                    await creation_message.edit(
                        content=creation_message_content.format(
                            author=ctx.author.mention,
                            cancel=cancel_command,
                            title=team_title,
                            size=team_size,
                            chat=f"<#{chat_presence_id}>",
                            requisito=role_str,
                            requisito_secundario=role_str2
                        )
                    )
                except ValueError:
                    await creation_message.delete()
                    return await ctx.send(f"Criação de time cancelada. Role inválido ({role_message2.content}).")
                except IndexError:
                    await creation_message.delete()
                    return await ctx.send(f"Criação de time cancelada. Role inválido ({role_message2.content}).")

            invite_channel = self.bot.get_channel(chat_presence_id)

            description = f'Marque presença no <#{chat_presence_id}>\nCriador: <@{ctx.author.id}>'
            requisito = ""
            requisito2 = ""
            if role_id:
                requisito = f"Requisito: <@&{role_id}>\n"
            if role_id2:
                requisito2 = f"Requisito Secundário: <@&{role_id2}>\n\n"

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
                'team_id': team_id,
                'title': team_title,
                'size': team_size,
                'role': role_id,
                'role_secondary': role_id2,
                'author_id': ctx.author.id,
                'invite_channel_id': invite_channel.id,
                'invite_message_id': invite_embed_message.id,
                'team_channel_id': ctx.channel.id,
                'team_message_id': team_embed_message.id,
            }
            self.save_team(team=created_team)
            await creation_message.delete()
        except discord.errors.NotFound:
            return await ctx.send(f"Criação de time cancelada. A mensagem do Bot não foi encontrada.")
        except asyncio.TimeoutError:
            await creation_message.delete()
            return await ctx.send("Criação de time cancelada. Tempo Esgotado.")

    @staticmethod
    def save_team(team: dict):
        with db.Session() as session:
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
                team_message_id=str(team.get('team_message_id'))
            )
            session.add(team)
            session.commit()

    @staticmethod
    def current_id():
        with db.Session() as session:
            try:
                current_id = int(session.query(Team).filter(Team.team_id != 'raids').order_by(
                    Team.team_id.desc()).first().team_id)
            except (AttributeError, ValueError):
                return 0
        return current_id


def setup(bot):
    bot.add_cog(TeamCommands(bot))
