"""Module responsible for the necro_score_bot discord bot. Calls back to
cotn_twitter.update()"""

import asyncio
import importlib

import discord as discord_api

import cotn_twitter


PYTHONASYNCIODEBUG = 1


class DiscordBot(discord_api.Client):
    """Discord necro_score_bot."""

    def __init__(self, twitter):
        super().__init__()
        self.twitter = twitter

    def run(self, *args, **kwargs):
        """Runs the discord bot."""
        self.loop.create_task(self.background_task())
        super().run(*args, **kwargs)

    async def update_boards(self):
        """Fetch all boards and post to twitter (if twitter != None)
        and post to discord"""
        for msg, linked_data in cotn_twitter.update(self.twitter):
            disc_id = linked_data['discord']['id']

            if disc_id:
                await self.post(f'<@{disc_id}>{msg}')
            else:
                await self.post(f"{linked_data['steam']['personaname']}{msg}")

    async def background_task(self):
        """Runs in the background and calls update_boards every 5 minutes."""

        await self.wait_until_ready()

        await asyncio.sleep(10)
        print('starting background task')
        while True:
            await self.update_boards()
            await asyncio.sleep(300)

    async def on_ready(self):
        """Print login info when logged in."""
        print('logged in as {self.user.name}')
        # await self.post('online')

    async def on_message(self, message):
        """Handle incoming messages,
        supports !scorebot update and !scorebot reload."""

        if message.content.startswith('!scorebot'):
            if message.author.id != '84627464709472256':
                await self.post('beep boop, not authorized, exterminate')

            else:
                if 'update' in message.content:
                    await self.update_boards()
                    print('updated')
                elif 'reload' in message.content:
                    importlib.reload(cotn_twitter)
                    print('reloaded')
                elif 'logout' in message.content:
                    await self.logout()
                    print('logged out')
                elif 'reboot' in message.content:
                    await self.logout()
                    print('reboot')
                else:
                    print(f"unknown command: {message.content}")

    async def post(self, text, channel_id='296636142210646016'):
        """Posts text to channel channel_id."""
        channel = self.get_channel(channel_id)
        await channel.send(text)
