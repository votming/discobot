import math
import re

import discord
from discord.ext import commands

from config import FILM_EMOJI, FILM_SEEN_EMOJI, FILM_PLAN_TO_WATCH_EMOJI, FILM_RATING_EMOJI, FILM_RATING_EMOJIS, \
    BACK_EMOJI, SESSION_EMOJI, JOIN_SESSION_EMOJI, RANDOM_MOVIE_SESSION_EMOJI, FINISH_SESSION_EMOJI, \
    DECLINE_MOVIE_SESSION_EMOJI, HISTORY_EMOJI, ARROW_RIGHT, ARROW_LEFT, SESSIONS_PER_PAGE, FILM_DONT_WANT_TO_WATCH
from models import ParsedMovie

from network_layer import subscribe_to_see, get_movie, set_watched, set_rating, get_guild_session, \
    join_session, leave_session, set_unwatched, select_movie, decline_movie, select_random_movie, finish_session, \
    get_session, get_history, set_dont_want_to_watch
from utils.renderer import generate_embed_for_movie, generate_embed_for_session, generate_embed_for_finishing_movie, \
    generate_embed_for_history


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
        film_reaction = message.embeds[0].title.endswith(FILM_EMOJI) if has_embeds else False
        session_reaction = message.embeds[0].title.endswith(SESSION_EMOJI) if has_embeds else False

        try:
            if valid_reaction and session_reaction:
                session = get_guild_session(message.guild.id)
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
        film_reaction = message.embeds[0].title.endswith(FILM_EMOJI) if has_embeds else False
        film_rating = message.embeds[0].title.endswith(FILM_RATING_EMOJI) if has_embeds else False
        session_reaction = message.embeds[0].title.endswith(SESSION_EMOJI) if has_embeds else False
        history_reaction = message.embeds[0].title.endswith(HISTORY_EMOJI) if has_embeds else False

        try:
            if valid_reaction and film_reaction:
                movie = get_movie(name=message.embeds[0].title.replace(f' {FILM_EMOJI}', ''), guild_id=message.guild.id)
                await self.handle_film_reaction(movie, user, channel, emoji.name, message)
            elif valid_reaction and film_rating:
                movie = get_movie(name=message.embeds[0].title.replace(f' {FILM_RATING_EMOJI}', ''), guild_id=message.guild.id)
                await self.set_rating(movie, user, message, emoji)
            elif valid_reaction and session_reaction:
                session = get_guild_session(message.guild.id)
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

        await generate_embed_for_history(message.guild.id, page=next_page-1, message=message)


    @classmethod
    async def handle_session_reaction(cls, session, user, message, emoji):
        if emoji == JOIN_SESSION_EMOJI:
            join_session(session.id, user)
            #await message.edit(embed=await generate_embed_for_session(session, message, True))
            await generate_embed_for_session(message.guild.id, message)
        elif emoji == RANDOM_MOVIE_SESSION_EMOJI:
            select_random_movie(session.id)
            #await message.delete()
            await generate_embed_for_session(message.guild.id, message)
            pass
        elif emoji == FINISH_SESSION_EMOJI:
            finish_session(session.id)
            await message.delete()
            await generate_embed_for_finishing_movie(session_id=session.id, channel=message.channel, guild=message.guild)
            pass
        elif emoji == DECLINE_MOVIE_SESSION_EMOJI:
            decline_movie(session.id)
            #await message.delete()
            await generate_embed_for_session(message.guild.id, message)

    @classmethod
    async def handle_session_unreaction(cls, session, user, message, emoji):
        if emoji == JOIN_SESSION_EMOJI:
            leave_session(session.id, user)
            #await message.edit(embed=await generate_embed_for_session(session, message, True))
            await generate_embed_for_session(message.guild.id, message)

    @classmethod
    async def set_rating(cls, movie, user, message, emoji):
        if emoji.name == BACK_EMOJI:
            #await message.delete()
            await generate_embed_for_movie(movie.uuid, message.guild.id, message)
        else:
            set_rating(movie.uuid, message.guild.id, user, FILM_RATING_EMOJIS.index(emoji.name)-1)
            movie = get_movie(uuid=movie.uuid, guild_id=message.guild.id)
            await message.remove_reaction(emoji, user)
            await generate_embed_for_finishing_movie(movie=movie, message=message)


    @classmethod
    async def handle_film_reaction(cls, movie: ParsedMovie, user: discord.User, channel, emoji, message=None):
        if emoji == FILM_SEEN_EMOJI:
            set_watched(movie.uuid, message.guild.id, user)
            await generate_embed_for_movie(movie.uuid, message.guild.id, message)
        elif emoji == FILM_PLAN_TO_WATCH_EMOJI:
            subscribe_to_see(movie.uuid, message.guild.id, user)
            await generate_embed_for_movie(movie.uuid, message.guild.id, message)
        elif emoji == FILM_DONT_WANT_TO_WATCH:
            set_dont_want_to_watch(movie.uuid, message.guild.id, user)
            await generate_embed_for_movie(movie.uuid, message.guild.id, message)
        elif emoji == FILM_RATING_EMOJI:
            await generate_embed_for_finishing_movie(movie=movie, message=message)

    @classmethod
    async def handle_film_unreaction(cls, movie: ParsedMovie, user: discord.User, channel, emoji, message=None):
        if emoji == FILM_SEEN_EMOJI or emoji == FILM_PLAN_TO_WATCH_EMOJI or emoji == FILM_DONT_WANT_TO_WATCH:
            set_unwatched(movie.uuid, message.guild.id, user)
            await generate_embed_for_movie(movie.uuid, message.guild.id, message)


async def setup(bot):
    await bot.add_cog(ReactionsModule(bot))

