import asyncio
from typing import NamedTuple

import yt_dlp
from backend import crud
from backend.utils import dev_mode

# VIEW means visible view

# Hybrid history + yt search
# Hybrid mode mix both user and guild history data,
# and group by playable name (distinct)
MAX_PLAYABLE_VIEW_NUM = 10

# Use it if you have both hybrid history and yt search data.
# The yt search dynamic view num will correspondingly shrink to
# MAX_PLAYABLE_VIEW_NUM - min(playable_history_matched_num, MAX_PLAYABLE_PARTIAL_HISTORY_VIEW_NUM)
# the playable_history_matched_num will be dynamically adjusted based on the DB matching result
MAX_PLAYABLE_PARTIAL_HISTORY_VIEW_NUM = 5


def create_ydl_search_engine():
    ydl = yt_dlp.YoutubeDL(
        {
            "quiet": True,  # Quiet mode to reduce output
            "extract_flat": True,  # Extract video information only, without downloading
            "skip_download": True,  # Skip the download
            "max_downloads": 10,  # Limit the maximum number of queries to 10
        }
    )
    return ydl


ydl_search_engine = create_ydl_search_engine()

_debounce_tasks: dict[str, asyncio.Task] = {}


class PlayableDataTuple(NamedTuple):
    name: str
    url: str
    is_history_data: bool = False


async def _fetch_playable_history(value: str, user_id: str, guild_id: str):
    # playable history
    cursor = crud.read_playable_history(
        user_id,
        guild_id,
        keywords=value,
        limit=MAX_PLAYABLE_VIEW_NUM,
    )

    return [
        PlayableDataTuple(i["name"], i["url"], is_history_data=True)
        async for i in cursor
    ]


async def _fetch_yt_search(value: str):
    # Search from youtube

    # Search keyword
    query = f"ytsearch{str(MAX_PLAYABLE_VIEW_NUM)}:{value}"

    with ydl_search_engine as ydl:
        info = ydl.extract_info(query, download=False)

    return [
        PlayableDataTuple(entry["title"], entry["url"]) for entry in info["entries"]
    ]


async def _fetch(
    value: str,
    user_id: str | None,
    guild_id: str | None,
    *,
    only_playable_history: bool = False,
    only_yt_search: bool = False,
):
    if only_playable_history and only_yt_search:
        raise ValueError(
            "``only_playable_history`` and ``only_yt_search`` cannot be both True"
        )

    async def empty_coroutine():
        return []

    coros = [
        (
            _fetch_playable_history(value, user_id, guild_id)
            if not only_yt_search and user_id is not None and guild_id is not None
            else empty_coroutine()
        ),
        (_fetch_yt_search(value) if not only_playable_history else empty_coroutine()),
    ]
    gathered = asyncio.gather(*coros)
    gathered.add_done_callback(lambda _: _debounce_tasks.pop(user_id, None))
    _debounce_tasks[user_id] = gathered
    return await gathered


async def get_list(value: str, user_id: str | None, guild_id: str | None):

    if dev_mode():
        print(f"<------- {value} ------->")

    if user_id is not None and (task := _debounce_tasks.get(user_id, None)) is not None:
        try:
            task.cancel("Debounced")
        except asyncio.CancelledError:
            print("Task was cancelled")

    if value is None or value == "":
        history_list, _ = await _fetch(
            value, user_id, guild_id, only_playable_history=True
        )
        _list = history_list
    else:
        history_list, yt_search_list = await _fetch(value, user_id, guild_id)
        history_partial_size = min(
            len(history_list), MAX_PLAYABLE_PARTIAL_HISTORY_VIEW_NUM
        )
        _list: list[PlayableDataTuple] = (
            history_list[:history_partial_size]
            + yt_search_list[: MAX_PLAYABLE_VIEW_NUM - history_partial_size]
        )

    if dev_mode():
        print([i.name for i in _list])

    return _list


async def save_new_playable_history(user_id: str, guild_id: str, name: str, url: str):
    await crud.update_playable_history(user_id, guild_id, name, url)
