import discord

from config import FILM_EMOJI, FILM_CONTROL_EMOJIS, FILM_RATING_EMOJI, BACK_EMOJI, FILM_RATING_EMOJIS
from models import ParsedMovie


async def generate_embed_for_movie(movie: ParsedMovie, message, return_message=False):
    title = f'{movie.name} {FILM_EMOJI}'
    want_to_see = ', '.join([user['mention'] for user in movie.want_to_see]) if len(movie.want_to_see) > 0 else 'никто'
    already_seen = ', '.join([user['mention'] for user in movie.already_seen]) if len(movie.already_seen) > 0 else 'никто'
    embed = discord.Embed(title=title)
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
    if return_message:
        return embed
    message = await message.channel.send(embed=embed)
    await message.add_reaction(BACK_EMOJI)
    for emoji in FILM_RATING_EMOJIS:
        await message.add_reaction(emoji)
