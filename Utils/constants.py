from hashlib import sha256

ATLAS_GREEN = 12255017

emojis = {
    "yes": "<:yes:1355487364616818770>",
    "no": "<:no:1355487363119186053>",
    "settings": "<:settings:1355487765650870435>",
    "modules": "<:layout:1355486552343707830>",
    "help": "<:help:1355487564349308978>",
    "moderation": "<:moderation:1355487124165623919>",
    "permissions": "<:permissions:1355487125637697585>",
    "reports": "<:reports:1355487276213338112>",
    "notifications": "<:mail:1355486652730052618>",
    "suggestions": "<:suggestions:1362156110265454724>",
    "confetti": "<:confetti:1362332141924515951>"}

hash_obj = sha256()
