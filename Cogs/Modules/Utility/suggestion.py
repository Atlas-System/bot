from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from Utils.constants import emojis
from discord import ui, ButtonStyle, Interaction, Button, Embed, Color, utils


class SuggestionViews(ui.View):
    def __init__(self, mongo):
        super().__init__(timeout=None)
        self.mongo = mongo
        self.db = self.mongo["Data"]
        self.collection = self.db["Suggestions"]

    async def has_voted(self, user_id, suggestion_id):
        suggestion = await self.collection.find_one({"message_id": suggestion_id})
        if suggestion:
            upvoters = suggestion.get("Upvoters", [])
            downvoters = suggestion.get("Downvoters", [])
            if user_id in upvoters:
                return "upvote"
            elif user_id in downvoters:
                return "downvote"
        return None

    async def remove_vote(self, user_id, suggestion_id, vote_type):
        await self.collection.update_one(
            {"message_id": suggestion_id},
            {"$pull": {f"{vote_type}rs": user_id}}
        )

    async def add_vote(self, user_id, suggestion_id, vote_type):
        await self.collection.update_one(
            {"message_id": suggestion_id},
            {"$addToSet": {f"{vote_type}rs": user_id}}
        )

    @ui.button(label="Upvote", style=ButtonStyle.green, custom_id=f"persistent_view:upvote")
    async def upvote(self, interaction: Interaction, button: Button):
        user_id = interaction.user.id
        suggestion_id = interaction.message.id

        vote_status = await self.has_voted(user_id, suggestion_id)
        if vote_status == "upvote":
            await self.remove_vote(user_id, suggestion_id, "Upvote")
            await interaction.response.defer(ephemeral=True)
        elif vote_status == "downvote":
            await self.remove_vote(user_id, suggestion_id, "Downvote")
            await self.add_vote(user_id, suggestion_id, "Upvote")
            await interaction.response.defer(ephemeral=True)
        else:
            await self.add_vote(user_id, suggestion_id, "Upvote")
            await interaction.response.defer(ephemeral=True)

        await self.update_embed(suggestion_id, interaction)

    @ui.button(label="Downvote", style=ButtonStyle.red, custom_id=f"persistent_view:downvote")
    async def downvote(self, interaction: Interaction, button: Button):
        user_id = interaction.user.id
        suggestion_id = interaction.message.id

        vote_status = await self.has_voted(user_id, suggestion_id)
        if vote_status == "downvote":
            await self.remove_vote(user_id, suggestion_id, "Downvote")
            await interaction.response.defer(ephemeral=True)
        elif vote_status == "upvote":
            await self.remove_vote(user_id, suggestion_id, "Upvote")
            await self.add_vote(user_id, suggestion_id, "Downvote")
            await interaction.response.defer(ephemeral=True)
        else:
            await self.add_vote(user_id, suggestion_id, "Downvote")
            await interaction.response.defer(ephemeral=True)

        await self.update_embed(suggestion_id, interaction)

    async def update_embed(self, suggestion_id, interaction):
        suggestion = await self.collection.find_one({"message_id": suggestion_id})
        if suggestion:
            upvotes = len(suggestion.get("Upvoters", []))
            actual_suggestion = suggestion.get("suggestion")
            downvotes = len(suggestion.get("Downvoters", []))
            channel_id = suggestion["chnl_id"]
            channel = interaction.guild.get_channel(channel_id)
            message = await channel.fetch_message(interaction.message.id)
            embed = message.embeds[0]
            embed.set_footer(text=f"{upvotes} Upvotes | {downvotes} Downvotes")
            embed = Embed(title="New Suggestion", color=Color.dark_embed())
            embed.add_field(name=f"Suggestion", value=f"{actual_suggestion}", inline=False)
            embed.add_field(name=f"Vote Count", value=f"{upvotes} Upvoters | {downvotes} Downvoters", inline=False)
            user = await interaction.client.fetch_user(suggestion["user_id"])
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_author(icon_url=user.display_avatar.url, name=user.name)
            await message.edit(embeds=[embed])
            return await interaction.followup.send(f"{emojis['yes']} **{interaction.user.name},** your vote has been recorded.", ephemeral=True)
        
        return await interaction.followup.send(f"{emojis['no']} **{interaction.user.name},** I could not find the suggestion.", ephemeral=True)
            

    @ui.button(label="List Voters", style=ButtonStyle.grey, custom_id="persistent_view:list_voters")
    async def list_voters(self, interaction: Interaction, button: Button):
        suggestion_id = interaction.message.id
        suggestion = await self.collection.find_one({"message_id": suggestion_id})
        if suggestion:
            upvoters = [f"<@{user_id}> (Upvote)" for user_id in suggestion.get("Upvoters", [])]
            downvoters = [f"<@{user_id}> (Downvote)" for user_id in suggestion.get("Downvoters", [])]
            voters = upvoters + downvoters
            if voters:
                embed = Embed(title="Voters", description="\n".join(voters), color=Color.dark_embed())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("No votes recorded yet.", ephemeral=True)


class Suggestions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_group(name="suggestion", description="Suggestion based commands")
    async def suggestion(self, ctx):
        pass

    @suggestion.command(name=f"create", description=f"Make a suggestion.")
    async def suggest(self, ctx, *, suggestion):
        db = self.bot.mongo["Atlas"]["Config"]
        time = utils.utcnow()
        
        find = await db.find_one({"_id": ctx.guild.id})
        try:
            config = find["Config"]["suggestion_module"]
        except KeyError:
            return await ctx.send(content=f"{emojis['no']} **{ctx.author.name},** please setup your suggestions.", ephemeral=True)
        if not find: return await ctx.send(content=f"{emojis['no']} **{ctx.author.name},** please setup your server.", ephemeral=True)

        try:
            blacklisted_role_id = config["blacklisted_role_id"]
        except KeyError:
            pass

        channel_id = config["log_channel_id"]
        channel = await self.bot.fetch_channel(channel_id)
        await ctx.send(f"Thank you **{ctx.author.name}** for making a suggestion!", ephemeral=True)


        embed = Embed(title="New Suggestion", color=Color.dark_embed())
        embed.add_field(name=f"Suggestion", value=f"{suggestion}", inline=False)
        embed.add_field(name=f"Vote Count", value=f"0 Upvoters | 0 Downvoters", inline=False)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_author(icon_url=ctx.author.display_avatar.url, name=ctx.author.name)
        suggestion_message = await channel.send(embeds=[embed])
        db = self.bot.mongo["Data"]["Suggestions"]
        await db.insert_one({"user_id": ctx.author.id, "message_id": suggestion_message.id, "suggestion": suggestion, "chnl_id": suggestion_message.channel.id, "time": time, "Upvoters": [], "Downvoters": []})
        await suggestion_message.edit(view=SuggestionViews(mongo=self.bot.mongo))
        await suggestion_message.create_thread(name=f"Suggested by {ctx.author.name}")
        return
        




async def setup(bot):
    await bot.add_cog(Suggestions(bot))