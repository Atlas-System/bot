
from discord import Interaction, ui

class SuggestionsChannel(ui.ChannelSelect):
    def __init__(self, mongo, suggestions_channel):
        self.mongo = mongo
        super().__init__(placeholder="Select a suggestions channel", max_values=1, min_values=1, row=1, default_values=[suggestions_channel] if suggestions_channel else [])

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        guild_id = interaction.guild.id
        db = self.mongo["Atlas"]["Config"]

        insert = await db.update_one(
            {"_id": guild_id},
            {"$set": {"Config.suggestion_module.log_channel_id": self.values[0].id}},
            upsert=True
        )
        return await interaction.followup.send(ephemeral=True, content=f"**{interaction.user.name},** I have saved the suggestions channel.")
    

class SuggestionView(ui.View):
    def __init__(self, mongo, channel):
        super().__init__(timeout=None)
        self.mongo = mongo


        self.add_item(item=SuggestionsChannel(mongo=self.mongo, suggestions_channel=channel))

        from Cogs.Config.menu import ConfigPanel
        self.add_item(ConfigPanel(mongo=mongo))



