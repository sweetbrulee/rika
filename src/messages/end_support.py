import discord


def create_embed() -> discord.Embed:
    embed = discord.Embed(
        color=discord.Color.yellow(),
        title="Rika 以及 RikaAI 將於 2025 年 6 月 1 日停止服務",
        description="""
        使用者您好！感謝您在過去的幾年中對 Rika 以及 RikaAI 的支持。
        我們宣布，Rika 以及 RikaAI 將於 2025 年 6 月 1 日停止服務。
        我們將會在 2025 年 6 月 1 日之後陸續的關閉所有相關的伺服器，並且刪除所有的使用者資料。

        **幸運的是！** 
        我們現在已開放部分的 Rika 專案的原始碼，您可以在 [這裡](https://github.com/sweetbrulee/rika) 找到。
        如果您有興趣，您可以**自行架設**您自己的聊天機器人伺服器。

        您隨時可以使用 `/end_support_info` 指令重新查看這則訊息。
        """,
    )

    return embed
