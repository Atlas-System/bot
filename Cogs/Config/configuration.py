from discord.ext import commands, tasks
from Cogs.Config.menu import ConfigPanel
from collections import Counter
from discord import Color, ui, Embed



class Configuration(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()  
        self.client = client

    @commands.hybrid_command(name="config", description="Configure the settings for this guild")
    async def config(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send(ephemeral=True, content=f"{self.client.Emojis['no']} **{ctx.author.name},** you need **administrator** to use this.")
        embed = Embed(title="", color=Color.dark_embed(), description=f"**{self.client.Emojis['settings']} Setting Up**\n> To setup Atlas, please choose an option from below.\n\n**{self.client.Emojis['help']} Support**\n> If you have an issue with setting up or the bot in general, join our [support server](https://discord.gg/x2meHZN38N)")
        embed.set_thumbnail(url=(ctx.guild.icon.url if ctx.guild.icon else ctx.author.display_avatar.url))
        embed.set_author(icon_url=(ctx.guild.icon.url if ctx.guild.icon else ctx.author.display_avatar.url), name=ctx.guild.name)
        view = ui.View(timeout=None)
        find = await self.client.mongo["Atlas"]["Config"].find_one({"_id": ctx.guild.id})
        view.add_item(ConfigPanel(client=self.client, mongo=self.client.mongo))
        await ctx.send(
            embed=embed,
            view=view,
            ephemeral=True)
        
    
        return 



async def setup(client: commands.Bot) -> None:
    await client.add_cog(Configuration(client))