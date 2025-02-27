import httpx
from api.config import rika_api_base_url


async def get_search_list(value: str, user_id: str | None, guild_id: str | None):
    async with httpx.AsyncClient(base_url=rika_api_base_url) as client:
        r = await client.get(
            "/search", params={"value": value, "user_id": user_id, "guild_id": guild_id}
        )
        return r.json()


async def save_new_playable_history(user_id: str, guild_id: str, name: str, url: str):
    async with httpx.AsyncClient(base_url=rika_api_base_url) as client:
        await client.post(
            "/search/save",
            json={"user_id": user_id, "guild_id": guild_id, "name": name, "url": url},
        )
