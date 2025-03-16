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

# 用字典記錄曾與機器人私聊過的使用者 (Key 為使用者 ID)
dm_users = {}

@bot.event
async def on_ready():
    print(f'✅ 機器人 {bot.user} 已上線！')
    print(f'🔹 目前加入了 {len(bot.guilds)} 個伺服器')
    for guild in bot.guilds:
        print(f'🔸 伺服器名稱: {guild.name} | ID: {guild.id}')

@bot.event
async def on_message(message):
    # 如果訊息是在私聊頻道中，且不是機器人本身，則記錄該使用者
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        dm_users[message.author.id] = message.author
    await bot.process_commands(message)

# 以檔案名稱（不含副檔名）作為指令名稱
command_name = os.path.splitext(os.path.basename(__file__))[0]

@bot.command(name=command_name)
async def command_func(ctx, input_password: str = None):
    """
    指令名稱與檔案名稱相同
    使用方式：>檔案名稱 meng1212
    密碼驗證正確後，回覆機器人加入的伺服器與曾與機器人私聊過的個人使用者名稱
    """
    # 驗證密碼
    if input_password != PASSWORD:
        await ctx.send("❌ 密碼錯誤！請重新輸入正確的密碼。")
        return

    # 取得機器人加入的伺服器列表
    guild_list = "\n".join([f"🔹 {guild.name} (ID: {guild.id})" for guild in bot.guilds])
    
    # 從記錄中取得曾與機器人私聊的 Individual Users
    dm_list = "\n".join([f"🔸 {user.name}#{user.discriminator} (ID: {user.id})" for user in dm_users.values()])
    if not dm_list:
        dm_list = "沒有記錄到 Individual Users（請先私訊機器人一次）"
    
    response = (
        f"✅ **密碼驗證成功！**\n\n"
        f"🔹 **機器人目前加入的伺服器**：\n{guild_list}\n\n"
        f"📩 **Individual Users**：\n{dm_list}"
    )
    await ctx.send(response)

bot.run(TOKEN)
