from fastapi import FastAPI
from pydantic import BaseModel
from backend.services.search import get_list, save_new_playable_history

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello ASGI World! I'm Rika!"}


@app.get("/search")
async def search(value: str, user_id: str | None = None, guild_id: str | None = None):
    _list = await get_list(value, user_id, guild_id)
    return {
        "data": [
            {"name": i.name, "url": i.url, "is_history_data": i.is_history_data}
            for i in _list
        ]
    }


class SearchSave(BaseModel):
    user_id: str
    guild_id: str
    name: str
    url: str


@app.post("/search/save")
async def search_save(value: SearchSave):
    await save_new_playable_history(
        value.user_id, value.guild_id, value.name, value.url
    )
    return {"message": "OK"}
