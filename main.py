import discord
from discord.ext import commands

bot = commands.Bot(command_prefix = '/', help_command = None)  # 명령어 접두어 설정
token = ("Nzc4Mjk5NzEzMzY3NzAzNjQy.X7P-Fw.ABr7fsb-jsr-7Npfru7X-smzzxk")  # Discord RG Stock bot 토큰값(※노출금지)

@bot.event
async def on_ready() :
    print(f'부팅 성공: {bot.user.name}!')
    game = discord.Game("Beta Ver")  # ~~하는중에 표시
    await bot.change_presence(status = discord.Status.online, activity = game)

@bot.command()
async def 입장(ctx) :
    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command()
async def 퇴장(ctx) :
    await ctx.guild.voice_client.disconnect()

@bot.command()
async def test(ctx) :
    await ctx.send("test 123")

bot.run(token)