import discord
from discord.ext import commands
import asyncio
import random
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# 定義簡單版的遊戲章節（3 個章節）
game_chapters = [
    {
        "title": "序曲：月夜初遇",
        "narration": "在陰暗而神秘的月夜，你迎來了女僕月醬，她神秘又迷人。",
        "options": [
            {"id": "option1", "text": "坐下來聊聊吧！"},
            {"id": "option2", "text": "先觀察她一會兒……"},
            {"id": "option3", "text": "偷偷調查她的背景！"}
        ]
    },
    {
        "title": "第一篇章：迷霧交織",
        "narration": "日常相處中，你發現月醬行為時而溫柔，時而怪異。",
        "options": [
            {"id": "option1", "text": "關心她，提供幫助。"},
            {"id": "option2", "text": "深入交談了解真相。"},
            {"id": "option3", "text": "漸漸依賴她，迷失自我。"}
        ]
    },
    {
        "title": "第二篇章：面具背後",
        "narration": "隨著關係深入，她的過去逐漸浮現，充滿孤獨與痛苦。",
        "options": [
            {"id": "option1", "text": "鼓勵她正視過去。"},
            {"id": "option2", "text": "一同傾聽與療傷。"},
            {"id": "option3", "text": "選擇逃避現實。"}
        ]
    }
]

# 用來記錄玩家的選擇（依玩家 ID 記錄一個選項 id 列表）
user_choices = {}

# 定義簡化的按鈕互動 View，每個按鈕獨立分行（row 參數）
class ChoiceView(discord.ui.View):
    def __init__(self, author, options):
        super().__init__(timeout=60)
        self.author = author
        self.value = None
        # 依序建立按鈕，每個按鈕獨立一行
        for i, opt in enumerate(options, start=1):
            button = discord.ui.Button(label=f"{i}. {opt['text']}", style=discord.ButtonStyle.secondary, row=i-1)
            button.callback = self.make_callback(opt)
            self.add_item(button)
    
    def make_callback(self, option):
        async def callback(interaction: discord.Interaction):
            # 只允許遊戲發起者操作
            if interaction.user != self.author:
                await interaction.response.send_message("這不是你的遊戲！", ephemeral=True)
                return
            self.value = option["id"]
            await interaction.response.send_message(f"你選擇了：{option['text']}", ephemeral=False)
            self.stop()
        return callback

# 簡單的結局判定：根據選項出現次數，最多者決定最終結局
def determine_ending(choices):
    count1 = choices.count("option1")
    count2 = choices.count("option2")
    count3 = choices.count("option3")
    max_count = max(count1, count2, count3)
    if max_count == count1:
        return "溫馨結局：你與月醬建立了深厚的情感，生活充滿溫暖。"
    elif max_count == count2:
        return "平淡結局：你們的生活平穩而安靜，雖然平凡卻也真實。"
    else:
        return "恐怖結局：你最終陷入孤獨與恐懼，現實變得扭曲不堪。"

# 建立 Bot 實例
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def startgame(ctx):
    # 在每個章節中都顯示玩家的名字
    user_choices[ctx.author.id] = []
    await ctx.send(f"遊戲開始！玩家 **{ctx.author.name}** 正在遊玩。")
    for chapter in game_chapters:
        # 使用 Markdown 語法呈現大字體的章節標題與內容，
        # 並在最前面標示正在遊玩的玩家名字
        chapter_text = f"**玩家：{ctx.author.name}**\n\n# {chapter['title']}\n\n**{chapter['narration']}**"
        await ctx.send(chapter_text)
        view = ChoiceView(ctx.author, chapter["options"])
        await ctx.send("請點選以下選項：", view=view)
        await view.wait()
        if view.value is None:
            await ctx.send("等待超時，遊戲結束。")
            return
        user_choices[ctx.author.id].append(view.value)
        await asyncio.sleep(1)
    ending = determine_ending(user_choices[ctx.author.id])
    await ctx.send(f"你的選擇：{' -> '.join(user_choices[ctx.author.id])}\n最終結局：{ending}")

bot.run(TOKEN)
