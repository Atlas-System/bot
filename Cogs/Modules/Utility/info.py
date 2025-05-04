from discord.ext import commands
from Utils.constants import emojis
from discord import Embed, utils, Color, Member




class Info(commands.Cog):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client

    @commands.hybrid_command(name="server", description="Get information about the server")
    async def server(self, ctx: commands.Context): 
        owner = ctx.guild.owner
        members_length = len([member async for member in ctx.guild.fetch_members(limit=None)])


        text = ctx.guild.text_channels
        voice = ctx.guild.voice_channels

        embed = Embed(
            title=f"{ctx.guild.name}",
            description=f"**Owner:** {owner.mention}\n**Guild:** {ctx.guild.name} ``{ctx.guild.id}``\n **Members:** ``{ctx.guild.member_count}``\n **Created:** {utils.format_dt(ctx.guild.created_at, 'F')}\n **Channels:** {len(ctx.guild.channels)}\n**Roles:** {len(ctx.guild.roles)}",
            color=0x2B2D31,
        )
        embed.add_field(
            name="Channels",
            value=f"**Categories:** {len(ctx.guild.categories)}\n**Text:** {len(text)}\n**Forums:** {len(ctx.guild.forums)}\n**Voice:** {len(voice)}",
            inline=True,
        )
        embed.add_field(
            name="Data",
            value=f"**Members:** {members_length}\n**Boosts:** {ctx.guild.premium_subscription_count} (Level {ctx.guild.premium_tier})\n**Total Roles:** {len(ctx.guild.roles)}",
            inline=True,
        )

        if str(ctx.guild.explicit_content_filter).capitalize() == "All_members": f = "Everyone"
        else: f = {str(ctx.guild.explicit_content_filter).capitalize()}

        embed.add_field(
            name="Security",
            value=f"**Verification Level:** {str(ctx.guild.verification_level).capitalize()}\n**Filter:** `{f}`",
        )
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.set_author(name=f"{owner}'s Server", icon_url=owner.display_avatar)

        return await ctx.send(embed=embed)
    

    
    @commands.hybrid_command(name="user", description="Get information about a user")
    async def user(self, ctx: commands.Context, user: Member): 

        embed = Embed(
            title=f"@{user.name}",
            description=f"**User:** {user.mention} ``{user.id}``\n**Joined:** {utils.format_dt(user.joined_at, 'F')}\n **Created:** {utils.format_dt(user.created_at, 'F')}",
            color=0x2B2D31,
        )
        
        embed.add_field(
            name="Data",
            value=f"**Roles:** {len(user.roles)}\n**Boosting Since:** {user.premium_since if user.premium_since else 'Not Boosting'}\n**Status:** {user.status}\n**Activity:** {user.activity if user.activity else 'None'}",
            inline=True,
        )

        embed.set_thumbnail(url=user.display_avatar)
        embed.set_author(name=f"{user}", icon_url=user.display_avatar)

        return await ctx.send(embed=embed)







async def setup(client: commands.Bot) -> None:
    await client.add_cog(Info(client))