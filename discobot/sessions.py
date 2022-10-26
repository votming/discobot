import discord
from discord.ext import commands

import network_layer
from config import FILM_EMOJI, FILM_CONTROL_EMOJIS, SESSION_EMOJI
from imdb import MovieParser
from models import ParsedMovie
from utils import generate_embed_for_movie, generate_embed_for_session, generate_embed_for_history


class SessionsModule(commands.Cog):

    def __init__(self, bot):
        print('SessionsModule enabled')
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        print('new on_message')
        try:
            if message.author == self.bot.user:
                return

            if message.content.startswith('#киносеанс'):
                session = network_layer.create_new_session(message.guild)
                await generate_embed_for_session(session, channel=message.channel)
            if message.content.startswith('#история'):
                history = network_layer.get_history(message.guild.id)
                await generate_embed_for_history(history, channel=message.channel)
            if message.reference and message.reference.message_id:
                session = network_layer.create_new_session(message.guild)
                session_message = await message.channel.fetch_message(message.reference.message_id)
                is_bot = session_message.author == self.bot.user
                has_embeds = len(session_message.embeds) > 0
                session_reaction = session_message.embeds[0].title.endswith(SESSION_EMOJI) if has_embeds else False
                if is_bot and has_embeds and session_reaction:
                    selected_the_movie = network_layer.select_movie(session.id, message.content)
                    if selected_the_movie:
                        session = network_layer.create_new_session(message.guild)
                        await session_message.delete()
                        await generate_embed_for_session(session, channel=message.channel)
                    else:
                        await message.channel.send(f'Фильм не найден (`{message.content}`)')

        except Exception as e:
            print(str(e))


async def setup(bot):
    await bot.add_cog(SessionsModule(bot))

