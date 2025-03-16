import discord
from discord.ext import commands
import os

# 從環境變數獲取機器人 Token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 設定 Intents，需啟用 message_content、guilds 與 dm_messages
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.dm_messages = True

bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

PASSWORD = "meng1212"  # 設定密碼

@bot.event
async def on_ready():
    print(f'✅ 機器人 {bot.user} 已上線！')
    print(f'🔹 目前加入了 {len(bot.guilds)} 個伺服器')
    for guild in bot.guilds:
        print(f'🔸 伺服器名稱: {guild.name} | ID: {guild.id}')

# 以檔案名稱作為指令名稱（不含副檔名）
command_name = os.path.splitext(os.path.basename(__file__))[0]

@bot.command(name=command_name)
async def command_func(ctx, input_password: str = None):
    """
    指令名稱與檔案名稱相同
    使用範例：>檔案名稱 meng1212
    驗證密碼正確後，回覆機器人加入的伺服器與與機器人私聊過的用戶
    """
    # 驗證密碼
    if input_password != PASSWORD:
        await ctx.send("❌ 密碼錯誤！請重新輸入正確的密碼。")
        return

    # 取得機器人加入的伺服器列表
    guild_list = "\n".join([f"🔹 {guild.name} (ID: {guild.id})" for guild in bot.guilds])
    
    # 取得機器人已知的私聊頻道 (DM Channels) 中的對象
    dm_users = []
    for channel in bot.private_channels:
        if isinstance(channel, discord.DMChannel) and channel.recipient:
            user = channel.recipient
            dm_users.append(f"🔸 {user.name}#{user.discriminator} (ID: {user.id})")
    dm_list = "\n".join(dm_users) if dm_users else "無私聊記錄"

    # 直接在當前頻道回覆結果
    response = (
        f"✅ **密碼驗證成功！**\n\n"
        f"🔹 **機器人目前加入的伺服器**：\n{guild_list}\n\n"
        f"📩 **曾與機器人私聊的用戶**：\n{dm_list}"
    )
    await ctx.send(response)

bot.run(TOKEN)
