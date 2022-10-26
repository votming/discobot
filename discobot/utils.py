import math
import random

import discord

from config import FILM_EMOJI, FILM_CONTROL_EMOJIS, FILM_RATING_EMOJI, BACK_EMOJI, FILM_RATING_EMOJIS, POOP_EMOJI, \
    SESSION_EMOJI, SESSION_CONTROL_NO_FILM_EMOJIS, DECLINE_MOVIE_SESSION_EMOJI, SESSION_CONTROL_WITH_FILM_EMOJIS, \
    ANIMALS, BLACK_SCORE_EMOJI, SCORE_EMOJI, SESSIONS_PER_PAGE, HISTORY_CONTROL_EMOJIS, HISTORY_EMOJI
from models import ParsedMovie, Session, History
from network_layer import get_movie, create_new_session, get_session


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

async def generate_embed_for_movie(movie: ParsedMovie, message=None, channel=None):
    title = f'{movie.name} {FILM_EMOJI}'
    want_to_see = ', '.join([user['mention'] for user in movie.want_to_see]) if len(movie.want_to_see) > 0 else 'никто'
    already_seen = ', '.join([user['mention'] for user in movie.already_seen]) if len(movie.already_seen) > 0 else 'никто'
    #total_rating = get_total_rating(movie)
    embed = discord.Embed(title=title)
    if movie.average_rating is not None:
        #embed.add_field(name='Оценка киноклуба', value=total_rating, inline=False)
        embed.add_field(name='Оценка киноклуба', value=movie.average_rating if movie.average_rating>0 else POOP_EMOJI, inline=False)
    embed.add_field(name='Год', value=movie.year, inline=True)
    embed.add_field(name='В главных ролях', value=movie.actors, inline=True)
    embed.add_field(name='Кто хочет посмотреть', value=want_to_see, inline=False)
    embed.add_field(name='Кто уже видел', value=already_seen, inline=False)
    embed.set_thumbnail(url=movie.image)
    await display_message(embed, message, FILM_CONTROL_EMOJIS, channel)
    return

    if return_message:
        return embed
    message = await message.channel.send(embed=embed)
    for emoji in FILM_CONTROL_EMOJIS:
        await message.add_reaction(emoji)


# def get_total_rating(movie):
#     total_rating = get_ranking_value(
#         sum([ranking['rating'] for ranking in movie.rankings]) / len(movie.rankings)) if len(
#         movie.rankings) > 0 else None
#     return total_rating


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


async def generate_embed_for_session(session: Session, message=None, channel=None):
    embed = discord.Embed(title=f'Киносеанс {SESSION_EMOJI}')
    audience = ', '.join([user['mention'] for user in session.audience]) if len(session.audience) > 0 else 'Ещё никто не присоеденился'
    embed.add_field(name='Зрители', value=audience, inline=False)
    if session.movie:
        embed.add_field(name='Выбранный фильм', value=session.movie['name'], inline=False)
    else:
        embed.add_field(name='Доступно фильмов на рандоме', value=len(session.available_movies), inline=False)
        if len(session.audience_want_to_see_movies) > 0:
            crave_movies = []
            i = 0
            for movie in session.audience_want_to_see_movies:
                i += 1
                crave_movies.append(movie['name'])
                if i >= 10:
                    crave_movies.append(f'И ещё {len(session.available_movies)}...')
                    break
            embed.add_field(name='Все хотят посмотреть', value='\n'.join(crave_movies), inline=False)
    emojis_to_display = SESSION_CONTROL_WITH_FILM_EMOJIS if session.movie else SESSION_CONTROL_NO_FILM_EMOJIS
    await display_message(embed, message, emojis_to_display, channel)
    return
    if return_message:
        return embed
    message = await message.channel.send(embed=embed)
    if session.movie:
        for emoji in SESSION_CONTROL_WITH_FILM_EMOJIS:
            await message.add_reaction(emoji)
    else:
        for emoji in SESSION_CONTROL_NO_FILM_EMOJIS:
            await message.add_reaction(emoji)


async def generate_embed_for_finishing_movie(session: Session = None, movie: ParsedMovie = None, message=None, channel=None, guild=None):
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
    return
    if return_message:
        return embed
    message = await message.channel.send(embed=embed)
    await message.add_reaction(BACK_EMOJI)
    for emoji in FILM_RATING_EMOJIS:
        await message.add_reaction(emoji)


def get_audience(users: list, seed: str):
    if len(users) <= 0:
        return 'Никого не было D:'

    output = []
    for user in users:
        index = sum(map(ord, user['name'] + seed)) % len(ANIMALS)
        animal = ANIMALS[index] if 0 <= index <= len(ANIMALS) else random.choice(ANIMALS)
        output.append(f"{animal}{user['mention']}")
    return ', '.join(output)


async def generate_embed_for_history(history: History, message: discord.Message = None, channel: discord.TextChannel = None):
    guild_name = message.guild.name if message else channel.guild.name
    channel = channel if channel else message.channel
    title = f'Киносеансы **{guild_name}** {HISTORY_EMOJI}'
    embed = discord.Embed(title=title)
    if history.sessions:
        viewed_movies = []
        for session in history.sessions:
            rating = f"`({session.movie['average_rating'] if session.movie['average_rating'] and session.movie['average_rating']>0 else POOP_EMOJI})` " if session.movie else ' '
            movie_title = session.movie['name'] if session.movie else 'Фильм не указан'#история
            movie_title = f'{rating}{movie_title}'
            viewed_movies.append(f"`{session.seen_at}` {movie_title}")
        max_pages = math.ceil(history.count/SESSIONS_PER_PAGE)
        additional_info = f'({history.page}/{max_pages})' if max_pages > 1 else ''
        embed.add_field(name=f'История просмотров {additional_info}', value='\n'.join(viewed_movies), inline=False)
    await display_message(embed, message, HISTORY_CONTROL_EMOJIS, channel)
