from __future__ import unicode_literals
import asyncio
import re

import discord
import wikipedia
from discord.ext import commands
import config

from google_images_download import google_images_download

from background_worker import BackgroundWorkerModule
from reactions import WIKI_EMBED_TITLE


from googleapiclient.discovery import build
wikipedia.set_lang("ru")

number_emojies = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

response = google_images_download.googleimagesdownload()


@client.event
async def on_ready():
    print(client.guilds)
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message: discord.Message):
    print(message)
    global voice_channels
    if message.author == client.user:
        return

    await client.process_commands(message)

    print(message.content)
    if match := re.search('<@[!@&0-9]+>,? ты (.+)', message.content, re.IGNORECASE):
        await set_name(message, match.group(1))
    elif match := re.search('что за (.+)\??', message.content.lower(), re.IGNORECASE) \
            or re.search('что такое (.+)\??', message.content.lower(), re.IGNORECASE)\
            or re.search('кто такой (.+)\??', message.content.lower(), re.IGNORECASE)\
            or re.search('кто такая (.+)\??', message.content.lower(), re.IGNORECASE)\
            or re.search('кто такие (.+)\??', message.content.lower(), re.IGNORECASE)\
            or re.search('wtf is (.+)\??', message.content.lower(), re.IGNORECASE):
        query = match.group(1)
        await wiki_get_article(message, query)
    elif match := re.search('(.+)\?\?(\)\))?([0-9]+)?(\+)?', message.content, re.IGNORECASE):
        await get_google_images(message, match)


async def set_name(message, name):
    try:
        print(await message.mentions[0].edit(nick=name))
    except Exception as ex:
        await message.channel.send('Возникла ошибка при при установке имени.\nОшибка: `{}`'.format(ex))


async def wiki_get_article(message: discord.Message,query):
    try:
        pages = wikipedia.search(query, results=5)
        print(pages)
        response = ''
        counter = 1

        if len(pages)==0:
            raise Exception('Не найдено ни одной статьи')

        for page in pages:
            response += '{}. {}\n'.format(counter, page)
            counter += 1

        message = await message.channel.send(embed=discord.Embed(title=WIKI_EMBED_TITLE, description=response))
        for emoji in number_emojies:
            await message.add_reaction(emoji)
            '''results = list(search(query, num_results=10))
            for result in results:
                if 'wikipedia' in result:
    '''
    except Exception as ex:
        await message.channel.send('{} (`{}`)'.format(ex,query))


async def get_google_images(message, match):
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

            service = build(
                "customsearch", "v1", developerKey="AIzaSyC7g0oCCmwPgGqPHgjdRtie637kSC6pUDQ"
            )

            res = service.cse().list(
                q=query,
                cx="00f4cbbc858f5403a",
                searchType='image',
                num=images_count,
                imgType='clipart',
                safe='off'
            ).execute()

            if not 'items' in res:
                print('No result !!\nres is: {}'.format(res))
            else:
                for item in res['items']:
                    await message.channel.send(item['link'])

    except Exception as ex:
        await message.channel.send(
            'Возникла ошибка при загрузке картинок. \nЗапрос: `{}` \nОшибка: `{}`'.format(query, ex))
    except SystemExit as ex:
        await message.channel.send(
            'Возникла ошибка при загрузке картинок. \nЗапрос: `{}` \nОшибка: `{}`'.format(query, ex))



async def main():
    await client.load_extension('reactions')
    await client.load_extension('movies')
    await client.load_extension('sessions')
    await client.load_extension('voice')
    await client.start(config.bot_token)


loop = None

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    BackgroundWorkerModule(client).register(loop)
    loop.run_forever()
