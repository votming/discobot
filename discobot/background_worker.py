import asyncio

import discord

import network_layer
from config import FILM_EMOJI, FILM_CONTROL_EMOJIS, RED_CIRCLE, GREEN_CIRCLE
from imdb import MovieParser


class BackgroundWorkerModule:

    def __init__(self, bot):
        print('BackgroundWorkerModule enabled')
        self.bot = bot

    def register(self, event_loop):
        event_loop.create_task(self.heartbeating())

    async def heartbeating(self):
        sleep = 5
        while True:
            try:
                if self.bot.is_ready():
                    is_backend_alive = network_layer.handshake()
                    activity = GREEN_CIRCLE if is_backend_alive else RED_CIRCLE
                    sleep = 5 * 60 if is_backend_alive else 5
                    await self.bot.change_presence(activity=discord.Game(name=activity))
            except Exception as ex:
                print(str(ex))
            await asyncio.sleep(sleep)



