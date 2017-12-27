import asyncio
import discord
from discord.ext import commands
import logging
import random
import subprocess
import re

""" NOTES """
# Documentation: http://discordpy.readthedocs.io/
# Replaced Deprecated function change_status with change_presence
# Coded server region automatic swapping based on lowest ping

"""Command Prefix"""
bot = commands.Bot(command_prefix='!')

# LOGGING 
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG) #Settings: DEBUG, WARNING, REFER TO DOCS
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@bot.event
async def on_ready():
    """Called on bot done preparing data, NOT FIRST always"""
    print('Logged in as: ' + bot.user.name)
    print('Bot ID: ' + bot.user.id)
    bot.loop.create_task(pick_status())     # Status Rotation
    bot.loop.create_task(ping())            # Ping to current server monitor

def check_ping(ip):
    avg_ping = 0.0
    ping_command = "ping -n -c 5 -W 3 " + ip

    (output, error) = subprocess.Popen(ping_command,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=True).communicate()

    # Regex to parse the decoded byte input into string
    pattern = r'time=([0-9]+(\.[0-9]+)*)'
    pings = re.findall(pattern, output.decode('utf=8'))

    # Calculate Average ping
    for ping in pings:
        avg_ping += float(ping[0])
    avg_ping = avg_ping/5

    return avg_ping

async def ping():
    region_dict = {}
    region_dict['us-west'] = 0.0
    region_dict['us-central'] = 0.0
    region_dict['us-east'] = 0.0

    # Default Server Location : us-west
    current_region = "us-west"
    id = "131339092830060544"  # The Crew server id MUST BE STRING FORMAT
    server = bot.get_server(id)
    await bot.edit_server(server, region=discord.ServerRegion(current_region))

    while bot.is_logged_in:
        avg_west = check_ping("45.35.39.162") # WEST 144
        avg_central = check_ping("104.200.145.226") # CENTRAL 165
        avg_east = check_ping("138.128.21.106") # EAST 119

        # Update existing ping values
        region_dict['us-west'] = avg_west
        region_dict['us-central'] = avg_central
        region_dict['us-east'] = avg_east

        print("Current West Average:{0}".format(avg_west))
        print("Current Central Average:{0}".format(avg_central))
        print("Current East Average:{0}".format(avg_east))

        #for key,value in region_dict.items():
        #    print(key,value)

        # Determine region with lowest ping and change server region if it does not match the current region
        min_region = min(region_dict.items(), key=lambda x: x[1])[0]
        if min_region != current_region:
            print("Region changed from {0} to {1}".format(current_region, min_region))
            await bot.edit_server(server, region=discord.ServerRegion(min_region))
        await asyncio.sleep(30) # loops every 30 seconds

@bot.command()
async def test(newRegion : str):
    id = "131339092830060544"  # The Crew server id MUST BE STRING FORMAT
    server = bot.get_server(id)
    # Server ID validity check
    if server is None:
        await bot.say('Invalid Server ID provided')
        return

    # Compose all regions into a list
    regions = [region.value for region in discord.ServerRegion]
    print(regions)

    # Parameter check for input validity
    if newRegion not in regions:
        print("{0} is not a valid server region".format(newRegion))
        return

    try:
        await bot.edit_server(server, region=discord.ServerRegion(newRegion))
        await bot.say("Successfully changed the Server Region to {0}".format(newRegion))
    except Exception:
        await bot.say("Failed to change Server Region to {0}".format(newRegion))
    return

async def pick_status():
    """Randomly generates a new status on duration"""
    counter = 0
    
    while bot.is_logged_in:
        status = random.choice(["with Rem",
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
                                "with kazu", # yaya no
                                "with Indekkusu"])
        
        print("Loop Counter: " + str(int(counter)) + ",Picked a new status: " + status)
        counter += 1
        await bot.change_presence(game=discord.Game(name=status, type=1), status=discord.Status.online)
        await asyncio.sleep(12) # loops every 12 seconds

@bot.command()
async def rtd(min_number : str ,max_number: str):
    """ Rolls the Dice function, takes in integers """  
    try:
        dice_number = random.randint(int(str(min_number)), int(str(max_number)))
    except Exception:
        await bot.say('Invalid Input, Please enter numbers only')
        return

    await bot.say('You rolled ' + str(int(dice_number)))

@bot.command()
async def rps(user_hand : str):
    """ Rock Paper Scissors function, takes in string
        Easter Egg: はさみ For User Scissors in JP """
    bot_choice = random.choice(["rock","paper","scissors"])
    
    if user_hand == "rock" or user_hand == "paper" or user_hand == "scissors" or user_hand == "はさみ":
        if bot_choice == user_hand:
            await bot.say("Its a tie. It isn't like you won or anything! BAKA")
                
        elif bot_choice == "rock" and user_hand == "paper":
            await bot.say("You win against " + bot.user.name + "'s Rock. It's not like I let you win or anything BAKA!")
        elif bot_choice == "rock" and user_hand == "scissors":
            await bot.say("You lose against " + bot.user.name + "'s Rock")
                
        elif bot_choice == "paper" and user_hand == "rock":
             await bot.say("You lose against " + bot.user.name + "'s Paper")
        elif bot_choice == "paper" and user_hand == "scissors":
             await bot.say("You win against " + bot.user.name + "'s Paper. It's not like I let you win or anything BAKA!")
                
        elif bot_choice == "scissors" and user_hand == "rock":
             await bot.say("You win against " + bot.user.name + "'s Scissors. It's not like I let you win or anything BAKA!")
                
        elif bot_choice == "paper" and user_hand == "はさみ":
             await bot.say("You win against " + bot.user.name + "'s Paper baka weeb")
        elif bot_choice == "rock" and user_hand == "はさみ":
             await bot.say("You lose against " + bot.user.name + "'s Rock baka weeb")
                
        else:
             await bot.say ("You lose against " + bot.user.name + "'s Scissors")
    else:
         await bot.say('Invalid input, I want rock, paper or scissors! BAKA')

@bot.command()
async def coinflip():
    """ Flips a coin"""
    bot_coin = random.choice(["heads", "tails"])
    
    await bot.say("You want me to flip you a coin? That's it?")
    await bot.say("*flips*")
    await bot.say("The coin lands as " + bot_coin)

@bot.command()
async def ratewaifu(waifu : str):
    """ Rates the given waifu from 1-10 """
    rating = random.randint(0, 10)

    if(rating == 0):
        await bot.say("I rate your waifu: " + waifu + " a " + str(int(rating)) + ". Serves you right for picking her BAKA!")
    elif(rating == 10):
        await bot.say("I rate your waifu: " + waifu + " a " + str(int(rating)) + ". She.. isn't that good, b-b-BAKA!")
    elif(waifu == bot.user.name):
        await bot.say("I rate myself a 10! THE BEST, how dare you question me BAKA!")
    else:
        await bot.say("I rate your waifu: " + waifu + " a " + str(int(rating)) + ".")

@bot.command()
async def choice(*options : str):
    """Makes a choice for the user"""
    bot_option_choice = random.choice(options)
    await bot.say("I'd choose " + bot_option_choice)
    
"""Bot execution using token"""
bot.run('MTcxNTQ0NzI2MTU4MTgwMzU0.CsZ7hA.j8pERaIZY0SObQujX2C0Yyb8HIU')

    
    
