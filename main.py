import discord
import youtube_dl
from discord.ext import commands, tasks
from random import choice
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

ffmpeg_options = {
    'options' : '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop = None, stream = False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda : ytdl.extract_info(url, download = not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data = data)

bot = commands.Bot(command_prefix = '/', help_command = None) # 명령어 접두어 설정
token = 'Nzc4Mjk5NzEzMzY3NzAzNjQy.X7P-Fw.ABr7fsb-jsr-7Npfru7X-smzzxk' # Discord Rhooa Music bot 토큰값(※노출금지)
status = ['Jamming out to music!', '/help', 'RhooaMusic Beta Ver']

@bot.event
async def on_ready() :
    change_status.start()
    print(f'부팅 성공: {bot.user.name}!')

@bot.command()
async def ping(ctx) :
    await ctx.send(f'**Pong!** Latency : {round(bot.latency * 1000)}ms')

@bot.command()
async def play(ctx, url) :
    if not ctx.message.author.voice :
        await ctx.send('You are not connected to a voice channel')
        return
    else :
        channel = ctx.message.author.voice.channel
    await channel.connect()
    server = ctx.message.guild
    voice_channel = server.voice_client
    async with ctx.typing() :
        player = await YTDLSource.from_url(url, loop = bot.loop)
        voice_channel.play(player, after = lambda e : print('Player error : %s' %e) if e else None)
    await ctx.send(f'**Now playing : ** {player.title}')

@bot.command()
async def stop(ctx) :
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@tasks.loop(seconds = 20)
async def change_status() :
    await bot.change_presence(activity = discord.Game(choice(status)))

bot.run(token)