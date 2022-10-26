import math
import re

import discord
from discord.ext import commands
from discord.ext.commands import cog
import wikipedia

from config import FILM_EMOJI, FILM_SEEN_EMOJI, FILM_PLAN_TO_WATCH_EMOJI, FILM_RATING_EMOJI, FILM_RATING_EMOJIS, \
    BACK_EMOJI, SESSION_EMOJI, JOIN_SESSION_EMOJI, RANDOM_MOVIE_SESSION_EMOJI, FINISH_SESSION_EMOJI, \
    DECLINE_MOVIE_SESSION_EMOJI, HISTORY_EMOJI, ARROW_RIGHT, ARROW_LEFT, SESSIONS_PER_PAGE
from models import ParsedMovie

from network_layer import subscribe_to_see, get_movie, set_watched, set_rating, create_new_session, \
    join_session, leave_session, set_unwatched, select_movie, decline_movie, select_random_movie, finish_session, \
    get_session, get_history
from utils import generate_embed_for_movie, generate_embed_for_session, generate_embed_for_finishing_movie, \
    generate_embed_for_history

number_emojies = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
WIKI_EMBED_TITLE = 'Выберите тему'


class ReactionsModule(commands.Cog):

    def __init__(self, bot):
        print('ReactionsModule enabled')
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        user = await self.bot.fetch_user(payload.user_id)
        if user == self.bot.user:
            return
        print('new reactions')
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        emoji = payload.emoji

        valid_reaction = message.author == self.bot.user and user != self.bot.user
        has_embeds = len(message.embeds) > 0
        #wiki_question = message.embeds[0].title == WIKI_EMBED_TITLE if has_embeds else False
        film_reaction = message.embeds[0].title.endswith(FILM_EMOJI) if has_embeds else False
        #film_rating = message.embeds[0].title.endswith(FILM_RATING_EMOJI) if has_embeds else False
        session_reaction = message.embeds[0].title.endswith(SESSION_EMOJI) if has_embeds else False

        try:
            if valid_reaction and session_reaction:
                session = create_new_session(message.guild)
                await self.handle_session_unreaction(session, user, message, emoji.name)
            elif valid_reaction and film_reaction:
                movie = get_movie(name=message.embeds[0].title.replace(f' {FILM_EMOJI}', ''), guild_id=message.guild.id)
                await self.handle_film_unreaction(movie, user, channel, emoji.name, message)
        except Exception as e:
            print(str(e))



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = await self.bot.fetch_user(payload.user_id)
        if user == self.bot.user:
            return
        print('new reactions')
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        emoji = payload.emoji

        valid_reaction = message.author == self.bot.user and user != self.bot.user
        has_embeds = len(message.embeds) > 0
        wiki_question = message.embeds[0].title == WIKI_EMBED_TITLE if has_embeds else False
        film_reaction = message.embeds[0].title.endswith(FILM_EMOJI) if has_embeds else False
        film_rating = message.embeds[0].title.endswith(FILM_RATING_EMOJI) if has_embeds else False
        session_reaction = message.embeds[0].title.endswith(SESSION_EMOJI) if has_embeds else False
        history_reaction = message.embeds[0].title.endswith(HISTORY_EMOJI) if has_embeds else False

        try:
            if valid_reaction and wiki_question:
                await self.handle_wiki_reaction(message, emoji)
            elif valid_reaction and film_reaction:
                movie = get_movie(name=message.embeds[0].title.replace(f' {FILM_EMOJI}', ''), guild_id=message.guild.id)
                await self.handle_film_reaction(movie, user, channel, emoji.name, message)
            elif valid_reaction and film_rating:
                movie = get_movie(name=message.embeds[0].title.replace(f' {FILM_RATING_EMOJI}', ''), guild_id=message.guild.id)
                await self.set_rating(movie, user, message, emoji)
            elif valid_reaction and session_reaction:
                session = create_new_session(message.guild)
                await self.handle_session_reaction(session, user, message, emoji.name)
            elif valid_reaction and history_reaction:
                await self.handle_history_reaction(user, message, emoji)
        except Exception as e:
            print(str(e))

    @classmethod
    async def handle_history_reaction(cls, user, message: discord.Message, emoji):
        history = get_history(message.guild.id)
        next_page = 0
        for fields in message.embeds[0].fields:
            if fields.name.startswith('История просмотров '):
                next_page = int(re.search('\d+', fields.name).group())

        if emoji.name == ARROW_RIGHT:
            next_page += 1
        elif emoji.name == ARROW_LEFT:
            next_page -= 1
        await message.remove_reaction(emoji, user)

        if next_page < 1:
            next_page = 1
        elif next_page > math.ceil(history.count/SESSIONS_PER_PAGE):
            next_page -= 1

        history = get_history(message.guild.id, offset=next_page-1)
        await generate_embed_for_history(history, message=message)


    @classmethod
    async def handle_session_reaction(cls, session, user, message, emoji):
        if emoji == JOIN_SESSION_EMOJI:
            join_session(session.id, user)
            session = create_new_session(message.guild)
            #await message.edit(embed=await generate_embed_for_session(session, message, True))
            await generate_embed_for_session(session, message)
        elif emoji == RANDOM_MOVIE_SESSION_EMOJI:
            select_random_movie(session.id)
            #await message.delete()
            session = create_new_session(message.guild)
            await generate_embed_for_session(session, message)
            pass
        elif emoji == FINISH_SESSION_EMOJI:
            finish_session(session.id)
            session = get_session(session.id)
            await message.delete()
            await generate_embed_for_finishing_movie(session=session, channel=message.channel, guild=message.guild)
            pass
        elif emoji == DECLINE_MOVIE_SESSION_EMOJI:
            decline_movie(session.id)
            session = create_new_session(message.guild)
            #await message.delete()
            await generate_embed_for_session(session, message)

    @classmethod
    async def handle_session_unreaction(cls, session, user, message, emoji):
        if emoji == JOIN_SESSION_EMOJI:
            leave_session(session.id, user)
            session = create_new_session(message.guild)
            #await message.edit(embed=await generate_embed_for_session(session, message, True))
            await generate_embed_for_session(session, message)

    @classmethod
    async def set_rating(cls, movie, user, message, emoji):
        if emoji.name == BACK_EMOJI:
            #await message.delete()
            await generate_embed_for_movie(movie, message)
        else:
            set_rating(movie.uuid, message.guild.id, user, FILM_RATING_EMOJIS.index(emoji.name)-1)
            movie = get_movie(uuid=movie.uuid, guild_id=message.guild.id)
            await message.remove_reaction(emoji, user)
            #await message.edit(embed=await generate_embed_for_finishing_movie(movie=movie, message=message, return_message=True))
            await generate_embed_for_finishing_movie(movie=movie, message=message)


    @classmethod
    async def handle_film_reaction(cls, movie: ParsedMovie, user: discord.User, channel, emoji, message=None):
        if emoji == FILM_SEEN_EMOJI:
            set_watched(movie.uuid, message.guild.id, user)
            movie = get_movie(uuid=movie.uuid, guild_id=message.guild.id)
            #await message.edit(embed=await generate_embed_for_movie(movie, message, True))
            await generate_embed_for_movie(movie, message)
        elif emoji == FILM_PLAN_TO_WATCH_EMOJI:
            subscribe_to_see(movie.uuid, message.guild.id, user)
            movie = get_movie(uuid=movie.uuid, guild_id=message.guild.id)
            #await message.edit(embed=await generate_embed_for_movie(movie, message, True))
            await generate_embed_for_movie(movie, message)
        elif emoji == FILM_RATING_EMOJI:
            #await message.delete()
            await generate_embed_for_finishing_movie(movie=movie, message=message)

    @classmethod
    async def handle_film_unreaction(cls, movie: ParsedMovie, user: discord.User, channel, emoji, message=None):
        if emoji == FILM_SEEN_EMOJI:
            set_unwatched(movie.uuid, message.guild.id, user)
            movie = get_movie(uuid=movie.uuid, guild_id=message.guild.id)
            #await message.edit(embed=await generate_embed_for_movie(movie, message, True))
            await generate_embed_for_movie(movie, message)
        elif emoji == FILM_PLAN_TO_WATCH_EMOJI:
            set_unwatched(movie.uuid, message.guild.id, user)
            movie = get_movie(uuid=movie.uuid, guild_id=message.guild.id)
            #await message.edit(embed=await generate_embed_for_movie(movie, message, True))
            await generate_embed_for_movie(movie, message)

    @classmethod
    async def handle_wiki_reaction(cls, message, emoji):
        try:
            request = message.embeds[0].description.split('\n')[number_emojies.index(emoji.name)]
            print(request[3:])
            request = request[3:]
            await message.delete()
            page = wikipedia.page(request)
            summary = page.summary
            url = page.url
            embed = discord.Embed(title=request, description='{}\n{}'.format(summary[0:3500], url))
            for image in page.images:
                print(image[-4:])
                if image[-4:] in ['.png', '.jpg', 'jpeg']:
                    embed.set_image(url=image)
                    break
            await message.channel.send(embed=embed)
        except Exception as ex:
            await message.channel.send('Ошибка при загрузке статьи (`{}`) {}'.format(request, ex))


async def setup(bot):
    await bot.add_cog(ReactionsModule(bot))

