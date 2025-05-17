import discord


class StaffTeamRole(discord.ui.RoleSelect):
    def __init__(self, mongo, staff_roles):
        self.mongo = mongo
        super().__init__(placeholder="Select your staff roles", max_values=3, min_values=1, row=1, default_values=staff_roles if staff_roles else [])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        role_ids = [role.id for role in self.values]
        guild_id = interaction.guild.id
        db = self.mongo["Atlas"]["Config"]

        await db.update_one(
            {"_id": guild_id},
            {"$set": {"staff_roles": role_ids}},
            upsert=True
        )
        return await interaction.followup.send(ephemeral=True, content=f"**{interaction.user.name},** I have saved the staff roles")


class ManagementRole(discord.ui.RoleSelect):
    def __init__(self, mongo, management_roles):
        self.mongo = mongo

        super().__init__(placeholder="Select your management roles", max_values=3, min_values=1, row=2, default_values=management_roles if management_roles else [])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        role_ids = [role.id for role in self.values]
        guild_id = interaction.guild.id
        db = self.mongo["Atlas"]["Config"]

        await db.update_one(
            {"_id": guild_id},
            {"$set": {"management_roles": role_ids}},
            upsert=True
        )
        return await interaction.followup.send(ephemeral=True, content=f"**{interaction.user.name},** I have saved the management roles")

class PermissionsView(discord.ui.View):
    def __init__(self, mongo, staff_roles, mgmt_roles):
        super().__init__(timeout=None)
        self.mongo = mongo

        self.staff_role_view = StaffTeamRole(mongo=mongo, staff_roles=staff_roles)
        self.management_role_view = ManagementRole(mongo=mongo, management_roles=mgmt_roles)

        self.add_item(item=self.staff_role_view)
        self.add_item(item=self.management_role_view)

        from Cogs.Config.menu import ConfigPanel
        self.add_item(ConfigPanel(mongo=mongo))



