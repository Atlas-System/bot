from discord.ext import commands
from discord.ext.commands import HybridCommandError
from discord import Embed, Color
from Utils.embeds import (
    MissingPermissions,
    ModuleDisabled,
    ModuleNotFound,
    ChannelNotFound
)

class OnCommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, ctx, error):
        print(error)

        if isinstance(error, commands.CheckFailure):
            data = MissingPermissions()
            return await ctx.send(embed=data["embed"],view=data["view"] ,ephemeral=True)
        
        db = self.bot.mongo["Atlas"]["Errors"]
        error_id = await db.count_documents({}) + 1
        await db.insert_one({"_id": error_id, "error": str(error)})
        embed = Embed(
            title="Unexpected Error",
            description=f"An unexpected error occurred. Please report this to our [support server](https://discord.gg/GnFUSVHtkK)",
            timestamp=ctx.message.created_at,
            color=Color.red()
        )

        embed.set_footer(text=f"Error ID: {error_id}")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        return await ctx.send(embed=embed, ephemeral=True)



        



async def setup(bot):
    await bot.add_cog(OnCommandError(bot))