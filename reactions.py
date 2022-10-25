import discord
from discord.ext import commands
from discord.ext.commands import cog
import wikipedia

from config import FILM_EMOJI, FILM_SEEN_EMOJI, FILM_PLAN_TO_WATCH_EMOJI, FILM_RATING_EMOJI, FILM_RATING_EMOJIS, \
    BACK_EMOJI
from models import ParsedMovie

from network_layer import subscribe_to_see, get_movie, get_movie_by_name, set_watched, set_rating
from utils import generate_embed_for_movie, generate_embed_for_reaction

number_emojies = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
WIKI_EMBED_TITLE = 'Выберите тему'


class ReactionsModule(commands.Cog):

    def __init__(self, bot):
        print('ReactionsModule enabled')
        self.bot = bot

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

        try:
            if valid_reaction and wiki_question:
                await self.handle_wiki_reaction(message, emoji)
            elif valid_reaction and film_reaction:
                movie = get_movie_by_name(message.embeds[0].title.replace(f' {FILM_EMOJI}', ''))#Movie.objects.get(title=message.embeds[0].title.replace(f' {FILM_EMOJI}', ''))
                await self.handle_film_reaction(movie, user, channel, emoji.name, message)
            elif valid_reaction and film_rating:
                movie = get_movie_by_name(message.embeds[0].title.replace(f' {FILM_RATING_EMOJI}', ''))
                await self.set_rating(movie, user, message, emoji.name)
        except Exception as e:
            print(str(e))

    @classmethod
    async def set_rating(cls, movie, user, message, emoji):
        if emoji == BACK_EMOJI:
            await message.delete()
            await generate_embed_for_movie(movie, message)
        else:
            set_rating(movie.id, user, FILM_RATING_EMOJIS.index(emoji))
            movie = get_movie(movie.id)
            await message.edit(embed=await generate_embed_for_reaction(movie, message, True))


    @classmethod
    async def handle_film_reaction(cls, movie: ParsedMovie, user: discord.User, channel, emoji, message=None):
        if emoji == FILM_SEEN_EMOJI:
            set_watched(movie.id, user)
            movie = get_movie(movie.id)
            await message.edit(embed=await generate_embed_for_movie(movie, message, True))
        elif emoji == FILM_PLAN_TO_WATCH_EMOJI:
            subscribe_to_see(movie.id, user)
            movie = get_movie(movie.id)
            await message.edit(embed=await generate_embed_for_movie(movie, message, True))
        elif emoji == FILM_RATING_EMOJI:
            await message.delete()
            await generate_embed_for_reaction(movie, message)

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

