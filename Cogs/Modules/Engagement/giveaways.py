import discord
from discord.ext import commands, tasks

import re
from datetime import datetime, timedelta
from typing import Optional, Union
import random


class GiveawaysView(discord.ui.View):
    def __init__(self,client ,mongo):
        super().__init__(timeout=None)
        self.mongo = mongo
        self.client = client
        self.db = self.mongo["Data"]
        self.collection = self.db["Giveaways"]

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, custom_id=f"persistent_view:enter")
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        find = await self.collection.find_one({"message_id": interaction.message.id})
        joined = find.get("Joined", [])

        if interaction.user.id in joined:
            joined.remove(interaction.user.id)
            await interaction.followup.send(ephemeral=True, content=f"{self.client.Emojis['no']} **{interaction.user.name},** you have left the giveaway.")
        else:
            joined.append(interaction.user.id)
            await interaction.followup.send(ephemeral=True, content=f"{self.client.Emojis['yes']} **{interaction.user.name},** you have joined the giveaway.")

        prize = find.get("prize")
        winners = find.get("winners")
        duration = find.get("duration")
        time = find.get("ends")
        user = await interaction.guild.fetch_member(find.get("hosted_by"))
        timestamp = discord.utils.format_dt(time, "R")
        embed = discord.Embed(title="Giveaway!", description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** {timestamp}\n**Joined:** {len(joined)}", color=discord.Color.dark_embed())
        
        try:
            embed.set_footer(text=f"Hosted by: {user.name}", icon_url=user.display_avatar.url)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_author(icon_url=user.display_avatar.url, name=user.name)
        except Exception as e:
            print(f"Error fetching user: {e}")

        await interaction.message.edit(embed=embed, view=self)
        return await self.collection.update_one({"message_id": interaction.message.id}, {"$set": {"Joined": joined}})
    
    @discord.ui.button(label="Voters", style=discord.ButtonStyle.blurple, custom_id=f"persistent_view:voters")
    async def voters(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        find = await self.collection.find_one({"message_id": interaction.message.id})
        joined = find.get("Joined", [])

        if not joined:
            return await interaction.followup.send(ephemeral=True, content=f"{self.client.Emojis['no']} **{interaction.user.name},** no one has joined yet.")

        user_mentions = [f"<@{user_id}>" for user_id in joined]
        user_mentions_str = "\n".join(user_mentions)

        embed = discord.Embed(title="Giveaway Participants", description=user_mentions_str, color=discord.Color.dark_embed())
        embed.set_footer(text=f"Total Participants: {len(joined)}")
        await interaction.followup.send(embed=embed, ephemeral=True)
        return


class Giveaways(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.check_giveaways.start()

    @commands.hybrid_group(name="giveaway", description="Manage giveaways")
    async def giveaways(self, ctx: commands.Context):
        pass

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        current_time = datetime.now()
        giveaways = await self.client.mongo["Data"]["Giveaways"].find({"ends": {"$lt": current_time}}).to_list(length=None)
        for giveaway in giveaways:
            channel = self.client.get_channel(giveaway["channel_id"])
            if channel:
                try:
                    message = await channel.fetch_message(giveaway["message_id"])
                    view = GiveawaysView(client=self.client, mongo=self.client.mongo)
                    view.enter.disabled = True
                    view.stop()
                    await message.edit(view=view)
                
                    winners = giveaway["winners"]
                    joined = giveaway.get("Joined", [])
                    if len(joined) < winners:
                        winners = len(joined)

                    winner_ids = random.sample(joined, winners) if joined else []
                    winner_mentions = [f"<@{winner_id}>" for winner_id in winner_ids]
                    await self.client.mongo["Data"]["Giveaways"].delete_one({"message_id": giveaway["message_id"]})

                    return await message.reply(f"**Giveaway Winner(s):** {', '.join(winner_mentions)}")
                except discord.NotFound:
                    await self.client.mongo["Data"]["Giveaways"].delete_one({"message_id": giveaway["message_id"]})

                    pass

            await self.client.mongo["Data"]["Giveaways"].update_one({"message_id": giveaway["message_id"]}, {"$set": {"ended": True}})

    @giveaways.command(name="create", description="Create a giveaway")
    async def create_giveaway(self, ctx: commands.Context, duration: str, winners: int, prize: str):
        if ctx.interaction:
            try:
                await ctx.interaction.response.defer(ephemeral=True)
            except:
                pass

        match = re.fullmatch(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?', duration)
        if not match or not any(match.groups()):
            return await ctx.send(f"{self.client.Emojis['no']} **{ctx.author.name},** please use `d, h, m, s`")

        days = int(match.group(1)) if match.group(1) else 0
        hours = int(match.group(2)) if match.group(2) else 0
        minutes = int(match.group(3)) if match.group(3) else 0
        seconds = int(match.group(4)) if match.group(4) else 0

        reminder_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        if winners < 1:
            return await ctx.send(f"{self.client.Emojis['no']} **{ctx.author.name},** please specify at least one winner")

        embed = discord.Embed(title="Giveaway!", description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Ends:** {discord.utils.format_dt(reminder_time, 'R')}\n**Joined:** 0", color=discord.Color.dark_embed())
        embed.set_footer(text=f"Hosted by: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.name)
        giveaway_message = await ctx.channel.send(embed=embed)
        await self.client.mongo["Data"]["Giveaways"].insert_one({
            "guild_id": ctx.guild.id,
            "message_id": giveaway_message.id,
            "channel_id": ctx.channel.id,
            "ends": reminder_time,
            "winners": winners,
            "prize": prize,
            "hosted_by": ctx.author.id,
            "created_at": ctx.message.created_at.timestamp(),
            "Joined": [],
            "ended": False
        })
        await giveaway_message.edit(view=GiveawaysView(mongo=self.client.mongo))

        return
    
    @giveaways.command(name="reroll", description="Reroll a giveaway")
    async def reroll(self, ctx: commands.Context, message_id: str):
        if ctx.interaction:
            try:
                await ctx.interaction.response.defer(ephemeral=True)
            except:
                pass

        giveaway = await self.client.mongo["Data"]["Giveaways"].find_one({"message_id": message_id})
        if not giveaway:
            return await ctx.send(f"{self.client.Emojis['no']} **{ctx.author.name},** I could not find that giveaway.")

        channel = self.client.get_channel(giveaway["channel_id"])
        if not channel:
            return await ctx.send(f"{self.client.Emojis['no']} **{ctx.author.name},** I could not find that channel.")

        message = await channel.fetch_message(giveaway["message_id"])
        winners = giveaway["winners"]
        if giveaway.get("ended", False) is False:
            return await ctx.send(f"{self.client.Emojis['no']} **{ctx.author.name},** that giveaway is still active.")
        joined = giveaway.get("Joined", [])
        if len(joined) < winners:
            winners = len(joined)

        winner_ids = random.sample(joined, winners) if joined else []
        winner_mentions = [f"<@{winner_id}>" for winner_id in winner_ids]

        return await message.reply(f"**Giveaway Winner(s):** {', '.join(winner_mentions)}")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Giveaways cog is ready!")
        self.check_giveaways.start()

    @commands.Cog.listener()
    async def on_cog_unload(self):
        self.check_giveaways.stop()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Giveaways(client))
