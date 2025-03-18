import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 取得目前檔案名稱（不含副檔名）作為指令名稱
command_name = os.path.splitext(os.path.basename(__file__))[0]

# 啟用 intents，包括 members 與 message_content
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# 自訂按鈕：點擊後會檢查使用者是否已有該身分組，並依狀態新增或移除
class RoleButton(discord.ui.Button):
    def __init__(self, role_name: str, label: str):
        # 設定 custom_id 以達到持久化效果
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"role_button_{role_name}")
        self.role_name = role_name

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=self.role_name)
        if role is None:
            await interaction.response.send_message(f"無法找到身分組：{self.role_name}", ephemeral=True)
            return

        member = interaction.user
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"已移除 {self.role_name} 身分組。", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"已領取 {self.role_name} 身分組！", ephemeral=True)

# 自訂 View，加入三個按鈕，timeout 設為 None 讓其永久有效
class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleButton("Cyloris★圓環之理", "Cyloris★圓環之理"))
        self.add_item(RoleButton("異世界旅行者", "異世界旅行者"))
        self.add_item(RoleButton("官方資訊", "官方資訊"))

@bot.event
async def on_ready():
    print(f"機器人已登入：{bot.user} (ID: {bot.user.id})")
    print("------")
    # 註冊持久性 View，確保按鈕永遠有效，即使重啟後也能正常互動
    bot.add_view(RoleView())

# 指令名稱會與檔案名稱一致，例如檔案為 send_roles.py，則使用 !send_roles 發送訊息
@bot.command(name=command_name)
@commands.has_permissions(administrator=True)
async def send_roles(ctx):
    embed = discord.Embed(
        title="✨ 歡迎來到『Cyloris★圓環之理』 ✨",
        description=(
            "歡迎新成員，一起打造屬於大家的溫暖家園~！\n\n"
            "🔹 **Cyloris★圓環之理**：公會內成員點選這個。\n\n"
            "🔹 **異世界旅行者**：公會外的朋友們點選這個。\n\n"
            "🔹 **官方資訊**：托蘭官方資訊通知，掌握最新動態。\n\n"
            "點擊最下方按鈕領取相應身分組後，即可解鎖頻道~！\n\n"
            "選完後記得要填寫遊戲名和自我介紹~：\n[前往自我介紹頻道](https://discord.com/channels/1300829523742298142/1300843562098757672)"
        ),
        color=0xFFB6C1  # 粉紅色
    )
    # 加入橫幅圖片及縮略圖（可依需求自行更換圖片網址）
    embed.set_image(url="https://i.imgur.com/gfWgSUP.jpeg")
    embed.set_thumbnail(url="https://i.imgur.com/TIujgzc.png")
    embed.set_footer(text="與大家一起，邁向夢想的未來 ♡")
    await ctx.send(embed=embed, view=RoleView())

bot.run(TOKEN)