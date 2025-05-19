import sys
import dotenv 
sys.dont_write_bytecode = True
from os import getenv, path, remove
from gc import collect
from tracemalloc import start, take_snapshot
from discord import Intents, MemberCacheFlags, CustomActivity, Embed, Color, VoiceChannel, TextChannel, CategoryChannel, File
from discord.ext import commands
from collections import Counter
from objgraph import get_leaking_objects, typestats, show_backrefs, by_type
from cogwatch import watch
import pymongo
from Cogs.Modules.Utility.suggestion import SuggestionViews
from Cogs.Modules.Engagement.giveaways import GiveawaysView
from Utils.emojis import EmojiManager
from Utils.logger import get_logger
dotenv.load_dotenv()
TOKEN = getenv("PROD_TOKEN")

intents = Intents.default().all()

start()


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("!!"), intents=intents)
        self.mongo = pymongo.AsyncMongoClient(host=f"mongodb://{getenv('DATABASE_USER')}:{getenv('DATABASE_PASS')}@{getenv('DATABASE_HOST')}:{getenv('DATABASE_PORT')}/?authSource=admin&tls=false", maxPoolSize=10, minPoolSize=1)
        self.help_command = None
        self.Emoji_Manager = EmojiManager(self)
        self.Emojis = self.Emoji_Manager.emojis

        self.logger = get_logger("bot", "bot.log")
        self.logger.info("Logging Setup.")
    
    @watch(path="Cogs", preload=True)
    async def on_ready(self):
        try:
            await self.Emoji_Manager.setup_emojis()
        
        except Exception as e:
            self.logger.error(f"Error setting up emojis: {e}")
            self.Emoji_Manager = None
            return
        
        await self.unload_extension("Cogs.Modules.Moderation.moderation")
        if not self.mongo:
            self.logger.error("MongoDB Setup Failed, Retrying.")
            self.mongo = pymongo.AsyncMongoClient(getenv("MONGO"), maxPoolSize=10, minPoolSize=1)

        try:
            await self.mongo.admin.command("ping")
            self.logger.info(f"MongoDB connection successful on {getenv('DATABASE_HOST')}:{getenv('DATABASE_PORT')}.")
        except Exception as e:
            self.logger.error(f"MongoDB connection failed: {e}")
            return await super().close()

        self.add_view(SuggestionViews(mongo=self.mongo, client=self))
        self.add_view(GiveawaysView(mongo=self.mongo, client=self))



        await self.tree.sync()
        self.logger.info(f"Commands Synced Globally: {len(self.tree.get_commands())}")
        self.logger.info(f"Bot is ready, logged in as {self.user.name} ({self.user.id})")
        await self.change_presence(activity=CustomActivity("Atlas Testing"))


    async def close(self):
        if self.mongo:
            await self.mongo.close()
        await super().close()


bot = Bot()


@bot.command()
async def leakcheck(ctx):    
    collect()

    start()
    snapshot = take_snapshot()
    top_stats = snapshot.statistics("lineno")

    leaks = get_leaking_objects()

    _typestats = typestats(shortnames=False)

    def sanity(left, name, *, _stats=_typestats):
        try:
            right = _stats[name]
        except KeyError:
            return f"{name}: {left}. Not found"
        else:
            cmp = '!=' if left != right else '=='
            return f"{name}: {left} {cmp} {right}"

    channels = Counter(type(c) for c in bot.get_all_channels())

    sanity_results = [
        sanity(channels[TextChannel], 'discord.channel.TextChannel'),
        sanity(channels[VoiceChannel], 'discord.channel.VoiceChannel'),
        sanity(128, 'discord.channel.DMChannel'),
        sanity(channels[CategoryChannel], 'discord.channel.CategoryChannel'),
        sanity(len(bot.guilds), 'discord.guild.Guild'),
        sanity(5000, 'discord.message.Message'),
        sanity(len(bot.users), 'discord.user.User'),
        sanity(sum(1 for _ in bot.get_all_members()), 'discord.member.Member'),
        sanity(len(bot.emojis), 'discord.emoji.Emoji'),
    ]

    embed = Embed(title="Memory Usage & Leaks", color=Color.red())
    embed.add_field(name="Leaking Objects", value=f"{len(leaks)} objects detected", inline=False)

    top_memory = "\n".join(
        [f"**#{i+1}**: `{stat.traceback[0].filename}:{stat.traceback[0].lineno}` - `{stat.size / 1024:.1f} KiB`"
         for i, stat in enumerate(top_stats[:5])]
    )
    embed.add_field(name="Top Memory Allocations", value=top_memory or "No data", inline=False)

    embed.add_field(name="Cache Sanity", value="\n".join(sanity_results) or "No issues", inline=False)

    await ctx.send(embed=embed)


@bot.command(name="topram")
async def top_ram_files(ctx, top: int = 5):
    """Shows top files using the most RAM."""
    snapshot = take_snapshot()
    stats = snapshot.statistics('filename')

    embed = Embed(
        title=f"Top {top} RAM-Heavy Files",
        description="Tracked by tracemalloc (Python-level)",
        color=Color.green()
    )

    for stat in stats[:top]:
        path = stat.traceback[0].filename
        size_kb = stat.size / 1024
        embed.add_field(name=path, value=f"{size_kb:.2f} KB", inline=False)

    await ctx.send(embed=embed)

@bot.command(name="memgraph")
async def memory_graph(ctx, objtype: str = "discord.member.Member", count: int = 5):
    """
    Generates a memory reference graph of the most 'connected' objects of a given type.
    Example: !!memgraph discord.member.Member
    """
    await ctx.send("🔍 Collecting garbage and generating memory graph...")

    collect()

    try:
        objs = by_type(objtype)
    except Exception as e:
        await ctx.send(f"❌ Could not find objects of type `{objtype}`. Error: {e}")
        return

    if not objs:
        await ctx.send(f"✅ No live objects of type `{objtype}`.")
        return

    # Only keep the top N
    sample = objs[:count]

    # Create the graph
    filename = "memgraph.png"
    show_backrefs(
        sample,
        filename=filename,
        max_depth=3,
        too_many=20
    )

    if path.exists(filename):
        await ctx.send(file=File(filename))
        remove(filename)
    else:
        await ctx.send("❌ Failed to generate graph.")

if __name__ == "__main__":
    bot.run(TOKEN, reconnect=True)
