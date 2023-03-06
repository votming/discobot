from __future__ import unicode_literals
import asyncio

import config
import discord
from discord.ext import commands
from discord import app_commands

from modules.background_worker import BackgroundWorkerModule

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())


async def main():
    await client.load_extension('modules.reactions')
    await client.load_extension('modules.movies')
    await client.load_extension('modules.sessions')
    await client.load_extension('modules.voice')
    await client.load_extension('modules.base')
    await client.load_extension('modules.chatgpt')
    await client.start(config.bot_token)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    BackgroundWorkerModule(client).register(loop)
    loop.run_forever()
