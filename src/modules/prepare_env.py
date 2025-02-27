import asyncio
import discord
import os
import pymongo
from motor import motor_asyncio
from typing import override


cluster_async = motor_asyncio.AsyncIOMotorClient(
    os.getenv("RIKA_DISCORD_BOT_DB_STRING")
)
cluster_sync = pymongo.MongoClient(os.getenv("RIKA_DISCORD_BOT_DB_STRING"))

if os.getenv("RIKA_DISCORD_BOT_TYPE") == "production":
    db_sync = cluster_sync["main"]
    db_async = cluster_async["main"]
elif os.getenv("RIKA_DISCORD_BOT_TYPE") == "staged":
    db_sync = cluster_sync["test"]
    db_async = cluster_async["test"]


class Bot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @override
    async def on_application_command_auto_complete(
        self, interaction: discord.Interaction, command: discord.ApplicationCommand
    ) -> None:
        """This method overrides the default `discord.ApplicationCommandMixin.on_application_command_auto_complete` method."""

        async def callback() -> None:
            ctx = await self.get_autocomplete_context(interaction)
            ctx.command = command
            return await command.invoke_autocomplete_callback(ctx)

        autocomplete_task = self._bot.loop.create_task(callback())
        try:
            await self._bot.wait_for(
                "application_command_auto_complete",
                check=lambda i, c: c == command,
                timeout=3,
            )
        except asyncio.TimeoutError:
            return
        else:
            if not autocomplete_task.done():
                autocomplete_task.cancel()


client = Bot(
    intents=discord.Intents.all(),
    activity=discord.Game(name="💕"),
)
