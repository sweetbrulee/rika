import datetime
import discord
from zoneinfo import ZoneInfo
from commands.voice import VoiceHelper
from messages import end_support
from modules.prepare_env import client
from modules import scheduler
from utils.bulk import bulk_operation_members


@client.event
async def on_connect():
    if client.auto_sync_commands:
        await client.sync_commands()

    @scheduler.event(
        time=datetime.datetime(2025, 2, 28, 0, 0, tzinfo=ZoneInfo("Asia/Taipei")),
        client=client,
    )
    async def to_end_support(client: discord.Bot):
        await bulk_operation_members(
            client,
            lambda p: p.use_slash_commands,
            member_corofunc=lambda m: m.send(embed=end_support.create_embed()),
        )

    # Start the scheduler
    await scheduler.Scheduler.schedule()

    print(f"{client.user.name} connected.")


@client.event
async def on_voice_state_update(
    member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
):
    # To reduce the waste of compute resources, call custom disconnect method as a side effect when the bot get detected disconnected.
    # If no one is in the voice channel, disconnect it.

    if after.channel is not None or member != client.user:
        return

    return await VoiceHelper.disconnect(member.guild.voice_client)
