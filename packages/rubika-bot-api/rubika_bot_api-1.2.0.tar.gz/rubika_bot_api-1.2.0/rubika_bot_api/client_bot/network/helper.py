import aiohttp
import asyncio
from json import loads
from random import randint, choice


class Helper:
    """Async helpers for network endpoints."""

    @classmethod
    async def get_dcmess(cls) -> dict:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://getdcmess.iranlms.ir/") as resp:
                text = await resp.text()
                return loads(text)["data"]

    @classmethod
    async def get_api_server(cls) -> str:
        # randomized selection, kept async for consistency
        return f"https://messengerg2c{randint(2, 3)}.iranlms.ir"

    @classmethod
    async def get_socket_server(cls) -> str:
        dcmess = await cls.get_dcmess()
        return choice(list(dcmess["socket"].values()))