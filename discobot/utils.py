import discord

from config import FILM_EMOJI, FILM_CONTROL_EMOJIS, FILM_RATING_EMOJI, BACK_EMOJI, FILM_RATING_EMOJIS, POOP_EMOJI, \
    SESSION_EMOJI, SESSION_CONTROL_NO_FILM_EMOJIS, DECLINE_MOVIE_SESSION_EMOJI, SESSION_CONTROL_WITH_FILM_EMOJIS
from models import ParsedMovie, Session
from network_layer import get_movie, create_new_session


async def generate_embed_for_movie(movie: ParsedMovie, message, return_message=False):
    title = f'{movie.name} {FILM_EMOJI}'
    want_to_see = ', '.join([user['mention'] for user in movie.want_to_see]) if len(movie.want_to_see) > 0 else 'никто'
    already_seen = ', '.join([user['mention'] for user in movie.already_seen]) if len(movie.already_seen) > 0 else 'никто'
    total_rating = get_total_rating(movie)
    embed = discord.Embed(title=title)
    if total_rating:
        embed.add_field(name='Оценка киноклуба', value=total_rating, inline=False)
    embed.add_field(name='Год', value=movie.year, inline=True)
    embed.add_field(name='В главных ролях', value=movie.actors, inline=True)
    embed.add_field(name='Кто хочет посмотреть', value=want_to_see, inline=False)
    embed.add_field(name='Кто уже видел', value=already_seen, inline=False)
    embed.set_thumbnail(url=movie.image)
    if return_message:
        return embed
    message = await message.channel.send(embed=embed)
    for emoji in FILM_CONTROL_EMOJIS:
        await message.add_reaction(emoji)


def get_total_rating(movie):
    total_rating = get_ranking_value(
        sum([ranking['rating'] for ranking in movie.rankings]) / len(movie.rankings)) if len(
        movie.rankings) > 0 else None
    return total_rating


def get_ranking_value(rating):
    result = rating if type(rating) is int else round(rating, 1)
    return result if result > 0 else POOP_EMOJI


async def generate_embed_for_session(session: Session, message, return_message=False):
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
    if return_message:
        return embed
    message = await message.channel.send(embed=embed)
    if session.movie:
        for emoji in SESSION_CONTROL_WITH_FILM_EMOJIS:
            await message.add_reaction(emoji)
    else:
        for emoji in SESSION_CONTROL_NO_FILM_EMOJIS:
            await message.add_reaction(emoji)


async def generate_embed_for_finishing_movie(session: Session = None, movie: ParsedMovie = None, message=None, return_message=False):
    if not movie:
        movie = get_movie(session.movie['id'])
    if not session and movie and movie.session:
        session = create_new_session(message.guild)

    embed = discord.Embed(title=f'{movie.name} {FILM_RATING_EMOJI}')

    if session and session.seen_at:
        embed.description = 'Спасибо за просмотр!'
        audience = ', '.join([user['mention'] for user in session.audience]) if len(session.audience) > 0 else 'Никого не было D:'
        embed.add_field(name='Зрители', value=audience, inline=False)
        if movie.seen_at:
            embed.add_field(name='Показ состоялся', value=movie.seen_at, inline=False)

    total_rating = get_total_rating(movie)
    ratings = '\n'.join([f"""{ranking['user']['mention']}: \t{get_ranking_value(ranking['rating'])}""" for ranking in movie.rankings]) if len(movie.rankings) > 0 else None
    embed.add_field(name='Оценка киноклуба', value=total_rating if total_rating else 'Нет оценок', inline=False)
    embed.add_field(name='Оценки', value=ratings, inline=False)
    if return_message:
        return embed
    message = await message.channel.send(embed=embed)
    for emoji in FILM_RATING_EMOJIS:
        await message.add_reaction(emoji)
