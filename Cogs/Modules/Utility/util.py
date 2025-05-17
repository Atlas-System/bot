from discord.ext import commands


class Util(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()

        self.client = client

    @commands.hybrid_command(name="ping", description="Check the bot's latency")
    async def ping(self, ctx: commands.Context):
        return await ctx.send(f"{self.client.Emojis['yes']} Pong! {round(self.client.latency * 1000)}ms",
                              ephemeral=True)

    @commands.hybrid_command(name="help", description="Get help with a command")
    async def help(self, ctx: commands.Context):
        return await ctx.send(f"{self.client.Emojis['yes']} You can get help in the support server: [here](https://discord.gg/mmVYkZRG8h)",
                              ephemeral=True)




async def setup(client: commands.Bot) -> None:
    await client.add_cog(Util(client))