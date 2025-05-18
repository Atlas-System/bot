from pydantic import BaseModel
import aiohttp

class RobloxUser(BaseModel):
    id: int
    username: str
    display_name: str
    avatar_url: str
    description: str

async def fetch_roblox_user(user_id: int) -> RobloxUser:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/isers/{user_id}") as response:
            if response.status == 200:
                data = await response.json()
                return RobloxUser(**data)
            else:
                raise Exception(f"Failed to fetch user: {response.status}")