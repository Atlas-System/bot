from discord import SelectOption, Interaction, ButtonStyle, Embed, Color, ui
from discord.ext import commands 
from Utils.constants import emojis
from Cogs.Config.Modules import permissions, moderation, notifications, suggestions


class ModulesView(ui.Select):
    def __init__(self, modules, mongo):
        self.mongo = mongo

        options = [
            SelectOption(
                label="Notifications",  
                value="notifications",
                default=modules.get("notifications", {}).get("is_enabled", False)
            ),
            #SelectOption(
                #label="Moderation",  
                #value="moderation_module",
                #default=modules.get("moderation_module", {}).get("is_enabled", False)
            #),
            SelectOption(
                label="Reports",  
                value="report_module",
                default=modules.get("report_module", {}).get("is_enabled", False)
            ),

            SelectOption(
                label="Suggestions",
                value="suggestion_module",
                default=modules.get("suggestion_module", {}).get("is_enabled", False)
            )
        ]

        super().__init__(placeholder="Choose Enabled Modules", max_values=len(options), min_values=1, options=options)

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild.id
        config_collection = self.mongo["Atlas"]["Config"]
        
        guild_config = await config_collection.find_one({"_id": guild_id})
        
        if not guild_config or "Config" not in guild_config:
            return await interaction.followup.send(f"{emojis['no']} **{interaction.user.name},** no guild configuration was found.", ephemeral=True)
            
        
        updated_config = guild_config["Config"]
        
        for module_name, module_data in updated_config.items():
            module_data["is_enabled"] = module_name in self.values
        
        await config_collection.update_one({"_id": guild_id}, {"$set": {"Config": updated_config}})
        
        return await interaction.followup.send(f"{emojis['yes']} **{interaction.user.name},** I have updated the modules.", ephemeral=True)



        

class ConfigPanel(ui.Select):
    def __init__(self, mongo):
        self.mongo = mongo
        options=[
            SelectOption(label="Modules", description="Manage your servers enabled modules",value="modules" ,emoji=emojis.get("modules", None)),
            SelectOption(label="Logging", description="Manage your servers logging channels", value="logging", emoji=emojis.get("logging", None)),
            SelectOption(label="Notifications", description="Manage your servers notifications", value="notifications", emoji=emojis.get("notifications", None)),
            SelectOption(label="Permissions", description="Manage what roles can do what", value="perms", emoji=emojis.get("permissions", None)),
            #SelectOption(label="Moderation", description="Manage your servers moderation", value="moderation", emoji=emojis.get("moderation", None)),
            SelectOption(label="Suggestions", description="Manage your servers suggestions", value="suggestions", emoji=emojis.get("suggestions", None)),

            ]
        super().__init__(placeholder="Configuration Menu",max_values=1,min_values=1,options=options, row=4)
    async def callback(self, interaction: Interaction):
        db = self.mongo["Atlas"]["Config"]
        find = await db.find_one({"_id": interaction.guild.id})
        if not find:
            insert = await db.insert_one({"_id": interaction.guild.id, "Config": {}})
            find = await db.find_one({"_id": interaction.guild.id})

            
        await interaction.response.defer()


        if self.values[0] == "perms":
            db = self.mongo["Atlas"]["Config"]
                        
            modules = find["Config"] if find and "Config" in find else {}
            staff_roles_find = find.get("staff_roles", [])
            mgmt_roles_find = find.get("management_roles", [])

            all_roles = {role.id: role for role in interaction.guild.roles}
            all_role_ids = set(staff_roles_find + mgmt_roles_find)

            staff_roles = [all_roles.get(role_id) for role_id in staff_roles_find if
                           role_id in all_role_ids and role_id in all_roles]
            mgmt_roles = [all_roles.get(role_id) for role_id in mgmt_roles_find if
                          role_id in all_role_ids and role_id in all_roles]

            staff_roles = [role for role in staff_roles if role is not None]
            mgmt_roles = [role for role in mgmt_roles if role is not None]

            view = permissions.PermissionsView(
                mongo=self.mongo, 
                staff_roles=staff_roles,
                mgmt_roles=mgmt_roles 
            )

            embed = Embed(
                title="", 
                description="> In this view, you can select which roles have higher permissions than normal members.", 
                color=Color.dark_embed()
            )
            embed.set_thumbnail(url=(interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url))
            embed.set_author(
                icon_url=(interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url),
                name=interaction.guild.name
            )

            return await interaction.edit_original_response(embed=embed, view=view)
        
        if self.values[0] == "modules":
            db = self.mongo["Atlas"]["Config"]
            
            modules = find["Config"] if find and "Config" in find else {}

            view = ui.View(timeout=None)
            view.add_item(ModulesView(mongo=self.mongo, modules=modules))
            view.add_item(ConfigPanel(mongo=self.mongo))

            embed = Embed(
                title="", 
                description="> In this view, you can Enable and Disable different modules and their functionality.", 
                color=Color.dark_embed()
            )
            embed.set_thumbnail(url=(interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url))
            embed.set_author(
                icon_url=(interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url),
                name=interaction.guild.name
            )

            return await interaction.edit_original_response(view=view, embed=embed)
        


        if self.values[0] == "moderation":
            db = self.mongo["Atlas"]["Config"]
            
            modules = find["Config"] if find and "Config" in find else {}
            modlog_channel = modules.get("moderation_module", {}).get("log_channel_id")
            enabled = modules.get("moderation_module", {}).get("confirmation", False)
            channel = interaction.guild.get_channel(modlog_channel)

            view = moderation.ModerationView(
                mongo=self.mongo,
                modlog_channel=channel,
                enabled=enabled
            )


            embed = Embed(
                title="",
                description="> In this view, you can config the moderation settings.",
                color=Color.dark_embed()
            )
            embed.set_thumbnail(url=(
                interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url))
            embed.set_author(
                icon_url=(
                    interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url),
                name=interaction.guild.name
            )

            return await interaction.edit_original_response(view=view, embed=embed)
        

                
        if self.values[0] == "notifications":
            db = self.mongo["Atlas"]["Config"]

            modules = find["Config"] if find and "Config" in find else {}
            channel = modules.get("notifications", {}).get("log_channel_id")
            channel = interaction.guild.get_channel(channel)

            view = notifications.NotificationsView(
                mongo=self.mongo,
                channel=channel
            )

            embed = Embed(
                title="",
                description="> In this view, you can config the notification settings.",
                color=Color.dark_embed()
            )
            embed.set_thumbnail(url=(
                interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url))
            embed.set_author(
                icon_url=(
                    interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url),
                name=interaction.guild.name
            )

            return await interaction.edit_original_response(view=view, embed=embed)

        
        if self.values[0] == "suggestions":
            db = self.mongo["Atlas"]["Config"]


            modules = find["Config"] if find and "Config" in find else {}
            channel = modules.get("suggestion_module", {}).get("log_channel_id")
            enabled = modules.get("suggestion_module", {}).get("confirmation", False)
            channel = interaction.guild.get_channel(channel)

            view = suggestions.SuggestionView(
                mongo=self.mongo,
                channel=channel
            )

            
            embed = Embed(
                title="",
                description="> In this view, you can config the suggestion settings.",
                color=Color.dark_embed()
            )
            embed.set_thumbnail(url=(
                interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url))
            embed.set_author(
                icon_url=(
                    interaction.guild.icon.url if interaction.guild.icon else interaction.user.display_avatar.url),
                name=interaction.guild.name
            )

            return await interaction.edit_original_response(view=view, embed=embed)
        

