import discord
from discord.ext import commands
import os

# 從環境變數中讀取機器人 Token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.dm_messages = True  # 允許監聽私聊訊息
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

PASSWORD = "meng1212"  # 設定密碼

# 用字典記錄曾與機器人私聊過的使用者資訊，儲存 (使用者物件, 首次私聊時間)
dm_users = {}

@bot.event
async def on_ready():
    print(f'✅ 機器人 {bot.user} 已上線！')
    print(f'🔹 目前加入了 {len(bot.guilds)} 個伺服器')
    for guild in bot.guilds:
        print(f'🔸 伺服器名稱: {guild.name} | ID: {guild.id}')

@bot.event
async def on_message(message):
    # 若訊息是在私聊頻道且非機器人所發，則記錄使用者與首次私聊時間
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        if message.author.id not in dm_users:
            dm_users[message.author.id] = (message.author, message.created_at)
    await bot.process_commands(message)

# 以檔案名稱（不含副檔名）作為指令名稱
command_name = os.path.splitext(os.path.basename(__file__))[0]

@bot.command(name=command_name)
async def command_func(ctx, input_password: str = None):
    """
    指令名稱與檔案名稱相同
    使用方式：>檔案名稱 meng1212
    驗證密碼正確後，回覆機器人加入的伺服器與曾與機器人私聊過的個人使用者，
    並顯示各自的加入時間。
    """
    # 驗證密碼
    if input_password != PASSWORD:
        await ctx.send("❌ 密碼錯誤！請重新輸入正確的密碼。")
        return

    # 組裝機器人加入的伺服器列表與加入時間
    guild_lines = []
    for guild in bot.guilds:
        joined_at = guild.me.joined_at
        joined_str = joined_at.strftime("%Y-%m-%d %H:%M:%S") if joined_at else "N/A"
        guild_lines.append(f"🔹 {guild.name} (ID: {guild.id}) - 加入時間：{joined_str}")
    guild_list = "\n".join(guild_lines) if guild_lines else "無伺服器記錄"

    # 組裝曾與機器人私聊過的個人使用者列表與首次私聊時間
    dm_lines = []
    for user_id, (user, join_time) in dm_users.items():
        join_str = join_time.strftime("%Y-%m-%d %H:%M:%S")
        dm_lines.append(f"🔸 {user.name}#{user.discriminator} (ID: {user.id}) - 首次私聊時間：{join_str}")
    dm_list = "\n".join(dm_lines) if dm_lines else "無私聊記錄（請先私訊機器人一次）"

    # 組合回覆內容並直接在當前頻道發送
    response = (
        f"✅ **密碼驗證成功！**\n\n"
        f"🔹 **機器人目前加入的伺服器**：\n{guild_list}\n\n"
        f"📩 **個人使用者（私聊記錄）**：\n{dm_list}"
    )
    await ctx.send(response)

bot.run(TOKEN)
