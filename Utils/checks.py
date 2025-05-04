from discord.ext import commands

async def staff_check(mongo, guild, member):
    find = await mongo["Atlas"]["Config"].find_one({"_id": guild.id})
    if find:
        staff_roles = find.get("staff_roles", [])

        user_role_ids = {role.id for role in member.roles}

        return any(role_id in user_role_ids for role_id in staff_roles)
    return False



async def staff_predicate(ctx):
    if ctx.guild is None:
        return True
    else:
        return await staff_check(ctx.bot, ctx.guild, ctx.author)


def is_staff():
    return commands.check(staff_predicate)


async def has_premium_slots(mongo, user_id):
    db = mongo["Atlas"]["Subscriptions"]
    find = await db.find_one({"_id": user_id})
    if find:
        return True
    
