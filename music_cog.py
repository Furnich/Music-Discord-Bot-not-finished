import requests
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from googleapiclient.discovery import build
import asyncio
import os


api_key = "api_key"
youtube = build('youtube', 'v3', developerKey=api_key)



# Ког  для  музыки
class Music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.music_queue = []
        self.vc = None

        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True','socket_timeout': 180}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    async def search_yt(self, item):
        print("Выполняю поиск песни...")
        search_terms = item.split(" ")
        request = youtube.search().list(
            part="snippet",
            q=' '.join(search_terms),
            type="video",
            maxResults=1
        )

        response = request.execute()

        if response['items']:
            video_id = response['items'][0]['id']['videoId']
            title = response['items'][0]['snippet']['title']

            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                try:
                    info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=True)
                    
                    download_path = ydl.prepare_filename(info)
                    return {'source': download_path, 'title': title}
                except Exception as e:
                    print(f"Ошибка при скачивании: {e}") 
                    return False
        else:
            return False
        
    async def play_music(self, ctx):
        print('музыка должна начаться')
        print(self.music_queue)
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if not self.vc:
                self.vc = await ctx.author.voice.channel.connect()
                print("Подключился  к  каналу!")

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            await ctx.send(f'Now playing: {self.music_queue[0][0]["title"]}')
            self.music_queue.pop(0)  
        else:
            self.is_playing = False
            if self.vc:
                self.vc.stop()
            await ctx.send('The queue is empty.')

    async def play_next(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            
            if self.vc:
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
                await ctx.send(f'Now playing: {self.music_queue[0][0]["title"]}')
                self.music_queue.pop(0) 
            else:
                print("Не удалось подключиться к голосовому каналу.")  
                await ctx.send("Не удалось подключиться к голосовому каналу.")  
        else:
            self.is_playing = False
            self.vc.stop()

    @commands.command(name='play', aliases=['p'], help='воспросизводи выбранную песню из Ютуба')
    async def play(self, ctx, *args):
        print("Команда 'play' вызвана!")
        if ctx.author.voice is None:
            print('011111000')
            await ctx.send("Зайдите в голосовой канал.")
        elif self.is_playing:
            print('000000000')
            await ctx.send("Песня уже играет.")
        else:
            print('033333333')
            query = ' '.join(args)
            song = await self.search_yt(query) 
            if type(song) == type(False):
                await ctx.send(f'Не могу найти песню, повторите попытку.')
            else:
                self.music_queue.append([song, ctx.author.voice.channel])
                await self.play_music(ctx)




    @commands.command(name='pause', aliases=['stop'], help='Ставит музыку на паузу')
    async def pause(self, ctx):
        if self.vc:
            self.is_playing = False
            self.vc.pause()
        else:
            await ctx.send('Я ничего не играю.')


    @commands.command(name='resume', aliases=['r'], help='Продолжает воспроизведение музыки')
    async def resume(self, ctx):
        if self.vc:
            self.is_playing = True
            self.vc.resume()
        else:
            await ctx.send('Я ничего не играю.')


    @commands.command(name='leave', aliases=['l'], help='выходит из голосового канала')
    async def leave(self, ctx):
        if self.vc:
            await self.vc.disconnect()
        else:
            await ctx.send('Я не в голосовом канале.')

    @commands.command(name='skip', aliases=['s'], help='пропускает песню')
    async def skip(self, ctx):
        if self.vc and self.vc.is_playing():
            self.vc.stop()
        else:
            await ctx.send('Я ничего не играю.')

    @commands.command(name='queue', aliases=['q'], help='показывает всю очередь песен')
    async def queue(self, ctx):
        retval = ''
        for i in range(0, len(self.music_queue)):
            retval += f'**{i+1}.** {self.music_queue[i][0]["title"]}\n'

        if retval != '':
            await ctx.send(f'**Очередь:**\n{retval}')
        else:
            await ctx.send('Очередь пуста.')


    @commands.command(name="clear",aliases=['c'], help='Удаляет все песни из очереди')
    async def clear(self,ctx, *args):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send('Очередь очищена')
    
    @commands.command(name="leave", aliases=['l','disconnect','d'],help='Отключает бота из голосового канала')
    async def leave(self,ctx, *args):
        self.is_playing = False
        await self.vc.disconnect()
