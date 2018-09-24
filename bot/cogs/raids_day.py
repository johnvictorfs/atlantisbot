# Non-Standard lib imports
from discord.ext import commands
import discord

# Local imports
import definesettings as setting

def check_role(ctx, *roles):
    for role in roles:
        if role in str(ctx.message.author.roles):
            return True
    return False


class RaidsDay:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def set_raids_day(self, ctx, *, day):
        print(f"{ctx.author} has issued set_raids_day command.")
        if not check_role(ctx, "Mod+", "Admin"):
            print("    - Denied")
            return

        day = int(day)
        with open("dia_de_raids.txt", "w") as f:
            f.write(f"; 0 = par, 1 = ímpar\n{day}")
            await ctx.send(f"Raids day foi marcado para {day} - (0 = par, 1 = ímpar)")

    @commands.command()
    async def test_raids_notif(self, ctx):
        print(f"{ctx.author} has issued test_raids_notif command.")

        if not check_role(ctx, "Admin"):
            print("    - Denied.")
            return

        embed_title = "**Raids**"
        clan_banner_url = f"http://services.runescape.com/m=avatar-rs/l=3/a=869/{setting.CLAN_NAME}/clanmotif.png"
        raids_notif_embed = discord.Embed(title=embed_title,
                                          description="",
                                          color=discord.Colour.dark_blue())
        raids_notif_embed.set_thumbnail(url=clan_banner_url)
        raids_notif_embed.add_field(
        name="Marque presença para os Raids de 21:00",
        value=f"{setting.RAIDS_CHAT_ID}\n"
              f"\n"
              f"É obrigatório ter a tag <@&376410304277512192>\n    - Leia os tópicos fixos para saber como obter\n"
              f"\n"
              f"Não mande mensagens desnecessárias no {setting.RAIDS_CHAT_ID}\n"
              f"\n"
              f"Não marque presença mais de uma vez\n"
              f"\n"
              f"Esteja online no jogo no mundo 75 até 20:50 em ponto.\n    - Risco de remoção do time caso contrário. Não cause atrasos.",
        inline=False)

        print("    - Answer sent")
        await ctx.send(content="@Notif", embed=raids_notif_embed)


def setup(bot):
    bot.add_cog(RaidsDay(bot))
