import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
bot = discord.Client(intents=discord.Intents.default())


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord")

    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(f"{bot.user} has connected to Discord")


bot.run(TOKEN)
