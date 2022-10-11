from __future__ import unicode_literals
import asyncio
import glob
import re
import discord
import wikipedia
from discord.ext import commands
import config
from gtts import gTTS
from pydub import AudioSegment
import os.path
from pytube import YouTube

from google_images_download import google_images_download
from simple_image_download import Downloader

wikipedia.set_lang("ru")

number_emojies = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

class Test():
    name = 'my name'

    def __test__(self):
        print('yo')

t = Test()



# client = discord.Client()
voice_channels = {}
discord.http.API_VERSION = 9
client = commands.Bot(command_prefix='!', intents=discord.Intents.all())
_lang = 'ru'
_speed = 1.3

response = google_images_download.googleimagesdownload()

search_queries = [
    'The smartphone also features an in display fingerprint sensor.',
    'The pop up selfie camera is placed aligning with the rear cameras.',
    '''In terms of storage Vivo V15 Pro could offer
       up to 6GB of RAM and 128GB of onboard storage.''',
    'The smartphone could be fuelled by a 3 700mAh battery.',
]


def play_message(guild_id):
    global voice_channels
    if guild_id not in voice_channels:
        print('guild not in the voice_channels')
        return

    if voice_channels[guild_id]['channel'].is_playing():
        print('bot is playing already... leave')
        return

    if len(voice_channels[guild_id]['messages']) == 0:
        print('no messages to say')
        return

    # filename = '/var/www/discobot/files/audio/{}.mp3'.format(guild_id)
    message = voice_channels[guild_id]['messages'].pop(0)
    say_message(message, guild_id)


def say_message(text, guild_id):
    global _lang, _speed
    text = re.sub('<@![1-9]*>', '', text)
    text = re.sub(':[1-9]*:', '', text)
    text = text.replace(',', '')
    print('text to say:', text)
    tts = gTTS(text=text, lang=_lang)
    filename = '/var/www/discobot/files/audio/{}.mp3'.format(guild_id)
    tts.save(filename)

    sound = AudioSegment.from_mp3(filename)
    _s = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * _speed)})
    sound = _s.set_frame_rate(sound.frame_rate)
    sound.export(filename, format="mp3")

    voice_channels[guild_id]['channel'].play(discord.FFmpegPCMAudio(filename), after=lambda e: play_message(guild_id))




@client.event
async def on_ready():
    print(client.guilds)
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_reaction_add(reaction: discord.Reaction, user):
    print('new reactions')
    request=''
    try:
        if len(reaction.message.embeds) > 0 and user != client.user:
            async with reaction.message.channel.typing():
                request = reaction.message.embeds[0].description.split('\n')[number_emojies.index(reaction.emoji)]
                print(request[3:])
                request = request[3:]
                await reaction.message.delete()
                page = wikipedia.page(request)
                summary = page.summary
                url = page.url
                embed = discord.Embed(title=request, description='{}\n{}'.format(summary[0:3500],url))
                for image in page.images:
                    print(image[-4:])
                    if (image[-4:] in ['.png', '.jpg', 'jpeg']):
                        embed.set_image(url=image)
                        break
                await reaction.message.channel.send(embed=embed)
    except Exception as ex:
        await reaction.message.channel.send('Ошибка при загрузке статьи (`{}`) {}'.format(request,ex))



@client.event
async def on_message(message: discord.Message):
    print(message)
    global voice_channels
    if message.author == client.user:
        return

    await client.process_commands(message)

    guild_id = str(message.guild.id)

    if not message.content.startswith('!') and guild_id in voice_channels:
        voice_channels[guild_id]['messages'].append(message.content)
        play_message(guild_id)

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

        message = await message.channel.send(embed=discord.Embed(title='Выберите тему', description=response))
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

            files = glob.glob('/var/www/discobot/files/images/{}/*'.format(query))
            for f in files:
                os.remove(f)

            response = google_images_download.googleimagesdownload()  # class instantiation

            arguments = {"keywords": query, "limit": images_count,
                         "output_directory": '/var/www/discobot/files/images/',
                         "print_urls": True, 'size': '>400*300', 'socket_timeout': 1,
                         'no_download': is_download}  # creating list of arguments
            paths = response.download(arguments)  # passing the arguments to the function

            if is_download:
                for url in paths[0][query]:
                    await message.channel.send(url)
            else:
                files = (os.listdir('/var/www/discobot/files/images/{}'.format(query)))
                for file in files:
                    picture = discord.File('/var/www/discobot/files/images/{}/{}'.format(query, file))
                    await message.channel.send(file=picture)
    except Exception as ex:
        await message.channel.send(
            'Возникла ошибка при загрузке картинок. \nЗапрос: `{}` \nОшибка: `{}`'.format(query, ex))
    except SystemExit as ex:
        await message.channel.send(
            'Возникла ошибка при загрузке картинок. \nЗапрос: `{}` \nОшибка: `{}`'.format(query, ex))



@client.command()
async def join(ctx: commands.Context):
    global voice_channels
    guild_id = str(ctx.guild.id)

    if not ctx.author.voice.channel:
        await ctx.send('Не могу присоединиться - вы не находитесь в войс-чате')
        return

    if guild_id in voice_channels and voice_channels[guild_id] == ctx.author.voice.channel:
        await ctx.send('Я уже на канале')
        return

    voice_channel = await ctx.author.voice.channel.connect()
    voice_channels[guild_id] = {'channel': voice_channel, 'messages': []}
    print(voice_channels)

    if guild_id in voice_channels:
        say_message("Здарова агалы", guild_id)
    '''
    vc.play(discord.FFmpegPCMAudio('/var/www/discobot/1.mp3'), after=lambda e: print('done', e))
    print('end playing')
    await vc.disconnect()
    '''


@client.command()
async def leave(ctx: commands.Context):
    global voice_channels
    guild_id = str(ctx.guild.id)

    if guild_id in voice_channels:
        say_message("Давайте братишки, до связи", guild_id)

        while voice_channels[guild_id]['channel'].is_playing():
            await asyncio.sleep(1)

        await ctx.message.delete()

        await voice_channels[guild_id]['channel'].disconnect()
        del voice_channels[guild_id]


@client.command()
async def play(ctx: commands.Context, url):
    global voice_channels
    guild_id = str(ctx.guild.id)

    await ctx.message.delete()

    if guild_id not in voice_channels:
        await ctx.send('Я не в войс-чате')
        return

    yt = YouTube(url)
    title = yt.title
    message = await ctx.send('Скачиваю видео от __**{}**__'.format(ctx.author.display_name))
    stream = yt.streams.filter(only_audio=True).first()

    path = stream.download(output_path='/var/www/discobot/files/videos')
    await message.delete()
    # msg = await ctx.send()
    #embed = await ctx.send(
    #    embed=discord.Embed(title=title, description='Сейчас в эфире: __**{}**__'.format(title), url=url))

    if guild_id in voice_channels:
        if 'мирон' in title.lower() or 'окси' in title.lower() or 'oxxxymiron' in title.lower():
            message = 'В эфире оксимирон со своим новым треком'
            say_message(message, guild_id)

    while voice_channels[guild_id]['channel'].is_playing():
        await asyncio.sleep(1)

    voice_channels[guild_id]['channel'].play(discord.FFmpegPCMAudio(path))


@client.command()
async def stop(ctx: commands.Context):
    global voice_channels
    guild_id = str(ctx.guild.id)

    await ctx.message.delete()

    if guild_id not in voice_channels:
        await ctx.send('Я не в войс-чате')
        return

    if voice_channels[guild_id]['channel'].is_playing():
        voice_channels[guild_id]['channel'].stop()

    if guild_id in voice_channels:
        say_message("Ок, перестал базарить", guild_id)


@client.command()
async def lang(ctx, language):
    global _lang
    guild_id = str(ctx.guild.id)
    _lang = language.lower()

    await ctx.message.delete()

    message = f'Язык установлен: {language.upper()} :flag_{language.lower()}:'
    await ctx.send(message)


@client.command()
async def speed(ctx: commands.Context, speed):
    global _speed
    guild_id = str(ctx.guild.id)
    await ctx.message.delete()

    try:
        speed = float(speed.replace(',', '.'))
        if speed > 2.0:
            speed = 2.0
        if speed < 0.5:
            speed = 0.5

        _speed = speed
        message = 'Скорость установлена, новое значение - {}'.format(speed)
    except:
        message = 'Что-то пошло не так. Сбрасываю скорость на 1.3. Пример использования команды - `!speed 1.8`'
        _speed = 1.3

    await ctx.send(message)


client.run(config.bot_token)
