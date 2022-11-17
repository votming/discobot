import discord
from discord.ext import commands

import network_layer
from config import SESSION_EMOJI
from utils.renderer import generate_embed_for_session, generate_embed_for_history


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

            history_command = message.content.startswith('#история') or message.content.startswith('history')
            session_command = message.content.startswith('#киносеанс') or message.content.startswith('session')
            session_command_with_movie = message.content.startswith('#киносеанс ') and len(message.content) > 11
            reply = message.reference and message.reference.message_id

            if session_command:
                session = network_layer.get_guild_session(message.guild.id)
                if session_command_with_movie:
                    selected_the_movie = network_layer.select_movie(session.id, message.content.replace('#киносеанс ', ''))
                    if not selected_the_movie:
                        await message.channel.send(f'Фильм не найден (`{message.content}`)')
                        return
                await generate_embed_for_session(message.guild.id, channel=message.channel)
            if history_command:
                await generate_embed_for_history(message.guild.id, channel=message.channel)
            if reply:
                session = network_layer.get_guild_session(message.guild.id)
                session_message = await message.channel.fetch_message(message.reference.message_id)
                is_bot = session_message.author == self.bot.user
                has_embeds = len(session_message.embeds) > 0
                session_reaction = session_message.embeds[0].title.endswith(SESSION_EMOJI) if has_embeds else False
                if is_bot and has_embeds and session_reaction:
                    selected_the_movie = network_layer.select_movie(session.id, message.content)
                    if selected_the_movie:
                        await session_message.delete()
                        await generate_embed_for_session(message.guild.id, channel=message.channel)
                    else:
                        await message.channel.send(f'Фильм не найден (`{message.content}`)')

        except Exception as e:
            print(str(e))


async def setup(bot):
    await bot.add_cog(SessionsModule(bot))

