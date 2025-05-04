from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from discord import Embed, Color


async def check_module_status(guild_id, module, mongo):
    """
    Args:
        guild_id: Integer = The ID of the guild that the module is under
        module: String = The name of the module in the Config dict that you are looking for
        mongo: AsyncioMotorClient = The mongo connection

    Returns:
        Boolean
    """

    try:
        db = mongo["Atlas"]["Config"]
        find = await db.find_one({"_id": guild_id})

        if not find:
            return False
        
        try:
            config = find["Config"][module]
            if not config:
                return False
        except KeyError:
            return False
        
        enabled = config["is_enabled"]
        return enabled
        


    except Exception:
        return False


async def permission_check(ctx: commands.Context, permission: str, module: str = None) -> bool:
    """
    Checks if the user has the required permission based on role IDs.

    Args:
        ctx: commands.Context - The context of the command.
        permission: str - The required permission level ("staff" or "manage").

    Returns:
        bool - True if the user has the required permission, False otherwise.
    """

    db = ctx.bot.mongo["Atlas"]["Config"]
    find = await db.find_one({"_id": ctx.guild.id})

    if not find:
        return False

    if permission == "staff":
        staff_roles = find.get("staff_roles", [])

        user_role_ids = {role.id for role in ctx.author.roles}

        return any(role_id in user_role_ids for role_id in staff_roles)

    if permission == "manage":
        staff_roles = find.get("management_roles", [])

        user_role_ids = {role.id for role in ctx.author.roles}

        return any(role_id in user_role_ids for role_id in staff_roles)

    return False

async def advanced_permission_check(ctx: commands.Context, command: str, fallback: int, module: str):
    """
    Args:
        ctx: commands.Context - The context of the command.
        command: str - The command name.
        fallback: int - The permission level to check for if advanced permissions are not present in the configuration.
        module: str - The module name.
        
    Returns:
        bool - True if the user has the required permission, False otherwise.
    """
    db = ctx.bot.mongo["Atlas"]["Config"]
    find = await db.find_one({"_id": ctx.guild.id})

    if not find:
        return False

    try:
        config = find["Config"].get(module, {})
        permissions = config.get("permissions", {})

        cmd = permissions.get(command, None)
        if not cmd:
            raise ValueError(f"Command '{command}' not found in perms")

        permission_level = cmd  

        if permission_level == 1:  
            staff_roles = find.get("staff_roles", [])
            user_role_ids = {role.id for role in ctx.author.roles}
            return any(role_id in user_role_ids for role_id in staff_roles)
        
        elif permission_level == 2:  
            management_roles = find.get("management_roles", [])
            user_role_ids = {role.id for role in ctx.author.roles}
            return any(role_id in user_role_ids for role_id in management_roles)

        return False

    except Exception as e:        
        notifications = find.get("notifications", {})
        if notifications.get("enabled", False):
            embed = Embed(
                title="Permissions Fallback",
                description=f"{ctx.author.mention} was using **{command}** which supports advanced permissions, but I could not find advanced permissions set up!\n\nFallback Permissions = {'Staff' if fallback == 1 else 'Management'}",
                color=Color.red()
            )
            embed.set_footer(text="Please contact a server administrator to set up advanced permissions.")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

            channel_id = notifications.get("channel_id", 0)
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)

        if fallback == 1:
            staff_roles = find.get("staff_roles", [])
            user_role_ids = {role.id for role in ctx.author.roles}
            return any(role_id in user_role_ids for role_id in staff_roles)
        elif fallback == 2:
            management_roles = find.get("management_roles", [])
            user_role_ids = {role.id for role in ctx.author.roles}
            return any(role_id in user_role_ids for role_id in management_roles)

        return False



async def get_guild_config(guild_id: int, mongo: AsyncIOMotorClient):
    """
    Args:
        guild_id: Integer = The ID of the guild that the module is under
        mongo: AsyncioMotorClient = The mongo connection

    Returns:
        Dict
    """

    db = mongo["Atlas"]["Config"]
    find = await db.find_one({"_id": guild_id})

    return find

async def fetch_user_flags(user: int, mongo: AsyncIOMotorClient):
    """
    Args:
        user: Integer = The ID of the user
        mongo: AsyncioMotorClient = The mongo connection

    Returns:
        List
    """

    db = mongo["Atlas"]["Users"]
    find = await db.find_one({"_id": user})

    return find.get("flags", [])
