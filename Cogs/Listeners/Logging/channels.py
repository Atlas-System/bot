import discord
from discord.ext import commands

class LoggingChannels(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded.")

    async def log_event(self, event_type: str, channel: discord.abc.GuildChannel):
        try:
            db = self.bot.mongo["Atlas"]["Config"]
            find = await db.find_one({"_id": channel.guild.id})
            if not find: 
                return
            
            channel_id = find.get("Config", {}).get("logging", {}).get(event_type)
            if not channel_id:
                return
            
            channel_config = self.bot.get_channel(channel_id)
            if not channel_config:
                return
            

            if event_type == "create":
                embed = discord.Embed(
                    title="Channel Created",
                    description=f"Channel {channel.mention} ``({channel.id})`` has been created.",
                    color=discord.Color.green()
                )

                embed.set_author(
                    name=channel.guild.name,
                    icon_url=channel.guild.icon.url if channel.guild.icon else "https://media.discordapp.net/attachments/1352018215835795610/1362092388633415911/discord-logo-icon-editorial-free-vector.jpg?ex=681986a3&is=68183523&hm=76664b1fa4467bacf7a24e6bb2f00537c947908a054b6e1d8c2df6327cf8b3b2&=&format=webp&width=936&height=936" 
                )

                return await channel_config.send(embed=embed)

        
        except Exception as e:
            print(f"Error logging {event_type} event: {e}")
            return




    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if channel.guild.system_channel:
            await channel.guild.system_channel.send(f"Channel created: {channel.mention}")
    

async def setup(bot: commands.Bot):
    await bot.add_cog(LoggingChannels(bot))