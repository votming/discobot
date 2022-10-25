import discord
from discord.ext import commands

import network_layer
from config import FILM_EMOJI, FILM_CONTROL_EMOJIS
from imdb import MovieParser
from models import ParsedMovie
from utils import generate_embed_for_movie


class MoviesModule(commands.Cog):

    def __init__(self, bot):
        print('MoviesModule enabled')
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


async def setup(bot):
    await bot.add_cog(MoviesModule(bot))

