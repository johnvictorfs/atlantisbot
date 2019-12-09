from discord.ext import commands
from typing import Dict, List, Union
import discord

from bot.bot_client import Bot
from bot.utils.context import Context

Categories = Dict[str, Dict[str, Union[discord.Role, List[discord.Role]]]]


class RolesManager(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.debugging = False

    @commands.Cog.listener(name='on_member_update')
    async def update_member_categories(self, before: discord.Member, after: discord.Member):
        if not (self.bot.setting.mode == 'prod' or self.debugging):
            return

        if before.bot:
            return

        if before.roles != after.roles:
            categories = self.get_role_categories()
            await self.update_category(after, categories)

    def get_role_categories(self) -> Categories:
        """
        Returns all the Role categories in the following format:

        >>> categories = {
        ...     '    • Category Name •    ': {
        ...         'role': discord.Role(),  # The Role of that category
        ...         'roles': List[discord.Role]  # The Roles from that category
        ...     }
        ... }
        """
        atlantis: discord.Guild = self.bot.get_guild(self.bot.setting.server_id)

        categories: Categories = {}

        all_roles: List[discord.Role] = list(reversed(atlantis.roles))

        # Make dict of categories
        for role in all_roles:
            if '•' in role.name:
                categories[role.name] = {
                    'role': role,
                    'roles': []
                }

        # Add the roles from a Category into its entry on the Categories dict
        for name, category in categories.items():
            found = False

            for role in all_roles:
                if role.name == name:
                    found = True

                if found and '•' in role.name and role.name != name:
                    break  # Got to the next Category role

                if found and role.name != '@everyone' and role.name != name:
                    category['roles'].append(role)

        return categories

    async def update_category(self, member: discord.Member, categories: Categories):
        """
        Updates Role Categories for a single discord Member
        """
        for name, category in categories.items():
            if any(role in category['roles'] for role in member.roles):
                await member.add_roles(category['role'])
            else:
                await member.remove_roles(category['role'])

    @commands.command()
    @commands.is_owner()
    async def update_all_categories(self, ctx: Context):
        """
        Updates the Categories Roles for everyone in the Atlantis Server

        Adds a Category role for everyone who has at least one role in that category
        and doesn't already have it

        Removes Category role for everyone who doesn't have any roles in that category
        but still has the Category role

        Category Roles follow the following format:

        'ﾠﾠﾠﾠ• Category Name •ﾠﾠﾠﾠ'

        Where every whitespace there is a non-breaking space

        They also have the color: #2f3136 to match Discord's background (on dark mode)
        """
        await ctx.send('Atualizando Cargos de Categorias de todos os Membros...')
        categories = self.get_role_categories()

        member: discord.Member
        for member in ctx.guild.members:
            await self.update_category(member, categories)

        await ctx.send('Cargos de Categorias atualizados com sucesso!')


def setup(bot):
    bot.add_cog(RolesManager(bot))
