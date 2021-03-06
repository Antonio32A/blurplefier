# -*- coding: utf-8 -*-

import asyncio
import base64
import json
import logging
import os
import signal
import traceback

import aiohttp
import aioredis
import discord.http
import json

from .magic import convert_image, check_image


log = logging.getLogger(__name__)


WORKER_COUNT = int(os.environ.get('WORKER_COUNT', '1'))

CONNECTION_ERRORS = (
    asyncio.TimeoutError,
    aiohttp.ClientConnectionError,
    aiohttp.ClientConnectorError,
    aiohttp.ClientOSError,
    aiohttp.ServerConnectionError,
)


# Please ignore this ugliness
async def _yield_forever():
    while True:
        await asyncio.sleep(1)


class Worker:
    def __init__(self, config):
        self.config = config

        self.http = None
        self.session = None

        self.redis = None

        self.token = None
        self.worker_id = None

        self._bot_user_id = int(base64.b64decode(self.config['bot']['token'].split('.', 1)[0]))

        self.loop = asyncio.get_event_loop()

    @classmethod
    def with_config(cls, path='config.json'):
        """Create a bot instance with a Config."""
        with open('config.json', 'r', encoding="utf8") as file:
            data = json.load(file)
        return cls(data)


    async def start(self):
        self.redis = await aioredis.create_redis_pool(**self.config['redis'])

        await self.claim_token()
        self._claim_task = self.loop.create_task(self._keep_claim())

        # We're using discord.py's HTTP class for rate limit handling
        # This is not intended to be used so there's no pretty way of creating it
        self.http = http = discord.http.HTTPClient()
        http._token(self.token)
        self.session = http._HTTPClient__session = aiohttp.ClientSession()

        self.loop.create_task(self.run_jobs())

        await _yield_forever()

    def run(self):
        loop = self.loop

        loop.create_task(self.start())

        try:
            loop.add_signal_handler(signal.SIGINT, loop.stop)
            loop.add_signal_handler(signal.SIGTERM, loop.stop)
        except RuntimeError:  # Windows
            pass

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()

    async def claim_token(self):
        # We have a token per active worker
        # As we don't know which worker we are we simply claim a token by setting a key in redis
        # If it's set we can assume it to be currently used (unless the worker crashed - but it'll expire)
        # Should we not find a free token we'll simply wait for 10 seconds and try again

        while self.token is None:
            for worker_id in range(WORKER_COUNT):
                if await self.redis.execute('SET', f'blurple:worker:{worker_id}', ':ablobwave:', 'NX', 'EX', '30'):
                    self.worker_id = worker_id
                    self.token = self.config['workers'][worker_id]
                    break

            if self.token is None:
                log.warning('Failed to claim worker ID, retrying in 10 seconds ..')
                await asyncio.sleep(10)

    async def _keep_claim(self):
        while not self.loop.is_closed():
            try:
                with await self.redis as conn:
                    await conn.set(f'blurple:worker:{self.worker_id}', ':ablobwavereverse:', expire=30)
            except (aioredis.ConnectionClosedError, aioredis.ProtocolError, aioredis.ReplyError, TypeError):
                log.exception('Failed to continue worker ID claim, retrying in 10 seconds ..')

            await asyncio.sleep(10)

    async def run_jobs(self):
        while self.loop.is_running():
            _, data = await self.redis.blpop('blurple:queue')

            job = json.loads(data)
            log.info(f'Running job {job}.')

            try:
                await self.run_job(job)
            except Exception:
                log.exception(f'Failed to run job: {job}.')

    async def run_job(self, data):
        user_id = data['requester']
        guild_id = data['guild']
        channel_id = data['channel']
        message_id = data['message']

        async def blurplefy():
            try:
                async with self.session.get(data['url']) as resp:
                    if int(resp.headers.get('Content-Length', 0)) > 1024 ** 2 * 8:
                        image = None
                    else:
                        image = await resp.read()
            except (Exception, *CONNECTION_ERRORS):  # Catch bare Exception to be safe
                await self._send_error(f'I failed to download your image, please try again <@!{user_id}>!', channel_id)
                return

            if image is None:
                await self._send_error(
                    f'Your image is above 8MiB large, please use smaller images <@!{user_id}>!', channel_id
                )
                return

            try:
                result = convert_image(image, data['modifier'], data['method'], data['variation'])
            except RuntimeError as e:
                await self._send_error(f'<@!{user_id}> I failed to convert your image: **{e}**', channel_id)
                return
            except Exception as e:
                await self._send_error(f'<@!{user_id}> I failed to convert your image.', channel_id)
                traceback.print_exc()
                return

            try:
                msg = f'Here is your image <@!{user_id}>!'
                await self.http.send_files(channel_id, content=msg, files=(result,))
            except discord.HTTPException:
                await self._send_error(
                    f'I couldn\'t upload your image to Discord, it may be too big <@!{user_id}>!', channel_id
                )

            try:
                await self.http.remove_reaction(message_id, channel_id, self.config['queue_emoji'], self._bot_user_id)
            except discord.HTTPException:
                pass

        async def check():
            try:
                image = await self.http.get_from_cdn(data['url'])
            except discord.HTTPException:
                await self._send_error(f'I failed to download your image, please try again <@!{user_id}>!', channel_id)
                return

            if len(image) >= 8388608 * 2:
                await self._send_error(
                    f'Your image is above 16MiB large, please use smaller images <@!{user_id}>!', channel_id
                )
                return

            try:
                result = check_image(image, data['modifier'], data['method'])
            except RuntimeError as e:
                await self._send_error(f'<@!{user_id}> I failed to check your image: **{e}**', channel_id)
                return
            except Exception as e:
                await self._send_error(f'<@!{user_id}> I failed to check your image.', channel_id)
                traceback.print_exc()
                return

            try:
                description = ""
                for i in range(4):
                    description += f"{result['colors'][i]['name']}: {result['colors'][i]['ratio']}%\n"
                passed = result['passed']
                if passed and data['variation'] == 'avatar':
                    if data['modifier'] == 'light':
                        await self.http.remove_role(guild_id, user_id, self.config["guilds"][str(guild_id)]['pending_blurple_light_role'])
                        await self.http.add_role(guild_id, user_id, self.config["guilds"][str(guild_id)]['blurple_light_role'])
                    else:
                        await self.http.remove_role(guild_id, user_id, self.config["guilds"][str(guild_id)]['pending_blurple_dark_role'])
                        await self.http.add_role(guild_id, user_id, self.config["guilds"][str(guild_id)]['blurple_dark_role'])
                    description += "Status: **Passed** (Blurple Team Role Added)"
                elif passed:
                    description += "Status: **Passed**"
                else:
                    description += "Status: **Failed**"
                embed = discord.Embed(colour=discord.Colour(0x7289da),
                                      description=description)
                embed.set_image(url=data['url'])
                embed.set_author(name="Blurple Checker")
                embed.set_footer(text=f"Blurplefier | {data['author']}",
                                 icon_url=self.config['footer_thumbnail_url'])
                await self.http.send_message(channel_id, content=None, embed=embed.to_dict())
            except discord.HTTPException:
                await self._send_error(
                    f'I couldn\'t upload your image to Discord, it may be too big <@!{user_id}>!', channel_id
                )

            try:
                await self.http.remove_reaction(message_id, channel_id, self.config['queue_emoji'], self._bot_user_id)
            except discord.HTTPException:
                pass

        if data['method'] == 'check':
            await check()
        else:
            await blurplefy()

    async def _send_error(self, message, channel_id):
        try:
            await self.http.send_message(channel_id, message)
        except discord.HTTPException:
            pass
