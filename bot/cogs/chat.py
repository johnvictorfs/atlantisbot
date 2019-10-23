from discord.ext import commands
import discord
import asyncio
import aiohttp
import rs3clans

import datetime
import json

from bot.bot_client import Bot
from bot.cogs.raids import time_till_raids
from bot.utils.tools import right_arrow, has_any_role


class Chat(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    async def get_price(item_id: int):
        """
        Gets the current price for an item in the GE based on its Item ID
        """
        url = f"http://services.runescape.com/m=itemdb_rs/api/catalogue/detail.json?item={item_id}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                data = await r.text()
                data = json.loads(data)
                try:
                    return int(data['item']['current']['price'].replace(',', ''))
                except ValueError:
                    return data['item']['current']['price']

    # @commands.guild_only()
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # @commands.command(aliases=['role', 'membro'])
    # async def aplicar_role(self, ctx: commands.Context):
    #     if not has_any_role(ctx.author, self.bot.setting.role.get('convidado')):
    #         return await ctx.send("Fool! Você não é um Convidado!")
    #
    #     def check(message):
    #         return message.author == ctx.author
    #
    #     await ctx.send(f"{ctx.author.mention}, por favor me diga o seu nome no jogo.")
    #
    #     try:
    #         ingame_name = await self.bot.wait_for('message', timeout=180.0, check=check)
    #     except asyncio.TimeoutError:
    #         return await ctx.send(f"{ctx.author.mention}, autenticação Cancelada. Tempo Esgotado.")
    #     await ctx.trigger_typing()
    #     player = rs3clans.Player(ingame_name.content)
    #     if not player.exists:
    #         return await ctx.send(f"{ctx.author.mention}, o jogador '{player.name}' não existe.")
    #     elif player.clan != self.bot.setting.clan_name:
    #         return await ctx.send(f"{ctx.author.mention}, o jogador '{player.name}' não é um membro do Clã Atlantis.")
    #     return await ctx.send(
    #         f"{ctx.author.mention} um <@&{self.bot.setting.role.get('mod')}> ou "
    #         f"<@&{self.bot.setting.role.get('admin')}> irá dar seu cargo em breve :)"
    #     )

    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(aliases=['raids'])
    async def aplicar_raids(self, ctx: commands.Context):
        denied_message = "Fool! Você já tem permissão para ir Raids!"
        if has_any_role(ctx.author, self.bot.setting.role.get('raids')):
            return await ctx.send(denied_message)

        await ctx.send(f"Olá {ctx.author.mention}, por favor me diga o seu nome no Jogo.")

        raids_channel = f"<#{self.bot.setting.chat.get('raids')}>"

        def check(message):
            return message.author == ctx.author

        try:
            ingame_name = await self.bot.wait_for('message', timeout=180.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send(f"{ctx.author.mention}, aplicação Cancelada. Tempo Esgotado.")

        await ctx.trigger_typing()

        try:
            player = rs3clans.Player(ingame_name.content)
        except ConnectionError:
            return await ctx.send('Não foi possível acessar a API do Runemetrics no momento, tente novamente mais tarde.')

        if not player.exists:
            return await ctx.send(f"{ctx.author.mention}, o jogador '{player.name}' não existe.")
        elif player.clan != self.bot.setting.clan_name:
            return await ctx.send(f"{ctx.author.mention}, o jogador '{player.name}' não é um membro do Clã Atlantis.")
        elif player.private_profile:
            return await ctx.send(
                f"{ctx.author.mention}, seu perfil no Runemetrics está privado, por favor o deixe público "
                f"e tente aplicar novamente."
            )

        emojis = {
            'prayer': '<:prayer:499707566012497921>',
            'herblore': '<:herblore:499707566272544778>',
            'attack': '<:attack:499707565949583391>',
            'invention': '<:invention:499707566419607552>',
            'inventory': '<:inventory:615747024775675925>',
            'full_manual': '<:full_manual:615751745049722880>'
        }

        herb_level = player.skill('herblore').level
        if herb_level < 90:
            await ctx.send(f"Ei {ctx.author.mention}, vejo aqui que seu nível de {emojis['herblore']} "
                           f"Herbologia é apenas "
                           f"**{herb_level}**. Isso é um pouco baixo!\n"
                           f"**Irei continuar com o processo de aplicação, mas não será possível te dar permissão para "
                           f"participar no momento, aplique novamente quando obter um nível de {emojis['herblore']} "
                           f"Herbologia superior a "
                           f"90**, falta apenas **{5_346_332 - player.skill('herblore').exp:,.0f}** de Exp!")
        elif 96 > herb_level >= 90:
            await ctx.send(f"Ei {ctx.author.mention}, vejo aqui que seu nível de {emojis['herblore']} "
                           f"Herbologia é **{herb_level}**. "
                           f"Isso é suficiente para fazer Poções de sobrecarregamento (Overloads), mas "
                           f"apenas usando Boosts, caso já não tenha, faça alguns usando o seguinte "
                           f"boost (ou outro se possível/preferir) <https://rs.wiki/Spicy_stew>")

        prayer_level = player.skill('prayer').level
        left_to_95 = 8_771_558 - player.skill('prayer').exp

        if prayer_level < 95:
            d_bones_price = await self.get_price(536)
            d_bones_exp = 252
            d_bones_till_99 = int(left_to_95 / d_bones_exp)

            f_bones_price = await self.get_price(18832)
            frost_bones_exp = 630
            f_bones_till_99 = int(left_to_95 / frost_bones_exp)

            gp_emoji = "<:coins:573305319661240340>"

            await ctx.send(
                f"Ei {ctx.author.mention}, vejo aqui que seu nível de {emojis['prayer']} Oração é "
                f"apenas **{prayer_level}**. Isso é um pouco baixo!\n"
                f"Mas tudo bem, falta apenas **{int(left_to_95):,.0f}** de Exp para o nível 95. Com esse nível você "
                f"irá poder usar as segundas melhores Maldições de aumento de dano. Há diversas formas de você "
                f"alcançar o nível 95. Veja algumas abaixo:\n"
                f"⯈ {int(left_to_95 / d_bones_exp):,.0f} Ossos de Dragão no Altar de Casa sem nenhum Boost "
                f"({gp_emoji} {int(d_bones_till_99 * d_bones_price):,.0f})\n"
                f"⯈ {int(left_to_95 / frost_bones_exp):,.0f} Ossos de Dragão Gelado no Altar de Casa sem nenhum Boost "
                f"({gp_emoji} {int(f_bones_till_99 * f_bones_price):,.0f})\n"
            )

        embed = discord.Embed(
            title="Aplicação para Raids",
            description=f"Olá! Você aplicou para receber o cargo <@&{self.bot.setting.role.get('raids')}> para "
                        f"participar dos Raids do Clã.",
            color=discord.Color.blue()
        )

        nb_space = '\u200B'

        embed.set_thumbnail(url="https://i.imgur.com/CMNzquL.png")

        embed.add_field(
            name=f"{nb_space}\nPor favor postar uma ou mais screenshots com os itens abaixo. "
                 f"(pode enviar uma de cada vez)",
            value=f"⯈ {emojis['attack']} Equipamento (Arma/Armadura/Acessórios/Switches etc.)\n"
                  f"⯈ {emojis['inventory']} Inventário\n"
                  f"⯈ {emojis['invention']} Perks de Arma, Armadura, Escudo e Switches que irá usar\n\n",
            inline=False
        )

        perks_pocketbook = 'https://rspocketbook.com/rs_pocketbook.pdf#page=6'
        embed.add_field(
            name=f"{nb_space}\nLinks Úteis",
            value=f"⯈ {emojis['full_manual']} [Exemplos de Barras de Habilidade](https://imgur.com/a/XKzqyFs)\n"
                  f"⯈ {emojis['invention']} [Melhores Perks e como os obter]({perks_pocketbook})\n"
                  f"⯈ [Exemplo de Aplicação](https://i.imgur.com/CMNzquL.png)\n"
                  f"⯈ Guia de Yakamaru: <#{self.bot.setting.chat.get('guia_yaka')}>\n\n",
            inline=False
        )

        seconds_till_raids = time_till_raids(self.bot.setting.raids_start_date)
        raids_diff = datetime.timedelta(seconds=seconds_till_raids)

        days = raids_diff.days
        hours = raids_diff.seconds // 3600
        minutes = (raids_diff.seconds // 60) % 60

        embed.add_field(
            name=f"{nb_space}\nInformações sobre os Times",
            value=f"Os times de Raids acontecem a cada 2 Dias.\n**A próxima "
                  f"notificação de Raids será em {days} Dia(s), {hours} Hora(s) e "
                  f"{minutes} Minuto(s)**.\n\nPara participar basta digitar **`in raids`** no canal "
                  f"<#{self.bot.setting.chat.get('raids_chat')}> após a notificação do Bot, e ele irá o colocar "
                  f"no time automaticamente, caso o time já esteja cheio, ele te colocará como substituto até que "
                  f"abra alguma vaga. Caso aconteça, ele irá te notificar.\n\n1 hora após o Bot ter iniciado o time "
                  f"irá começar o Raids no jogo, não chegue atrasado. Mais informações no canal {raids_channel}.",
            inline=False
        )
        await ctx.send(embed=embed, content=f"<@&{self.bot.setting.role.get('raids_teacher')}>")

    @commands.command(aliases=['aplicaraod', 'aod', 'aodaplicar', 'aod_aplicar'])
    async def aplicar_aod(self, ctx: commands.Context):
        aod_channel = f"<#{self.bot.setting.chat.get('aod')}>"
        aod_teacher = f"<@&{self.bot.setting.role.get('aod_teacher')}>"

        aplicar_message = f"""
Olá! Você aplicou para receber a tag de AoD e participar dos times de Nex: AoD do Clã.

Favor postar uma screenshot que siga ao máximo possível as normas que estão escritas no topo do canal {aod_channel}
Use a imagem a seguir como base:

Inclua na screenshot:
 {right_arrow} Aba de Equipamento que irá usar
 {right_arrow} Aba de Inventário que irá usar
 {right_arrow} Perks de todas as suas Armas e Armaduras que pretende usar
 {right_arrow} Stats
 {right_arrow} Barra de Habilidades no modo de combate que utiliza
 {right_arrow} Nome de usuário in-game

Aguarde uma resposta de um {aod_teacher}.

***Exemplo(Aplicação para Raids): *** https: // i.imgur.com/CMNzquL.png"""

        denied_message = "Fool! Você já tem permissão para ir nos times de AoD!"

        if has_any_role(ctx.author, self.bot.setting.role.get('aod')):
            return await ctx.send(denied_message)
        return await ctx.send(aplicar_message)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=['git', 'source'])
    async def github(self, ctx: commands.Context):
        github_icon = "https://assets-cdn.github.com/images/modules/logos_page/GitHub-Mark.png"
        repo_url = "https://github.com/johnvictorfs/atlantisbot-rewrite"
        johnvictorfs_img = "https://avatars1.githubusercontent.com/u/37747572?s=460&v=4"
        johnvictorfs_url = "https://github.com/johnvictorfs"

        github_embed = discord.Embed(title="atlantisbot-rewrite", description="", color=discord.Colour.dark_blue(),
                                     url=repo_url)
        github_embed.set_author(icon_url=johnvictorfs_img, url=johnvictorfs_url, name="johnvictorfs")
        github_embed.set_thumbnail(url=github_icon)
        return await ctx.send(content=None, embed=github_embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=['atlbot', 'atlbotcommands'])
    async def atlcommands(self, ctx: commands.Context):
        runeclan_url = f"https://runeclan.com/clan/{self.bot.setting.clan_name}"
        clan_banner = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{self.bot.setting.clan_name}/clanmotif.png"
        embed_title = "RuneClan"

        atlcommands_embed = discord.Embed(
            title=embed_title,
            description="`<argumento>` : Obrigatório\n`(argumento|padrão:máximo)` : Opcional",
            color=discord.Colour.dark_blue(),
            url=runeclan_url,
        )
        atlcommands_embed.set_author(icon_url=clan_banner, name="AtlantisBot")
        atlcommands_embed.set_thumbnail(url=self.bot.setting.banner_image)

        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}claninfo <nome de jogador>",
            value="Ver info de Clã de Jogador",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}clan <nome de clã>",
            value=f"Ver info Básica de um Clã",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}ptbr_rankings (número de clãs|10:25)",
            value=f"Ver os Rankings dos Clãs PT-BR por base em Exp",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}raids",
            value="Aplicar para ter acesso aos Raids do Clã",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}aod",
            value="Aplicar para ter acesso aos times de AoD do Clã",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}membro",
            value="Aplicar para receber o role de Membro no Discord",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}comp (número da comp|1) (número de jogadores|10:50)",
            value="Ver as competições ativas do Clã",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}pcomp (número de jogadores|10:50)",
            value="Ver informação sobre a atual competição de Pontos em andamento",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}ranks",
            value="Ver os Ranks do Clã pendentes a serem atualizados",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}team",
            value="Criar um Time com presenças automáticas",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}github",
            value="Ver o repositório desse bot no Github",
            inline=False
        )
        atlcommands_embed.add_field(
            name=f"{self.bot.setting.prefix}atlbot",
            value="Ver essa mensagem",
            inline=False
        )
        atlcommands_embed.set_footer(text="Criado por @NRiver#2263")
        return await ctx.send(embed=atlcommands_embed)

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=['atlrepeat'])
    async def atlsay(self, ctx: commands.Context, *, message: str):
        message = message.split(' ')
        channel = message[-1]
        try:
            channel_id = int(channel.replace('<', '').replace('#', '').replace('>', ''))
        except ValueError:
            channel_id = None
        channel = self.bot.get_channel(channel_id)
        ext = ctx.channel
        if channel:
            ext = channel
            del message[-1]
        try:
            await ext.send(' '.join(message))
        except discord.errors.Forbidden as e:
            await ctx.send(f"{e}: Sem permissão para enviar mensagens no canal {ext.mention}")


def setup(bot):
    bot.add_cog(Chat(bot))
