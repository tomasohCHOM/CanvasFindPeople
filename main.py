import discord
import os
import sqlite3
import canvasapi.exceptions
from canvas import *
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

token = os.getenv("BOT_TOKEN")


def get_api_key(guild_id: discord.guild):
    """
    Returns the Canvas API key from the guild_id
    """
    conn = sqlite3.connect("bot.db")

    try:
        with conn:
            cur = conn.cursor()
            cur.execute(f"SELECT api_key FROM keys WHERE guild_id = {guild_id}")
        return cur.fetchone()[0]
    except (AttributeError, TypeError):
        return "401"
    finally:
        conn.close()


def create_embed(title):
    embed = discord.Embed(title=title, color=14695977)
    embed.set_author(name=client.user.display_name, icon_url=client.user.avatar)
    embed.set_footer(text="Use !help for the complete commands list")

    return embed


async def register_user(message: discord.Message, key):
    # Verify Canvas API Key
    if key == "":
        await message.channel.send(embed=create_embed("Invalid API Key! Try again."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API Key! Try again."))

    # Place the key into SQLite DB
    try:
        conn = sqlite3.connect("bot.db")
        cur = conn.cursor()
        cur.execute(
            f'REPLACE INTO keys (guild_id, canvas_api_key) VALUES (({message.guild.id}), ("{key}"))'
        )
    finally:
        conn.close()
    await message.channel.send(embed=create_embed("User has been registered!"))


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user or not message.guild:
        return
    user_message = message.content

    REGISTER_LEN = len("!register")
    if user_message.lower().startswith("!register"):
        key = user_message[REGISTER_LEN::].strip()
        await register_user(message, key)

    # await message.channel.send("Hello")


@client.event
async def on_ready():
    print(f"{client.user} Bot is now online.")

    try:
        conn = sqlite3.connect("bot.db")
        cur = conn.cursor()
        print("Database successfully connected")

        cur.execute(
            "CREATE TABLE IF NOT EXISTS keys (guild_id int UNIQUE, canvas_api_key string, course_name string)"
        )
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        conn.close()


if __name__ == "__main__":
    client.run(token)
