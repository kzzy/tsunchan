import asyncio
import discord
from discord.ext import commands
import logging
import random

# DOCS http://discordpy.readthedocs.io/
""" TO DO """
# Rematch function
# Captains mode [Manual pick of captains 1-2-2-1-1]
# Revise init function auto-ready those already present in lobby channel
# Revise inhouse to automatically exec next phase[start] when the final player readys
# Status command to reprint status

startup_extensions = (
    'cogs.rng',
    'cogs.inhouse',
    'cogs.voice'
)

"""Command Prefix"""
bot = commands.Bot(command_prefix='!')

# LOGGING 
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG) #Settings: DEBUG, WARNING, REFER TO DOCS
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@bot.event
async def on_ready():
    """Called on bot done preparing data, NOT FIRST always"""
    print('Logged in as: ' + bot.user.name)
    print('Bot ID: ' + bot.user.id)
    bot.loop.create_task(pick_status())     # Status Rotation
   # bot.loop.create_task(ping())            # Ping to current server monitor

@bot.command(hidden=True)
async def load(extension_name : str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command(hidden=True)
async def unload(extension_name : str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))

async def pick_status():
    """Randomly generates a new status on duration"""
    playing_status = ["with Rem",
                      "with Ram",
                      "with Emilia",
                      "with Noumi Kudryavka",
                      "with Illya",
                      "with Chitoge",
                      "with Yoshino",
                      "with Arisu Shimada",
                      "with Shirokuma",
                      "with Karen",
                      "with Kyon's Sister",
                      "with Est",
                      "with Aria Kanzaki",
                      "with the Nep Sisters",
                      "with Chino",
                      "with Kyouko",
                      "with Konata",
                      "with Enju",
                      "with Kirin Toudou",
                      "with Shinobu",
                      "with Megumin",
                      "with Mikan",
                      "with kazu",  # yaya no
                      "with Indekkusu"
                      ]

                        # GET SUMTING G00D
    listening_status = ["",
                        "",
                        ""
                        ]

                        # Titles
    watching_status = ["To Love-Ru",
                       "Seirei Tsukai no Blade Dance",
                       "Hidan no Aria",
                       "No Game No Life",
                       "KonoSuba",
                       "Haiyore!",
                       "Gabriel Dropout",
                       "Eromanga-sensei",
                       "Date a Live",
                       # Other
                       "Umaru cheat",
                       "Sagiri draw",
                       "",
                       # Server Easter Eggs
                       "Urban's MMR drop",
                       "-sg get killstolen",
                       "kazu carry ~kyaa",
                       "Tracker get rained"
                       ]
    status = [playing_status, watching_status]
    # type=1 playing, type=2 listening, type=3 watching
    while bot.is_logged_in:
        pick = random.choice(status)
        if pick is playing_status:
            await bot.change_presence(game=discord.Game(name=random.choice(pick), type=1), status=discord.Status.online)
        elif pick is watching_status:
            await bot.change_presence(game=discord.Game(name=random.choice(pick), type=3), status=discord.Status.online)

        await asyncio.sleep(30)  # loops every 30 seconds

if __name__ == "__main__":
    # Cycle through startup extensions
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    """Bot execution using token"""
    # NOTE: REMOVE TOKEN BEFORE COMMIT
    bot.run('')
