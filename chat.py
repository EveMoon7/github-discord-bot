import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # 啟用讀取訊息的權限

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ 已成功登入為 {bot.user}')

@bot.command()
async def 嗨(ctx):
    await ctx.send("嗨嗨~, 宇宙第一可愛林夕月在此噠！")

@bot.command()
async def 誰是小男娘(ctx):
    await ctx.send("是千千噠喲~ 雜魚♡雜魚♡")

@bot.command()
async def 奧爾(ctx):
    await ctx.send("奧爾哥哥人家好想你（（撲倒")

@bot.command()
async def 辰子(ctx):
    await ctx.send("嗷嗷嗷唔（（飛撲咬頭")

@bot.command()
async def 午茶(ctx):
    await ctx.send("矮額，雜魚木頭人（站遠遠")

@bot.command()
async def 餃子(ctx):
    await ctx.send("||查無此人||")  

@bot.command()
async def 晚安(ctx):
    await ctx.send("祝好夢♡（蓋被被")

@bot.command()
async def 餃子2(ctx):
    await ctx.send("態度好差喔")

@bot.command()
async def 餃子3(ctx):
    await ctx.send("好了啦")

@bot.command()
async def 芙蕊99(ctx):
    await ctx.send("||前列腺剎車||")    

@bot.command()
async def 月醬99(ctx):
    await ctx.send("還不快感動的流淚請問我的腳")     

@bot.command()
async def 天城99(ctx):
    await ctx.send("身為腿、足控的我看到這個可精神了 by天城")

@bot.command()
async def 天城98(ctx):
    await ctx.send("啊~大力點 by天城") 

@bot.command()
async def 天城97(ctx):
    await ctx.send("因為我最愛當牛頭人了 by天城")        

@bot.command()
async def 鼬99(ctx):
    await ctx.send("會長就是要被成員玩啊 by宇智波渣") 

@bot.command()
async def 亞亞(ctx):
    await ctx.send("我裝備隨便都很貴的 by亞爾瑪")

@bot.command()
async def 亞亞99(ctx):
    await ctx.send("我在看18+動畫 by亞爾瑪")    

@bot.command()
async def 千千(ctx):
    await ctx.send("（拿起戒指，下跪抬起月醬的手")

@bot.command()
async def 呵(ctx):
    await ctx.send("男人") 

@bot.command()
async def 妖艷賤貨(ctx):
    await ctx.send("外面那些妖艷賤貨哪有人家好")       

@bot.command()
async def 垃圾(ctx):
    await ctx.send("（看垃圾眼神") 

@bot.command()
async def 梨衣(ctx):
    await ctx.send("不知道為什麼聽這叫聲好有感覺")

@bot.command()
async def FTS是什麼(ctx):
    await ctx.send("Flinch膽怯,Tumble翻覆,Stun昏厥")

@bot.command()
async def PH是什麼(ctx):
    await ctx.send("Phase的縮寫,階段的意思")

@bot.command()
async def lfp是什麼(ctx):
    await ctx.send("Looking for party,尋找隊伍的意思")    

@bot.command()
async def lfm是什麼(ctx):
    await ctx.send("Looking for member,尋找/缺隊友的意思")

@bot.command()
async def 我要投訴(ctx):
    await ctx.send("給你一個大大的巴...咳w 擁抱")

@bot.command()
async def 屬性(ctx):
    await ctx.send("風>水>火>地>風，光<>暗")  

@bot.command()
async def 色色(ctx):
    await ctx.send("不可以色色(bonk)")                

bot.run(TOKEN)