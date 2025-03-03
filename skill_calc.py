import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput  # 請確認 discord.py 版本 >= 2.0
import re
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

LV_CAP = 295

# ----------------------------
# 輔助函式：從字串中擷取數字 (預設回傳值 1)
# ----------------------------
def extract_number(s: str, default: int = 1) -> int:
    m = re.search(r'\d+', s)
    if m:
        return int(m.group())
    return default

# ----------------------------
# 安全解析函式：若輸入以 "-" 開頭則回傳 fallback
# ----------------------------
def safe_parse_token(token, multiplier=1, fallback=0):
    token = token.strip()
    if token.startswith("-"):
        return fallback
    return parse_token(token, multiplier)

# ----------------------------
# 基礎計算函式
# ----------------------------
def stat_points(level: int) -> int:
    return level * 2

def max_lv_points(level: int) -> int:
    if level >= 5:
        return 5 * (((level - 5) // 10) + 1)
    return 0

def skill_points(level: int) -> int:
    return level + (level // 5)

# ----------------------------
# 里程碑取值與獎勵計算（戰神、坦克、後盾、輔助）
# ----------------------------
def effective_combat_count(count: int) -> int:
    if count < 10:
        return 0
    elif count < 100:
        return 10
    elif count < 1000:
        return 100
    elif count < 10000:
        return 1000
    elif count < 100000:
        return 10000
    elif count < 200000:
        return 100000
    else:
        return 200000

def calc_combat_bonus(count: int) -> (int, int):
    effective = effective_combat_count(count)
    ability_bonus = 5 if effective >= 100 else 0
    skill_bonus = (1 if effective >= 10 else 0) \
                  + (1 if effective >= 1000 else 0) \
                  + (1 if effective >= 10000 else 0) \
                  + (1 if effective >= 100000 else 0) \
                  + (1 if effective >= 200000 else 0)
    return ability_bonus, skill_bonus

# ----------------------------
# 里程碑取值與獎勵計算（急救與戰死）
# ----------------------------
def effective_help_count(count: int) -> int:
    if count < 100:
        return 0
    elif count < 400:
        return 100
    elif count < 700:
        return 400
    elif count < 1000:
        return 700
    else:
        return 1000

def calc_help_bonus(count: int) -> int:
    effective = effective_help_count(count)
    bonus = (1 if effective >= 100 else 0) \
            + (1 if effective >= 400 else 0) \
            + (1 if effective >= 700 else 0) \
            + (1 if effective >= 1000 else 0)
    return bonus

# ----------------------------
# 遊玩時長解析與獎勵計算
# ----------------------------
def parse_play_time(token: str) -> int:
    token = token.strip()
    if token.startswith("-"):
        return 0
    m = re.search(r'(\d+)', token)
    if not m:
        return 0
    value = int(m.group(1))
    if '分' in token:
        return value
    elif '小時' in token or '时' in token:
        return value * 60
    else:
        return value * 60

def calc_play_time_bonus(minutes: int) -> int:
    thresholds = [15, 30, 60, 120, 180, 240, 300, 360]
    bonus = 0
    for t in thresholds:
        if minutes >= t:
            bonus += 1
    return bonus

# ----------------------------
# 總點數計算（技能點數、能力點數）
# ----------------------------
def calculate_points(level: int, highest_level: int,
                     attacker_rank, defender_rank, supporter_rank, breaker_rank,
                     first_aid, KO,
                     max_chapter, minigame_bk, minigame_cg, minigame_pet,
                     mastered_skills, mastered_trees, play_time_bonus) -> (int, int):
    base_stat = stat_points(level) + max_lv_points(highest_level)
    base_skill = skill_points(level)
    
    abil_bonus_total = 0
    skill_bonus_total = 0
    for count in [attacker_rank, defender_rank, supporter_rank, breaker_rank]:
        abil, skl = calc_combat_bonus(count)
        abil_bonus_total += abil
        skill_bonus_total += skl

    help_bonus = calc_help_bonus(first_aid) + calc_help_bonus(KO)
    
    if int(max_chapter) >= 11:
        chapter_bonus = 2
    elif int(max_chapter) >= 8:
        chapter_bonus = 1
    else:
        chapter_bonus = 0

    other_bonus = chapter_bonus + int(mastered_skills) + int(mastered_trees) + play_time_bonus
    mini_bonus = (1 if minigame_bk else 0) + (1 if minigame_cg else 0) + (1 if minigame_pet else 0)
    
    stat_total = base_stat + abil_bonus_total
    skill_total = base_skill + skill_bonus_total + help_bonus + other_bonus + mini_bonus
    return stat_total, skill_total

def calculate_ability_points(level: int, highest_level: int,
                             attacker, defender, supporter, breaker) -> int:
    base_stat = stat_points(level) + max_lv_points(highest_level)
    ability_bonus_total = 0
    for count in [attacker, defender, supporter, breaker]:
        abil, _ = calc_combat_bonus(count)
        ability_bonus_total += abil
    return base_stat + ability_bonus_total

# ----------------------------
# 修正後的 parse_token 函式，能夠正確解析 "1000aaa" 這種情況
# ----------------------------
def parse_token(token, multiplier=1):
    token = token.strip()
    if token == "" or token.startswith("-"):
        return 0
    # 檢查是否有 k 的縮寫，表示千
    m = re.search(r'([\d\.]+)k', token, re.IGNORECASE)
    if m:
        try:
            num = float(m.group(1))
            return int(num * 1000 * multiplier)
        except:
            return 0
    num = extract_number(token, 0)
    return num * multiplier

# ----------------------------
# Discord Modal 與按鈕 View
# ----------------------------
class SkillCalcModal(Modal, title="托蘭技能點計算器"):
    level_info = TextInput(
        label="當前角色等級 / 賬號最高章節",
        placeholder="Lv.? / 章節",
        default="Lv295 / 11章",
        required=False
    )
    combat_record = TextInput(
        label="遊玩實績【戰神/坦克/後盾/輔助】 (上限200000)",
        placeholder="",
        default="1000 / 1000 / 1000 / 1000",
        required=False
    )
    help_record = TextInput(
        label="遊玩實績【急救/戰死】 (上限1000)",
        placeholder="",
        default="1000 / 1000",
        required=False
    )
    mastery = TextInput(
        label="精通技能(項) / 同時點滿的技能樹(株) / 連續遊玩(時長)",
        placeholder="",
        default="10項 / 3株 / 6小時",
        required=False
    )
    mini_game = TextInput(
        label="基地迷你遊戲【黑騎士20k/卡牌30積分/寵物競速3項】 (Yes/No)",
        placeholder="",
        default="Yes / Yes / Yes",
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # 解析等級與最高章節（若輸入以 "-" 開頭則預設為 1）
        account_info_val = self.level_info.value.strip() or "1 / 1"
        parts = [p.strip() for p in account_info_val.split("/")]
        while len(parts) < 2:
            parts.append("1")
        current_level = 1 if parts[0].startswith("-") else extract_number(parts[0])
        max_chapter = 1 if parts[1].startswith("-") else extract_number(parts[1])
        # footed 章節上限為 11
        max_chapter_disp = min(max_chapter, 11)
        
        # 解析戰績數值（若輸入以 "-" 開頭則設定為 0）
        combat_value = self.combat_record.value.strip() or "0 0 0 0"
        if "/" in combat_value:
            combat_tokens = [t.strip() for t in combat_value.split("/")]
        else:
            combat_tokens = combat_value.split()
        while len(combat_tokens) < 4:
            combat_tokens.append("0")
        attacker_rank = safe_parse_token(combat_tokens[0], fallback=0)
        defender_rank = safe_parse_token(combat_tokens[1], fallback=0)
        supporter_rank = safe_parse_token(combat_tokens[2], fallback=0)
        breaker_rank = safe_parse_token(combat_tokens[3], fallback=0)
        
        # 解析急救/戰死
        help_value = self.help_record.value.strip() or "0 0"
        if "/" in help_value:
            help_tokens = [t.strip() for t in help_value.split("/")]
        else:
            help_tokens = help_value.split()
        while len(help_tokens) < 2:
            help_tokens.append("0")
        first_aid = safe_parse_token(help_tokens[0], fallback=0)
        KO = safe_parse_token(help_tokens[1], fallback=0)
        
        # 解析精通技能、技能樹、遊玩時長（若輸入以 "-" 開頭則設定為 0）
        mastery_value = self.mastery.value.strip() or "0項 0株 0小時"
        if "/" in mastery_value:
            mastery_tokens = [t.strip() for t in mastery_value.split("/")]
        else:
            mastery_tokens = mastery_value.split()
        while len(mastery_tokens) < 3:
            mastery_tokens.append("0")
        try:
            mastered_skills = 0 if mastery_tokens[0].startswith("-") else int(re.search(r'\d+', mastery_tokens[0]).group())
        except:
            mastered_skills = 0
        try:
            mastered_trees = 0 if mastery_tokens[1].startswith("-") else int(re.search(r'\d+', mastery_tokens[1]).group())
        except:
            mastered_trees = 0
        play_time_minutes = parse_play_time(mastery_tokens[2])
        play_time_bonus = calc_play_time_bonus(play_time_minutes)
        # 轉換為小時（若非整數則保留 1 位小數）
        play_time_hours = play_time_minutes / 60
        if play_time_hours.is_integer():
            play_time_hours = int(play_time_hours)
        else:
            play_time_hours = round(play_time_hours, 1)
        
        # 將精通技、技能樹與遊玩時間分別上限顯示為 10、3 與 6
        mastered_skills_disp = min(mastered_skills, 10)
        mastered_trees_disp = min(mastered_trees, 3)
        play_time_hours_disp = min(play_time_hours, 6)
        
        # 解析基地迷你遊戲，轉為 Yes/No
        mini_game_value = self.mini_game.value.strip() or "No No No"
        if "/" in mini_game_value:
            mini_tokens = [t.strip() for t in mini_game_value.split("/")]
        else:
            mini_tokens = mini_game_value.split()
        while len(mini_tokens) < 3:
            mini_tokens.append("No")
        minigame_bk = "Yes" if "yes" in mini_tokens[0].lower() else "No"
        minigame_cg = "Yes" if "yes" in mini_tokens[1].lower() else "No"
        minigame_pet = "Yes" if "yes" in mini_tokens[2].lower() else "No"
        
        # 計算技能點數
        _, skill_total = calculate_points(
            current_level, current_level,
            attacker_rank, defender_rank, supporter_rank, breaker_rank,
            first_aid, KO,
            max_chapter, (minigame_bk=="Yes"), (minigame_cg=="Yes"), (minigame_pet=="Yes"),
            mastered_skills, mastered_trees, play_time_bonus
        )
        
        # 限制 footed 數值上限
        attacker_disp = min(attacker_rank, 200000)
        defender_disp = min(defender_rank, 200000)
        supporter_disp = min(supporter_rank, 200000)
        breaker_disp = min(breaker_rank, 200000)
        first_aid_disp = min(first_aid, 1000)
        KO_disp = min(KO, 1000)
        
        description = f"**━━✨達成結果✨━━**\n\n**技能點數 = {skill_total}**\n**━━━━━━━━━━━━**"
        
        result_embed = discord.Embed(
            title="★⋆｡ 技能點數計算器 ｡⋆★",
            description=description,
            color=0xFFC0CB
        )
        result_embed.set_thumbnail(url="https://i.imgur.com/rO0Sp2P.png")
        
        # footer 顯示解析後的數據
        footer_text = (
            f"角色等級: {current_level} / 達成章節: {max_chapter_disp}\n"
            f"戰/坦/後/輔: {attacker_disp}/{defender_disp}/{supporter_disp}/{breaker_disp}\n"
            f"急救/戰死: {first_aid_disp}/{KO_disp}\n"
            f"精通技能: {mastered_skills_disp}項 / 同時點滿技能樹: {mastered_trees_disp}株 / 連續遊玩: {play_time_hours_disp}小時+\n"
            f"黑騎士20k: {minigame_bk}  卡牌30積分: {minigame_cg}  寵競3項: {minigame_pet}"
        )
        result_embed.set_footer(text=footer_text)
        
        await interaction.response.edit_message(embed=result_embed, view=None)

class AbilityCalcModal(Modal, title="托蘭能力值計算器"):
    level = TextInput(
        label="當前角色等級",
        placeholder="Lv.?",
        default="Lv295",
        required=False
    )
    account_info = TextInput(
        label="賬號最高等級",
        placeholder="Lv.?",
        default="Lv295",
        required=False
    )
    combat_stats = TextInput(
        label="遊玩實績【戰神/坦克/後盾/輔助】 (上限100)",
        placeholder="",
        default="100 / 100 / 100 / 100",
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        level_str = self.level.value.strip() or "1"
        account_str = self.account_info.value.strip() or "1"
        level_val = 1 if level_str.strip().startswith("-") else extract_number(level_str)
        highest_level_val = 1 if account_str.strip().startswith("-") else extract_number(account_str)
        
        combat_value = self.combat_stats.value.strip() or "0 0 0 0"
        if "/" in combat_value:
            tokens = [t.strip() for t in combat_value.split("/")]
        else:
            tokens = combat_value.split()
        while len(tokens) < 4:
            tokens.append("0")
        try:
            attacker = safe_parse_token(tokens[0], fallback=0)
            defender = safe_parse_token(tokens[1], fallback=0)
            supporter = safe_parse_token(tokens[2], fallback=0)
            breaker = safe_parse_token(tokens[3], fallback=0)
        except:
            await interaction.response.send_message("數值解析錯誤", ephemeral=True)
            return
        
        ability_total = calculate_ability_points(level_val, highest_level_val, attacker, defender, supporter, breaker)
        
        # 限制 footed 戰/坦/後/輔上限為 100
        attacker_disp = min(attacker, 100)
        defender_disp = min(defender, 100)
        supporter_disp = min(supporter, 100)
        breaker_disp = min(breaker, 100)
        
        description = f"**━━✨達成結果✨━━**\n\n**能力點數 = {ability_total}**\n**━━━━━━━━━━━━**"
        
        result_embed = discord.Embed(
            title="★⋆｡ 能力值計算器 ｡⋆★",
            description=description,
            color=0xFFC0CB
        )
        result_embed.set_thumbnail(url="https://i.imgur.com/rO0Sp2P.png")
        
        footer_text = (
            f"角色等級: {level_val}\n"
            f"賬號最高等級: {highest_level_val}\n"
            f"戰/坦/後/輔: {attacker_disp}/{defender_disp}/{supporter_disp}/{breaker_disp}"
        )
        result_embed.set_footer(text=footer_text)
        
        await interaction.response.edit_message(embed=result_embed, view=None)

class CalcView(View):
    def __init__(self, author):
        super().__init__()
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("要自己>calc喵～", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="技能點數計算器", style=discord.ButtonStyle.primary)
    async def skill_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SkillCalcModal())
    
    @discord.ui.button(label="能力點數計算器", style=discord.ButtonStyle.primary)
    async def ability_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AbilityCalcModal())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

@bot.command()
async def calc(ctx):
    view = CalcView(ctx.author)
    await ctx.send("", view=view)

bot.run(TOKEN)
