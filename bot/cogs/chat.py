from discord.ext import commands
import discord
import asyncio
import rs3clans

from bot.bot_client import Bot
from bot.utils.tools import right_arrow, has_any_role


class Chat(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(aliases=['role', 'membro'])
    async def aplicar_role(self, ctx: commands.Context):

        # F
        # if ctx.author.id == 403632514800943104:
        #     messages = [
        #         "Are u havin' a laugh mate?",
        #         "Umbasa",
        #         "⬆ ⬆ ⬇ ⬇ ⬅ ➡ ⬅ ➡ 🅱 🅰 `start`",
        #         "Keep Trying",
        #         "Shout, “Jesus is alive!”",
        #         "But Our Princess is in Another Castle!",
        #         "01110111 01110010 01101001 01101111 01100001 01111001 "
        #         "01110010 01100110 01101001 01101111 01100001 01110111 "
        #         "01100100 01101111 01101001 01110111 01100001 01101000 "
        #         "01101111 01101001 01100100 01101000 01110111 01100001 "
        #         "01101111 01101001 01111001 01110010 01101111 01101001 "
        #         "01100001 01110111 01101000 01100100 01101111 01101001 "
        #         "01100001 01101000 01110111 01101111 01101001 01100100"
        #         "Reality can be whatever I want",
        #         "I'm like TT, just like TT!",
        #         "1. e4 e5 2. Ke2 Ke7 3. Qe1 Qe8 4. Kd1 Kd8",
        #         "apt-get moo",
        #         "Hello World",
        #         "Kono Dio Da!",
        #         "lero lero lero lero lero",
        #         "Wryyyyyyyyyy"
        #     ]
        #     return await ctx.send(random.choice(messages))
        if not has_any_role(ctx.author, self.bot.setting.role.get('convidado')):
            return await ctx.send("Fool! Você não é um Convidado!")

        def check(message):
            return message.author == ctx.author

        await ctx.send(f"{ctx.author.mention}, por favor me diga o seu nome no jogo.")

        try:
            ingame_name = await self.bot.wait_for('message', timeout=180.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Tempo Esgotado. Por favor tente novamente mais tarde.")
        await ctx.trigger_typing()
        player = rs3clans.Player(ingame_name.content)
        if not player.exists:
            return await ctx.send(f"{ctx.author.mention}, o jogador '{player.name}' não existe.")
        elif player.clan != self.bot.setting.clan_name:
            return await ctx.send(f"{ctx.author.mention}, o jogador '{player.name}' não é um membro do Clã Atlantis.")
        return await ctx.send(
            f"{ctx.author.mention} um <@&{self.bot.setting.role.get('mod')}> ou "
            f"<@&{self.bot.setting.role.get('admin')}> irá dar seu cargo em breve :)"
        )

    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(aliases=['aplicar', 'raids'])
    async def aplicar_raids(self, ctx: commands.Context):
        print(f"> {ctx.author} issued command 'aplicar_raids'.")
        raids_channel = f"<#{self.bot.setting.chat.get('raids')}>"

        aplicar_message = f"""
Olá! Você aplicou para receber a tag de Raids e participar dos Raids do Clã.

Favor postar uma screenshot que siga ao máximo possível as normas que estão escritas no topo do canal {raids_channel}
Use a imagem a seguir como base: <https://i.imgur.com/M4sU24s.png>

**Inclua na screenshot:**
 {right_arrow} Aba de `Equipamento` que irá usar
 {right_arrow} Aba de `Inventário` que irá usar
 {right_arrow} **`Perks de todas as suas Armas e Armaduras que pretende usar`**
 {right_arrow} `Stats`
 {right_arrow} `Barra de Habilidades` no modo de combate que utiliza
 {right_arrow} `Nome de usuário in-game`

Aguarde uma resposta de um <@&{self.bot.setting.role.get('raids_teacher')}>.

***Exemplo:*** https://i.imgur.com/CMNzquL.png"""

        denied_message = "Fool! Você já tem permissão para ir Raids!"
        if has_any_role(ctx.author, self.bot.setting.role.get('raids')):
            return await ctx.send(denied_message)
        return await ctx.send(aplicar_message)

    @commands.command(aliases=['aplicaraod', 'aod', 'aodaplicar', 'aod_aplicar'])
    async def aplicar_aod(self, ctx: commands.Context):
        print(f"> {ctx.author} issued command 'aplicar_aod'.")
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

***Exemplo (Aplicação para Raids):*** https://i.imgur.com/CMNzquL.png"""

        denied_message = "Fool! Você já tem permissão para ir nos times de AoD!"

        if has_any_role(ctx.author, self.bot.setting.role.get('aod')):
            return await ctx.send(denied_message)
        return await ctx.send(aplicar_message)

    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=['git', 'source'])
    async def github(self, ctx: commands.Context):
        print(f"> {ctx.author} issued command 'github'.")
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
