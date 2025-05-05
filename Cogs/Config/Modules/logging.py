from Utils.constants import emojis
import discord

class EventChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, mongo, event):
        self.mongo = mongo
        self.type = event

        super().__init__(placeholder="Select a channel", max_values=1, min_values=1, row=1)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        db = self.mongo["Atlas"]["Config"]
        find = await db.find_one({"_id": interaction.guild.id})
        if not find:
            await db.insert_one({"_id": interaction.guild.id})
            return await interaction.followup.send(ephemeral=True, content=f"{emojis['no']} **{interaction.user.name},** please re run the command.")
        
        insert = await db.update_one(
            {"_id": interaction.guild.id},
            {"$set": {f"Config.logging.{self.type}": self.values[0].id}},
            upsert=True
        )

        return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** I have saved the selected channel.")




class LoggingType(discord.ui.Select):
    def __init__(self, mongo):
        self.mongo = mongo
        options=[
            discord.SelectOption(label="Channels", description="Where channel events log", value="channel"),
            ]
        super().__init__(placeholder="Advanced Permissions",max_values=1,min_values=1,options=options, row=1)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        db = self.mongo["Atlas"]["Config"]
        find = await db.find_one({"_id": interaction.guild.id})
        if not find:
            await db.insert_one({"_id": interaction.guild.id})
            return await interaction.followup.send(ephemeral=True, content=f"{emojis['no']} **{interaction.user.name},** please re run the command.")

        select = EventChannelSelect(mongo=self.mongo, event=self.values[0])
        view = discord.ui.View(timeout=120).add_item(select)
        return await interaction.followup.send(ephemeral=True, content=f"{emojis['yes']} **{interaction.user.name},** please select a channel for the event.", view=view)
            

        

class NotificationsView(discord.ui.View):
    def __init__(self, mongo, channel):
        super().__init__(timeout=None)
        self.mongo = mongo


        self.add_item(item=LoggingType(mongo=self.mongo, notifications_channel=channel))

        from Cogs.Config.menu import ConfigPanel
        self.add_item(ConfigPanel(mongo=mongo))



