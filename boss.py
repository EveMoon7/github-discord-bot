import os
import json
import discord
import unicodedata
import logging
import random
from discord.ext import commands
from dotenv import load_dotenv

# 载入 .env 文件
load_dotenv()

# 设置 logging 输出
logging.basicConfig(level=logging.INFO)

# 获取 Discord Bot Token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not TOKEN:
    raise ValueError("❌ 请先设置环境变量 DISCORD_BOT_TOKEN ！")

# 设置 intents，启用消息内容权限
intents = discord.Intents.default()
intents.message_content = True

# 初始化机器人
bot = commands.Bot(command_prefix=">", intents=intents, case_insensitive=True)

def normalize(text: str) -> str:
    """使用 Unicode NFKC 规范化字符串，方便匹配。"""
    return unicodedata.normalize("NFKC", text).lower().strip()

# 读取 JSON 数据
def load_json(filename):
    """读取 JSON 数据，出现错误时返回空字典。"""
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"❌ 读取 {filename} 时发生错误: {e}")
        return {}

# 载入所有 Boss 数据
main_quest_boss_data = load_json("Main_Quest_Boss_Data.json")
high_difficulty_boss_data = load_json("High_Difficulty_Boss_Data.json")
event_boss_data = load_json("Event_Boss_Data.json")
guild_raid_boss_data = load_json("Guild_Raid_Boss_Data.json")

# 整合所有 Boss 数据集
boss_data_sets = {
    "main": main_quest_boss_data,
    "high": high_difficulty_boss_data,
    "event": event_boss_data,
    "guild": guild_raid_boss_data
}

# 搜索 Boss
def find_boss(query: str):
    """
    根据查询字符串搜索所有 Boss 数据。
    先尝试完全匹配（名称或别名相同），若未找到则尝试模糊匹配。
    """
    query_norm = normalize(query)
    results = []

    for boss_type, data in boss_data_sets.items():
        for boss in data.values():
            name_norm = normalize(boss.get("名稱", ""))
            aliases_norm = [normalize(alias) for alias in boss.get("別名", [])]

            # 完全匹配
            if query_norm == name_norm or query_norm in aliases_norm:
                return boss, boss_type

            # 模糊匹配
            if query_norm in name_norm or any(query_norm in alias for alias in aliases_norm):
                results.append((boss, boss_type))

    return results[0] if results else None

# 创建 Boss Embed
def create_boss_embed(boss_info, boss_type):
    """
    生成 Boss 的 Discord Embed 信息卡片。
    """
    embed = discord.Embed(
        title=f"✧*。{boss_type.upper()} Boss: {boss_info.get('名稱', '未知')} 。*✧",
        description=f"❀ 章节: {boss_info.get('章節', '未知')} ❀\n❀ 地点: {boss_info.get('地點', '未知')} ❀",
        color=discord.Color.magenta()
    )

    embed.add_field(name="属性", value=f"{boss_info.get('屬性', 'N/A')}", inline=False)
    embed.add_field(name="物防 P.Def", value=f"{boss_info.get('物防', 'N/A')}", inline=True)
    embed.add_field(name="魔防 M.Def", value=f"{boss_info.get('魔防', 'N/A')}", inline=True)
    embed.add_field(name="物理抗性 P.Res", value=f"{boss_info.get('物理抗性', 'N/A')}", inline=True)
    embed.add_field(name="魔法抗性 M.Res", value=f"{boss_info.get('魔法抗性', 'N/A')}", inline=True)
    embed.add_field(name="回避 Flee", value=f"{boss_info.get('迴避', 'N/A')}", inline=True)

    # 处理暴抗信息
    crt_res = boss_info.get("暴抗", "N/A")
    if isinstance(crt_res, dict):
        crt_res = "\n".join([f"{k}: {v}" for k, v in crt_res.items()])
    embed.add_field(name="暴抗 Crt.Res", value=f"{crt_res}", inline=True)

    # 额外字段
    optional_fields = ["控制", "破位效果", "階段", "傷害上限 (MaxHP)"]
    for field in optional_fields:
        if boss_info.get(field):
            embed.add_field(name=field, value=boss_info[field], inline=False)

    # 设置图片
    if boss_info.get("圖片"):
        embed.set_image(url=boss_info["圖片"])

    return embed

# 处理 >boss 指令
@bot.command()
async def boss(ctx, *, query: str = None):
    """查询 Boss 相关信息。"""
    if not query:
        await ctx.send("❌ 请输入 Boss 名称或别名！")
        return

    result = find_boss(query)
    if not result:
        await ctx.send("❌ 未找到该 Boss，请检查名称是否正确！")
        return

    boss_info, boss_type = result
    embed = create_boss_embed(boss_info, boss_type)
    await ctx.send(embed=embed)

# 机器人启动日志
@bot.event
async def on_ready():
    logging.info(f"✅ 已登录为 {bot.user}")

# 运行机器人
bot.run(TOKEN)
