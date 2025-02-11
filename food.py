import discord
from discord.ext import commands
import os


# 請記得替換成你自己的 Bot Token，且避免硬編碼 Token（建議使用環境變數）
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# 定義粉紅色
PINK = discord.Color.from_rgb(255, 182, 193)

# ---------------------------
# 資料結構：所有料理資料依組別整理在這裡
# ---------------------------
data = {
    "mp": {
        "name": "MP上限 (Max Mp)",
        "items": [
            {"id": "1010216", "name": "Salmonella", "level": 10},
            {"id": "1011212", "name": "Epiey!!", "level": 10},
            {"id": "1020808", "name": "ココルル", "level": 10},
            {"id": "1027777", "name": "Aka Shiro", "level": 10},
            {"id": "2010510", "name": "Ultimateわんわん", "level": 10},
            {"id": "2020101", "name": "Paracetamol", "level": 10},
            {"id": "3017676", "name": "yuxieyoko", "level": 10},
            {"id": "3204544", "name": "Amatsuka Kirin", "level": 10},
            {"id": "4261111", "name": "maruna", "level": 10},
            {"id": "6053838", "name": "朋@", "level": 10},
            {"id": "7100720", "name": "Juda", "level": 10},
            {"id": "7150029", "name": "ORCA29", "level": 10},
        ]
    },
    "hp": {
        "name": "HP上限 (Max Hp)",
        "items": [
            {"id": "7071998", "name": "月白Hitomi", "level": 10},
            {"id": "1010032", "name": "★空猫", "level": 10},
            {"id": "1010084", "name": "あきら", "level": 10},
            {"id": "1010356", "name": "らいむ03", "level": 10},
            {"id": "1250015", "name": "雪島いちご", "level": 10},
            {"id": "2010228", "name": "~シュシュ~", "level": 10},
            {"id": "3090618", "name": "snow618", "level": 10},
            {"id": "3092003", "name": "◁ Rikka❤ ▷", "level": 10},
            {"id": "3191130", "name": "Kail NW", "level": 10},
            {"id": "3260178", "name": "maluth", "level": 10},
            {"id": "4262222", "name": "mashilo", "level": 10},
            {"id": "54154629", "name": "シャルム", "level": 10},
            {"id": "6010062", "name": "G - Thunder (JPN)", "level": 10},
            {"id": "6199999", "name": "garun1", "level": 10},
            {"id": "7034444", "name": "芙蕊", "level": 9},
        ]
    },
    "ampr": {
        "name": "攻擊回復 (Ampr)",
        "items": [
            {"id": "1010017", "name": "평온한날", "level": 10},
            {"id": "1010596", "name": "冷Hiro☆", "level": 10},
            {"id": "1011010", "name": "0 kara", "level": 10},
            {"id": "1023040", "name": "Quinone (K)", "level": 10},
            {"id": "1047777", "name": "~Zeref~", "level": 10},
            {"id": "1111000", "name": "カンコウ", "level": 10},
            {"id": "3020777", "name": "白最中", "level": 10},
            {"id": "3201003", "name": "『 K E R R Y 』", "level": 10},
            {"id": "4040404", "name": "S A R A", "level": 10},
            {"id": "4206969", "name": "xenesis5", "level": 10},
            {"id": "4233333", "name": "AlvinXxX", "level": 10},
            {"id": "5236969", "name": "黒澤タイア", "level": 10},
        ]
    },
    "暴擊": {
        "name": "暴击率 (Critical)",
        "items": [
            {"id": "1012654", "name": "奏かなで", "level": 10},
            {"id": "7071999", "name": "安潔利卡多醬耶耶", "level": 10},
            {"id": "1037777", "name": "Hati Hervor", "level": 10},
            {"id": "1100000", "name": "I n u G a m i •", "level": 10},
            {"id": "1181140", "name": "らんな", "level": 10},
            {"id": "2022020", "name": "#SAM#", "level": 10},
            {"id": "3010777", "name": "わん　•　にやー", "level": 10},
            {"id": "3030159", "name": "Lauryn_", "level": 10},
            {"id": "3149696", "name": "NoiR", "level": 10},
            {"id": "4010000", "name": "俺が青娥様", "level": 10},
            {"id": "5119105", "name": "- Kanna -", "level": 10},
            {"id": "6021230", "name": "☆Ｐｉｎａ☆", "level": 10},
            {"id": "7162029", "name": "Player20", "level": 10},
        ]
    },
    "減仇": {
        "name": "減仇 (-Aggro)",
        "items": [
            {"id": "1010038", "name": "dara", "level": 10},
            {"id": "1010147", "name": "터냐", "level": 10},
            {"id": "1010261", "name": "イグルー", "level": 10},
            {"id": "2020808", "name": "Ectoplasm", "level": 10},
            {"id": "3190038", "name": "☆カーミラ★", "level": 10},
        ]
    },
    "加仇": {
        "name": "仇恨 (+Aggro)",
        "items": [
            {"id": "1010207", "name": "Pew_Pew", "level": 10},
            {"id": "1130832", "name": "咲愛", "level": 10},
            {"id": "1140002", "name": "Neaki", "level": 10},
            {"id": "2020606", "name": "Biotin", "level": 10},
            {"id": "3053131", "name": "DaoNaga", "level": 10},
            {"id": "3158668", "name": "VoidWolf", "level": 10},
            {"id": "4220777", "name": "春姫❤", "level": 10},
            {"id": "5261002", "name": "マンモスマン", "level": 10},
        ]
    },
    "對火": {
        "name": "對火傷害增加 (Dte Fire)",
        "items": [
            {"id": "1121212", "name": "RioCakra", "level": 9},
            {"id": "3210106", "name": "♧火のうた", "level": 9},
            {"id": "7088807", "name": "@Ray", "level": 9},
            {"id": "9181111", "name": "#Ryopin#", "level": 9},
            {"id": "8120000", "name": "Lamlo", "level": 7},
        ]
    },
    "對地": {
        "name": "對地傷害增加 (Dte Earth)",
        "items": [
            {"id": "2020202", "name": "S A R A", "level": 10},
            {"id": "1011001", "name": "S i r F a t h", "level": 9},
            {"id": "4233333", "name": "AlvinXxX", "level": 9},
            {"id": "7100666", "name": "itspaez", "level": 9},
        ]
    },
    "對風": {
        "name": "對風傷害增加 (Dte Wind)",
        "items": [
            {"id": "3030303", "name": "S A R A", "level": 10},
        ]
    },
    "對水": {
        "name": "對水傷害增加 (Dte Water)",
        "items": [
            {"id": "1110111", "name": "S A R A", "level": 10},
            {"id": "3210100", "name": "♧水のうた", "level": 10},
            {"id": "7150030", "name": "ファレ", "level": 10},
            {"id": "7011001", "name": "【MB】 VolT‾へ凸", "level": 9},
        ]
    },
    "對暗": {
        "name": "對暗傷害增加 (Dte Dark)",
        "items": [
            {"id": "1190020", "name": "チュレ @迷路屋", "level": 10},
            {"id": "2130776", "name": "サトリール", "level": 10},
            {"id": "6116116", "name": "(⭗△⭗)", "level": 10},
            {"id": "5010092", "name": "Who's Wo", "level": 9},
        ]
    },
    "對光": {
        "name": "對光傷害增加 (Dte Light)",
        "items": [
            {"id": "1020345", "name": "Death · Gun", "level": 9},
            {"id": "3111999", "name": "Espur", "level": 8},
        ]
    },
    "對無": {
        "name": "對無傷害增加 (Dte Neutral)",
        "items": [
            {"id": "3080888", "name": "", "level": None},
            {"id": "1199999", "name": "", "level": None},
            {"id": "1018530", "name": "", "level": None},
            {"id": "1022318", "name": "", "level": None},
            {"id": "3210102", "name": "", "level": None},
            {"id": "3010095", "name": "", "level": None},
        ]
    },
    "物抗": {
        "name": "物理抗性 (Pyhsical Presistance)",
        "items": [
            {"id": "1010081", "name": "Kawasaki", "level": 10},
            {"id": "1020001", "name": "てんげん", "level": 10},
            {"id": "1231776", "name": "xxxdsmer", "level": 10},
            {"id": "2020111", "name": "L. casei", "level": 10},
            {"id": "2020345", "name": "- C H A R M Z ★", "level": 10},
            {"id": "2200117", "name": "しいぽ", "level": 10},
            {"id": "4010051", "name": "マグナ", "level": 10},
            {"id": "6010701", "name": "ramenEso", "level": 10},
        ]
    },
    "魔抗": {
        "name": "魔法抗性 (Magic Resistance)",
        "items": [
            {"id": "1023045", "name": "亞爾瑪", "level": 10},
            {"id": "1111575", "name": "Kiyanh", "level": 10},
            {"id": "1181220", "name": "梨花", "level": 10},
            {"id": "2020505", "name": "Niacin (B3)", "level": 10},
            {"id": "5200025", "name": "たつ猫☆", "level": 10},
            {"id": "6190007", "name": "nanako♪", "level": 10},
            {"id": "7010016", "name": "Lian戀", "level": 10},
            {"id": "8010016", "name": "° Roulecca", "level": 10},
        ]
    },
    "百分比": {
        "name": "百分比屏障 (Factical Barrier)",
        "items": [
            {"id": "1012222", "name": "gaito123", "level": 10},
            {"id": "4010024", "name": "いぐるん", "level": 10},
            {"id": "53010043", "name": "昂 k09", "level": 10},
            {"id": "53190003", "name": "桜乃宮　千都", "level": 10},
            {"id": "6150029", "name": "29ψ ORCA", "level": 10},
            {"id": "1074649", "name": "∮ ノマァ ∮", "level": 9},
            {"id": "3190038", "name": "☆カーミラ★", "level": 9},
            {"id": "6010062", "name": "G - Thunder (JPN)", "level": 9},
        ]
    },
    "str": {
        "name": "Str",
        "items": [
            {"id": "3210303", "name": "Valer", "level": 10},
            {"id": "1010055", "name": "Echidna@", "level": 10},
            {"id": "1010968", "name": "アジヤ", "level": 10},
            {"id": "1011069", "name": "A J I", "level": 10},
            {"id": "1110033", "name": "くりぼー☆", "level": 10},
            {"id": "2017890", "name": "みさき*", "level": 10},
            {"id": "2020303", "name": "Amanita", "level": 10},
            {"id": "2180000", "name": "Ryopin", "level": 10},
            {"id": "4010024", "name": "いぐるん", "level": 10},
            {"id": "5261919", "name": "ルージアル", "level": 10},
            {"id": "7070777", "name": "-Xen-", "level": 10},
        ]
    },
    "dex": {
        "name": "Dex",
        "items": [
            {"id": "1010058", "name": "· H20 ·", "level": 10},
            {"id": "1010106", "name": "Yoku'", "level": 10},
            {"id": "1010261", "name": "イグルー", "level": 10},
            {"id": "1074649", "name": "∮ ノマァ ∮", "level": 10},
            {"id": "1112220", "name": "Kirara♥", "level": 10},
            {"id": "2020222", "name": "Himura Oza", "level": 10},
            {"id": "3111999", "name": "Espur", "level": 10},
            {"id": "3220777", "name": "☆エトワール☆", "level": 10},
            {"id": "7011001", "name": "【MB】 VolT‾へ凸", "level": 10},
            {"id": "7140777", "name": "Aurianne", "level": 10},
        ]
    },
    "agi": {
        "name": "Agi",
        "items": [
            {"id": "1220777", "name": "サスケU^ェ^U", "level": 10},
            {"id": "2020037", "name": "Mana-T", "level": 10},
            {"id": "4262222", "name": "mashilo", "level": 10},
            {"id": "7162029", "name": "Player20", "level": 10},
            {"id": "1110033", "name": "くりぼー☆", "level": 9},
            {"id": "6269999", "name": "酒呑", "level": 9},
        ]
    },
    "int": {
        "name": "Int",
        "items": [
            {"id": "1010140", "name": "かがり", "level": 10},
            {"id": "1010498", "name": "桃夏", "level": 10},
            {"id": "1032222", "name": "Shyturu", "level": 10},
            {"id": "1047777", "name": "~Zeref~", "level": 10},
            {"id": "2020707", "name": "Ascorbic Acid", "level": 10},
            {"id": "5190001", "name": "シェリア.", "level": 10},
            {"id": "6010701", "name": "ramenEso", "level": 10},
            {"id": "7130001", "name": "@みげる", "level": 10},
        ]
    },
    "vit": {
        "name": "Vit",
        "items": [
            {"id": "4032850", "name": "Aphrodite tiger", "level": 10},
        ]
    },
    "武a": {
        "name": "武器攻擊力 (Watk)",
        "items": [
            {"id": "8010300", "name": "Arale", "level": 10},
            {"id": "", "name": "Dora朵朵", "level": 10},
            {"id": "1010810", "name": "夜トyato☆", "level": 10},
            {"id": "1011122", "name": "ベッキー", "level": 10},
            {"id": "1011126", "name": "ヾferyanz", "level": 10},
            {"id": "1067777", "name": "YusagKurumi", "level": 10},
            {"id": "1180020", "name": "Rouen", "level": 10},
            {"id": "1200020", "name": "ティーク", "level": 10},
            {"id": "2020404", "name": "HbA1c", "level": 10},
            {"id": "3010777", "name": "わん　•　にやー", "level": 10},
            {"id": "3180777", "name": "Reon∮", "level": 10},
            {"id": "4170999", "name": "おりぴ", "level": 10},
            {"id": "4240242", "name": "Nakean", "level": 10},
            {"id": "5110834", "name": "加寿葉", "level": 10},
            {"id": "6010024", "name": "『 G a p a p a 』", "level": 10},
            {"id": "6130623", "name": "雪羽", "level": 10},
            {"id": "6269999", "name": "酒呑", "level": 10},
            {"id": "7050301", "name": "Keith", "level": 10},
        ]
    },
    "atk": {
        "name": "Atk",
        "items": [
            {"id": "1119876", "name": "キヅツ", "level": 10},
            {"id": "7170717", "name": "Isuni☆", "level": 10},
        ]
    },
    "matk": {
        "name": "Matk",
        "items": [
            {"id": "1024649", "name": "BUFFERIN", "level": 10},
        ]
    },
    "hit": {
        "name": "命中 (Hit)",
        "items": [
            {"id": "4261111", "name": "", "level": 10},
            {"id": "2010408", "name": "", "level": 10},
            {"id": "1181220", "name": "", "level": 10},
        ]
    },
    "flee": {
        "name": "回避 (Flee)",
        "items": [
            {"id": "2010408", "name": "", "level": 10},
        ]
    },
    "掉寶": {
        "name": "掉寶率 (Drop Rate)",
        "items": [
            {"id": "4032850", "name": "Aphrodite tiger", "level": 6},
            {"id": "4196969", "name": "★Shiro☆", "level": 6},
            {"id": "4245922", "name": "ふると系#", "level": 6},
            {"id": "7057777", "name": "t a s t y", "level": 6},
        ]
    },
}

# ---------------------------
# 定義群組設定
# ---------------------------
# 將下列鍵在主選單中隱藏，改由群組提供子選項
group_stats = ["str", "dex", "agi", "int", "vit"]
group_element = ["對火", "對地", "對風", "對水", "對暗", "對光", "對無"]

# 定義子選單的資料來源
subgroup_mapping = {
    "group_ability": [(key, data[key]) for key in group_stats if key in data],
    "group_element": [(key, data[key]) for key in group_element if key in data],
}

# 建立主選單用的列表：先取出不屬於群組的項目（保留原定順序）
main_categories = []
for key, value in data.items():
    if key in group_stats or key in group_element:
        continue
    main_categories.append((key, value))

# 找出「加仇」在主選單中的位置
insert_index = None
for i, (key, _) in enumerate(main_categories):
    if key == "加仇":
        insert_index = i
        break
if insert_index is None:
    insert_index = len(main_categories)

# 將群組選項插入到「加仇」之後，先加入「對屬傷害增加 (DTE)」，再加入「能力值 (Stat)」
group_options = [
    ("group_element", {"name": "對屬傷害增加 (DTE)", "is_group": True}),
    ("group_ability", {"name": "能力值 (Stat)", "is_group": True}),
]
main_categories = main_categories[:insert_index+1] + group_options + main_categories[insert_index+1:]

# ---------------------------
# 定義限制使用者的互動 View
# ---------------------------
class RestrictedView(discord.ui.View):
    def __init__(self, author: discord.User, timeout: float = None):
        super().__init__(timeout=timeout)
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("要使用該指令需要自己>food喔~", ephemeral=True)
            return False
        return True

# ---------------------------
# 定義互動元件：下拉選單與 View
# ---------------------------
class CategorySelect(discord.ui.Select):
    def __init__(self, categories):
        options = []
        for cat_key, cat_data in categories:
            options.append(discord.SelectOption(
                label=cat_data["name"],
                description="",
                value=cat_key
            ))
        super().__init__(placeholder="請選擇料理...", min_values=1, max_values=1, options=options)
        self.categories = {cat_key: cat_data for cat_key, cat_data in categories}

    async def callback(self, interaction: discord.Interaction):
        cat_key = self.values[0]
        cat_data = self.categories.get(cat_key)
        if not cat_data:
            await interaction.response.send_message("找不到對應的料理組別。", ephemeral=True)
            return

        # 如果為群組選項，則顯示子選單
        if cat_data.get("is_group"):
            subgroup = subgroup_mapping.get(cat_key)
            if not subgroup:
                await interaction.response.send_message("該群組內無料理資料。", ephemeral=True)
                return
            new_header = f"選擇 {cat_data['name']} 料理 ："
            new_view = CategoryView(subgroup, header=new_header, author=self.view.author)
            await interaction.response.edit_message(content=new_header, embed=None, view=new_view)
        else:
            # 顯示料理資料
            embed = discord.Embed(title=f"{cat_data['name']} 料理列表", color=PINK)
            dish_list = ""
            for dish in cat_data["items"]:
                level = f"Lv {dish['level']}" if dish.get("level") else ""
                dish_list += f"ID: {dish['id']} | {dish['name']} {level}\n"
            embed.description = dish_list if dish_list else "無資料"
            await interaction.response.edit_message(content="請享用！", embed=embed, view=None)

class CategoryView(RestrictedView):
    def __init__(self, categories, header="請選擇你要查詢的料理組別：", author: discord.User = None, timeout: float = 60):
        # 若未傳入 author 則預設為 None（請務必傳入觸發指令的使用者）
        super().__init__(author, timeout=timeout)
        self.header = header
        # 若選項數量超過 25 則拆分多個下拉選單
        for i in range(0, len(categories), 25):
            chunk = categories[i : i + 25]
            self.add_item(CategorySelect(chunk))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

# ---------------------------
# 建立機器人（設定指令前綴為 "!"）
# ---------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"已登入：{bot.user.name}")

@bot.command(aliases=["addr", "food", "料理", "料理地址"])
async def query(ctx, *, dish: str = None):
    """
    若僅輸入指令（例如：!food），則顯示主下拉選單；
    若輸入料理名稱（例如：!food MP上限），則直接搜尋並顯示料理資料。
    """
    if dish:
        # 搜尋名稱中包含參數字串（不分大小寫）的料理組別
        found = None
        for cat_key, cat_data in data.items():
            if dish.lower() in cat_data["name"].lower():
                found = cat_data
                break
        if found:
            embed = discord.Embed(title=f"{found['name']} 料理列表", color=PINK)
            dish_list = ""
            for item in found["items"]:
                level = f"Lv {item['level']}" if item.get("level") else ""
                dish_list += f"ID: {item['id']} | {item['name']} {level}\n"
            embed.description = dish_list if dish_list else "無資料"
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"料理名稱內沒有 **{dish}** 的料理，好笨笨喔。")
    else:
        # 若無參數，僅顯示主下拉選單，並綁定原指令使用者
        header = "主人大人，你要吃什麽~（貼近問"
        view = CategoryView(main_categories, header=header, author=ctx.author)
        await ctx.send(header, view=view)

bot.run(TOKEN)
