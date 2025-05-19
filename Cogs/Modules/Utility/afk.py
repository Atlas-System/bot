import discord
from discord.ext import commands, tasks
import datetime

class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.client = bot

    @tasks.loop(seconds=30)
    async def AFK_Notices(self):
        current_time = datetime.datetime.now()
        afks = await self.client.mongo["Data"]["AFK"].find({"ends": {"$lt": current_time}}).to_list(length=None)
        for afk in afks:
            try:
                channel = self.client.get_channel(afk["channel_id"])
                message_id = channel.get_partial_message()
        
async def setup(bot):