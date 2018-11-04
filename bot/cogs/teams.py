# Standard lib imports
import os
import datetime
import traceback

# Non-Standard lib imports
import discord
from discord.ext import commands

# Local imports
from .utils import separator
import definesettings as setting


def check_role(ctx, *roles):
    for role in roles:
        if role in str(ctx.message.author.roles):
            return True
    return False


class TeamCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['maketeam', 'newteam', 'createteam'])
    async def team(self, ctx, title, team_size, channel=None, role=None):
        try:
            try:
                TEAM_ID = int(os.environ.get('TEAM_ID', "0"))
                if TEAM_ID == 0:
                    os.environ['TEAM_ID'] = str(1)
                else:
                    os.environ['TEAM_ID'] = str(TEAM_ID + 1)
                TEAM_ID += 1
            except Exception as e:
                await ctx.send("Erro inesperado. Contate ")
            print(f"$ Created Team '{title}' with TEAM_ID: {TEAM_ID} by '{ctx.author}'")
            if channel:
                try:
                    team_size = int(team_size)
                except ValueError:
                    return await ctx.send(f"Valor inválido: Tamanho de time ({team_size})")
                try:
                    channel_id = int(channel.replace('<', '').replace('#', '').replace('>', ''))
                except ValueError:
                    return await ctx.send(f"Valor inválido: Canal ({channel})")
                try:
                    input_channel = channel
                    channel = self.bot.get_channel(int(channel_id))
                    if not channel:
                        return await ctx.send(f"Valor inválido: Canal ({input_channel})")
                except Exception as e:
                    await ctx.send(f"{e}: Erro inesperado.")
            else:
                channel = ctx.channel
            description = ""
            requisito = "\n"
            if role:
                description += f"Necessário: {role}"
                requisito = f"Requisito: {role}\n\n"
            if channel:
                description += f"\nMarque presença no: {channel.mention}"
            invite_embed = discord.Embed(
                title=f"Marque presença para '{title}' ({team_size} pessoas)",
                description=f"{separator}\nTime: {ctx.channel.mention}\n{requisito}"
                            f"`in {TEAM_ID}`: Marcar presença\n"
                            f"`out {TEAM_ID}`: Retirar presença"
            )
            embed_footer = f"Digite '{setting.PREFIX}del {TEAM_ID}' para excluir o time."
            team_embed = discord.Embed(
                title=f"__{title}__ - 0/{team_size}",
                description=description,
                color=discord.Color.purple()
            )
            team_embed.set_footer(
                text=embed_footer
            )
            await ctx.send(embed=team_embed)
            team_message = await ctx.channel.history().get(author=self.bot.user)
            try:
                await channel.send(embed=invite_embed)
            except discord.errors.Forbidden as e:
                await team_message.delete()
                return await ctx.send(f"{e}: Permissões insuficientes para enviar mensagens no canal {channel.mention}")
            last_message = await channel.history().get(author=self.bot.user)
            invite_message = await channel.history().get(author=self.bot.user)
            team_list = []  # TODO: Change this into a dictionary, so users can also pass in their roles when joining a team
            while True:
                async for message in channel.history(after=last_message):
                    if message.content.lower() == f'in {TEAM_ID}':
                        if message.author.bot:
                            await channel.send(f"`beep boop`\nHow do you do fellow human?")
                            continue
                        try:
                            await message.delete()
                        except discord.errors.Forbidden:
                            print(f'$ No permissions to delete messages in channel {message.channel.mention} ({message.channel})')
                        roles = []
                        for role_ in message.author.roles:
                            # This makes it so roles list contains all the roles the user has, in mention format
                            # since this is what's passed in when creating a team
                            roles.append(f"<@&{role_.id}>")
                        # If user has required role or if no required role was passed when creating the team, then
                        # the user can procceed to be added to the team (or not if it's already full or if he's in it already)
                        if role in roles or not role:
                            if message.author.mention in team_list:
                                await channel.send(f"Ei {message.author.mention}, você já está no time '{title}'! Não tente me enganar.")
                            elif len(team_list) >= int(team_size):
                                await channel.send(f"{message.author.mention}, o time '{title}' já está cheio! ({len(team_list)}/{team_size})")
                            else:
                                team_list.append(message.author.mention)
                                await channel.send(f"{message.author.mention} foi adicionado ao time '{title}'. ({len(team_list)}/{team_size})")
                        else:
                            no_perm_embed = discord.Embed(
                                title=f"__Permissões insuficientes__",
                                description=f"Você precisa ter o cargo {role} para entrar nesse time.",
                                color=discord.Color.dark_red()
                            )
                            await channel.send(content=message.author.mention, embed=no_perm_embed)
                    elif message.content.lower() == f'out {TEAM_ID}':
                        if message.author.bot:
                            await channel.send(f"`beep boop`\nHow do you do fellow human?")
                            continue
                        try:
                            await message.delete()
                        except discord.errors.Forbidden:
                            print(f'$ No permissions to delete messages in channel {message.channel.mention} ({message.channel})')
                        if message.author.mention in team_list:
                            team_list.remove(message.author.mention)
                            await channel.send(f"{message.author.mention} foi removido do time '{title}'. ({len(team_list)}/{team_size})")
                        else:
                            await channel.send(f"Ei {message.author.mention}, você já não estava no time '{title}'! Não tente me enganar.")
                    elif message.content.lower() == f'{setting.PREFIX}del {TEAM_ID}' and message.author == ctx.message.author:
                        print(f'$ Team \'{title}\' has been issued for deletion. ID: {TEAM_ID}')
                        try:
                            await team_message.delete()
                            await ctx.message.delete()
                            await invite_message.delete()
                            return await message.delete()
                        except discord.errors.Forbidden as e:
                            await message.channel.send(f"{e}: Permissões insuficientes para deletar mensagens no canal {message.channel.mention}")
                    last_message = message
                    async for message in ctx.channel.history(after=team_message):
                        if message.content.lower() == f'{setting.PREFIX}del {TEAM_ID}':
                            if message.author != ctx.message.author:
                                await message.channel.send(f"Você não é o autor desse time, portanto não tem permissão para o deletar.")
                            else:
                                print(f'$ Team \'{title}\' has been issued for deletion. ID: {TEAM_ID}')
                                try:
                                    await team_message.delete()
                                    await ctx.message.delete()
                                    await invite_message.delete()
                                    return await message.delete()
                                except Exception as e:
                                    await message.channel.send(f"{e}: Permissões insuficientes para deletar mensagens no canal {message.channel.mention}")
                team_embed = discord.Embed(
                    title=f"__{title}__ - {len(team_list)}/{team_size}",
                    description=description,
                    color=discord.Color.purple()
                )
                team_embed.set_footer(
                    text=embed_footer
                )
                # Adds fields to the team embed with all the members in the team list
                for index, member in enumerate(team_list):
                    team_embed.add_field(
                        name=separator,
                        value=f"{index + 1}- {member}",
                        inline=False
                    )
                try:
                    # Updates the team message with the new list
                    await team_message.edit(embed=team_embed)
                except discord.NotFound:
                    # This breaks out of the loop and ends the command if the team list message has been deleted.
                    # This way a team can be interrupted by a Mod/Admin in case the person who created it isn't feeling like
                    # removing it
                    try:
                        await ctx.message.delete()
                    except discord.NotFound:
                        pass
                    break
        except Exception as e:
            traceback.print_exc()
            logs_channel = self.bot.get_channel(int(setting.LOGS_CHANNEL))
            await logs_channel.send(f"""
<@148175892596785152>

Exception: `{e}`

Command: `teams`

Author: `{ctx.author}`

Channel: `#{ctx.channel}`

**Arguments:**

`title::`
    {title}

`team_size::`
    {team_size}

`channel::`
    {channel}

`role::`
    {str(role)}


DATE: `{datetime.datetime.now()}`
ID: `{TEAM_ID}`
""")


def setup(bot):
    bot.add_cog(TeamCommands(bot))
