import re
import math
import discord
from discord.ext import commands
import os

# ─────────────────────────────
# TOKEN（請將下面的 TOKEN 替換成您的 Bot Token）
# ─────────────────────────────
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# ─────────────────────────────
# 定義「皇魔前遺跡」任務的常數
EMPEROR_RELIC_TASK_INDEX = 9       # 在 Chapter 9 中，【皇魔前遺跡】任務的任務序號
EMPEROR_RELIC_BONUS = 12500000       # 【皇魔前遺跡】任務的 bonus 經驗

# ─────────────────────────────
# 解析用戶輸入的等級與進度，支持多種格式：
def parse_level_progress(s: str) -> (int, float):
    s = s.strip()
    pattern = r"^\s*(?:Lv\s*)?(\d+)(?:\s*(?:\(\s*(\d+)\s*%?\s*\)|\s+(\d+)%?))?\s*$"
    match = re.search(pattern, s, re.IGNORECASE)
    if match:
        level = int(match.group(1))
        if match.group(2) is not None:
            progress = float(match.group(2))
        elif match.group(3) is not None:
            progress = float(match.group(3))
        else:
            progress = 0.0
        return level, progress
    else:
        raise ValueError("無法解析等級和進度，請檢查格式。")

# ─────────────────────────────
# 輔助函式：將 xp 轉為數值（若 xp 為 tuple 則相加）
def xp_to_int(xp):
    if isinstance(xp, tuple):
        return xp[0] + xp[1]
    return xp

# ─────────────────────────────
# 計算每一級所需的 XP，並使用 floor() 取整，使其符合遊戲公式：
def get_xp(lv: int) -> int:
    return math.floor(0.025 * (lv ** 4) + 2 * lv)

def get_total_xp(begin: int, begin_percentage: float, end: int) -> float:
    xp = (1 - begin_percentage / 100) * get_xp(begin)
    for i in range(begin + 1, end):
        xp += get_xp(i)
    return xp

# 此函式計算從指定 (level, progress) 到 target 所需的 EXP
def required_xp_from_level(from_lv: int, from_progress: float, target_lv: int, target_progress: float) -> float:
    if from_lv == target_lv:
        return max(0, (target_progress - from_progress) / 100 * get_xp(from_lv))
    xp = (1 - from_progress / 100) * get_xp(from_lv)
    for i in range(from_lv + 1, target_lv):
        xp += get_xp(i)
    xp += (target_progress / 100) * get_xp(target_lv)
    return xp

def add_xp(begin: int, begin_percentage: float, extra_xp: float) -> (int, float):
    remaining_xp = extra_xp
    xp_required_next = (1 - begin_percentage / 100) * get_xp(begin)
    if extra_xp < xp_required_next:
        current_xp = (begin_percentage / 100) * get_xp(begin) + extra_xp
        return begin, 100 * current_xp / get_xp(begin)
    else:
        remaining_xp -= xp_required_next
        lv = begin + 1
        while get_xp(lv) <= remaining_xp:
            remaining_xp -= get_xp(lv)
            lv += 1
        lv_percentage = 100 * remaining_xp / get_xp(lv)
        return lv, lv_percentage

# ─────────────────────────────
# 主線任務資料（mq_data）
mq_data = {
    "Chapter 1 混沌的序幕": "",
    "陌生的街道與人群 First Time Visit": 30,
    "斯特列兄妹 Straye Brother and Sister": 80,
    "魔像暴動 A Golem on a Rampage": 730,
    "智慧女神 The Goddess of Wisdom": 2050,
    "湧龍穴 The Dragon's Den": 4700,
    "廢棄的寺院 The Ruined Temple": 9330,
    "最初的魔石 The First Magic Stone": 16700,
    "滅帳香 Purification Incense": 27900,
    "龍與黑色結晶 The Dragon and Black Crystal": 43000,
    "Chapter 2 神聖晶石騷動記": "",
    "不請自來的商人女孩 The Merchant Girl": 64000,
    "尋找神聖晶石 Where Are the Gems?": 92000,
    "神秘的黑騎士 Who is the Black Knight?!": 118200,
    "新月鬼殿的試煉 Trials in the Palace": 149000,
    "月之魔導師 The Moon Wizard": 172000,
    "敬之，恨之 The Follower and Hater": 227000,
    "魔導士的洞穴 The Wizard's Cave": 240000,
    "星之魔導士 The Star Wizard": 255000,
    "Chapter 3 舊神之戰": "",
    "最強大的勁敵?? The Invincible... Enemy??": 270000,
    "上古女帝 The Ancient Empress": 284000,
    "襲擊犯的真面目 The Culprit": 319000,
    "堡壘的存亡 Fate of the Fortress": 335000,
    "回憶於消失的城鎮 Memory in the Lost Town": 398000,
    "被奪走的聖魔晶石 The Stolen Sorcery Gem": 417000,
    "與龍群居的人民 Living with a Dragon": 462300,
    "來自異界的異形 Monsters from Outerworld": 540000,
    "Chapter 4 新的黑影": "",
    "魔法族人迪魯 The Mage Diels": 562000,
    "流離只為再興 Journey for Reconstruction": 585000,
    "阿卡克的聖寶石 The Sacred Gem in Akaku": 710000,
    "達魯剛國王 The King of Darkan": 740000,
    "暗雲湧動的處理廠 The Lurking Evil": 803000,
    "捉捕冒牌黑騎士！ Find the False Black Knight!": 913000,
    "泰尼斯塔初現Technista's Movement": 1000000,
    "飄零的死亡之羽 The Falling Feather of Death": 1100000,
    "Chapter 5 席卷黑暗的風暴": "",
    "未知的黑暗中 In The Unknown Darkness": 1150000,
    "符咒的下落 The Charm": 1310000,
    "乾涸的暗之鏡 Parching Dark Mirror": 1370000,
    "激戰昇華觀園 Fierce Battle in the Garden": 1550000,
    "照射黑暗之光 A Light in the Darkness": 1750000,
    "盤據暗之館的怪物 The Ones Nesting in the Manor": 1970000,
    "暗之城 The Dark Castle": 2210000,
    "前往眾生世界 To The Living World": 2220000,
    "Chapter 6 兩派泰尼斯塔": "",
    "戴米馬其納 Demi Machina": 2600000,
    "和平派城鎮 The Town of Pax Faction": 2700000,
    "機關亦有心 Mechanical Heart": 2800000,
    "激進派黑騎士 Black Knights of Lyark": 2820000,
    "神秘遺物 The Mysterious Artifact": 3030000,
    "遺物真相 Truth of the Artifact": 3099000,
    "背叛的代價 The Price of Treachery": 3320000,
    "褻瀆生命的工廠 The Blasphemous Factory": 3640000,
    "黑騎士之謎 Mystery of the Black Knights": 4020000,
    "Chapter 7 動亂的阿爾堤玫亞": "",
    "怪物之森 Monster's Forest": 4730000,
    "游擊隊的地下城市 The Underground Town": 4820000,
    "激進派領地內的艾路菲族 The Elves in Lyark": 5070000,
    "瘋狂的研究所 The Mad Laboratory": 5500000,
    "監獄裡的慘況 Tragedy in the Jail": 6000000,
    "多洛馬廣場的慘劇 Calamity in Droma Square": 6400000,
    "前往阿爾堤玫亞宮殿 Head for Ultimea Palace": 6900000,
    "混沌真相 The Chaotic Truth": 7400000,
    "Chapter 8 通往艾路登波姆之戰": "",
    "怪物棲息的礦道 The Mine Where Monsters Lurk": 8400000,
    "神秘人影 The Mysterious Shadow": 8500000,
    "迪魯族的新國度 The New Diel Country": 8600000,
    "眾神遺跡之處 The Ruins of the Gods": 8800000,
    "前代正義之神 The Former God of Justice": 9100000,
    "留在神殿的寶座 The Remaining Thrones in the Shrine": 9700000,
    "眾神之所在 Gods' Whereabouts": 10400000,
    "種子神殿內的等待者 The Wait at Specia's Shrine": 11100000,
    "冰雪中的守衛 The Warden of Ice & Snow": 11800000,
    "山脈中的盡頭 At Mountains' End": 12500000,
    "Chapter 9 艾路登波奪還戰": "",
    "通往艾路登波姆的險路 Deadly Road to Eldenbaum": 15800000,
    "意外的陷阱 Unforeseen Traps": 17100000,
    "進步的遺跡 Traces of Technological Progress": 18200000,
    "意外的熟人 An Unexpected Acquaintance": 19200000,
    "前線基地啟用 Front Line Base Operation": 20300000,
    "奪回樹上港口 Strategy to Redeem the Treetop Harbor": 21500000,
    "遺產是轉移裝置 The Teleporter Left Behind": 22700000,
    "一心尋死的男人 The Man Who Seeks Death": 23900000,
    # 注意：此處 Chapter 9 中的任務，序號為 EMPEROR_RELIC_TASK_INDEX (9) 的任務代表【皇魔前遺跡】
    # 若不跳過（skip_center=False）則獲得總經驗 (主要 xp + 皇魔前遺跡 bonus)，
    # 若跳過（skip_center=True）則僅採用主要 xp。
    "艾路登波奪還戰(皇魔前遺跡-可跳過) The Battle to Recapture Eldenbaum": "25000000,12500000",
    "新的開始 A New Beginning": 13000000,
    "Chapter 10 失落的神之舟": "",
    "向命運之地進發 Off to the Fateful Land": 26000000,
    "山崖下的占領者 The Inhabitants Under the Cliff": 27400000,
    "與噩夢重逢 The Nightmare Returns": 28800000,
    "消失僧侶的行蹤 The Whereabouts of the Missing Monks": 30200000,
    "勇敢女神與非法佔領之民 The Goddess of Justice and the Squatters": 31600000,
    "方舟掌舵人(怪物清剿-可跳過) Navigator of the Ark": "33100000 , 0",
    "森林中的魔女 Witch in the Woods": 34600000,
    "諾芙．蒂拉的決鬥 The Duel in Nov Diela": 36200000,
    "Chapter 11 前往托蘭": "",
    "方舟飛行 Flying the Ark": 37800000,
    "在未知的土地 Land of the Unknown": 49000000,
    "林中散步 The Strolling Forest": 51000000,
    "森之人尤馬諾 Eumanos the Forest Dwellers": 53400000,
    "發芽者 A Sproutling is Born": 55700000,
    "帶來恩惠者 The Blessing-Bearer": 58100000,
    "寇珥連生體要塞的激鬥 Intense Battle in Coenubia's Stronghold": 60500000,
    "燃煙山中影 The Shadow of a Smoky Mountain": 63000000,
    "龍人與地底世 The Weredragons & the Underground World": 65500000,
    "Chapter 12 龍人聖域": "",
    "有屋頂的天空 The Sky with a Ceiling": 73400000,
    "相剋的龍與龍人 Rivalry Between Dragons and Weredragons": 76300000,
    "帶孩子的龍人夫妻 Weredragon Couple and a Baby": 79300000,
    "龍人聖域 Weredragoon's Vital Point": 82300000,
    "推進機中的激戰 Intense Battle in Propulsion System": 85300000,
    "為了獲得新技術 Discovering a New Technology": 44200000,
    "修繕方舟 Ark Repair": 92700000,
    "龍人相爭 Weredragoon Dispute": 96000000,
    "冰牆中的繭 Cocoon in the Ice Wall": 99300000,
    "Chapter 13 水之民族、龍、寇珥連生體": "",
    "住在水中的民族 Underwater Inhabitants": 112600000,
    "水之穹頂 Water Dome": 116500000,
    "水中都市 Underwater City": 60200000,
    "廢棄區的潛伏者 The Thing in the Abandoned District": 125800000,
    "來自深海的影子 Shadow from the Abyss": 129900000,
    "冷酷無情的評議會 The Ruthless Council": 67000000,
    "神殿中的秘密 Mysterious Entity in the Little Shrine": 139900000,
    "水下決戰 The Great Battle Underwater": 144200000,
    "Chapter 14 托蘭本土": "",
    "本土上空的危機 Crisis in the Sky": 159100000,
    "倖存的尤馬諾兄妹 The Surviving Siblings": 164000000,
    "被擾亂的戰況 Chaotic Situation": 168900000,
    "苦澀的真相 The Bitter Truth": 173800000,
    "粗野的拉納族王子 The Uncouth Rana Prince": 178800000,
    "變異寇現連生體村 Mutant Coenubia Village": 183900000,
    "與變異利古希族的激戰 Fierce Battle with Mutant Lixis": 189000000
}

def build_chapters_dict(mq_data: dict) -> dict:
    chapters = {}
    current_chapter = None
    for key, value in mq_data.items():
        if key.startswith("Chapter"):
            parts = key.split(maxsplit=2)
            if len(parts) >= 3:
                chap_code = parts[0] + " " + parts[1]
                chap_title = parts[2]
            else:
                chap_code = key
                chap_title = ""
            chapters[chap_code] = {"title": chap_title, "tasks": []}
            current_chapter = chap_code
        else:
            if isinstance(value, str) and ',' in value:
                parts = value.split(',')
                main_xp = int(parts[0].strip())
                bonus_xp = int(parts[1].strip())
                xp_val = (main_xp, bonus_xp)
            else:
                xp_val = int(value) if value not in ["", None] else 0
            chapters[current_chapter]["tasks"].append((key, xp_val))
    return chapters

chapters_dict = build_chapters_dict(mq_data)

# ─────────────────────────────
# 全域字典：儲存用戶基本資訊與啟動訊息
user_start_message = {}

# ─────────────────────────────
# 新增函式：靈活解析章節範圍輸入，支援多種分隔符號
def parse_chapter_range(chapter_range_str: str) -> (str, str):
    # 嘗試匹配常見的分隔符號： >, to, ->, ～, ~
    pattern = re.compile(r'^\s*(\S+)\s*(?:>|to|->|～|~)\s*(\S+)\s*$', re.IGNORECASE)
    match = pattern.match(chapter_range_str)
    if match:
        return match.group(1), match.group(2)
    # 若無匹配，嘗試以空格分隔，若恰好兩個部分則視為有效
    parts = chapter_range_str.split()
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ValueError("章節範圍格式錯誤，請使用類似 '11-1 > 14-7' 的格式。")

# ─────────────────────────────
# 新版 Modal：填寫基本資訊＋章節範圍、冒險者日記模式與跳過皇魔前遺跡 bonus 開關
class BaseModal(discord.ui.Modal, title="角色等級＆目標"):
    def __init__(self, author_id: int):
        super().__init__()
        self.author_id = author_id

    level_progress = discord.ui.TextInput(
        label="角色等級-進度%",
        placeholder="例: 77 或 77 (87%)",
        style=discord.TextStyle.short,
        default="",
        required=False
    )
    target_level = discord.ui.TextInput(
        label="目標等級",
        placeholder="例: 295 或 295 (50%)",
        style=discord.TextStyle.short,
        default="295",
        required=False
    )
    chapter_range = discord.ui.TextInput(
        label="開始章節 > 結束章節 (例: 11-1 > 14-7)",
        placeholder="填寫 <最後>/<Final> = 最後一個主綫任務",
        style=discord.TextStyle.short,
        default="11-1 > Final",
        required=False
    )
    diary_mode = discord.ui.TextInput(
        label="冒險者日記模式 (Yes/No)",
        placeholder="空白 = No",
        style=discord.TextStyle.short,
        default="Yes",
        required=False
    )
    skip_center_exp = discord.ui.TextInput(
        label="跳過 Chapter 9-9 艾路鄧波爭還戰【皇魔前遺跡】 (Yes/No)",
        placeholder="空白 = No",
        style=discord.TextStyle.short,
        default="Yes",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        # 使用本地變數來處理空白值，設定預設值：
        level_input = self.level_progress.value.strip() if self.level_progress.value.strip() else "1 (0%)"
        target_input = self.target_level.value.strip() if self.target_level.value.strip() else "1"
        chapter_input = self.chapter_range.value.strip() if self.chapter_range.value.strip() else "1-1 > Final"
        diary_input = self.diary_mode.value.strip() if self.diary_mode.value.strip() else "No"
        skip_input = self.skip_center_exp.value.strip() if self.skip_center_exp.value.strip() else "No"

        if interaction.user.id != self.author_id:
            await interaction.response.send_message("要使用該指令需要自己>exp_calc喔～", ephemeral=True)
            return
        try:
            # 取得表單中初始的角色等級與進度
            level, progress = parse_level_progress(level_input)
            # 目標等級與進度也支援 (例如：295 (50%))
            target_level, target_progress = parse_level_progress(target_input)
            # 解析章節範圍輸入，支援多種分隔符號格式
            try:
                start_input, end_input = parse_chapter_range(chapter_input)
            except ValueError as e:
                await interaction.response.send_message(str(e), ephemeral=True)
                return
            # 若結尾輸入 final 或 最後，則替換為最後章節的最後任務
            if end_input.lower() in ["final", "最後"]:
                ordered_chapters = sorted(chapters_dict.keys(), key=lambda x: int(x.split()[1]))
                final_chap = ordered_chapters[-1]
                end_input = f"{int(final_chap.split()[1])}-{len(chapters_dict[final_chap]['tasks'])}"
            if '-' not in start_input:
                start_input = f"{start_input}-1"
            if '-' not in end_input:
                end_input = f"{end_input}-1"

            diary_mode_enabled = True if diary_input.lower() in ["yes", "y", "1"] else False
            skip_center = True if skip_input.lower() in ["yes", "y", "1"] else False
        except ValueError as e:
            await interaction.response.send_message("請確認數值輸入正確～" + str(e), ephemeral=True)
            return

        # 驗證開始章節任務是否存在
        try:
            start_parts = start_input.split('-')
            start_chap_num = int(start_parts[0])
            start_task_index = int(start_parts[1])
            start_key = None
            for key in chapters_dict:
                if int(key.split()[1]) == start_chap_num:
                    start_key = key
                    break
            if start_key is None or start_task_index > len(chapters_dict[start_key]["tasks"]) or start_task_index <= 0:
                msg = "你寫的開始章節任務不存在喵~\n"
                if start_key is not None:
                    msg += "【當前所選章節下的所有任務】\n"
                    for idx, (quest, xp) in enumerate(chapters_dict[start_key]["tasks"], start=1):
                        msg += f"{start_key}-{idx} {quest}\n"
                await interaction.response.send_message(msg, ephemeral=True)
                return
            else:
                start_task_name = chapters_dict[start_key]["tasks"][start_task_index - 1][0].split()[0]
        except Exception:
            await interaction.response.send_message("你寫的開始章節任務不存在喵~", ephemeral=True)
            return

        # 驗證結束章節任務是否存在
        try:
            end_parts = end_input.split('-')
            end_chap_num = int(end_parts[0])
            end_task_index = int(end_parts[1])
            end_key = None
            for key in chapters_dict:
                if int(key.split()[1]) == end_chap_num:
                    end_key = key
                    break
            if end_key is None or end_task_index > len(chapters_dict[end_key]["tasks"]) or end_task_index <= 0:
                msg = "你寫的結束章節任務不存在喵~\n"
                if end_key is not None:
                    msg += "【當前所選章節下的所有任務】\n"
                    for idx, (quest, xp) in enumerate(chapters_dict[end_key]["tasks"], start=1):
                        msg += f"{end_key}-{idx} {quest}\n"
                await interaction.response.send_message(msg, ephemeral=True)
                return
            else:
                end_task_name = chapters_dict[end_key]["tasks"][end_task_index - 1][0].split()[0]
        except Exception:
            await interaction.response.send_message("你寫的結束章節任務不存在喵~", ephemeral=True)
            return

        try:
            extra_xp, tasks_sequence = get_extra_xp_and_tasks_sequence(chapters_dict, start_input, end_input, skip_center)
        except Exception as e:
            await interaction.response.send_message("章節輸入錯誤：" + str(e), ephemeral=True)
            return

        if extra_xp <= 0:
            await interaction.response.send_message("選擇的章節範圍無法提供經驗喵～", ephemeral=True)
            return

        final_level, final_progress = add_xp(level, progress, extra_xp)
        # 模擬計算得到的最終結果（用於描述區塊）
        if final_level > target_level or (final_level == target_level and final_progress >= target_progress):
            _ = 0
        else:
            _ = required_xp_from_level(final_level, final_progress, target_level, target_progress)

        diary_runs = []
        if diary_mode_enabled:
            local_level = level
            local_progress = progress
            while True:
                new_level, new_progress, final_task = simulate_diary_pass(local_level, local_progress, tasks_sequence, target_level, target_progress, skip_center)
                diary_runs.append((final_task, new_level, new_progress))
                if new_level == local_level and new_progress == local_progress:
                    break
                if new_level > target_level or (new_level == target_level and new_progress >= target_progress):
                    break
                local_level, local_progress = new_level, new_progress

        # 組合主要描述 (描述區塊中仍顯示計算後的結果)
        description = f"**━━✨達成結果✨━━**\n\n"
        description += f"角色等級: Lv.{level} ({int(progress)}%)\n"
        description += f"目標等級: Lv.{target_level} ({int(target_progress)}%)\n"
        description += f"主綫章節: {start_input} {start_task_name} ➜ {end_input} {end_task_name}\n"
        description += f"Exp獲得: {int(extra_xp):,}\n"
        description += f"達成等級: **Lv.{final_level}** **({int(final_progress)}%)**\n"
        if diary_runs:
            description += "\n【冒險者日記模式】\n"
            for i, (final_task, run_level, run_progress) in enumerate(diary_runs, start=1):
                if final_task:
                    chapter, task_num, task_name = final_task
                    description += f"{i}. {chapter}-{task_num} {task_name} Lv.{run_level} ({int(run_progress)}%)\n"
                else:
                    description += f"{i}. 未能完成任務 Lv.{run_level} ({int(run_progress)}%)\n"

        result_embed = discord.Embed(
            title="★⋆｡ 女僕月醬的主線經驗計算器 ｡⋆★",
            description=description,
            color=0xFFC0CB
        )
        result_embed.set_thumbnail(url="https://i.imgur.com/rO0Sp2P.png")
        # footer 顯示初始表單中所選擇的角色等級與進度到目標等級所需的 EXP
        initial_req_xp = required_xp_from_level(level, progress, target_level, target_progress)
        footer_text = f"※ 距離 Lv.{level} ({int(progress)}%) > Lv.{target_level} ({int(target_progress)}%) 所需 {int(initial_req_xp):,} Exp."
        # 若選取的章節範圍中包含 Chapter 9-9 任務，則在 footer 中附加跳過皇魔前遺跡的設定
        if any(ch for ch in tasks_sequence if ch[0].startswith("Chapter 9") and ch[1] == EMPEROR_RELIC_TASK_INDEX):
            footer_text += f" \n※ 跳過 Chapter 9-9 艾路鄧波爭還戰【皇魔前遺跡】= {'Yes' if skip_center else 'No'}"
        result_embed.set_footer(text=footer_text)
        
        if interaction.user.id in user_start_message:
            await interaction.response.edit_message(content="", embed=result_embed, view=None)
        else:
            await interaction.response.send_message("無法找到原始訊息，請重新啟動計算器。", ephemeral=False)

# ─────────────────────────────
# 取得使用者選定章節範圍內所有任務的序列及總經驗
def get_extra_xp_and_tasks_sequence(chapters: dict, start_input: str, end_input: str, skip_center: bool = False):
    try:
        start_parts = start_input.split('-')
        end_parts = end_input.split('-')
        if len(start_parts) != 2 or len(end_parts) != 2:
            raise ValueError("輸入格式錯誤，請使用 '章-任務' 格式，例如 '11-1'")
        start_chapter_num = int(start_parts[0])
        start_task_index = int(start_parts[1])
        end_chapter_num = int(end_parts[0])
        end_task_index = int(end_parts[1])
    except Exception:
        raise ValueError("解析章節輸入失敗，請確認格式。")
    ordered_chapters = sorted(chapters.keys(), key=lambda x: int(x.split()[1]))
    start_key = None
    end_key = None
    for key in ordered_chapters:
        chap_num = int(key.split()[1])
        if chap_num == start_chapter_num:
            start_key = key
        if chap_num == end_chapter_num:
            end_key = key
    if not start_key or not end_key:
        raise ValueError("找不到指定的章節。")
    start_idx = ordered_chapters.index(start_key)
    end_idx = ordered_chapters.index(end_key)
    if start_idx > end_idx:
        raise ValueError("開始章節必須在結束章節之前。")
    tasks_sequence = []
    for ch in ordered_chapters[start_idx:end_idx+1]:
        tasks = chapters[ch]["tasks"]
        if ch == start_key and ch == end_key:
            selected_tasks = tasks[start_task_index - 1: end_task_index]
            start_num = start_task_index
        elif ch == start_key:
            selected_tasks = tasks[start_task_index - 1:]
            start_num = start_task_index
        elif ch == end_key:
            selected_tasks = tasks[:end_task_index]
            start_num = 1
        else:
            selected_tasks = tasks
            start_num = 1
        for i, (quest, xp) in enumerate(selected_tasks, start=start_num):
            tasks_sequence.append((ch, i, quest.split()[0], xp))
    extra_xp = 0
    for (chapter, task_num, quest, xp) in tasks_sequence:
        # 處理 Chapter 9 中的【皇魔前遺跡】任務
        if chapter.startswith("Chapter 9") and task_num == EMPEROR_RELIC_TASK_INDEX:
            if skip_center:
                if isinstance(xp, tuple):
                    extra_xp += xp[0]
                else:
                    extra_xp += xp
            else:
                if isinstance(xp, tuple):
                    extra_xp += xp[0] + xp[1]
                else:
                    extra_xp += xp
        else:
            extra_xp += xp_to_int(xp)
    return extra_xp, tasks_sequence

# ─────────────────────────────
# 模擬一次完整的「冒險者日記」輪次：
def simulate_diary_pass(start_level: int, start_progress: float, tasks_sequence: list, target_level: int, target_progress: float, skip_center: bool = False) -> (int, float, tuple):
    xp_current = (start_progress / 100) * get_xp(start_level)
    current_level = start_level
    final_task = None
    for (chapter, task_num, task_name, xp_val_raw) in tasks_sequence:
        # 處理 Chapter 9 中的【皇魔前遺跡】任務
        if chapter.startswith("Chapter 9") and task_num == EMPEROR_RELIC_TASK_INDEX:
            if skip_center:
                if isinstance(xp_val_raw, tuple):
                    xp_gain = xp_val_raw[0]
                else:
                    xp_gain = xp_val_raw
            else:
                if isinstance(xp_val_raw, tuple):
                    xp_gain = xp_val_raw[0] + xp_val_raw[1]
                else:
                    xp_gain = xp_val_raw
        else:
            xp_gain = xp_to_int(xp_val_raw)
        xp_current += xp_gain
        Final_task = (chapter, task_num, task_name)
        while xp_current >= get_xp(current_level):
            xp_current -= get_xp(current_level)
            current_level += 1
        # 若已達目標等級與進度則中斷
        if current_level > target_level or (current_level == target_level and xp_current >= (target_progress / 100) * get_xp(current_level)):
            break
    progress = 100 * xp_current / get_xp(current_level)
    return current_level, progress, final_task

# ─────────────────────────────
# 開始按鈕 View：觸發 BaseModal
class StartCalcButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="主綫經驗計算器 Link Start☆！", style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BaseModal(author_id=interaction.user.id))

class StartCalcView(discord.ui.View):
    def __init__(self, author_id: int, timeout: int = None):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.add_item(StartCalcButton())
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("要使用該指令需要>exp_calc自己喔～", ephemeral=True)
            return False
        return True

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"女僕月醬 已上線！({bot.user})")

@bot.command(name="exp_calc")
async def exp_calc(ctx):
    msg = await ctx.send("", view=StartCalcView(ctx.author.id))
    user_start_message[ctx.author.id] = msg

@bot.command(name="主線經驗計算器")
async def zh_exp_calc(ctx):
    msg = await ctx.send("", view=StartCalcView(ctx.author.id))
    user_start_message[ctx.author.id] = msg

bot.run(TOKEN)
