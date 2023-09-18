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
    """
    Creates a discord embed to be used everywhere.
    """
    embed = discord.Embed(title=title, color=14695977)
    if description:
        embed.description = description
    embed.set_author(name=client.user.display_name, icon_url=client.user.avatar)
    if set_footer:
        embed.set_footer(text="Use !help for the complete commands list")
    return embed


async def register_user(message: discord.Message, key):
    """
    Registers a user with their Canvas Access Token, placing the token in DB.
    """
    # Verify Canvas API Key
    if key == "":
        await message.channel.send(embed=create_embed("Invalid API Key! Try again."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API Key! Try again."))
        return

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
    """
    Displays all courses that the user is currently enrolled in.
    """
    key = get_api_key(message.guild.id)
    if key == "401":
        await message.channel.send(embed=create_embed("No API key was found."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API key!"))
        return

    courses = get_courses(key)
    courses_message = ""
    for course in courses:
        courses_message += course.name + "\n"
    await message.channel.send(embed=create_embed("Course List", courses_message))


async def display_all_people(message: discord.Message):
    """
    Displays all the people that the user shares a course with.
    """
    key = get_api_key(message.guild.id)
    if key == "401":
        await message.channel.send(embed=create_embed("No API key was found."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API key!"))
        return

    courses = get_courses(key)
    for course in courses:
        people_message = ""
        users = get_users_from_course(course)
        for user in users:
            people_message += user.name + "\n"
        await message.channel.send(
            embed=create_embed(f"People in {course.name}", people_message)
        )


async def search_people(message: discord.Message, query):
    """
    Searches for users that match the query.
    """
    key = get_api_key(message.guild.id)
    if key == "401":
        await message.channel.send(embed=create_embed("No API key was found."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API key!"))
        return

    if query == "" or query is None:
        await message.channel.send(embed=create_embed("Invalid query, try again!"))
        return

    found_users = search_user_in_all(query, key)
    if not found_users:
        await message.channel.send(embed=create_embed("No users found!"))
        return

    found_users_message = ""
    for found_user in found_users:
        # found_user[0] is the User object, while found_use[1] is the Course
        found_users_message += found_user[0].name + f" ({found_user[1].name})" + "\n"
    await message.channel.send(
        embed=create_embed(f"Users found with query `{query}`", found_users_message)
    )


async def search_by_last_name(message: discord.Message, query):
    """
    Performs Binary Search with the query being the searched person's last name.
    """
    key = get_api_key(message.guild.id)
    if key == "401":
        await message.channel.send(embed=create_embed("No API key was found."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API key!"))
        return

    if query == "" or query is None:
        await message.channel.send(embed=create_embed("Invalid query, try again!"))
        return

    found_users = search_user_by_last_name(query, key)
    if not found_users:
        await message.channel.send(embed=create_embed("No users found!"))
        return

    found_users_message = ""
    for found_user in found_users:
        found_users_message += found_user[0].name + f" ({found_user[1].name})" + "\n"
    await message.channel.send(
        embed=create_embed(f"Users found with last name `{query}`", found_users_message)
    )


async def set_course(message: discord.Message, query):
    """
    Sets a specific course and stores it in the DB
    (to be used whenever user searches courses with a specific user).
    """
    key = get_api_key(message.guild.id)
    if key == "401":
        await message.channel.send(embed=create_embed("No API key was found."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API key!"))
        return

    if query == "" or query is None:
        await message.channel.send(embed=create_embed("Invalid query, try again!"))
        return

    course = search_course(key, query)
    if not course:
        await message.channel.send(embed=create_embed("No courses found!"))
        return

    conn = sqlite3.connect("bot.db")
    with conn:
        cur = conn.cursor()
        cur.execute(
            f'REPLACE INTO keys (guild_id, canvas_api_key, course_name) VALUES (({message.guild.id}), ("{key}"), ("{course}"))'
        )
    conn.close()
    await message.channel.send(embed=create_embed(f"Course set as {course}"))


async def remove_course(message: discord.Message):
    """
    Removes the course that was stored in DB.
    """
    key = get_api_key(message.guild.id)
    if key == "401":
        await message.channel.send(embed=create_embed("No API key was found."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API key!"))
        return

    conn = sqlite3.connect("bot.db")
    with conn:
        cur = conn.cursor()
        cur.execute(
            f'REPLACE INTO keys (guild_id, canvas_api_key, course_name) VALUES (({message.guild.id}), ("{key}"), (""))'
        )
    conn.close()
    await message.channel.send(embed=create_embed(f"Course has been cleared!"))


async def search_people_in_course(message: discord.Message, query):
    """
    Retrieves the stored course from DB and searches for people in that course
    (must have used !set-course command prior).
    """
    key = get_api_key(message.guild.id)
    if key == "401":
        await message.channel.send(embed=create_embed("No API key was found."))
        return
    try:
        test_key(key)
    except canvasapi.exceptions.InvalidAccessToken:
        await message.channel.send(embed=create_embed("Invalid API key!"))
        return

    conn = sqlite3.connect("bot.db")
    with conn:
        cur = conn.cursor()
        cur.execute(f"SELECT course_name FROM keys WHERE guild_id = {message.guild.id}")
        course_name = cur.fetchone()[0]
    conn.close()

    if not course_name or course_name == "":
        await message.channel.send(embed=create_embed("No course set for guild!"))
        return

    course = search_course(key, course_name)
    found_users = search_user_in_course(course, query)
    if not found_users:
        await message.channel.send(embed=create_embed("No users found!"))
        return

    found_users_message = ""
    for found_user in found_users:
        found_users_message += found_user[0].name + "\n"
    await message.channel.send(
        embed=create_embed(
            f"Users found with query: `{query}` in {course_name}", found_users_message
        )
    )


async def display_help(message: discord.Message):
    help_description = (
        f"`!register [YOUR_API_KEY]`: Registers your Canvas API key with the bot."
        f"This step is required for the bot to function.\n\n"
        f"`!courses`: Lists all of the courses with an enrollment state of active.\n\n"
        f"`!set-course [query]`: Matches a course that the user is enrolled in to search "
        f"for users only in that course.\n\n"
        f"`!list-everyone`: Displays all the people that the user shares a course with."
        f" Each course's people is separated into its own embed.\n\n"
        f"`!search-user [query]`: Searches for user(s) that match the `query` (which "
        f"can be their last name, for example), and returns an embed with the found users "
        f"(or none if no users were found).\n\n"
        f"`!search-by-last-name [query]`: Searches for user(s) that match the `query`, which "
        f"needs to be their last name. The algorithm will perform a Binary Search.\n\n"
        f"`!search-in-course [query]`: Searches for user(s) that match the `query` with "
        f"the matching course (use `!set-course [query]` prior to this command.\n\n"
        f"NOTE: you should ignore the square braces when inputting your api key or query. "
        f"Input the necessary parameters without the square brackets (only separate it from "
        f"the command with a white space)\n\n"
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
    SEARCH_USER_LEN = len("!search-user")
    SEARCH_IN_COURSE_LEN = len("!search-in-course")
    SET_COURSE_LEN = len("!set-course")
    SEARCH_LAST_NAME_LEN = len("!search-by-last-name")

    if user_message.startswith("!register"):
        key = user_message[REGISTER_LEN::].strip()
        await register_user(message, key)
    elif user_message.startswith("!courses"):
        await display_courses(message)
    elif user_message.startswith("!set-course"):
        query = user_message[SET_COURSE_LEN::].strip()
        await set_course(message, query)
    elif user_message.startswith("!remove-course"):
        await remove_course(message)
    elif user_message.startswith("!list-everyone"):
        await display_all_people(message)
    elif user_message.startswith("!search-user"):
        query = user_message[SEARCH_USER_LEN::].lstrip()
        await search_people(message, query)
    elif user_message.startswith("!search-by-last-name"):
        query = user_message[SEARCH_LAST_NAME_LEN::].lstrip()
        await search_by_last_name(message, query)
    elif user_message.startswith("!search-in-course"):
        query = user_message[SEARCH_IN_COURSE_LEN::].lstrip()
        await search_people_in_course(message, query)
    elif user_message.startswith("!help"):
        await display_help(message)


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
