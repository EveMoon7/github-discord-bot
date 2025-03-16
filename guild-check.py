import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # 從環境變數獲取機器人 Token

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.dm_messages = True  # 允許機器人監聽私聊
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

PASSWORD = "meng1212"  # 設定密碼

@bot.event
async def on_ready():
    print(f'✅ 機器人 {bot.user} 已上線！')
    print(f'🔹 目前加入了 {len(bot.guilds)} 個伺服器')

    for guild in bot.guilds:
        print(f'🔸 伺服器名稱: {guild.name} | ID: {guild.id}')

@bot.command()
async def 指令(ctx, input_password: str = None):
    """使用 >指令 密碼 查詢機器人加入的伺服器 & 私聊過的用戶"""

    # 驗證密碼
    if input_password != PASSWORD:
        await ctx.send("❌ 密碼錯誤！請重新輸入正確的密碼。")
        return
    
    # 取得機器人加入的伺服器列表
    guild_list = "\n".join([f"🔹 {guild.name} (ID: {guild.id})" for guild in bot.guilds])
    
    # 取得機器人與誰私聊過（DM Channels）
    dm_users = []
    for user_id in bot._connection._private_channels:
        user = bot.get_user(user_id)
        if user:
            dm_users.append(f"🔸 {user.name}#{user.discriminator} (ID: {user.id})")
    
    dm_list = "\n".join(dm_users) if dm_users else "無私聊記錄"

    # 直接在當前服務器頻道回覆
    response = (
        f"✅ **密碼驗證成功！**\n\n"
        f"🔹 **機器人目前加入的伺服器**：\n{guild_list}\n\n"
        f"📩 **曾與機器人私聊的用戶**：\n{dm_list}"
    )

    await ctx.send(response)

bot.run(TOKEN)
