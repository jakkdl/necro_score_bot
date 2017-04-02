"""Module responsible for the necro_score_bot discord bot. Calls back to
cotn_twitter.update()"""

import asyncio
import imp

import cotn_twitter

import discord as discord_api

PYTHONASYNCIODEBUG = 1
__client__ = discord_api.Client()

class DiscordBot:
    """Discord necro_score_bot."""

    def __init__(self, token, twitter):
        self.token = token
        self.twitter = twitter

    async def update_boards(self):
        """Fetch all boards and post to twitter (if twitter != None)
        and post to discord"""
        for msg, linked_data in cotn_twitter.update(self.twitter):
            disc_id = linked_data['discord']['id']

            if disc_id:
                await self.post('<@{}>{}'.format(disc_id, msg))
            else:
                await self.post('{}{}'.format(linked_data['steam']['personaname'],
                                              msg))

    async def background_task(self):
        """Runs in the background and calls update_boards every 5 minutes."""

        await __client__.wait_until_ready()
        await asyncio.sleep(20)
        print('starting background task')
        while True:
            await self.update_boards()
            await asyncio.sleep(300)

    @__client__.event
    async def on_ready(self):
        """Print login info when logged in."""
        print('logged in as {}'.format(__client__.user.name))


    @__client__.event
    async def on_message(self, message):
        """Handle incoming messages,
        supports !scorebot update and !scorebot reload."""

        if message.content.startswith('!scorebot'):
            if message.author.id != '84627464709472256':
                await self.post('beep boop, not authorized, exterminate')

            else:
                if 'update' in message.content:
                    await self.update_boards()
                if 'reload' in message.content:
                    imp.reload(cotn_twitter)
                if 'logout' in message.content:
                    __client__.logout()

    async def post(self, text, channel_id='296636142210646016'):
        """Posts text to channel channel_id."""
        channel = __client__.get_channel(channel_id)
        await __client__.send_message(channel, text)

    def run(self,):
        """Runs the discord bot."""
        __client__.loop.create_task(self.background_task())
        __client__.run(self.token)
