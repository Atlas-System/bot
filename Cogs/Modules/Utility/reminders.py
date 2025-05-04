from discord.ext import commands
from re import fullmatch
from Utils.constants import emojis
from datetime import datetime, timedelta
from discord.ext import tasks
from Utils.pages import Simple
from discord import utils, Embed, Color

class Reminders(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.check_reminders.start()

    @commands.hybrid_group(name="reminder", description="Manage reminders")
    async def reminder(self, ctx: commands.Context):
        pass

    @reminder.command(name="create", description="Create a reminder")
    async def create_reminder(self, ctx: commands.Context, duration: str, *, message: str):

        match = fullmatch(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?', duration)
        if not match or not any(match.groups()):
            return await ctx.send(f"{emojis['no']} **{ctx.author.name},** please use `d, h, m, s`")

        days = int(match.group(1)) if match.group(1) else 0
        hours = int(match.group(2)) if match.group(2) else 0
        minutes = int(match.group(3)) if match.group(3) else 0
        seconds = int(match.group(4)) if match.group(4) else 0

        reminder_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        timestamp = utils.format_dt(reminder_time, style='f')
        mongo = self.client.mongo
        db = mongo["Data"]
        collection = db["reminders"]
        collection.insert_one({
            "user_id": ctx.author.id,
            "guild_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "message": message,
            "timestamp": reminder_time
        })

        await ctx.send(f"{emojis['yes']} **{ctx.author.name},** your reminder has been set at {timestamp} for **{message}**")
        return
    
    @reminder.command(name="active", description="Check active reminders")
    async def active_reminders(self, ctx: commands.Context):
        mongo = self.client.mongo
        db = mongo["Data"]
        collection = db["reminders"]
        reminders = collection.find({"guild_id": ctx.guild.id})

        reminders_list = await reminders.to_list(length=None)
        if not reminders_list:
            return await ctx.send(f"{emojis['no']} **{ctx.author.name},** there are no reminders active")
        if len(reminders_list) > 10:  
            pages = []
            for i in range(0, len(reminders_list), 10):
                embed = Embed(
                    title=f"Active Reminders {i + 1} - {i + 10}",
                    color=Color.dark_embed()
                )
                for reminder in reminders_list[i:i + 10]:
                    user = self.client.get_user(reminder["user_id"])
                    timestamp = utils.format_dt(reminder["timestamp"], style='f')
                    embed.add_field(
                        name=f"Reminder by {user.name if user else 'Unknown User'}",
                        value=f"**Message:** {reminder['message']}\n**Time:** {timestamp}",
                        inline=False
                    )
                pages.append(embed)

            paginator = Simple(pages)
            return await paginator.start(ctx)
        
        for i in reminders_list:
            user = self.client.get_user(i["user_id"])
            timestamp = utils.format_dt(i["timestamp"], style='f')
            embed = Embed(
                title=f"Active Reminders",
                color=Color.dark_embed()
            )
            embed.add_field(
                name=f"Reminder by {user.name if user else 'Unknown User'}",
                value=f"**Message:** {i['message']}\n**Time:** {timestamp}",
                inline=False
            )

            await ctx.send(embed=embed)
            return
        

    @tasks.loop(seconds=15)
    async def check_reminders(self):
        current_time = datetime.now()
        mongo = self.client.mongo
        db = mongo["Data"]
        collection = db["reminders"]

        reminders = collection.find({"timestamp": {"$lte": current_time}})
        li = await reminders.to_list(length=999)
        if not li:
            return
        
        for reminder in li:
            user = self.client.get_user(reminder["user_id"])
            if user:
                channel = self.client.get_channel(reminder["channel_id"])
                if channel:
                    await channel.send(f"{emojis['yes']} {user.mention}, **{reminder['message']}**")

            collection.delete_one({"_id": reminder["_id"]})

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_reminders.is_running():
            print(f"Starting reminder check loop")
            self.check_reminders.start()


    @commands.Cog.listener()
    async def on_cog_unload(self):
        if self.check_reminders.is_running():
            print(f"Stopping reminder check loop")
            self.check_reminders.stop()

    


        



async def setup(client: commands.Bot) -> None:
    await client.add_cog(Reminders(client))