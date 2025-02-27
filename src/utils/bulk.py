import asyncio
from typing import Callable, Coroutine
import discord


async def bulk_operation_members(
    client: discord.Bot,
    permissions_filter: Callable[[discord.Permissions], bool],
    *,
    member_corofunc: Callable[[discord.Member], Coroutine] | None = None,
    members_corofunc: Callable[[set[discord.Member]], Coroutine] | None = None,
):
    # Choose non-bot, user in their guilds, sendable members
    members: set[discord.Member] = set()

    for guild in client.guilds:
        for member in guild.members:
            if member.bot or not permissions_filter(member.guild_permissions):
                continue
            members.add(member)

    if callable(members_corofunc):
        await members_corofunc(members)
        return

    if not callable(member_corofunc):
        return

    coros = [member_corofunc(member) for member in members]
    await asyncio.gather(*coros)
