import os
import json
import discord
import unicodedata
import logging
from discord.ext import commands
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 設定 logging 輸出
logging.basicConfig(level=logging.INFO)

# 取得 Discord Bot Token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not TOKEN:
    raise ValueError("❌ 請先設定環境變數 DISCORD_BOT_TOKEN ！")

# 設置 intents，啟用訊息內容權限
intents = discord.Intents.default()
intents.message_content = True

# 初始化機器人
bot = commands.Bot(command_prefix=">", intents=intents, case_insensitive=True)

def normalize(text: str) -> str:
    """使用 Unicode NFKC 規範化字串，方便匹配。"""
    return unicodedata.normalize("NFKC", text).lower().strip()

# 讀取 JSON 數據
def load_json(filename):
    """讀取 JSON 數據，發生錯誤時返回空字典。"""
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"❌ 讀取 {filename} 時發生錯誤: {e}")
        return {}

# 載入所有 Boss 數據
main_quest_boss_data = load_json("Main_Quest_Boss_Data.json")
high_difficulty_boss_data = load_json("High_Difficulty_Boss_Data.json")
event_boss_data = load_json("Event_Boss_Data.json")
guild_raid_boss_data = load_json("Guild_Raid_Boss_Data.json")

# 整合所有 Boss 數據集
boss_data_sets = {
    "main": main_quest_boss_data,
    "high": high_difficulty_boss_data,
    "event": event_boss_data,
    "guild": guild_raid_boss_data
}

# 定義 Boss 類型的友好名稱與描述
boss_type_mapping = {
    "main": {"label": "主線王", "description": "Main Quest Boss"},
    "high": {"label": "高難王", "description": "High Difficulty Boss"},
    "event": {"label": "活動王", "description": "Event Boss"},
    "guild": {"label": "公會王", "description": "Guild Raid Boss"}
}

# 搜索 Boss
def find_boss(query: str):
    """
    根據查詢字串搜索所有 Boss 數據。
    優先嘗試完全匹配（名稱或別名相同），
    若未找到則嘗試模糊匹配：
      - 如果只有一項模糊匹配則直接返回該 Boss，
      - 如果存在多項匹配則返回匹配列表，用於下拉選單選擇。
    """
    query_norm = normalize(query)
    ambiguous = []

    for boss_type, data in boss_data_sets.items():
        for boss in data.values():
            name_norm = normalize(boss.get("名稱", ""))
            aliases_norm = [normalize(alias) for alias in boss.get("別名", [])]

            # 完全匹配
            if query_norm == name_norm or query_norm in aliases_norm:
                return boss, boss_type

            # 模糊匹配
            if query_norm in name_norm or any(query_norm in alias for alias in aliases_norm):
                ambiguous.append((boss, boss_type))

    if ambiguous:
        if len(ambiguous) == 1:
            return ambiguous[0]
        else:
            return ambiguous

    return None

# 創建 Boss Embed
def create_boss_embed(boss_info, boss_type):
    """
    生成 Boss 的 Discord Embed 資訊卡片。
    """
    friendly = boss_type_mapping.get(boss_type, {"label": boss_type.upper()})
    embed = discord.Embed(
        title=f"✧*。{friendly['label']} Boss: {boss_info.get('名稱', '未知')} 。*✧",
        description=f"❀ 章節 Phase: {boss_info.get('章節', '未知')} ❀\n❀ 地點: {boss_info.get('地點', '未知')} ❀",
        color=discord.Color.magenta()
    )

    embed.add_field(
        name="╭⋯⋯⋯⋯ 屬性 Element ⋯⋯⋯⋯╮",
        value=f"{boss_info.get('屬性', 'N/A')}\n\u200b",
        inline=False
    )
    embed.add_field(name="物防 P.Def", value=f"{boss_info.get('物防', 'N/A')}", inline=True)
    embed.add_field(name="魔防 M.Def", value=f"{boss_info.get('魔防', 'N/A')}\n\u200b", inline=True)
    embed.add_field(name="物理抗性 P.Res", value=f"{boss_info.get('物理抗性', 'N/A')}", inline=True)
    embed.add_field(name="魔法抗性 M.Res", value=f"{boss_info.get('魔法抗性', 'N/A')}\n\u200b", inline=True)
    embed.add_field(name="迴避 Flee", value=f"{boss_info.get('迴避', 'N/A')}", inline=True)

    # 處理暴抗資訊，可能為字典或其他型態
    crt_res = boss_info.get("暴抗", "N/A")
    if isinstance(crt_res, dict):
        crt_res = "\n".join([f"{k}: {v}" for k, v in crt_res.items()])
    else:
        crt_res = str(crt_res)
    embed.add_field(name="暴抗 Crt.Res", value=f"{crt_res}\n\u200b", inline=True)

    inertia_text = (
        f"物理: {boss_info.get('物理-慣性變動', 'N/A')}　"
        f"魔法: {boss_info.get('魔法-慣性變動', 'N/A')}　"
        f"普攻: {boss_info.get('普攻-慣性變動', 'N/A')}\n\u200b"
    )
    embed.add_field(name="慣性變動率 Proration", value=inertia_text, inline=False)

    # 使用自訂的顯示名稱

    if boss_info.get("控制"):
        embed.add_field(name="⋆˙ 控制 FTS ˙⋆", value=f"{boss_info.get('控制')}\n\u200b", inline=False)
    if boss_info.get("破位效果"):
        embed.add_field(name="⋆˙ 破位效果 Break ˙⋆", value=f"{boss_info.get('破位效果')}\n\u200b", inline=False)
    if boss_info.get("階段"):
        embed.add_field(name="⋆˙ 階段/模式 Phase ˙⋆", value=f"{boss_info.get('階段')}\n\u200b", inline=False)
    if boss_info.get("傷害上限 (MaxHP)"):
        embed.add_field(name="⋆˙ 傷害上限 (MaxHP) ˙⋆", value=f"{boss_info.get('傷害上限 (MaxHP)')}\n\u200b", inline=False)

    # 設置圖片
    if boss_info.get("圖片"):
        embed.set_image(url=boss_info["圖片"])

    # 主線王和活動王要顯示難度倍率
    if boss_type in ("main", "event"):
        embed.set_footer(text="✧*。 難度倍率 Difficulty 。*✧\n"
                           "EASY = 0.1 x 防禦 | 迴避\n"
                           "NORMAL = 1 x 防禦 | 迴避\n"
                           "HARD = 2 x 防禦 | 迴避\n"
                           "NIGHTMARE = 4 x 防禦 | 迴避\n"
                           "ULTIMATE = 6 x 防禦 | 迴避")

    return embed

# ================= 下拉選單相關類 =================
class BossSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="請選擇一個 Boss", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        boss_info, boss_type = self.view.boss_mapping[selected_value]
        embed = create_boss_embed(boss_info, boss_type)
        # 更新訊息，移除下拉選單
        await interaction.response.edit_message(content=None, embed=embed, view=None)

class BossSelectView(discord.ui.View):
    def __init__(self, boss_results):
        super().__init__(timeout=60)
        self.boss_mapping = {}
        options = []
        for idx, (boss, boss_type) in enumerate(boss_results):
            value = str(idx)
            self.boss_mapping[value] = (boss, boss_type)
            label = boss.get("名稱", "未知")
            # 取得該類型的友好名稱
            friendly_type = boss_type_mapping.get(boss_type, {"label": boss_type.upper()})["label"]
            description = f"章節 Phase: {boss.get('章節', '未知')}"
            options.append(discord.SelectOption(label=label, description=description, value=value))
        self.add_item(BossSelect(options))

class BossTypeSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="請選擇 Boss 類型", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_type = self.values[0]
        boss_list = []
        data = boss_data_sets.get(selected_type, {})
        for boss in data.values():
            boss_list.append((boss, selected_type))
        if not boss_list:
            await interaction.response.send_message("該類型沒有敵人。", ephemeral=True)
            return
        friendly_label = boss_type_mapping.get(selected_type, {"label": selected_type.upper()})["label"]
        view = BossSelectView(boss_list)
        await interaction.response.edit_message(content=f" {friendly_label} 類型的 Boss:", view=view)

class BossTypeSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        options = []
        for boss_type in boss_data_sets.keys():
            mapping = boss_type_mapping.get(boss_type, {"label": boss_type.upper(), "description": f"選擇 {boss_type.upper()} 類型的敵人"})
            options.append(discord.SelectOption(label=mapping["label"], value=boss_type, description=mapping["description"]))
        self.add_item(BossTypeSelect(options))
# ====================================================

# 處理 >boss 指令
@bot.command()
async def boss(ctx, *, query: str = None):
    """查詢 Boss 相關資訊。"""
    if not query:
        # 當無輸入時，顯示所有類型敵人的下拉選單
        view = BossTypeSelectView()
        await ctx.send("請選擇 Boss 類型：", view=view)
        return

    result = find_boss(query)
    if not result:
        await ctx.send("❌ 未找到該 Boss，請檢查名稱是否正確！")
        return

    if isinstance(result, list):
        view = BossSelectView(result)
        await ctx.send("該關鍵詞的 Boss:", view=view)
    else:
        boss_info, boss_type = result
        embed = create_boss_embed(boss_info, boss_type)
        await ctx.send(embed=embed)

# 機器人啟動日誌
@bot.event
async def on_ready():
    logging.info(f"✅ 已登入為 {bot.user}")

# 運行機器人
bot.run(TOKEN)
