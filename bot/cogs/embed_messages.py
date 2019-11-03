import json

from discord.ext import commands
import discord

from bot.bot_client import Bot
from bot.utils.tools import separator


class EmbedMessages(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    def welcome_embed(self) -> discord.Embed:
        welcome_embed = discord.Embed(
            title=f"Bem vindo ao Discord do Atlantis!",
            description=f"Caso seja um membro do Atlantis, use `{self.bot.setting.prefix}membro` para mim no privado!",
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
                message += f"\n• <#{self.bot.setting.chat.get(chat['name'])}> - {chat['text']}"

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
    async def update_welcome_message(self, ctx: commands.Context, message_id: int):
        """
        Updates message with the ID passed with the Welcome Message embed
        """
        channel: discord.TextChannel = self.bot.get_channel(self.bot.setting.welcome_channel_id)
        message: discord.Message = await channel.fetch_message(message_id)
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

    @commands.command()
    async def update_raids_embed(self, ctx: commands.Context, message_id: int):
        """
        Updates message with the ID passed with the Welcome Message embed
        """
        channel: discord.TextChannel = self.bot.get_channel(self.bot.setting.chat.get('raids'))
        message: discord.Message = await channel.fetch_message(message_id)
        await ctx.message.delete()
        return await message.edit(content=None, embed=self.raids_embed())

    def get_role_embed(self, file: dict, name: str, color: discord.Color) -> discord.Embed:
        embed = discord.Embed(
            title=file['roles'][name]['title'],
            description=file['roles'][name]['description'],
            color=color
        )

        nb_space = '\u200B'

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

            embed.add_field(name=nb_space, value=f"{role_name}\n{role['text']}\n{nb_space}", inline=False)
        return embed

    def raids_embed(self) -> discord.Embed:
        raids_role = f"<@&{self.bot.setting.role.get('raids')}>"

        text = f"""Utilize os canais <#393696030505435136> para conversas sobre Raids

• Para aplicar vá para o canal <#615960733800202252> e utilize o comando `!raids`. Tenha em mente todas as informações abaixo ao aplicar
    • ***Ninguém será julgado por experiência/kc baixo, mas é necessário avaliar todos os participantes, até para que possamos os ajudar com quaisquer dúvidas/dificuldades.***

• Os aprovados irão receber o cargo {raids_role}

• Esse cargo é utilizado para notificar sempre que irá ser montado um time de Raids do Clã, e é um requisito para entrar neles
{separator}"""

        emojis = {
            'prayer': '<:prayer:499707566012497921>',
            'herblore': '<:herblore:499707566272544778>',
            'attack': '<:attack:499707565949583391>',
            'invention': '<:invention:499707566419607552>',
            'inventory': '<:inventory:615747024775675925>',
            'full_manual': '<:full_manual:615751745049722880>'
        }

        text_2 = f"""• **Arma** <:attack:499707565949583391> T87+ com [Acerto 4/5](https://rs.wiki/precise) e [Equilíbrio 3](https://rs.wiki/equilibrium) (Preferível [Abalo 3](https://rs.wiki/aftershock) no lugar de Equilíbrio)
• **Armadura** <:defence:499707566033600513> T70+ com [Crackling 3](https://rs.wiki/crackling), [Biting 2/3](https://rs.wiki/biting), [Impatient 3](https://rs.wiki/impatient) e [ED 3](https://rs.wiki/ed) ou [CS 3](https://rs.wiki/w/Crystal_Shield)

• <:summoning:499707566335459368> 84+ para [Spirit Pack Pig](https://rs.wiki/w/Spirit_pack_pig#Tier_3) ou melhor
• <:herblore:499707566272544778> 90+ para [Overloads](https://rs.wiki/overload) e Poções de [Restabelecimento](https://rs.wiki/replenishment_potion)
• <:prayer:499707566012497921> [Acesso a Maldições](https://runescape.wiki/w/Curse_spells)

• {emojis['full_manual']} **Usar habilidades adequadas** [Exemplos de Barras de Habilidade](https://imgur.com/a/XKzqyFs)
• __**Ver guias de Yakamaru E Durzag!!!**__ <#425844417862041610>"""

        text_3 = f"""
            • 95 + Oração <:prayer:499707566012497921>
            • Alguma experiência PvM, mesmo que solo
            • Marfim dos [Elementos](https://rs.wiki/w/Scrimshaw_of_the_elements)/[Crueldade](https://rs.wiki/Scrimshaw_of_cruelty) (Mage/Ranged)
            • Perk [Planted feet](https://rs.wiki/w/Planted_Feet) em uma arma primária extra
            • [Acessórios adequados](https://guide.rspocketbook.com)
            • [Exemplo de Inventário e Equipamento](https://i.imgur.com/M4sU24s.png)
        """

        embed = discord.Embed(
            title="Raids",
            description="Bem vindo ao canal de Raids do Clã\n__**Leia o Texto Abaixo para saber como Aplicar para Participar**__",
            color=discord.Color.blue()
        )
        embed.add_field(name="\u200b", value=text, inline=False)
        embed.add_field(name="__**REQUISITOS OBRIGATÓRIOS**__", value=text_2, inline=False)
        embed.add_field(name=f"{separator}\n__**ULTRA RECOMENDADOS**__", value=text_3, inline=False)
        embed.set_thumbnail(url=self.bot.setting.banner_image)
        return embed

    @commands.command('raids_embed')
    async def raids_channel_embed(self, ctx: commands.Context):
        await ctx.send(embed=self.raids_embed())


def setup(bot):
    bot.add_cog(EmbedMessages(bot))
