import os
import discord
from discord.ext import commands

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# 定義素材資料
data = {
    "金屬": {
        "emoji": "<:mat_metal:1337713216410615869>",
        "entries": [
            {
                "level": "Lv 143",
                "name": "天使泡泡（水）",
                "recommended": False,
                "location": "眾神之殿·第2区",
                "categories": "金屬、布料、貝殼I",
                "drops": "神性石塊、裂掉的光圈、神秘光布\n\u200b"
            },
            {
                "level": "Lv 226",
                "name": "魚童獸（水）",
                "recommended": False,
                "location": "寒氣迴廊",
                "categories": "金屬、秘銀礦石、貝殼II",
                "drops": "結晶化的尾巴、結晶化的腳爪、秘銀礦石\n\u200b"
            }
        ]
    },
    "布料": {
        "emoji": "<:mat_cloth:1337713188476551240>",
        "entries": [
            {
                "level": "Lv 134",
                "name": "悟道波多姆（光）",
                "recommended": False,
                "location": "異端迴廊",
                "categories": "布料",
                "drops": "破碎裙布、覺醒者之羽\n\u200b"
            },
            {
                "level": "Lv 185",
                "name": "咩寶（風）",
                "recommended": False,
                "location": "城郊的街道",
                "categories": "布料、獸品",
                "drops": "美麗的羊毛、扭曲的粗角\n\u200b"
            },
            {
                "level": "Lv 217",
                "name": "拉偷（地）",
                "recommended": False,
                "location": "試煉的坑道",
                "categories": "布料、金屬、魔素",
                "drops": "盜坑的布、美麗的礦物、暗淡的發光眼球\n\u200b"
            }
        ]
    },
    "獸品": {
        "emoji": "<:emoji_94:1337713462184251483>",
        "entries": [
            {
                "level": "Lv 109",
                "name": "地底奈米可（風）",
                "recommended": False,
                "location": "阿爾提玫亞地下水道·東南",
                "categories": "獸品、布料、秘銀礦石",
                "drops": "蝙蝠耳朵、柔軟圍巾、秘銀礦石\n\u200b"
            },
            {
                "level": "Lv 216",
                "name": "酷龍（火）",
                "recommended": False,
                "location": "試煉的坑道",
                "categories": "獸品、藥品",
                "drops": "很燙的尾巴、很燙的角、灼熱的液體\n\u200b"
            },
            {
                "level": "Lv 243",
                "name": "魯尼牙魚（水）",
                "recommended": False,
                "location": "廢棄區·第一區",
                "categories": "獸品、布料、藥品、貝殼II",
                "drops": "魚的毒牙、銳利的胸鰭、美味魚肉\n\u200b"
            }
        ]
    },
    "木材": {
        "emoji": "<:mat_wood:1337713227127197708>",
        "entries": [
            {
                "level": "Lv 151",
                "name": "常春藤妖（地）",
                "recommended": False,
                "location": "暗龍神殿·中層",
                "categories": "木材、藥品",
                "drops": "常春藤的蔓鬚、健壯粗枝、馬鈴薯\n\u200b"
            }
        ]
    },
    "藥品": {
        "emoji": "<:mat_medicine:1337713205564276786>",
        "entries": [
            {
                "level": "Lv 110",
                "name": "葡萄果凍（暗）",
                "recommended": False,
                "location": "阿爾提玫亞地下水道·東南",
                "categories": "藥品、金屬",
                "drops": "酸甜液體、紅紫色果凍、阿爾堤玫亞石材\n\u200b"
            },
            {
                "level": "Lv 230",
                "name": "地佐龍（地）",
                "recommended": False,
                "location": "波瑪．空達．地下區域",
                "categories": "藥品、獸品",
                "drops": "髒髒的雜草、吃了一半的蘑菇\n\u200b"
            }
        ]
    },
    "魔素": {
        "emoji": "<:mat_mana:1337714184296857651>",
        "entries": [
            {
                "level": "Lv 143",
                "name": "天使泡泡（水）",
                "recommended": False,
                "location": "眾神之殿·第2区",
                "categories": "貝殼I、金屬(多)、布料(少)",
                "drops": "貝殼I、神性石塊、裂掉的光圈、神秘光布\n\u200b"
            },
            {
                "level": "Lv 226",
                "name": "魚童獸（水）",
                "recommended": False,
                "location": "寒氣迴廊",
                "categories": "貝殼II、金屬、秘銀礦石",
                "drops": "貝殼II、結晶化的尾巴、結晶化的腳爪、秘銀礦石\n\u200b"
            },    
            {
                "level": "Lv 224",
                "name": "冰狼（水）",
                "recommended": False,
                "location": "寒氣迴廊",
                "categories": "貝殼II、布料、獸品",
                "drops": "貝殼II、冰凍的羽翼、冰凍的鉤爪\n\u200b"
            },
            {
                "level": "Lv 240",
                "name": "鮟鱇（水）",
                "recommended": False,
                "location": "廢棄區·第一區",
                "categories": "貝殼II、布料、獸品",
                "drops": "貝殼II、有彈性的皮、鮟鱇魚柳、高級鮟鱇魚肝\n\u200b"
            },
            {
                "level": "Lv 243",
                "name": "魯尼牙魚（水）",
                "recommended": False,
                "location": "廢棄區·第三區",
                "categories": "貝殼II、獸品、布料、藥品",
                "drops": "貝殼II、魚的毒牙、銳利的胸鰭、美味魚肉\n\u200b"
            }     
        ]       
    }
}

# 自訂下拉選單 (Select)
class MaterialSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="金屬",
                emoji="<:mat_metal:1337713216410615869>",
                description="金屬素材查詢"
            ),
            discord.SelectOption(
                label="布料",
                emoji="<:mat_cloth:1337713188476551240>",
                description="布料素材查詢"
            ),
            discord.SelectOption(
                label="獸品",
                emoji="<:emoji_94:1337713462184251483>",
                description="獸品素材查詢"
            ),
            discord.SelectOption(
                label="木材",
                emoji="<:mat_wood:1337713227127197708>",
                description="木材素材查詢"
            ),
            discord.SelectOption(
                label="藥品",
                emoji="<:mat_medicine:1337713205564276786>",
                description="藥品素材查詢"
            ),
            discord.SelectOption(
                label="魔素",
                emoji="<:mat_mat:1337714184296857651>",
                description="魔素素材查詢"
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

        # 若選擇的分類為「魔素」，則在標題後面附加【貝殼季限定】
        extra_text = "【貝殼季限定】" if selected == "魔素" else ""
        
        # 利用裝飾符號與換行讓標題看起來更大、更好看
        embed = discord.Embed(
            title=f"━━━━━━━━━━━━━━━━━━\n✨ {selected} 素材刷點資訊 {emoji_display} ✨ {extra_text}\n━━━━━━━━━━━━━━━━━━",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        for entry in category_data["entries"]:
            rec_text = " (推薦)" if entry["recommended"] else ""
            embed.add_field(
                name=f"{entry['level']} {entry['name']}{rec_text}",
                value=(
                    f"**地點**：{entry['location']}\n"
                    f"**類別**：{entry['categories']}\n"
                    f"**掉落**：{entry['drops']}"
                ),
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

# 建立 Bot，使用 > 作為指令前綴
bot = commands.Bot(command_prefix=">", intents=intents)

@bot.command(aliases=["素材", "mat"])
async def material(ctx):
    """查詢素材刷點資訊"""
    await ctx.send("月醬正在為你導航 ~", view=MaterialView())

# 啟動 Bot
bot.run(TOKEN)
