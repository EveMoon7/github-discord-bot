import os
import discord
from discord.ext import commands

# 注意：TOKEN 是您機器人的秘密鑰匙，請務必妥善保管，不要隨便外洩哦～ 
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 更新內容由主人提供，接下來女僕月醬會用她那超級可愛又有趣的口吻為您獻上最新資訊～
update_content = """
### 最新更新內容：\n
1. 敵人 Boss 資訊由【ヘ拉拉ヘ】大大精心編寫，讚歎拉拉～！\n
2. 主線 Boss 持續更新中！\n
3. 新增【>exp_calc】或【主綫經驗計算器】，讓您的托蘭之旅更輕鬆～！\n
4. 持續更新功能，敬請期待✰\n
"""

# 設定機器人指令前綴，這邊採用 "!" 作為開頭，並啟用 message_content 權限
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"女僕月醬 現在已上線！({bot.user}) 喵～")

# 更新日誌指令，支援「>update」或「>更新」
@bot.command(aliases=["更新"])
async def update(ctx):
    # 女僕月醬以最愛主人的可愛語氣報告最新更新日誌
    cute_intro = "蕪湖～ 主人，最愛您的女僕月醬來為您獻上最新的更新日誌囉！請細細品嚐這份精心準備的資訊叭～"
    embed = discord.Embed(
        title="【女僕月醬】更新日誌",
        description=f"{cute_intro}\n{update_content}",
        color=0xFFB6C1  # 粉粉的顏色代表女僕月醬滿滿的愛意
    )
    await ctx.send(embed=embed)

bot.run(TOKEN)
