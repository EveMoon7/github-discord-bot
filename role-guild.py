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

bot = commands.Bot(command_prefix=">", intents=intents)

# 自訂按鈕：點擊後會檢查使用者是否已有該身分組，並依狀態新增或移除
class RoleButton(discord.ui.Button):
    def __init__(self, role_name: str, label: str):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
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

# 自訂 View 將三個按鈕加入其中
class RoleView(discord.ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)
        self.add_item(RoleButton("Cyloris★圓環之理", "Cyloris★圓環之理"))
        self.add_item(RoleButton("異世界旅行者", "異世界旅行者"))
        self.add_item(RoleButton("官方資訊", "官方資訊"))

@bot.event
async def on_ready():
    print(f"機器人已登入：{bot.user} (ID: {bot.user.id})")
    print("------")

# 指令名稱會與檔案名稱一致，例如檔案為 send_roles.py，則使用 !send_roles 發送訊息
@bot.command(name=command_name)
@commands.has_permissions(administrator=True)
async def send_roles(ctx):
    embed = discord.Embed(
        title="歡迎來到「Cyloris★圓環之理」，一起打造我們的家♡",
        description=(
            "「Cyloris★圓環之理」：在公會裡的成員選擇這個~\n\n"
            "「異世界旅行者」：不在公會的其他朋友們選這個~\n\n"
            "「官方資訊」：需要官方資訊通知的選擇這個~\n\n"
            "以下為身份組的領取/捨棄按鈕，領取了就能看見相關頻道啦☆"
        ),
        color=0xFFB6C1
    )
    # 加入橫幅圖片於訊息下方
    embed.set_image(url="https://i.imgur.com/gfWgSUP.jpeg")
    await ctx.send(embed=embed, view=RoleView())

bot.run(TOKEN)
