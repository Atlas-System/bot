from fastapi import FastAPI, APIRouter, HTTPException, Request, status
from discord.ext import commands
from os import getenv
from motor.motor_asyncio import AsyncIOMotorClient
from asyncio import create_task
from uvicorn import Config, Server
from discord.ext import commands

from discord import Client
MONGO_URL = getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)



async def apiKeyValid(apiKey: str) -> bool:
    stored_api_key = getenv("apiKey")

    if apiKey != stored_api_key:
        return False
    


    return True

class APIRoutes:
    # base class from https://github.com/bugsbirb/birb/blob/6970fa6a1d8243218f4177679fd26913edee6f54/utils/api.py#L77
    def __init__(self, client: Client):
        self.client = client
        self.router = APIRouter()
        self.ratelimits = {}
        for i in dir(self):
            if any(
                [i.startswith(a) for a in ("GET_", "POST_", "PATCH_", "DELETE_")]
            ) and not i.startswith("_"):
                x = i.split("_")[0]
                self.router.add_api_route(
                    f"/{i.removeprefix(x+'_')}",
                    getattr(self, i),
                    methods=[i.split("_")[0].upper()],
                )

    async def POST_mutual_servers(self, request: Request, apiKey: str):
        if not await apiKeyValid(apiKey):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Key"
            )
        
        try:
            body = await request.json()
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON"
            )

        guilds = body.get("guilds")
        userid = body.get("user")
        user = await self.client.fetch_user(userid["id"])
        print(user.name)

        if not guilds or not user or not userid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing guilds or user"
            )

        bot_guild_ids = {str(guild.id) for guild in self.client.guilds}

        mutuals = [g for g in guilds if str(g["id"]) in bot_guild_ids]

        permissions_correct = []
        print(mutuals)

        print("nearly there")

        for guilds in mutuals:
            print("first")
            find = await self.client.fetch_guild(int(guilds["id"]))
            if find is None:
                print("None?")
                return
            
            member = await find.fetch_member(user.id)
            
            if member:
                print("first")
                print(f"Guild Owner: {find.owner}")
                print(f"Authenticated User: {user}")

                if member.guild_permissions.administrator or find.owner_id == user.id:
                    permissions_correct.append({
                        "id": find.id,
                        "name": find.name,
                        "logo": find.icon.url if find.icon else "https://media.discordapp.net/attachments/1352018215835795610/1362092388633415911/discord-logo-icon-editorial-free-vector.jpg?ex=680122e3&is=67ffd163&hm=23eb679982451441f5b620160ac65eb656218e8c82adce819431162a41dbbc5a&=&format=webp&width=960&height=960",
                        "banner": find.banner.url if find.banner else "https://media.discordapp.net/attachments/1352018215835795610/1352018333318381599/Artboard_14.png?ex=6800bdf1&is=67ff6c71&hm=2eec0280bf8b287364e8fd91013b131abea4da52d5560e6e2e5c7abd1776b405&=&format=webp&quality=lossless&width=1521&height=856"
                    })

        print(permissions_correct)
        return {"guilds": permissions_correct}


        

    


class APICog(commands.Cog):
    def __init__(self, client: Client):
        self.client = client
        self.app = FastAPI()
        self.app.include_router(APIRoutes(client).router)
        self.server_task = None

    def cog_unload(self):
        if self.server_task and not self.server_task.done():
            self.server_task.cancel()

    async def cog_load(self):
        self.server_task = create_task(self.start_server())

    async def start_server(self):
        config = Config(
            app=self.app,
            host="0.0.0.0" if getenv("env") == "prod" else "127.0.0.1",
            port=8000,
            log_level="info",
        )
        server = Server(config)
        await server.serve()
        

        


async def setup(client: commands.Bot) -> None:
    await client.add_cog(APICog(client))