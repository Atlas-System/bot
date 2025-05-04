from discord.ext import commands
from jishaku.cog import OPTIONAL_FEATURES, STANDARD_FEATURES

class CustomDebugCog(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    pass
async def setup(bot: commands.Bot):
    await bot.add_cog(CustomDebugCog(bot=bot))