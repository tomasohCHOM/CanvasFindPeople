import discord
import os
from canvasapi import Canvas
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

token = os.getenv("BOT_TOKEN")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await message.channel.send("Hello")


@client.event
async def on_ready():
    print(f"{client.user} Bot is now online.")


client.run(token)
