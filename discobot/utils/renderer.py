import math
import random

import discord

from config import FILM_EMOJI, FILM_CONTROL_EMOJIS, FILM_RATING_EMOJI, BACK_EMOJI, FILM_RATING_EMOJIS, POOP_EMOJI, \
    SESSION_EMOJI, SESSION_CONTROL_NO_FILM_EMOJIS, DECLINE_MOVIE_SESSION_EMOJI, SESSION_CONTROL_WITH_FILM_EMOJIS, \
    ANIMALS, BLACK_SCORE_EMOJI, SCORE_EMOJI, SESSIONS_PER_PAGE, HISTORY_CONTROL_EMOJIS, HISTORY_EMOJI
from models import ParsedMovie, Session, History
from network_layer import get_movie, get_guild_session, get_session, get_history


async def display_message(embed: discord.Embed, message: discord.Message, new_emojis: list, channel):
    if message:
        print('there is message, changing')
        old_emojis = [e.emoji for e in message.reactions]
        await message.edit(embed=embed)
        if set(old_emojis) != set(new_emojis):
            await message.clear_reactions()
            for emoji in new_emojis:
                await message.add_reaction(emoji)
    else:
        print('no message, creating new')
        message = await channel.send(embed=embed)
        for emoji in new_emojis:
            await message.add_reaction(emoji)

async def generate_embed_for_movie(movie_uuid: int, guild_id:int, message=None, channel=None):
    movie = get_movie(uuid=movie_uuid, guild_id=guild_id)
    title = f'{movie.name} {FILM_EMOJI}'
    want_to_see = ', '.join([user['mention'] for user in movie.want_to_see]) if len(movie.want_to_see) > 0 else 'никто'
    already_seen = ', '.join([user['mention'] for user in movie.already_seen]) if len(movie.already_seen) > 0 else 'никто'
    dont_want_to_watch = ', '.join([user['mention'] for user in movie.dont_want_to_watch]) if len(movie.dont_want_to_watch) > 0 else None
    #total_rating = get_total_rating(movie)
    embed = discord.Embed(title=title)
    if movie.average_rating is not None:
        #embed.add_field(name='Оценка киноклуба', value=total_rating, inline=False)
        embed.add_field(name='Оценка киноклуба', value=movie.average_rating if movie.average_rating>0 else POOP_EMOJI, inline=False)
    embed.add_field(name='Год', value=movie.year, inline=True)
    embed.add_field(name='В главных ролях', value=movie.actors, inline=True)
    embed.add_field(name='Кто хочет посмотреть', value=want_to_see, inline=False)
    embed.add_field(name='Кто уже видел', value=already_seen, inline=False)
    if dont_want_to_watch:
        embed.add_field(name='Не хотят смотреть', value=dont_want_to_watch, inline=False)
    embed.set_thumbnail(url=movie.image)
    await display_message(embed, message, FILM_CONTROL_EMOJIS, channel)


def get_ranking_value(rating):
    if rating is None:
        return None
    output = ''
    result = rating if type(rating) is int else round(rating, 1)
    if type(result) is int and result > 0:
        for x in range(5):
            output += SCORE_EMOJI if x < result else BLACK_SCORE_EMOJI
    else:
        output = result if result > 0 else POOP_EMOJI
    return output


async def generate_embed_for_session(guild_id: int, message=None, channel=None):
    members = channel.members if channel else message.channel.members
    members_ids = [member.id for member in members if not member.bot]
    session: Session = get_guild_session(guild_id, members_ids=members_ids)
    embed = discord.Embed(title=f'Киносеанс {SESSION_EMOJI}')
    audience = ', '.join([user['mention'] for user in session.audience]) if len(session.audience) > 0 else 'Ещё никто не присоеденился'
    embed.add_field(name='Зрители', value=audience, inline=False)
    if session.movie:
        embed.add_field(name='Выбранный фильм', value=session.movie['name'], inline=False)
    else:
        #embed.add_field(name='Доступно фильмов на рандоме', value=len(session.available_movies), inline=False)
        if len(session.club_has_seen) > 0:
            crave_movies = []
            i = 0
            for movie in session.club_has_seen:
                i += 1
                rating = f"`{get_rating_value(movie['average_rating'])}`" if movie['average_rating'] else ''
                crave_movies.append(f"{movie['name']} {rating}")
                if i >= 10:
                    crave_movies.append(f'(И ещё {len(session.club_has_seen) - 10} других)')
                    break
            embed.add_field(name='Годнота от киноклуба', value='\n'.join(crave_movies), inline=False)
        if len(session.audience_want_to_see_movies) > 0:
            crave_movies = []
            i = 0
            for movie in session.audience_want_to_see_movies:
                i += 1
                crave_movies.append(movie['name'])
                if i >= 10:
                    crave_movies.append(f'(И ещё {len(session.available_movies) - 10} других)')
                    break
            embed.add_field(name='Все хотят посмотреть', value='\n'.join(crave_movies), inline=False)
    emojis_to_display = SESSION_CONTROL_WITH_FILM_EMOJIS if session.movie else SESSION_CONTROL_NO_FILM_EMOJIS
    await display_message(embed, message, emojis_to_display, channel)


async def generate_embed_for_finishing_movie(session_id: int = None, movie: ParsedMovie = None, message=None, channel=None, guild=None):
    session = None
    if session_id:
        session = get_session(session_id)
    if not movie and session:
        movie = get_movie(uuid=session.movie['uuid'], guild_id=guild.id)
    if not session and movie and movie.sessions:
        session = get_session(movie.sessions[-1])

    embed = discord.Embed(title=f'{movie.name} {FILM_RATING_EMOJI}')

    if session and session.seen_at:
        embed.description = 'Спасибо за просмотр!'
        audience = get_audience(session.audience, movie.name + str(session.seen_at))
        embed.add_field(name='Зрители', value=audience, inline=False)
        embed.add_field(name='Последний просмотр состоялся', value=session.seen_at, inline=False)

    total_rating = get_ranking_value(movie.average_rating)
    ratings = '\n'.join([f"""{ranking['user']['mention']}: \t{get_ranking_value(ranking['rating'])}""" for ranking in movie.rankings]) if len(movie.rankings) > 0 else None
    embed.add_field(name='Оценка киноклуба', value=total_rating if total_rating is not None else 'Нет оценок', inline=False)
    if ratings:
        embed.add_field(name='Оценки', value=ratings, inline=False)

    await display_message(embed, message, FILM_RATING_EMOJIS, channel)


def get_audience(users: list, seed: str):
    if len(users) <= 0:
        return 'Никого не было D:'

    output = []
    for user in users:
        index = sum(map(ord, user['name'] + seed)) % len(ANIMALS)
        animal = ANIMALS[index] if 0 <= index <= len(ANIMALS) else random.choice(ANIMALS)
        output.append(f"{animal}{user['mention']}")
    return ', '.join(output)


async def generate_embed_for_history(guild_id: int, page=0, message: discord.Message = None, channel: discord.TextChannel = None):
    history = get_history(guild_id, page=page)
    guild_name = message.guild.name if message else channel.guild.name
    channel = channel if channel else message.channel
    title = f'Киносеансы **{guild_name}** {HISTORY_EMOJI}'
    embed = discord.Embed(title=title)
    if history.sessions:
        viewed_movies = []
        for session in history.sessions:
            rating = get_rating_value(session.movie['average_rating']) if session.movie else ' '
            movie_title = session.movie['name'] if session.movie else 'Фильм не указан'
            movie_title = f'{rating}{movie_title}'
            viewed_movies.append(f"`{session.seen_at}` {movie_title}")
        max_pages = math.ceil(history.count/SESSIONS_PER_PAGE)
        additional_info = f'({history.page}/{max_pages})' if max_pages > 1 else ''
        embed.add_field(name=f'История просмотров {additional_info}', value='\n'.join(viewed_movies), inline=False)
    await display_message(embed, message, HISTORY_CONTROL_EMOJIS, channel)


def get_rating_value(value):
    return value if value and value > 0 else POOP_EMOJI