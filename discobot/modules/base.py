import re
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import network_layer
from googleapiclient.discovery import build

prompt = "I want you ALWAYS act as a homie who swears alot, swears every time in almost every word. Answer only in Russian. If you would not know the person or place I talk about just guess something funny and mumble something or hiccup sometimes. Your name is Хоуми, you are a gangster"
default_message = {
    "role": "system", "content": prompt
}
channels_chatgpt = dict()


class BaseModule(commands.Cog):

    def __init__(self, bot):
        print('BaseModule enabled')
        self.bot = bot
        self.synced = False

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            network_layer.update_guild({'id': guild.id, 'name': guild.name})

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        global voice_channels
        if message.author == self.bot.user:
            return

        await self.bot.process_commands(message)

        if message.content.startswith('!'):
            return

        if match := re.search('<@[!@&0-9]+>,? ты (.+)', message.content, re.IGNORECASE):
            await self.set_name(message, match.group(1))
        elif match := re.search('(.+)\?\?(\)\))?([0-9]+)?(\+)?', message.content, re.IGNORECASE):
            await self.get_google_images(message, match)

    def add_channel_to_chatgpt_settings(self, channel_id):
        channels_chatgpt[channel_id] = {'last_reply': datetime.now(), 'messages': [default_message]}

    async def set_name(self, message, name):
        try:
            print(await message.mentions[0].edit(nick=name))
        except Exception as ex:
            await message.channel.send('Возникла ошибка при при установке имени.\nОшибка: `{}`'.format(ex))

    async def get_google_images(self, message, match):
        try:
            async with message.channel.typing():
                print(match)
                query = match.group(1)
                is_rule34 = match.group(2)
                images_count = match.group(3)
                is_download = False if match.group(4) != None else True
                images_count = int(images_count) if images_count != None else 2
                images_count = images_count if images_count <= 7 else 7
                images_count = images_count if images_count >= 1 else 1

                if is_rule34 != None:
                    query += ' rule34'

                result = build("customsearch", "v1", developerKey="AIzaSyC7g0oCCmwPgGqPHgjdRtie637kSC6pUDQ").cse().list(
                    q=query, cx="00f4cbbc858f5403a", searchType='image', num=images_count, imgType='clipart', safe='off'
                ).execute()

                if not 'items' in result:
                    await message.channel.send(f'По вашему запросу картинки не найдены')
                    return

                for item in result['items']:
                    await message.channel.send(item['link'])

        except Exception as ex:
            await message.channel.send(f'Возникла ошибка при загрузке картинок. \nЗапрос: `{query}` \nОшибка: `{ex}`')

    @commands.command()
    async def sync(self, ctx: commands.Context):
        if ctx.author.id == 237325355696783364:
            await ctx.send('Trying to sync')
            await self.bot.tree.sync()
            await ctx.send('Command tree synced!')
        else:
            await ctx.send('You must be the owner to use this command!')

async def setup(bot):
    await bot.add_cog(BaseModule(bot))

