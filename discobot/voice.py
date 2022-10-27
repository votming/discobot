import asyncio
import re

import discord
from discord.ext import commands
from gtts import gTTS
from pydub import AudioSegment
from pytube import YouTube

import network_layer
from config import FILM_EMOJI, FILM_CONTROL_EMOJIS
from imdb import MovieParser
from models import ParsedMovie
from utils import generate_embed_for_movie

voice_channels = {}
_lang = 'ru'
_speed = 1.3

class VoiceModule(commands.Cog):

    def __init__(self, bot):
        print('VoiceModule enabled')
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            network_layer.update_guild({'id': guild.id, 'name': guild.name})

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        print('new on_message')
        try:
            if message.author == self.bot.user:
                return

            if message.content.startswith('#кинолента'):
                # Request movie from IMDB
                movie = MovieParser.get_movie(name=message.content.replace('#кинолента ', ''))
                movie.guild = message.guild.id
                # Get additional info about the movie from our backend
                backend_info = network_layer.get_movie(uuid=movie.uuid, guild_id=message.guild.id)

                if backend_info is None:
                    network_layer.register_movie(movie)
                movie = ParsedMovie(**{**movie.toJSON(), **network_layer.get_movie(uuid=movie.uuid, guild_id=message.guild.id).toJSON()})
                await generate_embed_for_movie(movie, channel=message.channel)
        except Exception as e:
            print(str(e))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        guild_id = str(message.guild.id)
        global voice_channels
        if message.author == self.bot.user:
            return

        if not message.content.startswith('!') and guild_id in voice_channels:
            voice_channels[guild_id]['messages'].append(message.content)
            play_message(guild_id)

    @commands.command()
    async def join(self, ctx: commands.Context):
        try:
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
        except Exception as ex:
            print(str(ex))
        '''
        vc.play(discord.FFmpegPCMAudio('/var/www/discobot/1.mp3'), after=lambda e: print('done', e))
        print('end playing')
        await vc.disconnect()
        '''

    @commands.command()
    async def leave(self, ctx: commands.Context):
        global voice_channels
        guild_id = str(ctx.guild.id)

        if guild_id in voice_channels:
            say_message("Давайте братишки, до связи", guild_id)

            while voice_channels[guild_id]['channel'].is_playing():
                await asyncio.sleep(1)

            await ctx.message.delete()

            await voice_channels[guild_id]['channel'].disconnect()
            del voice_channels[guild_id]

    @commands.command()
    async def play(self, ctx: commands.Context, url):
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

        path = stream.download(output_path='files/videos')
        await message.delete()
        # msg = await ctx.send()
        # embed = await ctx.send(
        #    embed=discord.Embed(title=title, description='Сейчас в эфире: __**{}**__'.format(title), url=url))

        if guild_id in voice_channels:
            if 'мирон' in title.lower() or 'окси' in title.lower() or 'oxxxymiron' in title.lower():
                message = 'В эфире оксимирон со своим новым треком'
                say_message(message, guild_id)

        while voice_channels[guild_id]['channel'].is_playing():
            await asyncio.sleep(1)

        voice_channels[guild_id]['channel'].play(discord.FFmpegPCMAudio(path))

    @commands.command()
    async def stop(self, ctx: commands.Context):
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

    @commands.command()
    async def lang(self, ctx, language):
        global _lang
        guild_id = str(ctx.guild.id)
        _lang = language.lower()

        await ctx.message.delete()

        message = f'Язык установлен: {language.upper()} :flag_{language.lower()}:'
        await ctx.send(message)

    @commands.command()
    async def speed(self, ctx: commands.Context, speed):
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
    filename = 'files/audio/{}.mp3'.format(guild_id)
    tts.save(filename)

    sound = AudioSegment.from_mp3(filename)
    _s = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * _speed)})
    sound = _s.set_frame_rate(sound.frame_rate)
    sound.export(filename, format="mp3")

    voice_channels[guild_id]['channel'].play(discord.FFmpegPCMAudio(filename),
                                             after=lambda e: play_message(guild_id))


async def setup(bot):
    await bot.add_cog(VoiceModule(bot))


# service = build(
#                 "customsearch", "v1", developerKey="AIzaSyC7g0oCCmwPgGqPHgjdRtie637kSC6pUDQ"
#             )
#
#             res = service.cse().list(
#                 q='butterfly',
#                 cx="009557628044748784875:5lejfe73wrw",
#                 searchType='image',
#                 num=10,
#                 imgType='clipart',
#                 safe='off'
#             ).execute()
#
#             if not 'items' in res:
#                 print('No result !!\nres is: {}'.format(res))
#             else:
#                 for item in res['items']:
#                     async with aiohttp.ClientSession() as session:  # creates session
#                         async with session.get(item['link'], ssl=False) as resp:  # gets image from url
#                             img = await resp.read()  # reads image from response
#                             with io.BytesIO(img) as file:  # converts to file-like object
#                                 await message.channel.send(file=discord.File(file, f"{hash(item['link'])}.png"))