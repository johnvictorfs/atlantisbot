class WelcomeMessage:

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def on_member_join(member):
        await member.send("Test message.")
        print(f'> {member.nick} joined {member.guild} at {member.joined_at}')


def setup(bot):
    bot.add_cog(WelcomeMessage(bot))
