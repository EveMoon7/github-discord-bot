import discord
import os
from discord.ext import commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>', help_command=None, intents=intents)

# 自訂 help 指令：由專屬女僕月醬來為主人服務
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="✨ 女僕月醬的指令幫助 ✨",
        description="嗚呼～女僕月醬向主人請安,以下是主人可以使用的指令～",
        color=0xFFB6C1  # 淡粉色調，展現可愛風格
    )
    # 可替換為你喜歡的女僕圖片網址
    embed.set_thumbnail(url="https://i.imgur.com/2MAYQyH.png")
    
    embed.add_field(name=">help", value="女僕月醬的指令介紹訊息～", inline=False)
    embed.add_field(name=">update", value="女僕月醬的更新日志～", inline=False)
    embed.add_field(name=">invite", value="女僕月醬的邀請函～", inline=False)
    embed.add_field(name=">boss", value="Boss數據查詢", inline=False)
    embed.add_field(name=">food", value="料理地址查詢", inline=False)
    embed.add_field(name=">mat", value="素材刷點導航", inline=False)
    
    embed.set_footer(text="要常常呼叫月醬出來玩哦～")
    await ctx.send(embed=embed)

# 其他示範指令
@bot.command()
async def ping(ctx):
    await ctx.send("Bonk! ～")

@bot.command()
async def info(ctx):
    await ctx.send("貴安，本女僕為托蘭型萬能機器人噠噠☆♪！")

# 啟動 Bot，請將 'YOUR_BOT_TOKEN' 替換成你自己的 Bot Token
bot.run(TOKEN)
