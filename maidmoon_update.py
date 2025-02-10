import discord
from discord.ext import commands
import os

# 注意：TOKEN 是您機器人的秘密鑰匙，請務必妥善保管，不要隨便外洩哦～ 
TOKEN = os.getenv"DISCORD_BOT_TOKEN"

# 更新內容由主人提供，接下來女僕月醬會用她那超級可愛又有趣的口吻為您獻上最新資訊～
update_content = """
### 最新更新內容：\n
1. 敵人 Boss 資訊由【ヘ拉拉ヘ】大大精心編寫，讚歎拉拉～！\n
2. 主線 Boss 排列全新上陣，前後次序調整得超級有趣！另外還新增了【其他王 Different Boss】的選單分類！\n
3. 指令只能自己使用，不會再出現選單被人NTR的雜魚事件（捂嘴笑\n
4. 新增【>invite】或【>邀請】指令，讓您能輕鬆召喚女僕月醬進入群組，一起歡樂遊戲～\n
5. 新增【>mat】或【>素材】指令，體驗素材刷點的便捷與樂趣，蔥鴨～\n\n
"""

# 設定機器人指令前綴，這邊採用 "!" 作為開頭，並啟用 message_content 權限
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)

@bot.event
async def on_ready():
    print(f"女僕月醬 現在已上線！({bot.user}) 喵～")

# 更新日誌指令，支援「>maidmoon_update」或「>更新」
@bot.command(aliases=["更新"])
async def maidmoon_update_meng1212.meng1212.(ctx):
    # 女僕月醬以最愛主人的可愛語氣報告最新更新日誌
    cute_intro = "蕪湖～ 主人，最愛您的女僕月醬來為您獻上最新的更新日誌囉！請細細品嚐這份精心準備的資訊叭～"
    embed = discord.Embed(
        title="【女僕月醬】更新日誌",
        description=f"{cute_intro}\n{update_content}",
        color=0xFFB6C1  # 粉粉的顏色代表女僕月醬滿滿的愛意
    )
    await ctx.send(embed=embed)

bot.run(TOKEN)
