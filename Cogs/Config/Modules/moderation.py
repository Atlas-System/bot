from Utils.constants import emojis
from discord import ui, Interaction, SelectOption


class AdvancedPermissionsToggle(ui.Select):
    def __init__(self, mongo, item):
        self.mongo = mongo
        self.item = item
        # quick reminder for me, 1: staff 2: admin
        options=[
            SelectOption(label="Staff Role ", description="Let staff use this command.",value="staff"),
            SelectOption(label="Admin Role", description="Let admins use this command.", value="admin")

            ]
        super().__init__(placeholder="Select Permission Group",max_values=1,min_values=1,options=options, row=2)
    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        if self.values[0] == "staff":
            db = self.mongo["Atlas"]["Config"]
            guild_id = interaction.guild.id
            await db.update_one({"_id": guild_id}, {"$set": {f"Config.moderation_module.permissions.{self.item}": 1}}, upsert=True)
            return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** The staff role can now use that command.")
        
        elif self.values[0] == "admin":
            db = self.mongo["Atlas"]["Config"]
            guild_id = interaction.guild.id
            await db.update_one({"_id": guild_id}, {"$set": {f"Config.moderation_module.permissions.{self.item}": 2}}, upsert=True)
            return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** The admin role can now use that command.")
        

class AdvancedPermissions(ui.Select):
    def __init__(self, mongo):
        self.mongo = mongo
        options=[
            SelectOption(label="Enable", description="Enable advanced permissions.", value="enable"),
            SelectOption(label="Disable", description="Disable advanced permissions.", value="disable"),
            SelectOption(label="Warning ", description="Setup permissions for warning.",value="warning")
            ]
        super().__init__(placeholder="Advanced Permissions",max_values=1,min_values=1,options=options, row=3)
    async def callback(self, interaction: Interaction):

        await interaction.response.defer()
        if self.values[0] == "warning":
            db = self.mongo["Atlas"]["Config"]
            find = await db.find_one({"_id": interaction.guild.id})
            if find is None:
                await db.insert_one({"_id": interaction.guild.id, "Config": {"moderation_module": {"permissions": {}}}})
                return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** I have created the advanced permissions for the warning command.")
            
            if find:
                if find.get("Config", {}).get("moderation_module", {}).get("permissions", {}).get("is_enabled", False) is False:
                    return await interaction.followup.send(ephemeral=True, content=f"{emojis['no']} **{interaction.user.name},** Advanced permissions are disabled.")

            view = ui.View(timeout=None)
            view.add_item(item=AdvancedPermissionsToggle(mongo=self.mongo, item=self.values[0]))
            return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** you can now select the permission group for the warning command.", view=view)


class ModlogChannel(ui.ChannelSelect):
    def __init__(self, mongo, modlog_channel):
        self.mongo = mongo
        super().__init__(placeholder="Select a mod log channel", max_values=1, min_values=1, row=1, default_values=[modlog_channel] if modlog_channel else [])

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        guild_id = interaction.guild.id
        db = self.mongo["Atlas"]["Config"]
        print("hi!!")

        insert = await db.update_one(
            {"_id": guild_id},
            {"$set": {"Config.moderation_module.log_channel_id": self.values[0].id}},
            upsert=True
        )
        return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** I have saved the moderation channel.")
    
class RequireConfirmation(ui.Select):
    def __init__(self, mongo, enabled):
        self.mongo = mongo
        options=[
            SelectOption(label="Enabled ", description="Enable moderation command confirmation.",value="enable",default=True if enabled is True else False),
            SelectOption(label="Disabled", description="Disable moderation command confirmation.", value="disable", default=True if enabled is False else False)

            ]
        super().__init__(placeholder="Command Confirmation",max_values=1,min_values=1,options=options, row=2)
    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        if self.values[0] == "enable":
            db = self.mongo["Atlas"]["Config"]
            guild_id = interaction.guild.id
            await db.update_one({"_id": guild_id}, {"$set": {"Config.moderation_module.confirmation": True}}, upsert=True)
            return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** I have enabled the confirmation for moderation commands.")
        
        elif self.values[0] == "disable":
            db = self.mongo["Atlas"]["Config"]
            guild_id = interaction.guild.id
            await db.update_one({"_id": guild_id}, {"$set": {"Config.moderation_module.confirmation": False}}, upsert=True)
            return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** I have disabled the confirmation for moderation commands.")
        
class ModerationView(ui.View):
    def __init__(self, mongo,  modlog_channel, enabled):
        super().__init__(timeout=None)
        self.mongo = mongo


        self.add_item(item=ModlogChannel(mongo=self.mongo, modlog_channel=modlog_channel))
        self.add_item(item=RequireConfirmation(mongo=self.mongo, enabled=enabled))
        self.add_item(item=AdvancedPermissions(mongo=self.mongo))

        from Cogs.Config.menu import ConfigPanel
        self.add_item(ConfigPanel(mongo=mongo))



