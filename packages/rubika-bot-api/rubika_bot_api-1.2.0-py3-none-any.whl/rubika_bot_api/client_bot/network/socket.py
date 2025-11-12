import sys
import subprocess
import asyncio
import aiohttp
from .helper import Helper
from json import dumps, loads
from ..types import Message
from ..exceptions import NotRegistered, TooRequests
from ..utils import Utils
from re import match


class Socket:
    """Async websocket client for Rubika messenger socket stream.

    Usage:
        socket = Socket(methods)
        await socket.connect()
        await socket.send(json_message)
        await socket.close()
    """

    def __init__(self, methods) -> None:
        self.methods = methods
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task | None = None
        self.handlers = []  # list of callables async def handler(message)
        self._running = False

    def add_handler(self, handler):
        """Register an async handler coroutine: async def handler(message: Message)"""
        self.handlers.append(handler)

    async def connect(self, url: str = None):
        if not url:
            url = await Helper.get_socket_server()

        session = await self.methods.get_network()._get_session() if hasattr(self.methods, 'get_network') else aiohttp.ClientSession()
        # ensure we have an aiohttp session
        if isinstance(session, aiohttp.ClientSession):
            self._session = session
        else:
            self._session = await self.methods.get_network()

        # open websocket
        self._ws = await self._session.ws_connect(url)
        self._running = True
        self._task = asyncio.create_task(self._listen())

    async def _listen(self):
        assert self._ws is not None
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = loads(msg.data)
                except Exception:
                    continue

                # wrap as Message where appropriate
                try:
                    message = Message(data=data, methods=self.methods)
                except Exception:
                    message = data

                # dispatch to handlers concurrently
                for h in list(self.handlers):
                    if asyncio.iscoroutinefunction(h):
                        asyncio.create_task(h(message))
                    else:
                        # run sync handler in executor
                        asyncio.get_event_loop().run_in_executor(None, h, message)

            elif msg.type == aiohttp.WSMsgType.ERROR:
                break

    async def send(self, data):
        if not self._ws:
            raise RuntimeError("Socket is not connected")
        if isinstance(data, (dict, list)):
            await self._ws.send_str(dumps(data))
        else:
            await self._ws.send_str(str(data))

    async def close(self):
        self._running = False
        if self._ws and not self._ws.closed:
            await self._ws.close()
        if self._task:
            await self._task
