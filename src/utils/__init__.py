import os
from functools import cache
import traceback

import discord


def TW(text):
    return {"zh-TW": text}


@cache
def dev_mode() -> bool:
    return os.getenv("RIKA_DISCORD_BOT_TYPE") == "staged"


async def error_handler(ctx: discord.ApplicationContext, e: Exception, ephemeral: bool):
    full_error = traceback.format_exception(e) if dev_mode() else [str(e)]
    selected_options = "\n".join(
        [
            f"name: {item['name']}, type: *{item['type']}*, value: {item['value']}"
            for item in ctx.selected_options
        ]
    )
    await ctx.respond(
        embed=discord.Embed(
            title="好像發生了一些錯誤...",
            description=f"使用者：`{ctx.user}`\n命令：`{ctx.command.qualified_name}`\n參數：\n{selected_options}\n\n```{''.join(full_error)}```",
            color=discord.Color.dark_red(),
        ),
        ephemeral=ephemeral,
    )
    raise e
