import discord

from config import FILM_EMOJI, FILM_CONTROL_EMOJIS, FILM_RATING_EMOJI, BACK_EMOJI, FILM_RATING_EMOJIS, POOP_EMOJI
from models import ParsedMovie


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


async def generate_embed_for_reaction(movie: ParsedMovie, message, return_message=False):
    embed = discord.Embed(title=f'{movie.name} {FILM_RATING_EMOJI}')
    total_rating = get_total_rating(movie)
    ratings = '\n'.join([f"""{ranking['user']['mention']}: \t{get_ranking_value(ranking['rating'])}""" for ranking in movie.rankings]) if len(movie.rankings) > 0 else None
    embed.add_field(name='Оценка киноклуба', value=total_rating if total_rating else 'Нет оценок', inline=False)
    embed.add_field(name='Оценки', value=ratings, inline=False)
    if return_message:
        return embed
    message = await message.channel.send(embed=embed)
    await message.add_reaction(BACK_EMOJI)
    for emoji in FILM_RATING_EMOJIS:
        await message.add_reaction(emoji)


def get_total_rating(movie):
    total_rating = get_ranking_value(
        sum([ranking['rating'] for ranking in movie.rankings]) / len(movie.rankings)) if len(
        movie.rankings) > 0 else None
    return total_rating


def get_ranking_value(rating):
    result = rating if type(rating) is int else round(rating, 1)
    return result if result > 0 else POOP_EMOJI
