import discord
from discord.ext import commands
import os

# 從環境變數中讀取機器人 Token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PASSWORD = "meng1212"  # 設定密碼

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

# 定義密碼輸入的 Modal
class PasswordModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="請輸入密碼", timeout=300)
        self.add_item(discord.ui.InputText(label="密碼", placeholder="請輸入密碼"))

    async def callback(self, interaction: discord.Interaction):
        # 取得使用者輸入的密碼
        password_input = self.children[0].value
        
        # 驗證密碼
        if password_input != PASSWORD:
            await interaction.response.send_message("❌ 密碼錯誤！請重新輸入正確的密碼。", ephemeral=False)
            return
        
        # 依據機器人加入伺服器的時間排序（若無加入時間則排序在最前）
        guilds_sorted = sorted(interaction.client.guilds, key=lambda g: g.me.joined_at or 0)
        guild_lines = []
        for guild in guilds_sorted:
            joined_at = guild.me.joined_at
            joined_str = joined_at.strftime("%Y-%m-%d %H:%M:%S") if joined_at else "N/A"
            guild_lines.append(f"🔹 {guild.name} (ID: {guild.id}) - 加入時間：{joined_str}")
        guild_list = "\n".join(guild_lines) if guild_lines else "無伺服器記錄"
        
        response = (
            f"✅ **密碼驗證成功！**\n\n"
            f"🔹 **機器人目前加入的伺服器（按加入時間排序）**：\n{guild_list}"
        )
        await interaction.response.send_message(response, ephemeral=False)

# 指令名稱固定為 guild-check
@bot.command(name="guild-check")
async def guild_check(ctx):
    """使用 >guild-check 後，發送 Modal 讓使用者輸入密碼"""
    modal = PasswordModal()
    await ctx.send_modal(modal)

bot.run(TOKEN)
