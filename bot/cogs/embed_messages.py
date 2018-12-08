from discord.ext import commands
import discord

from bot.utils import embeds


class EmbedMessages:

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.command(aliases=['server_tags_embed_', 'post_server_tags_embed'])
    async def server_tags_embed(self, ctx: commands.Context):
        pvm_embed = embeds.get_pvm_embed(
            chat=self.bot.setting.chat,
            role=self.bot.setting.role
        )
        general_embed = embeds.get_general_embed(
            chat=self.bot.setting.chat,
            role=self.bot.setting.role,
            prefix=self.bot.setting.prefix
        )
        reactions_embed = embeds.get_reactions_embed(
            role=self.bot.setting.role
        )

        await ctx.send(content=None, embed=pvm_embed)
        await ctx.send(content=None, embed=general_embed)
        await ctx.send(content=None, embed=reactions_embed)

    @commands.command()
    async def send_static_welcome_message(self, ctx: commands.Context):
        tags_do_server = f"<#{self.bot.setting.chat.get('tags_do_server')}>"
        discord_bots = f"<#{self.bot.setting.chat.get('discord_bots')}>"
        links_pvm = f"<#{self.bot.setting.chat.get('links_uteis')}>"
        raids = f"<#{self.bot.setting.chat.get('raids')}>"
        pvmemes = f"<#{self.bot.setting.chat.get('pvmemes')}>"
        guia_yaka = f"<#{self.bot.setting.chat.get('guia_yaka')}>"
        guia_aod = f"<#{self.bot.setting.chat.get('guia_aod')}>"
        geral = f"<#{self.bot.setting.chat.get('geral')}>"
        visitantes = f"<#{self.bot.setting.chat.get('visitantes')}>"
        drops_e_conquistas = f"<#{self.bot.setting.chat.get('drops_e_conquistas')}>"
        anuncios = f"<#{self.bot.setting.chat.get('anuncios')}>"
        aod = f"<#{self.bot.setting.chat.get('aod')}>"
        solak = f"<#{self.bot.setting.chat.get('solak')}>"

        welcome_embed = discord.Embed(
            title=f"Bem vindo ao Discord do Atlantis!",
            description=f"Caso seja um membro do Atlantis, use `{self.bot.setting.prefix}membro` no canal {visitantes}",
            color=discord.Color.blue()
        )

        welcome_embed.add_field(
            name=f"**Conheça os chats do Servidor:**",
            value=(
                f"⯈ {geral} Chat geral (Membros apenas)\n"
                f"⯈ {visitantes} Chat geral (Aberto para todos)\n"
                f"⯈ {anuncios} Anúncios feitos pela administração do Clã\n"
                f"⯈ {tags_do_server} para info sobre os Roles do server\n"
                f"\n"
                f"⯈ {links_pvm} para informações úteis sobre PvM\n"
                f"⯈ {pvmemes} para conversas gerais ou notificar trips de PvM\n"
                f"\n"
                f"⯈ {discord_bots} para comandos de Bots\n"
                f"⯈ {drops_e_conquistas} para mostrar suas conquistas no jogo\n"
                f"\n"
                f"⯈ {raids} para aplicar para os Raids do Clã (Membros apenas)\n"
                f"⯈ {aod} para aplicar para os times de AoD do Clã (Membros apenas)\n"
                f"⯈ {solak} para aplicar para os times de Solak do Clã (Membros apenas)\n"
                f"\n"
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
            text=f"Digite {self.bot.setting.prefix}atlbot para ver os meus comandos!")

        return await ctx.send(content=None, embed=welcome_embed)

    @commands.command(aliases=['embed_edit', ])
    async def edit_embed(self, ctx: commands.Context, message_id, category, channel_id=382691780996497416):
        try:
            message_id = int(message_id)
        except ValueError:
            return await ctx.send(f"Error: '{message_id}' is not a valid message id.")
        try:
            category = str(category)
        except ValueError:
            return await ctx.send(f"Error: '{category}' is not a valid category.")
        try:
            channel_id = int(channel_id)
        except ValueError:
            return await ctx.send(f"Error: '{channel_id}' is not a valid channel id.")
        if category.lower() == 'pvm':
            embed = embeds.get_pvm_embed(
                role=self.bot.setting.role,
                chat=self.bot.setting.chat
            )
        elif category.lower() == 'general':
            embed = embeds.get_general_embed(
                role=self.bot.setting.role,
                prefix=self.bot.setting.prefix,
                chat=self.bot.setting.chat
            )
        elif category.lower() == 'reaction':
            embed = embeds.get_reactions_embed(
                self.bot.setting.role
            )
        else:
            return await ctx.send(f"Error: '{category}' is not a valid category.")
        channel = self.bot.get_channel(channel_id)
        async for message in channel.history():
            if message.id == message_id:
                print(f"    Edited message: {message}")
                await message.edit(embed=embed)
                return await ctx.send("Mensagem editada com sucesso.")


def setup(bot):
    bot.add_cog(EmbedMessages(bot))
