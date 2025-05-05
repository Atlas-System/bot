from discord.ext import commands
import discord
from Utils.constants import emojis, ATLAS_GREEN
from Utils.utils import check_module_status, permission_check, get_guild_config
from Utils.embeds import MissingPermissions, ModuleDisabled, MissingConfigChannel, ChannelNotFound, ChannelSendFailure, PermissionError
from Utils.views import YesNoMenu


class Moderation(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()  
        self.client = client


    @commands.hybrid_command(name="warn", description="Warn a user")
    @discord.app_commands.describe(user="The user you want to warn", reason="The reason for the warning", silent="Whether to DM the user or not")
    async def warn(self, ctx: commands.Context, user: discord.Member, reason: str, silent: bool = False):
        if ctx.interaction:
            try:
                await ctx.interaction.response.defer(ephemeral=True)
            except:
                pass

        if not await permission_check(ctx, "staff"):
            data = MissingPermissions()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        status = await check_module_status(guild_id=ctx.guild.id,
                                           module="moderation_module",
                                           mongo=self.client.mongo)

        if status is False:
            data = ModuleDisabled()
            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        config = await get_guild_config(ctx.guild.id, self.client.mongo)
        module_config = config["Config"]["moderation_module"]
        confirmation = module_config.get("confirmation", False)

        log_channel_id = module_config.get("log_channel_id")
        if not log_channel_id:
            data = MissingConfigChannel()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        log_channel = ctx.guild.get_channel(log_channel_id)
        if not log_channel:
            data = ChannelNotFound()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        timestamp = discord.utils.utcnow()

        if confirmation is True:
            view = YesNoMenu(user_id=ctx.author.id)
            await ctx.send(content=f"{emojis['moderation']} **{ctx.author.name},** are you sure you want to warn {user.name} for ``{reason}``?",
                           view=view,
                           ephemeral=True,
                           allowed_mentions=discord.AllowedMentions.none())
            
            await view.wait()
            if view.value is False:
                return await ctx.send(content=f"{emojis['no']} **{ctx.author.name},** I have cancelled the warning.",
                                      ephemeral=True)



        case_id = await self.client.mongo["Data"]["Moderation"].count_documents({"guild_id": ctx.guild.id}) + 1


        

        embed = discord.Embed(title=f"Case #{case_id}",
                              color=discord.Color.dark_embed(),
                              timestamp=timestamp,
                              description=
                              f"> **User:** {user.mention} ``({user.id})``\n"
                              f"> **Moderator:** {ctx.author.mention} ``({ctx.author.id})``\n"
                              f"> **Action:** Warning\n"
                              f"> **Reason:** {reason}\n")
        embed.set_footer(text=f"Case ID: {case_id}", icon_url=ctx.author.display_avatar.url)
        try:
            await log_channel.send(embed=embed,
                                   allowed_mentions=discord.AllowedMentions.none())
        except discord.HTTPException:
            data = ChannelSendFailure()

            return await ctx.send(ephemeral=True,
                                  embed=data["embed"],
                                  view=data["view"],
                                  allowed_mentions=discord.AllowedMentions.none())

        try:
            await self.client.mongo["Data"]["Moderation"].insert_one({
                "guild_id": ctx.guild.id,
                "Case": {
                    "case_id": case_id,
                    "action": "warn",
                    "reason": reason,
                    "timestamp": timestamp
                },
                "User": {
                    "id": user.id,
                    "name": user.name
                },
                "Moderator": {
                    "id": ctx.author.id,
                    "name": ctx.author.name
                }})

        except Exception as e:
            print(f"Error inserting warn into database: {e} ({ctx.guild.id}")
            return await ctx.send(content=f"{emojis['no']} **{ctx.author.name},** I couldn't warn the user.",
                                  ephemeral=True)

        await ctx.send(content=f"{emojis['yes']} **{ctx.author.name},** I have warned {user.name} for ``{reason}``.",
                       ephemeral=True)

        if not silent:
            try:
                await user.send(f"{emojis['moderation']} You have been warned in **{ctx.guild.name}** for ``{reason}``.")
            except discord.HTTPException:
                pass

        return


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Moderation(client))