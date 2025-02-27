from types import SimpleNamespace
import discord
from modules.music import search
from utils import TW, error_handler
from utils.commands import autocomplete
from discord.ext import commands
from modules.prepare_env import client


music_option = SimpleNamespace(
    search=discord.option(
        "search",
        input_type=discord.SlashCommandOptionType.string,
        name_localizations=TW("關鍵字"),
        description_localizations=TW("輸入要播放的音樂名稱或網址"),
        autocomplete=autocomplete(search.get_list),
    ),
    new_playable_title=discord.option(
        "new_playable_title",
        input_type=discord.SlashCommandOptionType.string,
        name_localizations=TW("音樂名稱"),
        description_localizations=TW("輸入要保存的音樂名稱"),
    ),
    new_playable_url=discord.option(
        "new_playable_url",
        input_type=discord.SlashCommandOptionType.string,
        name_localizations=TW("音樂網址"),
        description_localizations=TW("輸入要保存的音樂網址"),
    ),
)


class Music(commands.Cog):

    def __init__(self, bot: discord.Bot):
        self.bot = bot


@client.command(
    name="search",
    name_localizations=TW("搜尋"),
    description_localizations=TW("搜尋 YouTube 影片"),
)
@music_option.search
async def search_command(
    ctx: discord.ApplicationContext,
    search: str,
):
    try:
        await ctx.interaction.respond(search)
    except Exception as e:
        await error_handler(ctx, e, ephemeral=True)


@client.command(
    name="new",
    name_localizations=TW("新增"),
    description_localizations=TW("新增並保存音樂或影片，之後可以用搜尋指令查詢到"),
)
@music_option.new_playable_title
@music_option.new_playable_url
async def new_playable(
    ctx: discord.ApplicationContext,
    new_playable_title: str,
    new_playable_url: str,
):
    try:
        await search.save_new_playable_history(
            ctx,
            new_playable_title,
            new_playable_url,
        )
        await ctx.interaction.respond("新增成功！")
    except Exception as e:
        await error_handler(ctx, e, ephemeral=True)


def setup(bot):
    bot.add_cog(Music(bot))
