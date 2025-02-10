import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from dotenv import load_dotenv  # 修正：確保 dotenv 被導入

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 更新內容
update_content = """
### 最新更新內容：\n
1. 敵人 Boss 資訊由【ヘ拉拉ヘ】大大精心編寫，讚歎拉拉～！\n
2. 主線 Boss 排列全新上陣，前後次序調整得超級有趣！另外還新增了【其他王 Different Boss】的選單分類！\n
3. 指令只能自己使用，不會再出現選單被人NTR的雜魚事件（捂嘴笑\n
4. 新增【>invite】或【>邀請】指令，讓您能輕鬆召喚女僕月醬進入群組，一起歡樂遊戲～\n
5. 新增【>mat】或【>素材】指令，體驗素材刷點的便捷與樂趣，蔥鴨～\n\n
"""

# 設定機器人
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)

@bot.event
async def on_ready():
    print(f"女僕月醬 現在已上線！({bot.user}) 喵～")

# 更新日誌指令
@bot.command(aliases=["更新"])
async def maidmoon_update(ctx):
<<<<<<< HEAD
=======
    # 女僕月醬以最愛主人的可愛語氣報告最新更新日誌
>>>>>>> 16722772134404663ed4b2d9e95a64a008614b2b
    cute_intro = "蕪湖～ 主人，最愛您的女僕月醬來為您獻上最新的更新日誌囉！請細細品嚐這份精心準備的資訊叭～"
    embed = discord.Embed(
        title="【女僕月醬】更新日誌",
        description=f"{cute_intro}\n{update_content}",
        color=0xFFB6C1  # 粉色代表可愛
    )
    await ctx.send(embed=embed)

bot.run(TOKEN)
