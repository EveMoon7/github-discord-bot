import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput  # 請確認 discord.py 版本 >= 2.0
import re
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

LV_CAP = 295

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
    """
    解析遊玩時長字串，返回以分鐘為單位的數值。
    若字串中含有「分」則視為分鐘，
    若含有「小時」或「时」則轉換為分鐘，
    若無單位則預設為小時。
    """
    token = token.strip()
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
    """
    根據遊玩時長計算技能點獎勵，依下列里程碑累計：
      15分、30分、1小時、2小時、3小時、4小時、5小時、6小時，各達成一項 +1pt
    """
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
    
    # 章節獎勵：若賬號最後章節>=8且小於11，加1點；若賬號最後章節>=11，加2點
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
    """
    能力值計算器只計算能力點數：
    能力點數 = (角色等級×2 + 賬號最高等級獎勵) + 四項 (戰神/坦克/後盾/輔助) 的能力獎勵
    """
    base_stat = stat_points(level) + max_lv_points(highest_level)
    ability_bonus_total = 0
    for count in [attacker, defender, supporter, breaker]:
        abil, _ = calc_combat_bonus(count)
        ability_bonus_total += abil
    return base_stat + ability_bonus_total

def parse_token(token, multiplier=1):
    token = token.strip()
    if token == "":
        return 0
    m = re.search(r'([\d\.]+)k', token, re.IGNORECASE)
    if m:
        num = float(m.group(1))
        return int(num * 1000)
    else:
        try:
            return int(token)
        except:
            return 0

# ----------------------------
# Discord Modal 與按鈕 View
# ----------------------------
class SkillCalcModal(Modal, title="托蘭技能點計算器"):
    # 第一個欄位：角色等級與賬號最高章節（用斜線區隔）
    level_info = TextInput(
        label="當前角色等級 / 賬號最高章節",
        placeholder="295 / 11",
        default="295 / 11"
    )
    # 第二個欄位：戰神/坦克/後盾/輔助 (上限200000)
    combat_record = TextInput(
        label="遊玩實績【戰神/坦克/後盾/輔助】 (上限200000)",
        placeholder="1000 / 1000 / 1000 / 1000",
        default="1000 / 1000 / 1000 / 1000"
    )
    # 第三個欄位：急救/戰死 (上限1000)
    help_record = TextInput(
        label="遊玩實績【急救/戰死 】(上限1000)",
        placeholder="1000 / 1000",
        default="1000 / 1000"
    )
    # 第四個欄位：精通技能(項) / 同時點滿的技能樹(株) / 連續遊玩(時長)
    mastery = TextInput(
        label="精通技能(項) / 同時點滿的技能樹(株) / 連續遊玩(時長)",
        placeholder="10項 / 3株 / 6小時",
        default="10項 / 3株 / 6小時"
    )
    # 第五個欄位：基地迷你遊戲-[黑騎士20k/卡牌10次/寵物競速3項] (Yes/No)
    mini_game = TextInput(
        label="基地迷你遊戲【黑騎士20k/卡牌10次/寵物競速3項】 (Yes/No)",
        placeholder="Yes / Yes / Yes",
        default="Yes / Yes / Yes"
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # 解析【角色等級 / 賬號最高章節】欄位
        account_info_val = self.level_info.value.strip()
        if "/" in account_info_val:
            parts = [p.strip() for p in account_info_val.split("/") if p.strip()]
            if len(parts) == 2:
                try:
                    level_val = int(parts[0] or "0")
                    # 此處最高等級與角色等級相同
                    highest_level_val = int(parts[0] or "0")
                    max_chapter = int(parts[1] or "0")
                except:
                    level_val = 0
                    highest_level_val = 0
                    max_chapter = 0
            else:
                level_val = 0
                highest_level_val = 0
                max_chapter = 0
        else:
            try:
                level_val = int(account_info_val)
                highest_level_val = level_val
                max_chapter = 0
            except:
                level_val = 0
                highest_level_val = 0
                max_chapter = 0
        
        # 解析【戰神/坦克/後盾/輔助】欄位
        combat_value = self.combat_record.value.strip()
        if "/" in combat_value:
            combat_tokens = [token.strip() for token in combat_value.split("/") if token.strip()]
        else:
            combat_tokens = combat_value.split()
        if len(combat_tokens) != 4:
            await interaction.response.send_message("戰神/坦克/後盾/輔助的輸入格式錯誤，請輸入4個數值", ephemeral=True)
            return
        attacker_rank = parse_token(combat_tokens[0])
        defender_rank = parse_token(combat_tokens[1])
        supporter_rank = parse_token(combat_tokens[2])
        breaker_rank = parse_token(combat_tokens[3])
        
        # 解析【急救/戰死】欄位
        help_value = self.help_record.value.strip()
        if "/" in help_value:
            help_tokens = [token.strip() for token in help_value.split("/") if token.strip()]
        else:
            help_tokens = help_value.split()
        if len(help_tokens) != 2:
            await interaction.response.send_message("急救/戰死的輸入格式錯誤，請輸入2個數值", ephemeral=True)
            return
        first_aid = parse_token(help_tokens[0])
        KO = parse_token(help_tokens[1])
        
        # 解析【精通技能/點滿技能樹/連續遊玩】欄位
        mastery_value = self.mastery.value.strip()
        if "/" in mastery_value:
            mastery_tokens = [token.strip() for token in mastery_value.split("/") if token.strip()]
        else:
            mastery_tokens = mastery_value.split()
        mastered_skills = 0
        mastered_trees = 0
        play_time_minutes = 0
        if len(mastery_tokens) == 3:
            try:
                mastered_skills = int(re.search(r'\d+', mastery_tokens[0]).group())
            except:
                mastered_skills = 0
            try:
                mastered_trees = int(re.search(r'\d+', mastery_tokens[1]).group())
            except:
                mastered_trees = 0
            play_time_minutes = parse_play_time(mastery_tokens[2])
        else:
            for token in mastery_tokens:
                if "精通" in token:
                    try:
                        mastered_skills = int(token.split(":")[1] or "0")
                    except:
                        mastered_skills = 0
                elif "同時" in token:
                    try:
                        mastered_trees = int(token.split(":")[1] or "0")
                    except:
                        mastered_trees = 0
                elif "連續" in token or "遊玩" in token:
                    play_time_minutes = parse_play_time(token)
        play_time_bonus = calc_play_time_bonus(play_time_minutes)
        
        # 解析【基地迷你遊戲】欄位，依照 "/" 分割
        mini_tokens = [token.strip() for token in self.mini_game.value.split("/") if token.strip()]
        if len(mini_tokens) == 3:
            minigame_bk = "yes" in mini_tokens[0].lower()
            minigame_cg = "yes" in mini_tokens[1].lower()
            minigame_pet = "yes" in mini_tokens[2].lower()
        else:
            minigame_bk = minigame_cg = minigame_pet = False
        
        # 計算點數，calculate_points 回傳 (能力點數, 技能點數)
        _, skill_total = calculate_points(
            level_val, highest_level_val,
            attacker_rank, defender_rank, supporter_rank, breaker_rank,
            first_aid, KO,
            max_chapter, minigame_bk, minigame_cg, minigame_pet,
            mastered_skills, mastered_trees, play_time_bonus
        )
        
        description = f"**━━✨達成結果✨━━**\n\n"
        description += f"技能點數 = {skill_total}\n\n"
        description += f"↓勛章點數條件查詢↓\n"
        description += "[永久強化類勛章整理](https://wiki2.gamer.com.tw/wiki.php?n=72740:%E6%B0%B8%E4%B9%85%E5%BC%B7%E5%8C%96%E9%A1%9E%E5%8B%B3%E7%AB%A0%E6%95%B4%E7%90%86&ss=72740&f=M)"
        
        result_embed = discord.Embed(
            title="★⋆｡ 技能點數點數計算器 ｡⋆★",
            description=description,
            color=0xFFC0CB
        )
        result_embed.set_thumbnail(url="https://i.imgur.com/rO0Sp2P.png")
        result_embed.set_footer(text="※ 功能測試中，有bug可以回報月醬本體")
        await interaction.response.edit_message(embed=result_embed, view=None)

class AbilityCalcModal(Modal, title="托蘭能力值計算器"):
    # 角色等級
    level = TextInput(
        label="當前角色等級",
        placeholder="Lv.?",
        default="295"
    )
    # 賬號最高等級
    account_info = TextInput(
        label="賬號最高等級",
        placeholder="295",
        default="295"
    )
    # 遊玩實績(戰神/坦克/後盾/輔助)，上限各為 100
    combat_stats = TextInput(
        label="遊玩實績【戰神/坦克/後盾/輔助】 (上限: 100)",
        placeholder="100 / 100 / 100 / 100",
        default="100 / 100 / 100 / 100"
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            level_val = int(self.level.value.strip() or "0")
        except:
            level_val = LV_CAP
        try:
            highest_level_val = int(self.account_info.value.strip() or "0")
        except:
            highest_level_val = level_val
        
        combat_value = self.combat_stats.value.strip()
        if "/" in combat_value:
            tokens = [token.strip() for token in combat_value.split("/") if token.strip()]
        else:
            tokens = combat_value.split()
        if len(tokens) != 4:
            await interaction.response.send_message("遊玩實績輸入格式錯誤，請輸入4個數值", ephemeral=True)
            return
        
        try:
            attacker = parse_token(tokens[0])
            defender = parse_token(tokens[1])
            supporter = parse_token(tokens[2])
            breaker = parse_token(tokens[3])
        except:
            await interaction.response.send_message("數值解析錯誤", ephemeral=True)
            return
        
        ability_total = calculate_ability_points(level_val, highest_level_val, attacker, defender, supporter, breaker)
        
        description = f"**━━✨達成結果✨━━**\n\n"
        description += f"能力點數 = {ability_total}\n\n"
        description += f"↓勛章點數條件查詢↓\n"
        description += "[永久強化類勛章整理](https://wiki2.gamer.com.tw/wiki.php?n=72740:%E6%B0%B8%E4%B9%85%E5%BC%B7%E5%8C%96%E9%A1%9E%E5%8B%B3%E7%AB%A0%E6%95%B4%E7%90%86&ss=72740&f=M)"
        
        result_embed = discord.Embed(
            title="★⋆｡ 能力值點數計算器 ｡⋆★",
            description=description,
            color=0xFFC0CB
        )
        result_embed.set_thumbnail(url="https://i.imgur.com/rO0Sp2P.png")
        result_embed.set_footer(text="※ 功能測試中，有bug可以回報月醬本體")
        await interaction.response.edit_message(embed=result_embed, view=None)

class CalcView(View):
    @discord.ui.button(label="技能點計算器", style=discord.ButtonStyle.primary)
    async def skill_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SkillCalcModal())
    
    @discord.ui.button(label="能力值計算器", style=discord.ButtonStyle.primary)
    async def ability_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AbilityCalcModal())

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

@bot.command()
async def calc(ctx):
    view = CalcView()
    await ctx.send("", view=view)

bot.run(TOKEN)
