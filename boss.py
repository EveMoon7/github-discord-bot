import os
import json
import discord
import unicodedata
import logging
import random  # 新增 random 模組，用於隨機選取圖片
from discord.ext import commands

# 設定 logging 輸出
logging.basicConfig(level=logging.INFO)

# 取得 Discord Bot Token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("請先設定環境變數 DISCORD_BOT_TOKEN！")

# 設定 intents，啟用訊息內容權限
intents = discord.Intents.default()
intents.message_content = True

# 初始化機器人
bot = commands.Bot(command_prefix=">", intents=intents, case_insensitive=True)

def normalize(text: str) -> str:
    """
    使用 Unicode NFKC 正規化字串，方便後續比對。
    """
    return unicodedata.normalize("NFKC", text)

# 載入 Main_Quest_Boss_Data.json（主線王資料）
try:
    with open("Main_Quest_Boss_Data.json", "r", encoding="utf-8") as file:
        main_quest_boss_data = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error("讀取 Main_Quest_Boss_Data.json 時發生錯誤: %s", e)
    main_quest_boss_data = {}

# 載入 High_Difficulty_Boss_Data.json（高難王資料）
try:
    with open("High_Difficulty_Boss_Data.json", "r", encoding="utf-8") as file:
        high_difficulty_boss_data = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error("讀取 High_Difficulty_Boss_Data.json 時發生錯誤: %s", e)
    high_difficulty_boss_data = {}

# 載入 Event_Boss_Data.json（活動王資料）
try:
    with open("Event_Boss_Data.json", "r", encoding="utf-8") as file:
        event_boss_data = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error("讀取 Event_Boss_Data.json 時發生錯誤: %s", e)
    event_boss_data = {}

# 載入 Guild_Raid_Boss_Data.json（公會王資料）
try:
    with open("Guild_Raid_Boss_Data.json", "r", encoding="utf-8") as file:
        guild_raid_boss_data = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error("讀取 Guild_Raid_Boss_Data.json 時發生錯誤: %s", e)
    guild_raid_boss_data = {}

def find_boss(query: str, data: dict):
    """
    根據查詢字串在資料中尋找符合的敵人資訊。
    先嘗試完全比對（名稱或別名完全相符），若未找到則嘗試包含比對。
    """
    query_norm = normalize(query.strip()).lower()
    # 先完全比對
    for info in data.values():
        name_norm = normalize(info.get("名稱", "")).lower()
        aliases_norm = [normalize(alias).lower() for alias in info.get("別名", [])]
        if query_norm == name_norm or query_norm in aliases_norm:
            return info
    # 若未找到，嘗試包含比對
    for info in data.values():
        name_norm = normalize(info.get("名稱", "")).lower()
        aliases_norm = [normalize(alias).lower() for alias in info.get("別名", [])]
        if query_norm in name_norm or any(query_norm in a for a in aliases_norm):
            return info
    return None

def create_boss_embed(info: dict, boss_type: str) -> discord.Embed:
    """
    根據 Boss 資料與 Boss 類型建立 Discord Embed。
    
    boss_type 可用值：
      - "main"：主線王 Main Quest Boss（顯示難度倍率）
      - "high"：高難王 High Difficulty Boss（不顯示難度倍率）
      - "event"：活動王 Event Boss（顯示難度倍率）
      - "guild"：公會王 Guild Raid Boss（不顯示難度倍率）
    """
    name = info.get("名稱", "未知")
    
    # 設定標題文字
    if boss_type == "main":
        title = f"✧*。主線王 Boss: {name}。*✧"
    elif boss_type == "high":
        title = f"✧*。高難王 Boss: {name}。*✧"
    elif boss_type == "event":
        title = f"✧*。活動王 Boss: {name}。*✧"
    elif boss_type == "guild":
        title = f"✧*。公會王 Boss: {name}。*✧"
    else:
        title = name

    embed = discord.Embed(
        title=title,
        description=f"❀ 章節 Chapter: {info.get('章節', '未知')} ❀\n❀ 地點: {info.get('地點', '未知')} ❀",
        color=discord.Color.magenta()
    )
    embed.add_field(name="╭⋯⋯⋯⋯ 屬性 Element ⋯⋯⋯⋯╮",
                    value=f"{info.get('屬性', 'N/A')}\n​",
                    inline=False)
    embed.add_field(name="物防 P.Def", value=f"{info.get('物防', 'N/A')}", inline=True)
    embed.add_field(name="魔防 M.Def", value=f"{info.get('魔防', 'N/A')}\n​", inline=True)
    embed.add_field(name="物理抗性 P.Res", value=f"{info.get('物理抗性', 'N/A')}", inline=True)
    embed.add_field(name="魔法抗性 M.Res", value=f"{info.get('魔法抗性', 'N/A')}\n​", inline=True)
    embed.add_field(name="迴避 Flee", value=f"{info.get('迴避', 'N/A')}", inline=True)
    
    # 處理暴抗資訊
    crt_res = info.get("暴抗", "N/A")
    if isinstance(crt_res, dict):
        crt_res = "\n".join([f"{k}: {v}" for k, v in crt_res.items()])
    embed.add_field(name="暴抗 Crt.Res", value=f"{crt_res}\n​", inline=True)
    
    inertia_text = (f"物理: {info.get('物理-慣性變動', 'N/A')}　"
                    f"魔法: {info.get('魔法-慣性變動', 'N/A')}　"
                    f"普攻: {info.get('普攻-慣性變動', 'N/A')}\n​")
    embed.add_field(name="慣性變動率 Proration", value=inertia_text, inline=False)
    
    # 使用自訂的顯示名稱
    optional_fields = ["控制", "破位效果", "階段", "傷害上限 (MaxHP)", "注意"]
    for field in optional_fields:
        if field in info:
            # 設定自訂名稱
            if field == "階段":
                display_name = "⋆˙ 階段 Phase ˙⋆"
            elif field == "控制":
                display_name = "⋆˙ 控制 FTS ˙⋆"
            elif field == "破位效果":
                display_name = "⋆˙ 破位效果 Break Effect ˙⋆"
            else:
                display_name = f"⋆˙ {field} ˙⋆"
            embed.add_field(name=display_name, value=f"{info[field]}\n​", inline=False)
    
    if info.get("圖片"):
        embed.set_image(url=info["圖片"])
    
    # 主線王和活動王要顯示難度倍率
    if boss_type in ("main", "event"):
        embed.set_footer(text="✧*。 難度倍率 Difficulty 。*✧\n"
                           "EASY = 0.1 x 防禦 | 迴避\n"
                           "NORMAL = 1 x 防禦 | 迴避\n"
                           "HARD = 2 x 防禦 | 迴避\n"
                           "NIGHTMARE = 4 x 防禦 | 迴避\n"
                           "ULTIMATE = 6 x 防禦 | 迴避")
    
    return embed

# 新增搜尋所有 Boss 的功能（支援部分比對）
def search_all_boss(query: str):
    """
    從所有 Boss 資料中搜尋符合查詢的敵人資訊，回傳符合項目列表。
    每筆項目為 (info, boss_type)，boss_type 可為 "main", "high", "event", "guild"。
    """
    query_norm = normalize(query.strip()).lower()
    results = []
    datasets = [
        ("main", main_quest_boss_data),
        ("high", high_difficulty_boss_data),
        ("event", event_boss_data),
        ("guild", guild_raid_boss_data)
    ]
    for boss_type, data in datasets:
        for info in data.values():
            name_norm = normalize(info.get("名稱", "")).lower()
            aliases_norm = [normalize(alias).lower() for alias in info.get("別名", [])]
            # 先嘗試完全比對
            if query_norm == name_norm or query_norm in aliases_norm:
                results.append((info, boss_type))
            # 若未完全匹配，嘗試包含比對
            elif query_norm in name_norm or any(query_norm in a for a in aliases_norm):
                results.append((info, boss_type))
    return results

#############################################
# 以下為 UI 互動元件（使用 discord.ui）

class BossSelect(discord.ui.Select):
    """從指定 Boss 類型中選擇單一 Boss"""
    def __init__(self, boss_type: str, options):
        super().__init__(
            placeholder="請選擇一個 Boss...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.boss_type = boss_type

    async def callback(self, interaction: discord.Interaction):
        selected_key = self.values[0]
        # 根據 boss_type 取得對應資料
        if self.boss_type == "main":
            info = main_quest_boss_data.get(selected_key)
        elif self.boss_type == "high":
            info = high_difficulty_boss_data.get(selected_key)
        elif self.boss_type == "event":
            info = event_boss_data.get(selected_key)
        elif self.boss_type == "guild":
            info = guild_raid_boss_data.get(selected_key)
        else:
            info = None
        if info is None:
            await interaction.response.send_message("找不到該 Boss 資訊。", ephemeral=True)
            return
        embed = create_boss_embed(info, boss_type=self.boss_type)
        await interaction.response.edit_message(content=None, embed=embed, view=None)

class BossTypeSelect(discord.ui.Select):
    """先選擇 Boss 類型"""
    def __init__(self):
        options = [
            discord.SelectOption(label="主線王", description="Main Quest Boss", value="main"),
            discord.SelectOption(label="高難王", description="High Difficulty Boss", value="high"),
            discord.SelectOption(label="活動王", description="Event Boss", value="event"),
            discord.SelectOption(label="公會王", description="Guild Raid Boss", value="guild")
        ]
        super().__init__(
            placeholder="請選擇 Boss 類型...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        boss_type = self.values[0]
        # 根據 boss_type 取得對應資料
        if boss_type == "main":
            data = main_quest_boss_data
            type_str = "主線王"
        elif boss_type == "high":
            data = high_difficulty_boss_data
            type_str = "高難王"
        elif boss_type == "event":
            data = event_boss_data
            type_str = "活動王"
        elif boss_type == "guild":
            data = guild_raid_boss_data
            type_str = "公會王"
        else:
            data = {}
            type_str = "未知"
        # 為了避免選項過多，此處假設該類型 Boss 不超過 25 筆
        options = []
        # 使用資料的 key 作為 select value
        for key, info in data.items():
            boss_name = info.get("名稱", "未知")
            options.append(discord.SelectOption(label=boss_name, value=key, description=type_str))
        view = discord.ui.View()
        view.add_item(BossSelect(boss_type, options))
        await interaction.response.edit_message(content="請選擇一個 Boss：", view=view)

class BossTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(BossTypeSelect())

#############################################
# 以下為原本的指令

# 主線王指令（從 Main_Quest_Boss_Data.json 查詢）
@bot.command()
async def mainquestboss(ctx, *, query: str = None):
    if not query:
        await ctx.send("請提供主線王 Boss 名稱或別名！")
        return
    boss_info = find_boss(query, main_quest_boss_data)
    if not boss_info:
        await ctx.send("✿❀ 找不到該主線王 Boss 資訊 ❀✿")
        return
    embed = create_boss_embed(boss_info, boss_type="main")
    await ctx.send(embed=embed)

# 高難王指令（從 High_Difficulty_Boss_Data.json 查詢）
@bot.command()
async def highdifficultyboss(ctx, *, query: str = None):
    if not query:
        await ctx.send("請提供高難王 Boss 名稱或別名！")
        return
    boss_info = find_boss(query, high_difficulty_boss_data)
    if not boss_info:
        await ctx.send("✿❀ 找不到該高難王 Boss 資訊 ❿✿")
        return
    embed = create_boss_embed(boss_info, boss_type="high")
    await ctx.send(embed=embed)

# 活動王指令（從 Event_Boss_Data.json 查詢）
@bot.command()
async def eventboss(ctx, *, query: str = None):
    if not query:
        await ctx.send("請提供活動 Boss 名稱或別名！")
        return
    boss_info = find_boss(query, event_boss_data)
    if not boss_info:
        await ctx.send("✿❀ 找不到該活動 Boss 資訊 ❿✿")
        return
    embed = create_boss_embed(boss_info, boss_type="event")
    await ctx.send(embed=embed)

# 公會王指令（從 Guild_Raid_Boss_Data.json 查詢）
@bot.command()
async def guildraidboss(ctx, *, query: str = None):
    if not query:
        await ctx.send("請提供公會王 Boss 名稱或別名！")
        return
    boss_info = find_boss(query, guild_raid_boss_data)
    if not boss_info:
        await ctx.send("✿❀ 找不到該公會王 Boss 資訊 ❿✿")
        return
    embed = create_boss_embed(boss_info, boss_type="guild")
    await ctx.send(embed=embed)

# 修改後的 boss 指令：若帶參數則採用搜尋模式；若不帶參數則發送互動式選擇列表
@bot.command()
async def boss(ctx, *, query: str = None):
    if query:
        # 舊有搜尋邏輯
        results = search_all_boss(query)
        if not results:
            await ctx.send("✿❀ 找不到該 Boss 資訊 ❀✿")
            return
        # 若只找到一筆結果則直接顯示詳細資訊
        if len(results) == 1:
            info, boss_type = results[0]
            embed = create_boss_embed(info, boss_type=boss_type)
            await ctx.send(embed=embed)
            return
        # 若找到多筆，則列出匹配項目，並提示使用者更精確查詢
        msg = "找到多個匹配項目：\n"
        for idx, (info, boss_type) in enumerate(results, start=1):
            type_str = ""
            if boss_type == "main":
                type_str = "主線王"
            elif boss_type == "high":
                type_str = "高難王"
            elif boss_type == "event":
                type_str = "活動王"
            elif boss_type == "guild":
                type_str = "公會王"
            msg += f"{idx}. {info.get('名稱', '未知')} ({type_str})\n"
        msg += "請更精確地查詢。"
        await ctx.send(msg)
    else:
        # 若無參數，發送 Boss 類型選單，進而進行選擇
        await ctx.send("請選擇 Boss 類型：", view=BossTypeView())

bot.run(TOKEN)
