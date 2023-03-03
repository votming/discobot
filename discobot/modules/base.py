import re

import discord
from discord.ext import commands

import config
import wikipedia
import network_layer
from modules.reactions import WIKI_EMBED_TITLE
from googleapiclient.discovery import build
import openai

openai.api_key = config.CHATGPT_API_KEY
default_message = {
    "role": "system", "content": "I want you ALWAYS act as a homie who swears alot, swears every time in almost "
                                 "every word. Answer in Russian. If you would not know the person or place I talk "
                                 "about just guess something"
}
channels_chatgpt = dict()


class BaseModule(commands.Cog):

    def __init__(self, bot):
        print('MoviesModule enabled')
        wikipedia.set_lang("ru")
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            network_layer.update_guild({'id': guild.id, 'name': guild.name})

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        print(message)
        global voice_channels
        if message.author == self.bot.user:
            return

        await self.bot.process_commands(message)

        print(message.content)
        if match := re.search('<@[!@&0-9]+>,? ты (.+)', message.content, re.IGNORECASE):
            await self.set_name(message, match.group(1))
        # elif match := re.search('что за (.+)\??', message.content.lower(), re.IGNORECASE) \
        #               or re.search('что такое (.+)\??', message.content.lower(), re.IGNORECASE) \
        #               or re.search('кто такой (.+)\??', message.content.lower(), re.IGNORECASE) \
        #               or re.search('кто такая (.+)\??', message.content.lower(), re.IGNORECASE) \
        #               or re.search('кто такие (.+)\??', message.content.lower(), re.IGNORECASE) \
        #               or re.search('wtf is (.+)\??', message.content.lower(), re.IGNORECASE):
        #     query = match.group(1)
        #     await self.wiki_get_article(message, query)
        elif match := re.search('(.+)\?\?(\)\))?([0-9]+)?(\+)?', message.content, re.IGNORECASE):
            await self.get_google_images(message, match)
        elif self.bot.user in message.mentions:
            m = message.content.replace(self.bot.user.mention, '')
            print(f'MESSAGE: {m}')
            if message.channel.id not in channels_chatgpt:
                channels_chatgpt[message.channel.id] = [default_message]
            messages = channels_chatgpt[message.channel.id]
            content = message.content.replace(self.bot.user.mention, '')
            messages.append({"role": str(message.author.id), "content": content})
            chat = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=messages[message.channel.id])
            reply = chat.choices[0].message.content
            messages.append({"role": "homie", "content": reply})
            await message.channel.send(reply)

    async def set_name(self, message, name):
        try:
            print(await message.mentions[0].edit(nick=name))
        except Exception as ex:
            await message.channel.send('Возникла ошибка при при установке имени.\nОшибка: `{}`'.format(ex))

    async def wiki_get_article(self, message: discord.Message, query):
        try:
            pages = wikipedia.search(query, results=5)
            print(pages)
            response = ''
            counter = 1

            if len(pages) == 0:
                raise Exception('Не найдено ни одной статьи')

            for page in pages:
                response += '{}. {}\n'.format(counter, page)
                counter += 1

            message = await message.channel.send(embed=discord.Embed(title=WIKI_EMBED_TITLE, description=response))
            for emoji in config.NUMBERS_ONE_TO_FIVE:
                await message.add_reaction(emoji)

        except Exception as ex:
            await message.channel.send(f'{ex} (`{query}`)')

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


async def setup(bot):
    await bot.add_cog(BaseModule(bot))

