import discord
from discord.ext import commands
import os
import pytz  # 載入 pytz 模組以支援時區轉換

# 從環境變數中讀取機器人 Token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

PASSWORD = "meng1212"  # 設定密碼

# 設定台灣時區
taipei_tz = pytz.timezone("Asia/Taipei")

@bot.event
async def on_ready():
    print(f'✅ 機器人 {bot.user} 已上線！')
    print(f'🔹 目前加入了 {len(bot.guilds)} 個伺服器')
    for guild in bot.guilds:
        print(f'🔸 伺服器名稱: {guild.name} | ID: {guild.id}')

# 以檔案名稱（不含副檔名）作為指令名稱
command_name = os.path.splitext(os.path.basename(__file__))[0]

@bot.command(name=command_name)
async def command_func(ctx, input_password: str = None):
    """
    指令名稱與檔案名稱相同
    使用方式：>檔案名稱 meng1212
    驗證密碼正確後，回覆機器人加入的伺服器及其加入時間（以台灣時區顯示，並按加入時間排序）。
    """
    # 驗證密碼
    if input_password != PASSWORD:
        await ctx.send("❌ 密碼錯誤！請重新輸入正確的密碼。")
        return

    # 根據機器人加入伺服器的時間排序
    guilds_sorted = sorted(bot.guilds, key=lambda g: g.me.joined_at or 0)

    # 組裝伺服器列表與加入時間（轉換成台灣時區）
    guild_lines = []
    for guild in guilds_sorted:
        joined_at = guild.me.joined_at
        if joined_at:
            # 轉換成台灣時區
            joined_at_taipei = joined_at.astimezone(taipei_tz)
            joined_str = joined_at_taipei.strftime("%Y-%m-%d %H:%M:%S")
        else:
            joined_str = "N/A"
        guild_lines.append(f"🔹 {guild.name} (ID: {guild.id}) - 加入時間：{joined_str}")
    guild_list = "\n".join(guild_lines) if guild_lines else "無伺服器記錄"

    # 回覆結果至當前頻道
    response = (
        f"✅ **密碼驗證成功！**\n\n"
        f"🔹 **機器人目前加入的伺服器（按加入時間排序）**：\n{guild_list}"
    )
    await ctx.send(response)

bot.run(TOKEN)
