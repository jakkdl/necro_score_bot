"""Module responsible for the necro_score_bot discord bot. Calls back to
cotn_twitter.update()"""

import asyncio
import importlib

import discord

import cotn_twitter
from nsb_config import options


PYTHONASYNCIODEBUG = 1


class DiscordBot(discord.Client):
    """Discord necro_score_bot."""

    def __init__(self) -> None:
        super().__init__()

    def run(self, *args, **kwargs) -> None:  # type: ignore
        """Runs the discord bot."""
        self.loop.create_task(self.background_task())
        super().run(*args, **kwargs)

    async def update_boards(self) -> None:
        """Fetch all boards and post to twitter (if twitter != None)
        and post to discord"""
        for msg in cotn_twitter.update():
            await self.post(msg)

    async def background_task(self) -> None:
        """Runs in the background and calls update_boards every 5 minutes."""

        await self.wait_until_ready()

        await asyncio.sleep(10)
        print("starting background task")
        while True:
            await self.update_boards()
            await asyncio.sleep(300)

    async def on_ready(self) -> None:
        """Print login info when logged in."""
        print(f"logged in as {self.user.name}")
        # await self.post('online')

    async def on_message(self, message: discord.Message) -> None:
        """Handle incoming messages,
        supports !scorebot update and !scorebot reload."""

        if message.content.startswith("!scorebot"):
            if message.author.id != 84627464709472256:
                await self.post("beep boop, not authorized, exterminate")

            else:
                if "update" in message.content:
                    await self.update_boards()
                    print("updated")
                elif "reload" in message.content:
                    importlib.reload(cotn_twitter)
                    print("reloaded")
                elif "logout" in message.content:
                    await self.logout()
                    print("logged out")
                elif "reboot" in message.content:
                    await self.logout()
                    print("reboot")
                else:
                    print(f"unknown command: {message.content}")

    async def post(self, text: str, channel_id: int = 296636142210646016) -> None:
        """Posts text to channel channel_id."""
        if not options["post_discord"]:
            print(f"Discord post: {text}")
            return

        channel = self.get_channel(channel_id)
        assert isinstance(channel, discord.TextChannel)
        await channel.send(text)
