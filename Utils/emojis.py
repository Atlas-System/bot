from importlib import invalidate_caches
from mimetypes import init
import discord
from discord.ext import commands
import os


class EmojiManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.init_emojis = [
            os.path.splitext(file)[0] for file in os.listdir("Assets/Emoji") if file.endswith(".png") 
        ]
        self.emojis = {}

    async def setup_emojis(self):
        emojis = await self.bot.fetch_application_emojis()
        for emoji in self.init_emojis:
            if emoji not in [e.name for e in emojis]:
                with open(f"Assets/Emoji/{emoji}.png", "rb") as image_file:
                    created_emoji = await self.bot.create_application_emoji(name=emoji, image=image_file.read())
                    self.emojis[emoji] = created_emoji.id
                    self.bot.logger.info(f"Emoji {created_emoji.name} created with ID {created_emoji.id}.")
            else:
                existing_emoji = next(e for e in emojis if e.name == emoji)
                self.emojis[emoji] = existing_emoji.id

        self.bot.logger.info("Application Emojis Setup.")
