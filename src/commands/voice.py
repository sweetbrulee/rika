import asyncio
import discord
from discord.ext import commands
from modules.prepare_env import client

from utils import TW, error_handler


class VoiceChannelSelectionView(discord.ui.View):
    def __init__(
        self, ctx: discord.ApplicationContext, cond: asyncio.Condition, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.ctx = ctx
        self.cond = cond
        self.selected_channel: discord.VoiceChannel | discord.StageChannel = None

    @discord.ui.select(
        placeholder="請選擇一個語音頻道",
        select_type=discord.ComponentType.channel_select,
        channel_types=[discord.ChannelType.voice, discord.ChannelType.stage_voice],
    )
    async def select_channel_callback(
        self, select: discord.ui.Select, interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)

        self.selected_channel = select.values[0]

        async with self.cond:
            self.cond.notify_all()


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class VoiceHelper:

    @staticmethod
    async def prepare_channel(ctx: discord.ApplicationContext):

        # Check if the ctx.author is in a voice channel
        if ctx.author.voice is not None:
            return ctx.author.voice.channel

        # If the bot has already been in a voice channel
        if ctx.voice_client is not None:
            return ctx.voice_client.channel

        return await VoiceHelper._wait_for_voice_channel_selection_finished(
            ctx, asyncio.Condition()
        )

    @staticmethod
    async def _wait_for_voice_channel_selection_finished(
        ctx: discord.ApplicationContext, cond: asyncio.Condition
    ):
        async with cond:
            view = await VoiceHelper._send_voice_channel_selection_view(ctx, cond)
            await cond.wait()
            return view.selected_channel

    @staticmethod
    async def _send_voice_channel_selection_view(
        ctx: discord.ApplicationContext, cond: asyncio.Condition
    ):
        view = VoiceChannelSelectionView(ctx, cond)
        await ctx.interaction.respond(view=view, ephemeral=True)
        return view

    @classmethod
    async def connect(
        cls,
        ctx: discord.ApplicationContext,
        channel: discord.VoiceChannel | discord.StageChannel,
    ):
        if ctx.voice_client is None:
            await channel.connect()
        await ctx.author.guild.change_voice_state(channel=channel, self_deaf=True)

    @staticmethod
    async def disconnect(voice_client: discord.VoiceClient):
        # Try to call voice_client._disconnect_raw()
        await VoiceHelper._disconnect_raw(voice_client)

    @staticmethod
    async def disconnect_with_message_send(
        ctx: discord.ApplicationContext,
        inprivate_bool: bool,
    ):
        # Try to call voice_client._disconnect_raw()
        voice = ctx.voice_client
        if await VoiceHelper._disconnect_raw(voice) is False:
            return
        embed = discord.Embed(title="👋 | 我先走囉~")
        await ctx.interaction.followup.send(embed=embed, ephemeral=inprivate_bool)

    @staticmethod
    async def _disconnect_raw(voice_client: discord.VoiceClient | None):
        try:
            if voice_client is None or not voice_client.is_connected():
                return False
            voice_client.stop()
            voice_client.cleanup()
            await voice_client.disconnect()
            return True
        except Exception as e:
            print(f"VoiceHelper._disconnect_raw() failed. {e}")
            return False


@client.command(
    name="join",
    name_localizations=TW("加入"),
    description_localizations=TW("加入語音頻道"),
)
async def join(ctx: discord.ApplicationContext):
    try:
        await VoiceHelper.connect(ctx, await VoiceHelper.prepare_channel(ctx))
    except Exception as e:
        await error_handler(ctx, e, ephemeral=True)


def setup(bot):
    bot.add_cog(Voice(bot))
