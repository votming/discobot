import asyncio

import discord

import network_layer
from config import RED_CIRCLE, GREEN_CIRCLE


class BackgroundWorkerModule:

    def __init__(self, bot):
        print('BackgroundWorkerModule enabled')
        self.bot = bot

    def register(self, event_loop):
        event_loop.create_task(self.heartbeating())

    async def heartbeating(self):
        while True:
            is_backend_alive = network_layer.handshake()
            sleep = await self._update_bot_status(is_backend_alive)
            await asyncio.sleep(sleep)

    async def _update_bot_status(self, is_backend_alive) -> int:
        try:
            sleep = 5
            if self.bot.is_ready():
                is_backend_alive = network_layer.handshake()
                activity = GREEN_CIRCLE if is_backend_alive else RED_CIRCLE
                sleep = 30 * 60 if is_backend_alive else 60
                await self.bot.change_presence(activity=discord.Game(name=activity))
            return sleep
        except Exception as ex:
            print(str(ex))
            return 30
