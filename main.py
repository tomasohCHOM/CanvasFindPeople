import discord
import os
import sqlite3
import canvasapi.exceptions
import canvasapi.course
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
            cur.execute(f"SELECT canvas_api_key FROM keys WHERE guild_id = {guild_id}")
        return cur.fetchone()[0]
    except (AttributeError, TypeError):
        return "401"
    finally:
        conn.close()


def create_embed(title, description="", set_footer=True):
    embed = discord.Embed(title=title, color=14695977)
    if description:
        embed.description = description
    embed.set_author(name=client.user.display_name, icon_url=client.user.avatar)
    if set_footer:
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
    conn = sqlite3.connect("bot.db")
    with conn:
        cur = conn.cursor()
        cur.execute(
            f'REPLACE INTO keys (guild_id, canvas_api_key) VALUES (({message.guild.id}), ("{key}"))'
        )
    conn.close()
    await message.channel.send(embed=create_embed("User has been registered!"))


async def display_courses(message: discord.Message):
    key = get_api_key(message.guild.id)
    if key == "401":
        await message.channel.send(embed=create_embed("No API key was found."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API key!"))
        return

    courses = list_courses(key)
    courses_message = ""
    for course in courses:
        courses_message += course.name + "\n"
    await message.channel.send(embed=create_embed("Course List", courses_message))


async def display_all_people(message: discord.Message):
    key = get_api_key(message.guild.id)
    if key == "401":
        await message.channel.send(embed=create_embed("No API key was found."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API key!"))
        return

    users = get_people(key)
    people_message = ""
    for user in users:
        people_message += user.name + "\n"
    await message.channel.send(embed=create_embed("Course List", people_message))


async def display_help(message: discord.Message):
    help_description = (
        f"`!register (api_key)` Registers your Canvas API key with the bot."
        f"This step is required for the bot to function.\n\n"
        f"`!courses` Intended for use during setup to list all possible "
        f"Canvas courses for the bot to pair with.\n\n"
    )
    await message.channel.send(
        embed=create_embed("List of Commands", help_description, set_footer=False)
    )


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user or not message.guild:
        return
    user_message = message.content

    REGISTER_LEN = len("!register")
    if user_message.lower().startswith("!register"):
        key = user_message[REGISTER_LEN::].strip()
        await register_user(message, key)
    elif user_message.lower().startswith("!courses"):
        await display_courses(message)
    elif user_message.lower().startswith("!all_people"):
        await display_all_people(message)
    elif user_message.lower().startswith("!help"):
        await display_help(message)

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
        print("Error while connecting to SQLite", error)
    finally:
        conn.close()


if __name__ == "__main__":
    client.run(token)
