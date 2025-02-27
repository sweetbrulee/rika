import re
import datetime
from backend.db.connect import db_async

__all__ = [
    "update_playable_history",
    "read_playable_history",
]

MAX_PLAYABLE_HISTORY_PER_USER_STORAGE_NUM = 200


async def update_playable_history(
    user_id: str,
    guild_id: str,
    playable_name: str,
    original_url: str,
):

    await db_async["music"].update_one(
        {"user": user_id, "guild": guild_id, "name": playable_name},
        {
            "$set": {
                "url": original_url,
                "create_time": datetime.datetime.now(),
            }
        },
        upsert=True,
    )

    # cleanup old records (only user's records (which may across multiple guilds))
    # Keep maximum MAX_PLAYABLE_HISTORY_PER_USER_STORAGE_NUM records
    cursor = db_async["music"].aggregate(
        [
            {"$match": {"user": user_id}},
            {"$sort": {"create_time": -1}},
            {"$skip": MAX_PLAYABLE_HISTORY_PER_USER_STORAGE_NUM},
            {"$project": {"_id": 1}},
        ]
    )

    # 收集需要删除的文档的 _id
    ids_to_delete = [doc["_id"] async for doc in cursor]

    # 删除旧数据
    if ids_to_delete:
        await db_async["music"].delete_many({"_id": {"$in": ids_to_delete}})

    # 兼容旧版本数据，将 没有 field: user 的数据设置为 user = user_id
    # 过段时间后，可以考虑删除下面这段代码
    await db_async["music"].update_many(
        {"user": {"$exists": False}, "guild": guild_id},
        {"$set": {"user": user_id}},
    )


def _escape_regex(word):
    return re.escape(word)


def read_playable_history(user_id: str, guild_id: str, *, keywords: str, limit: int):
    # Hybrid mode, mix both user and guild history data, and group by playable name (distinct)

    # Compile regex

    # 拆分输入字符串 (\s+ 方法)
    words = re.split(r"\s+", keywords.strip())

    # 拆分输入字符串 (空格方法)
    # words = re.split(r" ", keywords.strip())

    # 转义特殊字符
    words = list(map(_escape_regex, words))

    # 构建正则表达式模式
    # pattern = ".*".join(words)

    # 构建一个匹配任意单词顺序的正则表达式 (performance may be worse)
    patterns = [f"(?=.*{word})" for word in words]
    pattern = "".join(patterns)

    # 编译正则表达式
    # regex = re.compile(pattern, re.IGNORECASE)

    return db_async["music"].aggregate(
        [
            {
                "$match": {
                    "$or": [{"user": user_id}, {"guild": guild_id}],
                    "name": {
                        "$regex": pattern,
                        "$options": "i",
                    },  # Case-insensitive regex match
                }
            },
            {"$sort": {"create_time": -1}},
            {
                "$group": {
                    "_id": "$name",
                    "doc": {"$first": "$$ROOT"},
                }
            },
            {"$replaceRoot": {"newRoot": "$doc"}},
            {"$sort": {"create_time": -1}},
            {"$limit": limit},
        ]
    )
