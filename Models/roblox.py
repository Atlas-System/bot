from pydantic import BaseModel
import aiohttp
import os

class RobloxUser(BaseModel):
    id: int
    username: str
    display_name: str
    avatar_url: str
    description: str

async def fetch_roblox_user(user_id: int) -> RobloxUser:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as response:
            if response.status == 200:
                data = await response.json()
                return RobloxUser(**data)
            else:
                raise Exception(f"Failed to fetch user: {response.status}")

async def fetch_bloxlink_user(discord_user_id: int) -> RobloxUser:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"https://api.blox.link/v4/public/discord-to-roblox/:{discord_user_id}", headers={"Authorization": os.getenv("BLOXLINK_API_KEY")}) as response:
            if response.status == 200:
                data = await response.json()
                roblox_user = await fetch_roblox_user(data['robloxId'])
                return roblox_user
            else:
                raise Exception(response.text())
