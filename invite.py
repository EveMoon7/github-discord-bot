import discord
from discord.ext import commands

import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # 啟用訊息內容權限
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.command(aliases=["invite"])
async def 邀請(ctx):
    embed = discord.Embed(
        title="💌 女僕月醬的邀請函 ✨",
        description="💕 狗修金sama～點擊下方連結，讓本女僕加入您的伺服器吧！🎀",
        color=0xffa6c9  # 可愛少女粉
    )
    
    # 使用新的邀請鏈接
    invite_url = (
        "https://discord.com/oauth2/authorize?client_id=1323232531713359994"
    )
    
    embed.add_field(name="📌 邀請連結", value=f"[🌟 點我召喚 女僕月醬 ✨]({invite_url})", inline=False)
    embed.set_footer(text="女僕月醬等待主人召喚喔 ~ 💖")
    
    await ctx.send(embed=embed)

# 啟動 Bot
bot.run(TOKEN)
