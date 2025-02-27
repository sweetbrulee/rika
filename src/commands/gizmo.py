import discord
import sys
import requests
import psutil
from datetime import datetime
from discord import slash_command, option
from discord.ext import commands
from discord.ui import View, Button
from utils import TW
from modules.prepare_env import client, db_sync
from modules.hentai import send_hentai_message
from messages import end_support


class HentaiTermsView(View):
    @discord.ui.button(label="同意", style=discord.ButtonStyle.green)
    async def accept_callback(self, button: Button, interaction: discord.Interaction):
        # Tag user in db
        callers = db_sync["caller"]
        callers.update_one(
            {"_id": str(interaction.user.id)},
            {"$set": {"hentai_usage": True}},
            upsert=True,
        )
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="拒絕", style=discord.ButtonStyle.red)
    async def decline_callback(self, button: Button, interaction: discord.Interaction):
        # Tag user in db
        callers = db_sync["caller"]
        callers.update_one(
            {"_id": str(interaction.user.id)},
            {"$set": {"hentai_usage": False}},
            upsert=True,
        )
        await interaction.response.edit_message(view=self)


class Gizmo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_hentai_allowed(self, ctx):
        callers = db_sync["caller"]
        results = callers.find(
            {"_id": str(ctx.author.id), "hentai_usage": {"$exists": True}}
        )
        for result in results:
            if result["hentai_usage"]:
                return True  # Allow to use hentai

        # No results or not allowed to use hentai
        embed = discord.Embed(
            title="指令使用須知",
            description="""**如果您想使用hentai指令，以下是您必須遵守的規定：**\n"""
            """- 您不得使用此指令對任意伺服器發送垃圾內容，以及攻擊類型的訊息。\n"""
            """- 您必須在限制級頻道中使用此指令。\n"""
            """- 您不應該、也不允許使用此指令傳送違反**[Discord社群準則](https://discord.com/guidelines)**的內容；如果發生，我們將不承擔任何責任。\n"""
            """\n如果您都同意上述內容，請按下**同意**，您就可以使用啦q(≧▽≦q)\n""",
        )

        await ctx.respond(embed=embed, view=HentaiTermsView())
        return False

    @slash_command(name="hentai", name_localizations=TW("發本本"))
    @option(
        name="numbers",
        input_type=str,
        name_localizations=TW("車號"),
        description_localizations=TW("多個車號使用空格分隔"),
    )
    async def hentai(self, ctx: discord.ApplicationContext, numbers=None):
        await ctx.defer()
        if not await self.is_hentai_allowed(ctx):
            return
        if not ctx.channel.is_nsfw():
            return await ctx.respond(
                embed=discord.Embed(title="❌ | 必須在限制級頻道裡發送指令！")
            )

        if not numbers:
            # Random select
            redirect = (
                requests.Session()
                .head("https://nhentai.net/random/")
                .headers["Location"]
            )
            redirect = redirect[3:-1]
            try:
                return await send_hentai_message(
                    ctx, f"https://nhentai.net/g/{redirect}/"
                )
            except:
                raise commands.CommandError("發生錯誤！請稍後再試。")

        number_list = numbers.split()

        for number in number_list:
            try:
                secret = int(number)
            except Exception as e:
                await ctx.respond(
                    embed=discord.Embed(title=f'❌ | "{number}"不是一個正確的車號！')
                )
                print(e)
                continue

            await send_hentai_message(ctx, f"https://nhentai.net/g/{secret}/")

    async def ping(self, ctx):
        latency_ms = round(self.bot.latency * 1000)
        if latency_ms <= 150:
            title = "連線品質良好"
            color = discord.Colour.green()
        elif latency_ms <= 250:
            title = "延遲較大"
            color = discord.Colour.orange()
        elif latency_ms <= 350:
            title = "中度延遲"
            color = discord.Colour.dark_orange()
        elif latency_ms <= 1000:
            title = "高度延遲"
            color = discord.Colour.brand_red()
        else:
            title = "極度延遲"
            color = discord.Colour.dark_red()

        info = f"{title} " + "`%s`" % f"{latency_ms}ms"
        return info, color

    @slash_command(name="info", name_localizations=TW("機器人資訊"))
    async def info(self, ctx: discord.ApplicationContext):
        bot = self.bot

        (ping_info, ping_color) = await self.ping(ctx)

        embed = discord.Embed(
            description=f"""- **伺服器數量**：`{len(bot.guilds)}`\n\n"""
            f"""- **CPU**：`{psutil.cpu_percent()}%`\n"""
            f"""- **RAM**：`{psutil.virtual_memory()[2]}%`\n"""
            f"""- **PING**：{ping_info}""",
            color=ping_color,
        )
        embed.set_author(
            name=bot.user.display_name, icon_url=bot.user.display_avatar._url
        )
        embed.set_footer(
            text=f"Pycord版本：{discord.__version__}\n\nPython版本：{sys.version}"
        )

        await ctx.respond(embed=embed, ephemeral=True)


@client.command(
    name="end_support_info",
)
async def end_support_info_command(ctx: discord.ApplicationContext):
    await ctx.respond(embed=end_support.create_embed(), ephemeral=True)


def boot_elapsed_str():
    boot_elapsed = datetime.now() - datetime.fromtimestamp(psutil.boot_time())

    boot_days = boot_elapsed.days
    if boot_days:
        return f"`{boot_days}天前`"

    boot_hrs = boot_elapsed.seconds // 3600
    if boot_hrs:
        return f"`{boot_hrs}小時前`"

    boot_mins = boot_elapsed.seconds // 60
    return f"`{boot_mins}分鐘前`"


def setup(bot):
    bot.add_cog(Gizmo(bot))
