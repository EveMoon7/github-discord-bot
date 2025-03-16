import discord
from discord.ext import commands
import os
import pytz
import os.path

# 從環境變數中讀取機器人 Token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 設定 Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

PASSWORD = "meng1212"  # 設定密碼

# 設定台灣時區
taipei_tz = pytz.timezone("Asia/Taipei")

# 允許使用此指令的使用者 ID 集合
allowed_ids = {636783046363709440, 611517726225203229, 523475814155681792}

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
    只有指定的使用者能使用此命令，且機器人僅會以私聊方式回覆結果。
    """
    # 檢查使用者是否在允許名單中
    if ctx.author.id not in allowed_ids:
        try:
            await ctx.author.send("你沒有使用此命令的權限。")
        except Exception:
            pass
        return

    # 驗證密碼
    if input_password != PASSWORD:
        try:
            await ctx.author.send("❌ 密碼錯誤！請重新輸入正確的密碼。")
        except Exception:
            pass
        return

    # 根據機器人加入伺服器的時間排序
    guilds_sorted = sorted(bot.guilds, key=lambda g: g.me.joined_at or 0)

    # 組裝伺服器列表（轉換為台灣時區）
    guild_lines = []
    for guild in guilds_sorted:
        joined_at = guild.me.joined_at
        if joined_at:
            joined_at_taipei = joined_at.astimezone(taipei_tz)
            joined_str = joined_at_taipei.strftime("%Y-%m-%d %H:%M:%S")
        else:
            joined_str = "N/A"
        guild_lines.append(f"🔹 {guild.name} (ID: {guild.id}) - 加入時間：{joined_str}")
    guild_list = "\n".join(guild_lines) if guild_lines else "無伺服器記錄"

    response = (
        f"✅ **密碼驗證成功！**\n\n"
        f"🔹 **機器人目前加入的伺服器（按加入時間排序）**：\n{guild_list}"
    )

    # 僅以私聊方式回覆
    try:
        await ctx.author.send(response)
    except Exception as e:
        print("無法發送 DM:", e)

bot.run(TOKEN)
