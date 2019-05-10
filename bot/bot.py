# -*- coding: utf-8 -*-

import aioredis
from discord.ext import commands
import json


async def is_blacklisted(ctx):
    blacklist = ctx.bot.config['blacklist']
    return not ctx.author.id in blacklist


class Bot(commands.Bot):

    def __init__(self, config, **kwargs):
        super().__init__(
            command_prefix=config['bot']['prefix'],
            case_insensitive=True,
            owner_id=config['bot'].get('owner_id'),
            **kwargs,
        )

        self.config = config

        self.redis = None

        extensions = ('jishaku', 'bot.cogs.blurple', 'bot.cogs.errors', 'bot.cogs.help', 'bot.cogs.rollteam')

        for name in extensions:
            self.load_extension(name)

        self.add_check(is_blacklisted)

    @classmethod
    def with_config(cls, path='config.json'):
        """Create a bot instance with a Config."""
        with open('config.json', 'r', encoding="utf8") as file:
            data = json.load(file)
        return cls(data)

    async def start(self, *args, **kwargs):
        self.redis = await aioredis.create_redis_pool(**self.config['redis'])

        await super().start(*args, **kwargs)

    def run(self):
        super().run(self.config['bot']['token'])
