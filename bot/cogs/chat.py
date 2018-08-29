# Non-Standard lib imports
from discord.ext import commands

# Local imports
import definesettings as setting


class ChatCommands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['role', 'membro'])
    async def aplicar_role(self, ctx):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'aplicar_role'.")

        role_message = (f"Informe seu usuário in-game.\n\n"
                        f"{setting.MOD_ID} {setting.ADMIN_ID} "
                        f"- O(a) Senhor(a) acima deseja receber um cargo acima de Visitange. Favor verificar :)")

        denied_message = "Fool! Você não é um Convidado!"

        if self.check_role(ctx, "Convidado"):
            await ctx.send(role_message)
        else:
            await ctx.send(denied_message)

    @commands.command(aliases=['aplicar', 'raids'])
    async def aplicar_raids(self, ctx):
        await ctx.trigger_typing()
        print(f"> {ctx.author} issued command 'aplicar_raids'.")
        raids_chat = setting.RAIDS_CHAT_ID
        right_arrow = setting.MESSAGES["emoji"]["arrow_emoji"]

        aplicar_message = f"""
Olá! Você aplicou para receber a tag de Raids e participar dos Raids do Clã.

Favor postar uma screenshot que siga ao máximo possível as normas que estão escritas no topo do canal {raids_chat}
Use a imagem a seguir como base: <https://i.imgur.com/M4sU24s.png>

**Inclua na screenshot:**
 {right_arrow} Aba de `Equipamento` que irá usar
 {right_arrow} Aba de `Inventário` que irá usar
 {right_arrow} **`Perks de todas as suas Armas e Armaduras que pretende usar`**
 {right_arrow} `Stats`
 {right_arrow} `Barra de Habilidades` no modo de combate que utiliza
 {right_arrow} `Nome de usuário in-game`

Aguarde uma resposta de um {setting.RAIDS_TEACHER_ID}.

***Exemplo:*** https://i.imgur.com/CMNzquL.png"""

        denied_message = "Fool! Você já tem permissão para ir Raids!"

        if self.check_role(ctx, "Raids"):
            await ctx.send(denied_message)
        else:
            await ctx.send(aplicar_message)

    @staticmethod
    def check_role(ctx, *roles):
        for role in roles:
            if role in str(ctx.message.author.roles):
                return True
        return False


def setup(bot):
    bot.add_cog(ChatCommands(bot))
