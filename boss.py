import json
import discord
import unicodedata
import logging
import os
import sys
from discord.ext import commands

# 載入 .env 檔案

logging.basicConfig(level=logging.INFO)

# 注意：切勿將 token 直接硬編碼在程式內，請用環境變數或 .env 檔存取！
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ 請先設定環境變數 DISCORD_BOT_TOKEN ！")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=">", intents=intents, case_insensitive=True)

def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).lower().strip()

def load_json(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"❌ 讀取 {filename} 時發生錯誤: {e}")
        return {}

# 載入各類 Boss 資料
main_quest_boss_data = load_json("Main_Quest_Boss_Data.json")
high_difficulty_boss_data = load_json("High_Difficulty_Boss_Data.json")
event_boss_data = load_json("Event_Boss_Data.json")
guild_raid_boss_data = load_json("Guild_Raid_Boss_Data.json")
different_boss_data = load_json("Different_Boss_Data.json")

boss_data_sets = {
    "main": main_quest_boss_data,
    "high": high_difficulty_boss_data,
    "event": event_boss_data,
    "guild": guild_raid_boss_data,
    "different": different_boss_data
}

boss_type_mapping = {
    "main": {"label": "主線王", "description": "Main Quest Boss"},
    "high": {"label": "高難王", "description": "High Difficulty Boss"},
    "event": {"label": "活動王", "description": "Event Boss"},
    "guild": {"label": "公會王", "description": "Guild Raid Boss"},
    "different": {"label": "其他王", "description": "Different Boss"}
}

def find_boss(query: str):
    query_norm = normalize(query)
    ambiguous = []
    for boss_type, data in boss_data_sets.items():
        for boss in data.values():
            name_norm = normalize(boss.get("名稱", ""))
            aliases_norm = [normalize(alias) for alias in boss.get("別名", [])]
            if query_norm == name_norm or query_norm in aliases_norm:
                return boss, boss_type
            if query_norm in name_norm or any(query_norm in alias for alias in aliases_norm):
                ambiguous.append((boss, boss_type))
    if ambiguous:
        if len(ambiguous) == 1:
            return ambiguous[0]
        else:
            return ambiguous
    return None

def get_phase(boss_info):
    """
    取得 boss 的章節（若為字串且包含 "-"，只取 "-" 前面的部分）
    """
    raw_phase = boss_info.get("章節", "未知")
    raw_phase_str = str(raw_phase).strip()
    if "-" in raw_phase_str:
        return raw_phase_str.split("-")[0].strip()
    else:
        return raw_phase_str

def create_boss_embed(boss_info, boss_type):
    # 取得原始章節字串，若包含 "-" 只取前半部（用於回覆訊息）
    raw_phase = boss_info.get("章節", "未知")
    raw_phase_str = str(raw_phase).strip()
    if "-" in raw_phase_str:
        phase = raw_phase_str.split("-")[0].strip()
    else:
        phase = raw_phase_str

    friendly = boss_type_mapping.get(boss_type, {"label": boss_type.upper()})
    embed = discord.Embed(
        title=f"✧*。{friendly['label']} Boss: {boss_info.get('名稱', '未知')} 。*✧",
        description=f"❀ 章節 Chapter: {phase} ❀\n❀ 地點: {boss_info.get('地點', '未知')} ❀",
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

    crt_res = boss_info.get("暴抗", "N/A")
    if isinstance(crt_res, dict):
        crt_res = "\n".join([f"{k}: {v}" for k, v in crt_res.items()])
    else:
        crt_res = str(crt_res)
    embed.add_field(name="暴抗 Crt.Res", value=f"{crt_res}\n\u200b", inline=True)

    inertia_text = (
        f"物理: {boss_info.get('物理-慣性變動', 'N/A')}  "
        f"魔法: {boss_info.get('魔法-慣性變動', 'N/A')}  "
        f"普攻: {boss_info.get('普攻-慣性變動', 'N/A')}\n\u200b"
    )
    if boss_info.get("物理-慣性變動"):
        embed.add_field(name="慣性變動率 Proration", value=inertia_text, inline=False)


    if boss_info.get("物理-慣性變動-多"):
        embed.add_field(name="物理-慣性變動", value=f"{boss_info.get('物理-慣性變動-多')}", inline=True)
    if boss_info.get("魔法-慣性變動-多"):
        embed.add_field(name="魔法-慣性變動", value=f"{boss_info.get('魔法-慣性變動-多')}", inline=True)
    if boss_info.get("普攻-慣性變動-多"):
        embed.add_field(name="普攻-慣性變動", value=f"{boss_info.get('普攻-慣性變動-多')}\n\u200b", inline=True)
    

    if boss_info.get("控制"):
        embed.add_field(name="⋆˙ 控制 FTS ˙⋆", value=f"{boss_info.get('控制')}\n\u200b", inline=False)
    if boss_info.get("階段"):
        embed.add_field(name="⋆˙ 階段/模式 Phase ˙⋆", value=f"{boss_info.get('階段')}\n\u200b", inline=False)
    if boss_info.get("異常"):
        embed.add_field(name="⋆˙ 異常狀態 Status Ailment ˙⋆", value=f"{boss_info.get('異常')}\n\u200b", inline=False)
    if boss_info.get("破位效果"):
        embed.add_field(name="⋆˙ 破位效果 Break Effect˙⋆", value=f"{boss_info.get('破位效果')}\n\u200b", inline=False)
    if boss_info.get("傷害上限 (MaxHP)"):
        embed.add_field(name="⋆˙ 傷害上限 ˙⋆", value=f"{boss_info.get('傷害上限 (MaxHP)')}\n\u200b", inline=False)
    if boss_info.get("注意"):
        embed.add_field(name="⋆˙ 注意 Notice ˙⋆", value=f"{boss_info.get('注意')}\n\u200b", inline=False)

    if boss_info.get("圖片"):
        embed.set_image(url=boss_info["圖片"])

    if boss_type in ("main", "event", "different"):
        embed.set_footer(text="✧*。 難度倍率 Difficulty 。*✧\n"
                           "EASY = 0.1 x 防禦 | 迴避\n"
                           "NORMAL = 1 x 防禦 | 迴避\n"
                           "HARD = 2 x 防禦 | 迴避\n"
                           "NIGHTMARE = 4 x 防禦 | 迴避\n"
                           "ULTIMATE = 6 x 防禦 | 迴避")
    return embed

# ===== 限制只有原指令使用者能操作互動選單 =====

class RestrictedView(discord.ui.View):
    def __init__(self, author: discord.User, timeout: float = None):
        super().__init__(timeout=timeout)
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("要使用該指令需要自己>boss喔~", ephemeral=True)
            return False
        return True

class BackButton(discord.ui.Button):
    def __init__(self, author: discord.User):
        super().__init__(label="← 後退", style=discord.ButtonStyle.secondary)
        self.author = author

    async def callback(self, interaction: discord.Interaction):
        view = BossTypeSelectView(self.author)
        await interaction.response.edit_message(content="連自己要打什麼 Boss 都不知道，真是雜魚主人~", embed=None, view=view)

class BossSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="請選擇一個 Boss", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        boss_info, boss_type = self.view.boss_mapping[selected_value]
        embed = create_boss_embed(boss_info, boss_type)
        await interaction.response.edit_message(content=None, embed=embed, view=None)

class BossSelectView(RestrictedView):
    def __init__(self, author: discord.User, boss_results):
        super().__init__(author, timeout=None)
        self.boss_mapping = {}
        options = []
        for idx, (boss, boss_type) in enumerate(boss_results):
            value = str(idx)
            self.boss_mapping[value] = (boss, boss_type)
            label = boss.get("名稱", "未知")
            # 調整描述：顯示 "章節 Chapter (章節)"
            description = f"章節 Chapter {boss.get('章節', '未知')}"
            options.append(discord.SelectOption(label=label, description=description, value=value))
        self.add_item(BossSelect(options))
        self.add_item(BackButton(author))

# 新增：主線王的章節子選單
class MainPhaseSelect(discord.ui.Select):
    def __init__(self, options, author: discord.User, main_boss_data: dict):
        # placeholder 改為「選擇章節 Select Chapter」
        super().__init__(placeholder="選擇章節 Select Chapter", min_values=1, max_values=1, options=options)
        self.author = author
        self.main_boss_data = main_boss_data

    async def callback(self, interaction: discord.Interaction):
        selected_phase = self.values[0]
        filtered = []
        for boss in self.main_boss_data.values():
            if get_phase(boss) == selected_phase:
                filtered.append((boss, "main"))
        if not filtered:
            await interaction.response.send_message("該章節沒有敵人。", ephemeral=True)
            return
        view = BossSelectView(self.author, filtered)
        # 回覆訊息保持為 "主線王 Main Quest Boss - 章節 Chapter (章節)"
        await interaction.response.edit_message(content=f"章節 Chapter {selected_phase} | 是這裡嗎~(翻地圖", view=view)

class MainPhaseSelectView(RestrictedView):
    def __init__(self, author: discord.User):
        super().__init__(author, timeout=None)
        main_boss = boss_data_sets["main"]
        phase_to_bosses = {}
        for boss in main_boss.values():
            phase = get_phase(boss)
            phase_to_bosses.setdefault(phase, []).append(boss)
        def sort_key(p):
            try:
                return float(p)
            except:
                return p
        sorted_phases = sorted(phase_to_bosses.keys(), key=sort_key, reverse=True)
        options = []
        for phase in sorted_phases:
            boss_list = phase_to_bosses[phase]
            # 將每個 boss 的中文別名（取 "別名" 欄位第一項）串聯，以逗號分隔
            alias_list = []
            for boss in boss_list:
                aliases = boss.get("別名", [])
                if aliases:
                    alias_list.append(aliases[0])
                else:
                    alias_list.append(boss.get("名稱", "未知"))
            desc = ", ".join(alias_list)
            options.append(discord.SelectOption(
                label=f"章節 Chapter: {phase}",
                value=phase,
                description=desc
            ))
        self.add_item(MainPhaseSelect(options, author, main_boss))
        self.add_item(BackButton(author))

class BossTypeSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="請選擇 Boss 類型", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_type = self.values[0]
        if selected_type == "main":
            view = MainPhaseSelectView(interaction.user)
            await interaction.response.edit_message(content="女僕雷達尋找中 ~", view=view)
        else:
            boss_list = []
            data = boss_data_sets.get(selected_type, {})
            for boss in data.values():
                boss_list.append((boss, selected_type))
            if not boss_list:
                await interaction.response.send_message("該類型沒有敵人。", ephemeral=True)
                return
            friendly_label = boss_type_mapping.get(selected_type, {"label": selected_type.upper()})["label"]
            view = BossSelectView(interaction.user, boss_list)
            await interaction.response.edit_message(content=f"{friendly_label} 類型的 Boss:", view=view)

class BossTypeSelectView(RestrictedView):
    def __init__(self, author: discord.User):
        super().__init__(author, timeout=None)
        options = []
        for boss_type in boss_data_sets.keys():
            mapping = boss_type_mapping.get(
                boss_type,
                {"label": boss_type.upper(), "description": f"選擇 {boss_type.upper()} 類型的敵人"}
            )
            options.append(discord.SelectOption(label=mapping["label"], value=boss_type, description=mapping["description"]))
        self.add_item(BossTypeSelect(options))

# ============================================

@bot.command()
async def boss(ctx, *, query: str = None):
    """查詢 Boss 相關資訊。"""
    if not query:
        view = BossTypeSelectView(ctx.author)
        await ctx.send("♡ 祝主人凱旋而歸 ~ ", view=view)
        return

    result = find_boss(query)
    if not result:
        await ctx.send("❌ 未找到該 Boss，請檢查名稱是否正確！")
        return

    if isinstance(result, list):
        view = BossSelectView(ctx.author, result)
        await ctx.send("該關鍵詞的 Boss:", view=view)
    else:
        boss_info, boss_type = result
        embed = create_boss_embed(boss_info, boss_type)
        await ctx.send(embed=embed)

@bot.event
async def on_ready():
    logging.info(f"✅ 已登入為 {bot.user}")

bot.run(TOKEN)
