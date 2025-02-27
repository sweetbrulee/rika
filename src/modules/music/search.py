import discord
import api


async def get_list(ctx: discord.AutocompleteContext):
    r = await api.get_search_list(
        ctx.value,
        str(ctx.interaction.user.id),
        str(
            ctx.interaction.guild_id
            if ctx.interaction.guild_id is not None
            else f"dm:{ctx.interaction.user.id}"
        ),
    )  #! Actually it is insecure, you should use a session token inside auth header instead
    search_list = r["data"]

    return [
        discord.OptionChoice(
            f"{'⟲ ' if i["is_history_data"] else ''}{i["name"]}",
            f'{i["url"] if len(i["url"]) <= 100 else i["name"]}',
        )
        for i in search_list
    ]


async def save_new_playable_history(
    ctx: discord.ApplicationContext, name: str, url: str
):
    await api.save_new_playable_history(
        str(ctx.interaction.user.id),
        str(
            ctx.interaction.guild_id
            if ctx.interaction.guild_id is not None
            else f"dm:{ctx.interaction.user.id}"
        ),
        name,
        url,
    )
