# Non-Standard lib imports
from discord.ext import commands


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
            print("D E N I E D")
            return

        day = int(day)
        with open("dia_de_raids.txt", "w") as f:
            f.write(f"; 0 = par, 1 = ímpar\n{day}")
            await ctx.send(f"Raids day foi marcado para {day} - (0 = par, 1 = ímpar)")


def setup(bot):
    bot.add_cog(RaidsDay(bot))
