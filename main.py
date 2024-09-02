import discord
from discord.ext import commands
from config import TOKEN
import yt_dlp
import os
from help_cog import Help_cog  
from music_cog import Music_cog
import asyncio  

intents = discord.Intents.all()
intents.message_content = True  
intents.typing = True
intents.presences = True

bot = commands.Bot(command_prefix='&', intents=intents)

async def main():  
    await bot.add_cog(Help_cog(bot))  
    await bot.add_cog(Music_cog(bot))  
    await bot.start(TOKEN)  


asyncio.run(main())  
