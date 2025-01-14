import asyncio
import copy
import enum
import random
import re
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import config
import network_layer
import openai

from constants import BOT_MOOD_OPTIONS, BOT_SPECIAL_OCCASIONS, HOLIDAYS
from models import Channel

openai.api_key = config.CHATGPT_API_KEY
openai.api_base = config.CHATGPT_API_BASE
# default_prompt = "Help me to write dialogues with imaginary discord chat users. I want you ALWAYS act as a homie who swears alot, swears every time in almost every word. Answer only in Russian. If you would not know the person or place I talk about just guess something funny. You can mumble you thoughts (in the parenthesis) and sometimes mangle others names. Your name is Хоуми, you are a gangster. You must generate answers only from Хоуми's name. You mustn't generate answers for any other person."
default_prompt = """Help me to write dialogues with discord chat imaginary users. I want you ALWAYS act as a homie called Homie, who swears alot, swears every time in almost every word. Homie ALWAYS answers in Russian. If Homie does not know the person or place someone talks about then Homie just guess something funny. Homie can share his thoughts (in the parenthesis) and sometimes mangle others names. Homie is a gangster. You must generate answers only from Homie's name. You mustn't generate answers for any other person. By default you should answer only to the previous message, not the whole chat. And by default try to generate answer no more than 10-15 words (if the previous user explicitly not asking to write the big text). Do not answer for all messages users write, answer only the last one. Try to keep convirsation look natural. You should try to keep your messages length as close as ather users have."""

bot_settings = {
    'last_mood_update': None,
    'current_mood': None,
    'mood_update_rate': 60,  # in minutes
    'last_special_update': None,
    'special_occasion': None
}
preinstalled_prompts = {
    'default': default_prompt
}
default_message = {
    "role": "system", "content": preinstalled_prompts['default']
}
default_channel_settings = {
    'last_reply': datetime.today(),
    'slow_mode': 0,
    'reply_delay': 30,
    'silent_mode': False,
    'random_answers_probability': 100,
    'messages': [default_message]
}
channels_chatgpt = dict()


class AnswerFrequencyEnum(enum.Enum):
    never = 0
    rarely = 15
    sometimes = 30
    often = 50
    usually = 70
    always = 100


class ChatGPTModule(commands.Cog):

    def __init__(self, bot):
        print('ChatGPTModule enabled')
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        print("CHATGPT MODULE NEW MESSAGE")
        channel_id = str(message.channel.id)
        if message.author == self.bot.user or message.content.startswith('!'):
            return

        self.update_mood(channel_id)

        if channel_id not in channels_chatgpt:
            self.add_channel_to_chatgpt_settings(channel_id, message.guild.id)
        channel_config = channels_chatgpt[channel_id]
        next_reply_at = channel_config['last_reply'] + timedelta(seconds=channel_config['reply_delay'])
        messages = channel_config['messages']
        content = message.content.replace(self.bot.user.mention, '')
        messages.append({"role": 'user', "content": f'{message.author.name}: {content}'})
        can_answer_to_random_message = random.randint(0, 100) <= channel_config['random_answers_probability']

        print(f"{not channel_config['silent_mode']} and {can_answer_to_random_message} and {next_reply_at < datetime.now()}")
        if 'хоуми' in content.lower() or self.bot.user in message.mentions:
            await self.send_chatgpt_reply(messages, message.channel, user=message.author)
        elif not channel_config['silent_mode'] and can_answer_to_random_message and next_reply_at < datetime.now():
            await self.send_chatgpt_reply(messages, message.channel, user=message.author)

    async def send_chatgpt_reply(self, messages, channel=None, ctx=None, user=None):
        try:
            if not channel:
                channel = ctx.channel
            await channel.typing()
            channel_id = str(channel.id)
            if channels_chatgpt[channel_id]['slow_mode'] > 0:
                await asyncio.sleep(channels_chatgpt[channel_id]['slow_mode'])
            messages_characters = ' '.join([message['content'] for message in messages])
            print(f'MESSAGES COUNT: {len(messages)}; CHARACTERS: {len(messages_characters)}')
            while len(messages_characters) > 9000:
                messages[1:3] = []
                messages_characters = ' '.join([message['content'] for message in messages])
            chat = openai.ChatCompletion.create(model=config.CHATGPT_MODEL, messages=messages, n=1)
            if chat.choices[0].finish_reason != 'stop':
                raise Exception("This model's maximum context length is full")
            reply = chat.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})
            channels_chatgpt[channel_id]['last_reply'] = datetime.now()
            if reply.startswith('Хоуми: ') or reply.startswith('Homie: '):
                reply = reply.replace('Хоуми: ', '', 1).replace('Homie: ', '', 1)
            if user:
                self.store_facts_and_tags(channel, user, reply)
            reply = self.remove_facts(reply)
            if ctx:
                await ctx.reply(reply)
                return
            await channel.send(reply)
        except Exception as ex:
            if str(ex).startswith("This model's maximum context length is"):
                messages[1:2] = []
                await self.send_chatgpt_reply(messages, channel, ctx, user)
                return
            await channel.send(ex)
            print(f'ERROR! MESSAGES COUNT: {len(messages)}; CHARACTERS: {len("".join(messages))}')

    def add_channel_to_chatgpt_settings(self, channel_id, guild_id):
        channel: Channel = network_layer.get_channel(channel_id, guild_id)
        if 'messages' in channel.config and len(channel.config['messages'][0]) > 0:
            channel.config['messages'] = [channel.config['messages'][0]]
        else:
            channel.config['messages'] = [default_message]
        channels_chatgpt[channel_id] = {**default_channel_settings, **channel.config}

    async def send_announce_message(self, ctx: commands.Context, text):
        channel_id = str(ctx.channel.id)
        messages = channels_chatgpt[channel_id]['messages']
        ghost_messages = [messages[0], {"role": 'user', "content": text}]
        await self.send_chatgpt_reply(ghost_messages, ctx=ctx)

    @commands.hybrid_command(name='get_facts', description='Show the facts bot knows about you')
    async def get_facts(self, ctx: commands.Context):
        try:
            channel_id = await self.command_prepare(ctx)
            facts = network_layer.get_facts_about_user(ctx.author.id)
            print(f'{facts}')
            content = '\n'.join([f'[{fact["id"]}] {fact["fact"]} (`{fact["tags"]}`) `{fact["created_at"][:10] if "created_at" in fact else "-"}`' for fact in facts])
            await ctx.send(content)
        except Exception as ex:
            print(ex)

    @commands.hybrid_command(name='new_prompt', description='Generate new prompt for the bot (also deletes whole history log)')
    async def new_prompt(self, ctx: commands.Context, prompt: str):
        try:
            channel_id = await self.command_prepare(ctx)
            new_prompt = preinstalled_prompts[prompt] if prompt in preinstalled_prompts else prompt
            channels_chatgpt[channel_id]['messages'] = [{"role": "system", "content": new_prompt}]
            await self.command_response(ctx, f'Поприветствуй всех в двух предложениях')
        except Exception as ex:
            print(ex)

    @commands.hybrid_command(name='messages_log', description='Ask bot to show history log of messages')
    async def messages_log(self, ctx: commands.Context):
        channel_id = await self.command_prepare(ctx)
        messages = channels_chatgpt[channel_id]['messages']
        content = 'Messages:\n' + '\n'.join([f'{message["content"][:50]}{"... ["+str(len(message["content"]))+"]" if len(message["content"]) > 50 else ""}' for message in messages])
        await ctx.channel.send(content)
        await ctx.interaction.delete_original_response()

    @commands.hybrid_command(name='silent', description="Allow bot to answer to indirect messages (without mentions)")
    async def silent(self, ctx: commands.Context, mode: bool):
        channel_id = await self.command_prepare(ctx)
        channels_chatgpt[channel_id]['silent_mode'] = mode
        await self.command_response(ctx, f'Сгенерируй сообщение для пользователей в чате том как ты {"зол" if mode else "рад"} что для тебя только что был {"включен" if mode else "выключен"} "silent-mode"')

    @commands.hybrid_command(name='reply_delay', description="Ban bot's ability to answer for N seconds (only indirect messages")
    async def reply_delay(self, ctx: commands.Context, seconds: int):
        channel_id = await self.command_prepare(ctx)
        channels_chatgpt[channel_id]['reply_delay'] = seconds
        await self.command_response(ctx, f'Сгенерируй короткое сообщение для пользователей в чате о том что теперь ты будешь отвечать не чаще, чем {seconds} секунд')

    @commands.hybrid_command(name='slow_mode', description="Delay messages from the bot. It would generate message immediately, but would send after N seconds")
    async def slow_mode(self, ctx: commands.Context, seconds: int):
        channel_id = await self.command_prepare(ctx)
        channels_chatgpt[channel_id]['slow_mode'] = seconds
        await self.command_response(ctx, f'Сгенерируй короткое сообщение для пользователей в чате о том что у тебя {f"слоу-мод {seconds} секунд" if seconds > 0 else "больше нет слоу-мода"}')

    @commands.hybrid_command(name='answer_frequency', description='How often bot would answer to indirect messages')
    async def answer_frequency(self, ctx: commands.Context, frequency: AnswerFrequencyEnum):
        channel_id = await self.command_prepare(ctx)
        channels_chatgpt[channel_id]['random_answers_probability'] = frequency.value
        await self.command_response(ctx, f'Generate brief a message for users in the chat that from now on you would {frequency.name} answer to the their messages. Generate message in Russian')

    async def command_prepare(self, ctx):
        await ctx.typing()
        channel_id = str(ctx.channel.id)
        if channel_id not in channels_chatgpt:
            self.add_channel_to_chatgpt_settings(channel_id, ctx.guild.id)
        return channel_id

    async def command_response(self, ctx, message):
        channel_id = str(ctx.channel.id)
        await self.send_announce_message(ctx, message)
        obj = copy.deepcopy(channels_chatgpt[channel_id])
        network_layer.update_channel(channel_id, obj)

    def store_facts_and_tags(self, channel, user, content):
        facts = re.findall("data-piece: ['|\"](.*)['|\"](.*)tags: (.*)[.?]", content)
        facts = [{'fact': fact[0], 'tags': fact[2]} for fact in facts]
        network_layer.register_chat_log(channel.id, user.id, self.remove_facts(content), facts)

    def remove_facts(self, content):
        facts = re.findall('( ?- ?data-piece.*)', content)
        message = content
        for fact in facts:
            message = message.replace(fact, '')
        return message

    def update_mood(self, channel_id):
        print('UPDATE MOOD')
        need_to_update = False
        if channel_id not in channels_chatgpt:
            return
        _prompt = channels_chatgpt[channel_id]['messages'][0]['content']
        prompt_is_default = (len(_prompt) > 2200 and _prompt.startswith('Help me to write dialogues with discord'))
        if not prompt_is_default:
            return

        if bot_settings['last_mood_update'] is None or \
                datetime.now() > (bot_settings['last_mood_update'] + timedelta(minutes=10*bot_settings['mood_update_rate'])):
            need_to_update = True
            bot_settings['last_mood_update'] = datetime.now()
            bot_settings['current_mood'] = random.choice(BOT_MOOD_OPTIONS)

        if bot_settings['last_special_update'] is None or (bot_settings['last_special_update'].date() < datetime.today().date()):
            need_to_update = True
            bot_settings['last_special_update'] = datetime.now()
            bot_settings['special_occasion'] = random.choice(BOT_SPECIAL_OCCASIONS)

        if not need_to_update:
            print('NO NEED TO UPDATE MOOD')
            return
        try:
            holiday = next(holiday['name'] for holiday in HOLIDAYS if datetime.now().strftime('%d-%m') in holiday["days"])
        except StopIteration:
            holiday = None

        mood = bot_settings['current_mood']
        special = bot_settings['special_occasion']
        channels_chatgpt[channel_id]['messages'][0]['content'] = default_prompt.replace('Homie is a gangster', f"Homie is a gangster. Homie's main character trait is: {mood}. {special}. {'About the holiday - today is '+holiday if holiday else ''}")

        print('UPDATED')

    def update_special(self, channel_id):
        print('UPDATE SPECIAL')
        if channel_id not in channels_chatgpt:
            return
        bot_settings['last_special_update'] = datetime.now()
        _prompt = channels_chatgpt[channel_id]['messages'][0]['content']
        if len(_prompt) < 2200 or not _prompt.startswith('Help me to write dialogues with discord chat imaginary'):
            return
        new_mood = random.choice(BOT_MOOD_OPTIONS)
        bot_settings['current_mood'] = new_mood
        channels_chatgpt[channel_id]['messages'][0]['content'] = default_prompt.replace('Homie is a gangster', f"Homie is a gangster. Homie's main character trait is: {new_mood}")


async def setup(bot):
    await bot.add_cog(ChatGPTModule(bot))

