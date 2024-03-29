import discord
import youtube_dl
from discord.ext import commands, tasks
from random import choice
import random
import asyncio

youtube_dl.utils.bug_reports_message = lambda : ''

ytdl_format_options = {
    'format' : 'bestaudio/best',
    'outtmpl' : '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames' : True,
    'noplaylist' : True,
    'nocheckcertificate' : True,
    'ignoreerrors' : False,
    'logtostderr' : False,
    'quiet' : True,
    'no_warnings' : True,
    'default_search' : 'auto',
    'source_address' : '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {'options' : '-vn'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume = 0.5) :
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop = None, stream = False) :
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda : ytdl.extract_info(url, download = not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data = data)

bot = commands.Bot(command_prefix = '/', help_command = None) # 명령어 접두어 설정
token = '' # Discord Rhooa Music bot 토큰값(※노출금지)
status = ['Jamming out to music!', '/help', 'RhooaMusic Beta Ver']
queue_ = []

@bot.event
async def on_ready() :
    change_status.start()
    print(f'부팅 성공: {bot.user.name}!')

@bot.command()
async def ping(ctx) :
    embed = discord.Embed(title = ":ping_pong:Pong!", description = "Latency : `{}`ms".format(round(bot.latency * 1000)), color = 0xa9dbea)
    embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed = embed)

@bot.command()
async def join(ctx) :
    if not ctx.message.author.voice :
        embed = discord.Embed(description = "You are not connected to a voice channel", color = 0xff0000)
        embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
        return
    else :
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command()
async def leave(ctx) :
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@bot.command()
async def play(ctx) :
    global queue_
    server = ctx.message.guild
    voice_channel = server.voice_client
    try :
        async with ctx.typing() :
            player = await YTDLSource.from_url(queue_[0], loop = bot.loop)
            voice_channel.play(player, after = lambda e : print('Player error : %s' %e) if e else None)
            del(queue_[0])
        embed = discord.Embed(title = ':headphones:Now plyaing', description = "{}".format(player.title), color = 0xa9dbea)
        embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
    except IndexError :
        embed = discord.Embed(description = "Your queue is either **empty** or the index is **out of range**", color = 0xff0000)
        embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)

@bot.command()
async def pause(ctx) :
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.pause()

@bot.command()
async def resume(ctx) :
    server = ctx.message.guild
    voice_channel = server.voice_client
    voice_channel.resume()

@bot.command()
async def add(ctx) :
    global queue_
    url = ctx.message.content[5:]
    if url[5:10] == 'http:' or url[5:11] == 'https:' :
        url = ctx.message.content[5:]
    else :
        url = ctx.message.content[5:] + " Lyrics"
    player = await YTDLSource.from_url(url, loop = bot.loop)
    queue_.append(player.title)
    embed = discord.Embed(description = "queued **{}**\n".format(player.title), color = 0xa9dbea)
    embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed = embed)

@bot.command()
async def remove(ctx, number) :
    global queue_
    number = int(number)
    number -= 1
    try :
        embed = discord.Embed(description = "Removed **{}**".format(queue_[int(number)]), color = 0xa9dbea)
        embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)
        del(queue_[int(number)])
    except :
        embed = discord.Embed(description = "Your queue is either **empty** or the index is **out of range**", color = 0xff0000)
        embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
        await ctx.send(embed = embed)

@bot.command()
async def queue(ctx) :
    embed = discord.Embed(description = "Your queue is now `{}!`".format(queue_), color = 0xa9dbea)
    embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed = embed)

@bot.command()
async def q(ctx) :
    embed = discord.Embed(description = "Your queue is now `{}!`".format(queue_), color = 0xa9dbea)
    embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed = embed)

@bot.command()
async def shuffle(ctx) :
    global queue_
    i = 0
    while i < 4 :
        random.shuffle(queue_)
        i += 1
    embed = discord.Embed(description = "Successfully your queue was mixed!", color = 0xa9dbea)
    embed.set_footer(text = f"{ctx.message.author.name} | Rhmusic#4931", icon_url = ctx.message.author.avatar_url)
    await ctx.send(embed = embed)

@tasks.loop(seconds = 20)
async def change_status() :
    await bot.change_presence(activity = discord.Game(choice(status)))

bot.run(token)
