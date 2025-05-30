import discord
import requests
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# === 啟用 Gateway Intents ===
intents = discord.Intents.default()
intents.members = True       # ← 必須開啟
intents.message_content = True

bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

# === 設定 ===
TARGET_ROLE_NAME = "閱覽者"
WEBHOOK_URL      = "https://discord.com/api/webhooks/1377978739488460901/-IxnQkHeb39c7PxKAzoU56cdNQ3RauVOc8yLL7stupzdc5EATcNcw-jv74IvVPE2ZzeO"
WEBHOOK_NAME     = "Neko醬"
WEBHOOK_AVATAR   = "https://i.imgur.com/eK8MsDg.png"
WELCOME_TITLE    = "歡迎新成員！"
WELCOME_DESCRIPTION = "歡迎 {mention} 加入白森林！請記得到https://discord.com/channels/1357865064815661096/1361050253075157185自我介紹喔～\要解鎖攻略頻道可以在https://discord.com/channels/1357865064815661096/1361041670514409714解鎖。"
EMBED_COLOR      = 0xFFD700

@bot.event
async def on_member_update(before, after):
    old_roles = {r.id for r in before.roles}
    new_roles = {r.id for r in after.roles}
    added_roles = new_roles - old_roles

    # 檢查目標身分組是否在新增清單裡
    for role in after.guild.roles:
        if role.id in added_roles and role.name == TARGET_ROLE_NAME:
            send_webhook_welcome(after)
            break

def send_webhook_welcome(member: discord.Member):
    embed = {
        "title": WELCOME_TITLE,
        "description": WELCOME_DESCRIPTION.replace("{mention}", member.mention),
        "color": EMBED_COLOR,
        "thumbnail": { "url": str(member.display_avatar.url) }
    }
    data = {
        "username": WEBHOOK_NAME,
        "avatar_url": WEBHOOK_AVATAR,
        "embeds": [embed]
    }
    requests.post(WEBHOOK_URL, json=data)

bot.run(TOKEN)
