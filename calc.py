import re
import math
import discord
from discord.ext import commands
import os

# ─────────────────────────────
# TOKEN（請將下面的 TOKEN 替換成您的 Bot Token）
# ─────────────────────────────
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# ======================================================================
# 以下為 exp_calc.py 的數據邏輯與互動介面
# ======================================================================

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

def xp_to_int(xp):
    if isinstance(xp, tuple):
        return xp[0] + xp[1]
    return xp

def get_xp(lv: int) -> int:
    return math.floor(0.025 * (lv ** 4) + 2 * lv)

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
    "帶孩子的龍人夫妻 Weredragoon Couple and a Baby": 79300000,
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

def parse_chapter_range(chapter_range_str: str) -> (str, str):
    pattern = re.compile(r'^\s*(\S+)\s*(?:>|to|->|～|~)\s*(\S+)\s*$', re.IGNORECASE)
    match = pattern.match(chapter_range_str)
    if match:
        return match.group(1), match.group(2)
    parts = chapter_range_str.split()
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ValueError("章節範圍格式錯誤，請使用類似 '11-1 > 14-7' 的格式。")

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
    EMPEROR_RELIC_TASK_INDEX = 9
    for (chapter, task_num, quest, xp) in tasks_sequence:
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

def simulate_diary_pass(start_level: int, start_progress: float, tasks_sequence: list, target_level: int, target_progress: float, skip_center: bool = False) -> (int, float, tuple):
    xp_current = (start_progress / 100) * get_xp(start_level)
    current_level = start_level
    final_task = None
    EMPEROR_RELIC_TASK_INDEX = 9
    for (chapter, task_num, task_name, xp_val_raw) in tasks_sequence:
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
        final_task = (chapter, task_num, task_name)
        while xp_current >= get_xp(current_level):
            xp_current -= get_xp(current_level)
            current_level += 1
        if current_level > target_level or (current_level == target_level and xp_current >= (target_progress / 100) * get_xp(current_level)):
            break
    progress = 100 * xp_current / get_xp(current_level)
    return current_level, progress, final_task

# 為了讓 exp_calc 模態能夠修改原始訊息，這裡使用一個全域字典來記錄使用者的原始訊息
user_start_message = {}

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
        label="開始章節 > 結束章節 (例: 11-1 > Final)",
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
        label="跳過 Chapter 9-9 艾路登波爭還戰【皇魔前遺跡】 (Yes/No)",
        placeholder="空白 = No",
        style=discord.TextStyle.short,
        default="Yes",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        level_input = self.level_progress.value.strip() if self.level_progress.value.strip() else "1 (0%)"
        target_input = self.target_level.value.strip() if self.target_level.value.strip() else "1"
        chapter_input = self.chapter_range.value.strip() if self.chapter_range.value.strip() else "1-1 > Final"
        diary_input = self.diary_mode.value.strip() if self.diary_mode.value.strip() else "No"
        skip_input = self.skip_center_exp.value.strip() if self.skip_center_exp.value.strip() else "No"

        if interaction.user.id != self.author_id:
            await interaction.response.send_message("要使用該指令需要自己操作喵～", ephemeral=True)
            return
        try:
            level, progress = parse_level_progress(level_input)
            target_level, target_progress = parse_level_progress(target_input)
            try:
                start_input, end_input = parse_chapter_range(chapter_input)
            except ValueError as e:
                await interaction.response.send_message(str(e), ephemeral=True)
                return
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
                    msg += "【當前章節所有任務】\n"
                    for idx, (quest, xp) in enumerate(chapters_dict[start_key]["tasks"], start=1):
                        msg += f"{start_key}-{idx} {quest}\n"
                await interaction.response.send_message(msg, ephemeral=True)
                return
            else:
                start_task_name = chapters_dict[start_key]["tasks"][start_task_index - 1][0].split()[0]
        except Exception:
            await interaction.response.send_message("你寫的開始章節任務不存在喵~", ephemeral=True)
            return

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
                    msg += "【當前章節所有任務】\n"
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
            title="★⋆｡ 女僕月醬的主綫經驗計算器 ｡⋆★",
            description=description,
            color=0xFFC0CB
        )
        result_embed.set_thumbnail(url="https://i.imgur.com/rO0Sp2P.png")
        initial_req_xp = required_xp_from_level(level, progress, target_level, target_progress)
        footer_text = f"※ 距離 Lv.{level} ({int(progress)}%) > Lv.{target_level} ({int(target_progress)}%) 所需 {int(initial_req_xp):,} Exp."
        if any(ch for ch in tasks_sequence if ch[0].startswith("Chapter 9") and ch[1] == 9):
            footer_text += f" \n※ 跳過 Chapter 9-9 艾路登波爭還戰【皇魔前遺跡】= {'Yes' if skip_center else 'No'}"
        result_embed.set_footer(text=footer_text)
        
        if interaction.user.id in user_start_message:
            await interaction.response.edit_message(content="", embed=result_embed, view=None)
        else:
            await interaction.response.send_message("無法找到原始訊息，請重新啟動計算器。", ephemeral=False)

# ======================================================================
# 以下為 skill_calc.py 的數據邏輯與互動介面
# ======================================================================

def extract_number(s: str, default: int = 1) -> int:
    m = re.search(r'\d+', s)
    if m:
        return int(m.group())
    return default

def parse_token(token, multiplier=1):
    token = token.strip()
    if token == "" or token.startswith("-"):
        return 0
    m = re.search(r'([\d\.]+)k', token, re.IGNORECASE)
    if m:
        try:
            num = float(m.group(1))
            return int(num * 1000 * multiplier)
        except:
            return 0
    num = extract_number(token, 0)
    return num * multiplier

def safe_parse_token(token, multiplier=1, fallback=0):
    token = token.strip()
    if token.startswith("-"):
        return fallback
    return parse_token(token, multiplier)

def stat_points(level: int) -> int:
    return level * 2

def max_lv_points(level: int) -> int:
    if level >= 5:
        return 5 * (((level - 5) // 10) + 1)
    return 0

def skill_points(level: int) -> int:
    return level + (level // 5)

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

# SkillCalcModal 與 AbilityCalcModal（採用 discord.ui.Modal）
class SkillCalcModal(discord.ui.Modal, title="托蘭技能點計算器"):
    level_info = discord.ui.TextInput(
        label="當前角色等級 / 賬號最高章節",
        placeholder="Lv.? / 章節",
        default="Lv295 / 11章",
        required=False
    )
    combat_record = discord.ui.TextInput(
        label="遊玩實績【戰神/坦克/後盾/輔助】 (上限200000)",
        placeholder="",
        default="1000 / 1000 / 1000 / 1000",
        required=False
    )
    help_record = discord.ui.TextInput(
        label="遊玩實績【急救/戰死】 (上限1000)",
        placeholder="",
        default="1000 / 1000",
        required=False
    )
    mastery = discord.ui.TextInput(
        label="精通技能(項) / 同時點滿的技能樹(株) / 連續遊玩(時長)",
        placeholder="",
        default="10項 / 3株 / 6小時",
        required=False
    )
    mini_game = discord.ui.TextInput(
        label="基地迷你遊戲【黑騎士20k/卡牌30積分/寵物競速3項】 (Yes/No)",
        placeholder="",
        default="Yes / Yes / Yes",
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        account_info_val = self.level_info.value.strip() or "1 / 1"
        parts = [p.strip() for p in account_info_val.split("/")]
        while len(parts) < 2:
            parts.append("1")
        current_level = 1 if parts[0].startswith("-") else extract_number(parts[0])
        max_chapter = 1 if parts[1].startswith("-") else extract_number(parts[1])
        max_chapter_disp = min(max_chapter, 11)
        
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
        
        help_value = self.help_record.value.strip() or "0 0"
        if "/" in help_value:
            help_tokens = [t.strip() for t in help_value.split("/")]
        else:
            help_tokens = help_value.split()
        while len(help_tokens) < 2:
            help_tokens.append("0")
        first_aid = safe_parse_token(help_tokens[0], fallback=0)
        KO = safe_parse_token(help_tokens[1], fallback=0)
        
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
        play_time_hours = play_time_minutes / 60
        if play_time_hours.is_integer():
            play_time_hours = int(play_time_hours)
        else:
            play_time_hours = round(play_time_hours, 1)
        
        mastered_skills_disp = min(mastered_skills, 10)
        mastered_trees_disp = min(mastered_trees, 3)
        play_time_hours_disp = min(play_time_hours, 6)
        
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
        
        _, skill_total = calculate_points(
            current_level, current_level,
            attacker_rank, defender_rank, supporter_rank, breaker_rank,
            first_aid, KO,
            max_chapter, (minigame_bk=="Yes"), (minigame_cg=="Yes"), (minigame_pet=="Yes"),
            mastered_skills, mastered_trees, play_time_bonus
        )
        
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
        
        footer_text = (
            f"角色等級: {current_level} / 達成章節: {max_chapter_disp}\n"
            f"戰/坦/後/輔: {attacker_disp}/{defender_disp}/{supporter_disp}/{breaker_disp}\n"
            f"急救/戰死: {first_aid_disp}/{KO_disp}\n"
            f"精通技能: {mastered_skills_disp}項 / 同時點滿技能樹: {mastered_trees_disp}株 / 連續遊玩: {play_time_hours_disp}小時+\n"
            f"黑騎士20k: {minigame_bk}  卡牌30積分: {minigame_cg}  寵競3項: {minigame_pet}"
        )
        result_embed.set_footer(text=footer_text)
        
        await interaction.response.edit_message(embed=result_embed, view=None)

class AbilityCalcModal(discord.ui.Modal, title="托蘭能力值計算器"):
    level = discord.ui.TextInput(
        label="當前角色等級",
        placeholder="Lv.?",
        default="Lv295",
        required=False
    )
    account_info = discord.ui.TextInput(
        label="賬號最高等級",
        placeholder="Lv.?",
        default="Lv295",
        required=False
    )
    combat_stats = discord.ui.TextInput(
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

# ======================================================================
# 以下為按鈕 View 定義（供單獨指令使用）
# ======================================================================

class ExpCalcButtonView(discord.ui.View):
    def __init__(self, author):
        super().__init__()
        self.author = author
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("這個按鈕不是你的喵～", ephemeral=True)
            return False
        return True
    @discord.ui.button(label="主綫經驗計算器", style=discord.ButtonStyle.primary)
    async def exp_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BaseModal(author_id=interaction.user.id))

class SkillCalcButtonView(discord.ui.View):
    def __init__(self, author):
        super().__init__()
        self.author = author
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("這個按鈕不是你的喵～", ephemeral=True)
            return False
        return True
    @discord.ui.button(label="技能點數計算器", style=discord.ButtonStyle.primary)
    async def skill_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SkillCalcModal())

class StatCalcButtonView(discord.ui.View):
    def __init__(self, author):
        super().__init__()
        self.author = author
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("這個按鈕不是你的喵～", ephemeral=True)
            return False
        return True
    @discord.ui.button(label="能力點數計算器", style=discord.ButtonStyle.primary)
    async def stat_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AbilityCalcModal())

# ======================================================================
# 以下為綜合 View（供 >calc 指令使用）
# ======================================================================

class CombinedCalcView(discord.ui.View):
    def __init__(self, author):
        super().__init__()
        self.author = author
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("這個按鈕不是你的喵～", ephemeral=True)
            return False
        return True
    @discord.ui.button(label="主綫經驗計算器", style=discord.ButtonStyle.primary)
    async def exp_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BaseModal(author_id=interaction.user.id))
    @discord.ui.button(label="技能點數計算器", style=discord.ButtonStyle.primary)
    async def skill_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SkillCalcModal())
    @discord.ui.button(label="能力點數計算器", style=discord.ButtonStyle.primary)
    async def stat_calc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AbilityCalcModal())

# ======================================================================
# 建立 Bot 與指令（指令前綴設為 >）
# ======================================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

@bot.command()
async def calc(ctx):
    msg = await ctx.send("", view=CombinedCalcView(ctx.author))
    user_start_message[ctx.author.id] = msg

# 以下為單獨指令，透過文字指令回覆時先發送一則含單一按鈕的訊息，
# 點擊按鈕後再以 Interaction 的方式顯示模態視窗
@bot.command()
async def exp_calc(ctx):
    await ctx.send("", view=ExpCalcButtonView(ctx.author))

@bot.command()
async def skill_calc(ctx):
    await ctx.send("", view=SkillCalcButtonView(ctx.author))

@bot.command()
async def stat_calc(ctx):
    await ctx.send("", view=StatCalcButtonView(ctx.author))

bot.run(TOKEN)