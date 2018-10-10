# Non-Standard lib imports
from discord.ext import commands
import discord

# Local imports
import definesettings as setting
from . import embeds


def check_role(ctx, *roles):
    for role in roles:
        if role in str(ctx.message.author.roles):
            return True
    return False


class EmbedMessages:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['server_tags_embed_', 'post_server_tags_embed'])
    async def server_tags_embed(self, ctx):
        print(f"{ctx.author} issued command server_tags_embed")
        if not check_role(ctx, "Admin"):
            print(f"{ctx.author}: D E N I E D")
            return

        pvm_embed = embeds.get_pvm_embed()
        general_embed = embeds.get_general_embed()
        reactions_embed = embeds.get_reactions_embed()

        await ctx.send(content=None, embed=pvm_embed)
        await ctx.send(content=None, embed=general_embed)
        await ctx.send(content=None, embed=reactions_embed)

    @commands.command()
    async def send_static_welcome_message(self, ctx):
        print(f"{ctx.author} issued command send_static_welcome_message")

        if not check_role(ctx, "Admin"):
            print(f"{ctx.author}: D E N I E D")
            return
        tags_do_server = setting.MESSAGES["chat"]["tags_do_server"]
        discord_bots = setting.MESSAGES["chat"]["discord_bots"]
        links_pvm = setting.MESSAGES["chat"]["links_pvm"]
        raids = setting.MESSAGES["chat"]["raids"]
        pvmemes = setting.MESSAGES["chat"]["pvmemes"]
        durzag = "<#488112229430984704>"
        guia_yaka = "<#425844417862041610>"
        guia_aod = "<#354335920297738240>"
        geral = "<#321012292160454657>"
        visitantes = "<#321012324997529602>"
        drops_e_conquistas = "<#336182514886377482>"
        anuncios = "<#467069985270005760>"

        welcome_embed = discord.Embed(
            title=f"Bem vindo ao Discord do Atlantis!",
            description=f"Caso seja um membro do Atlantis, digite `{setting.PREFIX}role` no canal {visitantes}",
            color=discord.Color.blue()
        )

        welcome_embed.add_field(
            name=f"**Conheça os chats do Servidor:**",
            value=(
                f"⯈ {geral} Chat geral (Membros apenas)\n"
                f"⯈ {visitantes} Chat geral (Aberto para todos)\n"
                f"⯈ {anuncios} Anúncios feitos pela administração do Clã\n"
                f"\n"
                f"⯈ {tags_do_server} para info sobre os Roles do server\n"
                f"⯈ {links_pvm} para informações úteis sobre PvM\n"
                f"⯈ {pvmemes} para conversas gerais ou notificar trips de PvM\n"
                f"⯈ {discord_bots} para comandos de Bots\n"
                f"⯈ {drops_e_conquistas} para mostrar suas conquistas no jogo\n"
                f"⯈ {raids} para aplicar para os Raids do Clã (Membros apenas)\n"
                f"⯈ {durzag} para eventos de Beastmaster Durzag do Clã (Membros apenas)\n"
                f"⯈ {guia_yaka} Guia de Yakamaru\n"
                f"⯈ {guia_aod} Guia de Nex: Angel of Death\n"),
            inline=False
        )

        welcome_embed.add_field(
            name="Site do Clã",
            value="<https://rsatlantis.com/>",
            inline=False)

        welcome_embed.add_field(
            name="Verifique o calendário do Clã",
            value="<https://rsatlantis.com/calendario>",
            inline=False)

        welcome_embed.add_field(
            name="Convite para esse discord",
            value="<https://discord.me/atlantis>",
            inline=False
        )

        welcome_embed.add_field(
            name=f"Alguma reclamação/elogio/outro? Fale conosco!",
            value=f"<http://tiny.cc/atlantisouvidoria>"
        )

        welcome_embed.set_footer(
            text=f"Digite {setting.PREFIX}atlcommands para ver os meus comandos!")

        await ctx.send(content=None, embed=welcome_embed)

    @commands.command(aliases=['embed_edit', ])
    async def edit_embed(self, ctx, message_id, category, channel_id=382691780996497416):
        print(f'Command edit_embed issued by {ctx.author}.')
        if not check_role(ctx, "Admin"):
            print(f"{ctx.author}: D E N I E D")
            return
        try:
            message_id = int(message_id)
        except ValueError:
            await ctx.send(f"Error: '{message_id}' is not a valid message id.")
            return
        try:
            category = str(category)
        except ValueError:
            await ctx.send(f"Error: '{category}' is not a valid category.")
            return
        try:
            channel_id = int(channel_id)
        except ValueError:
            await ctx.send(f"Error: '{channel_id}' is not a valid channel id.")
            return
        if category.lower() == 'pvm':
            embed = embeds.get_pvm_embed()
        elif category.lower() == 'general':
            embed = embeds.get_general_embed()
        elif category.lower() == 'reaction':
            embed = embeds.get_reactions_embed()
        else:
            await ctx.send(f"Error: '{category}' is not a valid category.")
            return
        channel = self.bot.get_channel(channel_id)
        async for message in channel.history():
            if message.id == message_id:
                await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(EmbedMessages(bot))
