# CanvasFindPeople

CanvasFindPeople is a Discord Bot used to quickly search people in your Canvas's courses. You can use this bot if you want to know the friends that you share classes with (or maybe some secret crush 😉).

## Installation / Getting Started

First, make sure you have Python installed on your machine (version 3.11.0 and above). See here to [install Python](https://www.python.org/downloads/).

Clone this repository by running the following:

```bash
$ git clone https://github.com/tomasohCHOM/CanvasFindPeople.git
$ cd CanvasFindPeople
$ python3 main.py
```

And then install all the dependencies through this command (NOTE: It is suggested that you set up a [Python Virtual Environment](https://realpython.com/python-virtual-environments-a-primer/) before running the instruction):

```bash
$ pip install -r requirements.txt
```

Next, create a new Discord application to set up the bot with your server (read the Discord Documentation [here](https://discordpy.readthedocs.io/en/stable/discord.html)). Save the generated token into a new `.env` (template provided in `.env.example`) file and run the program to start using the CanvasFindPeople bot!

## Features / Commands:

Once you have the bot setup, you can run the command `!help` to see the full list of available options:

![List of commands](assets/commands-list.png)

You will register with the `!register` command and your Canvas Access Token (Go to your Dashboard > Account > Settings > New Access Token). Make sure you don't share neither your Canvas or Discord token with anyone! After you are all set up, you can start performing actions that are synced with your Canvas account.

![Searching example](assets/searching-example.png)

Thanks for stopping by! Cya 👋
