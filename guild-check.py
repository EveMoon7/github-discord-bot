import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'機器人 {bot.user} 已上線！')
    print(f'目前加入了 {len(bot.guilds)} 個伺服器')
    
    for guild in bot.guilds:
        print(f'伺服器名稱: {guild.name} | ID: {guild.id}')

bot.run(TOKEN)
