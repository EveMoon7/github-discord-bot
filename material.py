import os
import discord
from discord.ext import commands
import re

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 定義素材資料
data = {
    "金屬": {
        "emoji": "<:metal:1351949597878128661>",
        "entries": [
            {
                "level": "Lv 143",
                "name": "天使泡泡（水）",
                "recommended": True,
                "hp": "17488",
                "location": "眾神之殿·第2区",
                "categories": "金屬（多）、布料（少）、貝殼I（貝殼季）",
                "drops": "\n- (metal) 神性石塊 - 1425pt\n- (metal) 裂掉的光圈 - 1336pt\n- (cloth) 神秘光布 - 1603pt\n- (magic_device) 稜鏡之環\n\u200b"
            },
            {
                "level": "Lv 223",
                "name": "魚童獸（水）",
                "recommended": True,
                "hp": "27331",
                "location": "寒氣迴廊",
                "categories": "金屬（多）、秘銀礦石（中）、貝殼II（貝殼季）",
                "drops": "\n- (metal) 結晶化的尾巴 - 1960pt\n- (metal) 結晶化的腳爪 - 2138pt\n- (ore) 秘銀礦石\n- (additional) 淚痕\n\u200b"
            }
        ]
    },
    "布料": {
        "emoji": "<:cloth:1351949569759641601>",
        "entries": [
            {
                "level": "Lv 134",
                "name": "悟道波多姆（光）",
                "recommended": False,
                "hp": "8500",
                "location": "異端迴廊",
                "categories": "布料(多)",
                "drops": "\n- (cloth) 破碎裙布 - 1158pt\n- (cloth) 覺醒者之羽 - 1336pt\n- (potion_yellow) 疫苗I\n- (special) 覺醒者手環\n\u200b"
            },
            {
                "level": "Lv 185",
                "name": "咩寶（風）",
                "recommended": False,
                "hp": "15000",
                "location": "城郊的街道",
                "categories": "布料（中）、獸品（中）、魔素（極少）",
                "drops": "\n- (cloth) 美麗的羊毛 - 1603pt\n- (beast) 扭曲的粗角 - 1782pt\n- (mana) 羊之結晶 - 445pt\n- (special) 街道咩咩護符\n\u200b"
            },
            {
                "level": "Lv 217",
                "name": "拉偷（地）",
                "recommended": True,
                "hp": "17926",
                "location": "試煉的坑道",
                "categories": "布料（多）、金屬（多）、魔素（極少）",
                "drops": "\n- (cloth) 盜坑的布 - 1782pt\n- (metal) 美麗的礦物 - 2139pt\n- (mana) 暗淡的發光眼球 - 445pt\n- (additional) 可疑兜帽\n\u200b"
            }
        ]
    },
    "獸品": {
        "emoji": "<:beast:1351949547760390245>",
        "entries": [
            {
                "level": "Lv 109",
                "name": "地底奈米可（風）",
                "hp": "6500",
                "recommended": False,
                "location": "阿爾提玫亞地下水道·東南",
                "categories": "獸品（中）、布料（中）、秘銀礦石（中）",
                "drops": "\n- (beast) 蝙蝠耳朵 - 980pt\n- (cloth) 柔軟圍巾 - 1159pt\n- (ore) 秘銀礦石\n- (shield) 皇族之盾\n\u200b"
            },
            {
                "level": "Lv 216",
                "name": "酷龍（火）",
                "recommended": True,
                "hp": "19737",
                "location": "試煉的坑道",
                "categories": "獸品（多）、藥品（中）",
                "drops": "\n- (beast) 很燙的尾巴 - 1782pt\n- (beast) 很燙的角 - 2049pt\n- (potion_yellow) 灼熱的液體 - 2222pt\n- (arrow) 炎尾箭矢\n\u200b"
            },
            {
                "level": "Lv 243",
                "name": "魯尼牙魚（水）",
                "recommended": False,
                "hp": "51000",
                "location": "廢棄區·第一區",
                "categories": "獸品（中）、布料（中）、藥品（少）、貝殼II（貝殼季）",
                "drops": "\n- (beast) 魚的毒牙 - 2138pt\n- (cloth) 銳利的胸鰭 - 2316pt\n- (consu) 美味魚肉 - 2494pt\n- (staff) 扭曲法杖\n\u200b"
            }
        ]
    },
    "木材": {
        "emoji": "<:wood:1351949639980421140>",
        "entries": [
            {
                "level": "Lv 151",
                "name": "常春藤妖（地）",
                "recommended": False,
                "hp": "19464",
                "location": "暗龍神殿·中層",
                "categories": "木材（多）、藥品（少）",
                "drops": "\n- (wood) 常春藤的蔓鬚 - 1425pt\n- (wood) 健壯粗枝 - 1603pt\n- (consu) 馬鈴薯 - 1782pt\n- (arrow) 荊棘箭矢\n\u200b"
            },
            {
                "level": "Lv 251",
                "name": "被侵蝕的評議員（暗）",
                "recommended": False,
                "hp": "51000",
                "location": "水都瑪爾·第2區",
                "categories": "木材（多）",
                "drops": "\n- (wood) 水都木材 - 2049pt\n- (wood) 被侵蝕的護手 - 2405pt\n- (wood) 破碎的議員徽章 - 2583pt\n- (bowgun) 海藍弩\n\u200b"
            },
            {
                "level": "Lv 254",
                "name": "大腳樁（地）",
                "recommended": False,
                "hp": "63000",
                "location": "尤馬諾村落遺址·第2區",
                "categories": "木材（多）、魔素（極少）",
                "drops": "\n- (wood) 破碎的樹皮 - 2049pt\n- (wood) 不整齊的木材 - 2227pt\n- (wood) 易燃的木柴 - 2405pt\n- (magic_device) 圓環魔寶球 - 103pt\n\u200b"
            }    
        ]
    },
    "藥品": {
        "emoji": "<:medicine:1351983135960600616>",
        "entries": [
            {
                "level": "Lv 110",
                "name": "葡萄果凍（暗）",
                "recommended": False,
                "hp": "7000",
                "location": "阿爾提玫亞地下水道·東南",
                "categories": "藥品（多）、金屬（少）",
                "drops": "\n- (potion_green) 酸甜液體 - 1158pt\n- (potion_purple) 紅紫色果凍 - 1336pt\n- (metal) 阿爾堤玫亞石材 - 1336pt\n- (additional) 蝴蝶結\n\u200b"
            },
            {
                "level": "Lv 220",
                "name": "萵苣頭（地）",
                "recommended": False,
                "hp": "22500",
                "location": "波瑪．空達前",
                "categories": "藥品（多）、獸品（少）",
                "drops": "\n- (medicine) 頭上樹葉 - 1871pt\n- (potion_blue) 皂素眼淚 - 2227pt\n- (beast) 捲捲尾 - 2049pt\n- (additional) 休美蝶髮夾\n\u200b"
            }, 
            {
                "level": "Lv 230",
                "name": "地佐龍（地）",
                "recommended": False,
                "hp": "58115",
                "location": "波瑪．空達．地下區域",
                "categories": "藥品、獸品",
                "drops": "\n- (medicine) 髒髒的雜草 - 1960pt\n- (medicine) 吃了一半的蘑菇 - 2160pt\n- (beast) 巨大的頭盾 - 2317pt\n- (bowgun) 錨弩\n\u200b"
            } 
        ]
    },
    "魔素": {
        "emoji": "<:mana:1351949613359169627>",
        "entries": [
            {
                "level": "Lv 265",
                "name": "獸化利古希（暗）",
                "recommended": False,
                "hp": "60000",
                "location": "利古薩羅廢城．道路",
                "categories": "魔素（中）、藥品（中）、獸品（少）",
                "drops": "\n- (magic_device) 祈禱之衣 - 108pt\n- (consu_dust) 重度侵蝕的灰塵 - 2049pt\n- (potion_red) 赤紅淚滴 - 2583pt\n- (beast) 黑紅尾巴 - 2316pt\n\u200b"
            },   
        ]
    },         
    "貝殼": {
        "emoji": "<:ss:1351949655402876980>",
        "entries": [
            {
                "level": "Lv 143",
                "name": "天使泡泡（水）",
                "recommended": False,
                "hp": "17488",
                "location": "眾神之殿·第2区",
                "categories": "貝殼I（多）、金屬（多）、布料（少）",
                "drops": "\n- (ss) 盛夏貝殼 - 891pt\n- (metal) 神性石塊 - 1425pt\n- (metal) 裂掉的光圈 - 1336pt\n- (cloth) 神秘光布 - 1603pt\n\u200b"
            },
            {
                "level": "Lv 223",
                "name": "魚童獸（水）",
                "recommended": False,
                "hp": "27331",
                "location": "寒氣迴廊",
                "categories": "貝殼II（多）、金屬（多）、秘銀礦石（中）",
                "drops": "\n- (ss) 盛夏貝殼II - 1336pt\n- (metal) 結晶化的尾巴 - 1960pt\n- (metal) 結晶化的腳爪 - 2138pt\n- (ore) 秘銀礦石\n- (additional) 淚痕\n\u200b"
            },
            {
                "level": "Lv 224",
                "name": "冰狼（水）",
                "recommended": False,
                "hp": "19090",
                "location": "寒氣迴廊",
                "categories": "貝殼II（多）、布料（多）、木材（中）",
                "drops": "\n- (ss) 盛夏貝殼II - 1336pt\n- (cloth) 冰狼的皮毛 - 2160pt\n- (cloth) 冰狼的軟須-2300pt\n- (wood) 冰冷的樹枝-1980pt\n- (xtal) 迴避+16\n\u200b"
            },
            {
                "level": "Lv 240",
                "name": "鮟鱇（水）",
                "recommended": False,
                "hp": "58000",
                "location": "廢棄區·第一區",
                "categories": "貝殼II（多）、布料（中）、藥品（中）",
                "drops": "\n- (ss) 盛夏貝殼II - 1336pt\n- (cloth) 有彈性的皮 - 2138pt\n- (consu) 鮟鱇魚柳 - 2317pt\n- (consu) 高級鮟鱇魚肝 - 2495pt\n- (bowgun) 維托斯弩槍\n\u200b"
            },
            {
                "level": "Lv 243",
                "name": "魯尼牙魚（水）",
                "recommended": False,
                "hp": "51000",
                "location": "廢棄區·第一區",
                "categories": "貝殼II（多）、獸品（中）、布料（中）、藥品（少）",
                "drops": "\n- (ss) 盛夏貝殼II - 1336pt\n- (beast) 魚的毒牙 - 2138pt\n- (cloth) 銳利的胸鰭 - 2316pt\n- (consu) 美味魚肉 - 2494pt\n- (staff) 扭曲法杖\n\u200b"
            }     
        ]       
    }
}

# 新增：定義轉換規則字典，未來需新增其他轉換只要在此處添加即可
conversion_rules = {
    "(wood)": "<:wood:1351949639980421140>",
    "(beast)": "<:beast:1351949547760390245>",
    "(cloth)": "<:cloth:1351949569759641601>",
    "(metal)": "<:metal:1351949597878128661>",
    "(medicine)": "<:medicine:1351983135960600616>",
    "(ss)": "<:ss:1351949655402876980>",
    "(mana)": "<:mana:1351949613359169627>",
    "(potion_green)": "<:potion_green:1351949701586489374>",
    "(potion_purple)": "<:potion_purple:1351949720280498188>",
    "(potion_yellow)": "<:potion_yellow:1351949767969869956>",
    "(potion_blue)": "<:potion_blue:1351986356217319595>",
    "(potion_red)": "<:potion_red:1352003006253629530>",
    "(xtal)": "<:xtal:1351949865986556025>",
    "(consu)": "<:consu:1351949753122029618>",
    "(shield)": "<:shield:1351949807312306246>",
    "(additional)": "<:additional:1351949819630981253>",
    "(arrow)": "<:arrow:1351949895472250981>",
    "(special)": "<:special:1351949783362961448>",
    "(bowgun)": "<:bowgun:1351949794662154300>",
    "(magic_device)": "<:magic_device:1351949831999852655>",
    "(ore)": "<:ore:1351958692349870210>",
    "(staff)": "<:staff:1351996486887669770>",
    "(consu_dust)": "<:consu_dust:1352001065603567802>",
}

def apply_conversion(text):
    for key, value in conversion_rules.items():
        text = text.replace(key, value)
    return text

# 自訂下拉選單 (Select)
class MaterialSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="金屬",
                emoji=discord.PartialEmoji(name="metal", id=1351949597878128661),
                description="金屬素材查詢"
            ),
            discord.SelectOption(
                label="布料",
                emoji=discord.PartialEmoji(name="cloth", id=1351949569759641601),
                description="布料素材查詢"
            ),
            discord.SelectOption(
                label="獸品",
                emoji=discord.PartialEmoji(name="beast", id=1351949547760390245),
                description="獸品素材查詢"
            ),
            discord.SelectOption(
                label="木材",
                emoji=discord.PartialEmoji(name="wood", id=1351949639980421140),
                description="木材素材查詢"
            ),
            discord.SelectOption(
                label="藥品",
                emoji=discord.PartialEmoji(name="medicine", id=1351983135960600616),
                description="藥品素材查詢"
            ),
            discord.SelectOption(
                label="魔素",
                emoji=discord.PartialEmoji(name="mana", id=1351949613359169627),
                description="魔素素材查詢"                
            ),
            discord.SelectOption(
                label="貝殼",
                emoji=discord.PartialEmoji(name="ss", id=1351949655402876980),
                description="貝殼素材查詢"
            )
        ]
        super().__init__(placeholder="請選擇素材類別...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        category_data = data.get(selected)
        if not category_data:
            await interaction.response.edit_message(content="查無此素材資訊！", embed=None, view=None)
            return

        # 嘗試從 emoji 字串中解析 emoji ID 並取得 emoji 物件
        emoji_str = category_data['emoji']
        try:
            emoji_id = int(emoji_str.split(":")[-1].replace(">", ""))
            emoji_obj = interaction.client.get_emoji(emoji_id)
            if emoji_obj:
                emoji_display = str(emoji_obj)
            else:
                emoji_display = emoji_str  # fallback: 未找到 emoji 物件則使用原始字串
        except Exception:
            emoji_display = emoji_str

        # 若選擇的分類為「貝殼」，則在標題後面附加【貝殼季限定】
        extra_text = "【貝殼季限定】" if selected == "貝殼" else ""
        
        # 利用裝飾符號與換行讓標題看起來更大、更好看
        embed = discord.Embed(
            title=f"━━━━━━━━━━━━━━━━━━\n✨ {selected} 素材刷點資訊 {emoji_display} ✨ {extra_text}\n━━━━━━━━━━━━━━━━━━",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        for entry in category_data["entries"]:
            rec_text = " (推薦)" if entry["recommended"] else ""
            embed.add_field(
                name=f"{entry['level']} {entry['name']}{rec_text}",
                value=(f"**HP**：{entry['hp']}\n"
                       f"**地點**：{entry['location']}\n"

                       f"**類別**：{entry['categories']}\n"
                       f"**掉落**：{apply_conversion(entry['drops'])}"),
                inline=False
            )
        # 編輯原本的指令選單列表訊息，移除選單並以 embed 顯示查詢結果，同時修改內容為 "帕魯 啟動☆"
        await interaction.response.edit_message(content="帕魯 啟動☆", embed=embed, view=None)

# 建立 View 並加入下拉選單
class MaterialView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MaterialSelect())

# 啟用 intents，並允許 message_content（注意：此為敏感權限，請在 Bot 設定中啟用）
intents = discord.Intents.default()
intents.message_content = True

# 建立 Bot，使用 ! 作為指令前綴
bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)

@bot.command(aliases=["素材", "mat"])
async def material(ctx):
    """查詢素材刷點資訊"""
    await ctx.send("月醬正在為你導航 ~", view=MaterialView())

# 新增：利用 conversion_rules 字典自動轉換特定關鍵字（方便未來擴充其他轉換規則）
@bot.command()
async def convert(ctx, *, message: str):
    """
    將輸入文字中預定義的關鍵字進行轉換
    目前例如：(wood) 會轉換成 <:wood:1351949639980421140>
    """
    converted_message = apply_conversion(message)
    await ctx.send(converted_message)

# 啟動 Bot
bot.run(TOKEN)
