import discord
from discord.ext import commands

class Help_cog(commands.Cog):
    print("Help_cog imported!")
    def __init__(self, bot):
        self.bot = bot

        self.help_message = """
```
ОСНОВНЫЕ КОМАНДЫ ИСПОЛЬЗУЮТ &

play(p) - Воспроизводит выбранную музыку из Ютуба
pause(stop) - Ставит музыку на паузу
resume(r) - Продолжает воспроизведение музыки
leave(l) - Выходит из голосового канала
skip(s)- Пропускает песню
queue(q) - Показывает всю очередь песен
bot_help(h)  - Показывает список команд
```
        """

        self.commands_text_channel = []

    @commands.Cog.listener()  
    async def on_ready(self):
        print(f'{self.bot.user} is online!')  
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.commands_text_channel.append(channel)

        await self.send_to_all(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.commands_text_channel:
            await text_channel.send(msg)

    @commands.command(name="bot_help", aliases=["h"], help='Показывает список команд')
    async def custom_help(self, ctx): 
        await ctx.send(self.help_message)