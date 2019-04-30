import json

from discord.ext import commands
import discord

from bot.bot_client import Bot


class EmbedMessages(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    def welcome_embed(self) -> discord.Embed:
        visitantes = f"<#{self.bot.setting.chat.get('visitantes')}>"
        welcome_embed = discord.Embed(
            title=f"Bem vindo ao Discord do Atlantis!",
            description=f"Caso seja um membro do Atlantis, use `{self.bot.setting.prefix}membro` no canal {visitantes}",
            color=discord.Color.blue()
        )

        with open('bot/embeds.json') as f:
            embeds_file = json.load(f)

        message = ''
        for embed in embeds_file['welcome_message']['chats']:
            if embed['chats']:
                # Only add category if there are chats on it
                message += f"\n\n**- {embed['display_name']}**"
            for chat in embed['chats']:
                message += f"\n⯈ <#{self.bot.setting.chat.get(chat['name'])}> - {chat['text']}"

        welcome_embed.add_field(name=embeds_file['welcome_message']['title'], value=message, inline=False)

        for field in embeds_file['welcome_message']['extra_fields']:
            welcome_embed.add_field(name=field['name'], value=field['value'], inline=False)

        welcome_embed.set_footer(text=embeds_file['welcome_message']['footer'].format(prefix=self.bot.setting.prefix))

        return welcome_embed

    @commands.command(aliases=['send_welcome'])
    async def send_welcome_message(self, ctx: commands.Context):
        await ctx.message.delete()
        return await ctx.send(content=None, embed=self.welcome_embed())

    @commands.command(aliases=['update_welcome'])
    async def update_welcome_message(self, ctx: commands.Context):
        channel: discord.TextChannel = self.bot.get_channel(self.bot.setting.welcome_channel_id)
        message: discord.Message = await channel.fetch_message(self.bot.setting.welcome_message_id)
        await ctx.message.delete()
        return await message.edit(content=None, embed=self.welcome_embed())

    @commands.command()
    async def update_roles(self, ctx: commands.Context, test: bool = True):
        with open('bot/embeds.json') as f:
            embeds_file = json.load(f)
        channel: discord.TextChannel = self.bot.get_channel(self.bot.setting.roles_channel_id)

        pvm_message: discord.Message = await channel.fetch_message(self.bot.setting.pvm_roles_id)
        general_message: discord.Message = await channel.fetch_message(self.bot.setting.general_roles_id)
        react_message: discord.Message = await channel.fetch_message(self.bot.setting.react_roles_id)

        pvm_embed = self.get_role_embed(embeds_file, 'pvm', discord.Color.red())
        general_embed = self.get_role_embed(embeds_file, 'gerais', discord.Color.blue())

        react_embed = discord.Embed(
            title=embeds_file['react']['title'],
            description=embeds_file['react']['description'],
            color=discord.Color.purple()
        )

        for role in embeds_file['react']['roles']:
            react_embed.add_field(name=role['emoji'], value=f"<@&{self.bot.setting.role.get(role['name'])}>")

        if test:
            await ctx.send(content=None, embed=pvm_embed)
            await ctx.send(content=None, embed=general_embed)
            await ctx.send(content=None, embed=react_embed)
        else:
            await pvm_message.edit(content=None, embed=pvm_embed)
            await general_message.edit(content=None, embed=general_embed)
            await react_message.edit(content=None, embed=react_embed)

    def get_role_embed(self, file: dict, name: str, color: discord.Color) -> discord.Embed:
        embed = discord.Embed(
            title=file['roles'][name]['title'],
            description=file['roles'][name]['description'],
            color=color
        )
        for role in file['roles'][name]['roles']:
            # Use the role mention as the name if possible, else the raw name in the json file
            # Use all roles if there is a key 'names' instead of 'name'
            role_id = self.bot.setting.role.get(role.get('name'))
            role_name = role.get('name')
            if role_id:
                role_name = f"<@&{role_id}>"
            else:
                if role.get('names'):
                    role_name = ''
                    for sub_role in role.get('names'):
                        role_name += f"<@&{self.bot.setting.role.get(sub_role)}> | "
            embed.add_field(name='-', value=f"{role_name}\n{role['text']}", inline=False)
        return embed


def setup(bot):
    bot.add_cog(EmbedMessages(bot))
