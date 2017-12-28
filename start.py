import asyncio
import discord
from discord.ext import commands
import logging
import random
import sys
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
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

"""Global Variables"""
inhouse_active = False # Boolean Used for !inhouse series of commands
inhouse_started = False # Boolean Used to check for in-progress inhouse sessions
inhouse_ready = False # Ready state once total players are met
inhouse_game = ""
inhouse_players = [] # List for !inhouse players
inhouse_current = 0 # Current amount of players
inhouse_total = 0 # Total amount players
inhouse_t1 = [] # List for Team 1 players
inhouse_t2 = [] # List for Team 2 players
inhouse_t1_slots = 0 # Team 1 total slots
inhouse_t2_slots = 0 # Team 2 total slots

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
    #await bot.edit_server(server, region=discord.ServerRegion(current_region))

    while bot.is_logged_in:
        avg_west = check_ping("45.35.39.162") # WEST 144
        avg_central = check_ping("104.200.145.226") # CENTRAL 165
        avg_east = check_ping("138.128.21.106") # EAST 119

        # Update existing ping values
        region_dict['us-west'] = avg_west
        region_dict['us-central'] = avg_central
        region_dict['us-east'] = avg_east

        # Print to log file
        logger.info("Current West Average:{0}".format(avg_west))
        logger.info("Current Central Average:{0}".format(avg_central))
        logger.info("Current East Average:{0}".format(avg_east))

        # Determine region with lowest ping and change server region if it does not match the current region
        min_region = min(region_dict.items(), key=lambda x: x[1])[0]
        if min_region != current_region:
            logger.info("Region changed from {0} to {1}".format(current_region, min_region))
            await bot.edit_server(server, region=discord.ServerRegion(min_region))
        await asyncio.sleep(30) # loops every 30 seconds

def check_role(member, target):
    """ Validate given member with given target role"""
    for role in member.roles:
        if str(role) == target:
            return True
    return False

@bot.group(pass_context=True)
async def inhouse(ctx):
    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        await bot.say('You do not have the proper permissions to join/manage the inhouse')
        return

    # Validate subcommand usage
    if ctx.invoked_subcommand is None:
        await bot.say('Invalid inhouse command\nPlease refer to **!help inhouse**')
    return

@inhouse.command(pass_context=True)
async def init(ctx, game: str, t1_slots: str, t2_slots: str):
    """Initializes an inhouse session"""
    global inhouse_active
    global inhouse_total
    global inhouse_t1_slots
    global inhouse_t2_slots
    global inhouse_game

    # Parameter Check
    if int(t1_slots) < 1 or int(t2_slots) < 1:
        await bot.say("The team numbers are illegal, must be > 0")
        return

    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Check for active inhouse
    if inhouse_active is True:
        await bot.say("There is an active inhouse already. [Game: **{0}**]".format(inhouse_game))
        return

    inhouse_active = True
    inhouse_game = game
    inhouse_t1_slots = t1_slots
    inhouse_t2_slots = t2_slots
    inhouse_total = int(t1_slots) + int(t2_slots)

    await bot.say('**{0}** has started an inhouse.\n`{1}   [{2} VS {3}]`'.format(member.display_name, inhouse_game, t1_slots, t2_slots))
    return

@inhouse.command(pass_context=True)
async def finish(ctx):
    """Concludes an inhouse session"""
    global inhouse_active
    global inhouse_started
    global inhouse_ready
    global inhouse_current
    global inhouse_total
    global inhouse_players
    global inhouse_t1_slots
    global inhouse_t2_slots
    global inhouse_game

    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    if inhouse_active is True:
        # Reset variables
        inhouse_active = False
        inhouse_started = False
        inhouse_ready = False
        inhouse_current = 0
        inhouse_total = 0
        inhouse_t1_slots = 0
        inhouse_t2_slots = 0
        inhouse_game = ""
        del inhouse_players[:] # Delete current list of players
        del inhouse_t1[:]
        del inhouse_t2[:]
        await bot.say('The current inhouse session ended.')
    else:
        await bot.say('There is no active inhouse currently going.\nPlease refer to **!help inhouse**')
    return

@inhouse.command(pass_context=True)
async def start(ctx):
    """Starts a match"""
    global inhouse_active
    global inhouse_started
    global inhouse_ready
    global inhouse_players

    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Check for active inhouse
    if inhouse_active is False:
        await bot.say('There is no active inhouse currently going.\nPlease refer to **!help inhouse**')
        return

    # Check if inhouse is full and ready to go
    if inhouse_ready is False:
        await bot.say('There are not enough players in the queue.')
        return

    # Check if there is an inhouse in-progress
    if inhouse_started is True:
        await bot.say('There is an inhouse in-progress. Please wait until it\'s done.')
        return

    cur_t1_slots = 0
    cur_t2_slots = 0
    ih_channel_1 = bot.get_channel("346601499037663252") # Inhouse ch1
    ih_channel_2 = bot.get_channel("346603193163317249") # Inhouse ch2
    inhouse_started = True

    # While there are still players not on any teams
    while inhouse_players:
        # Random players onto team 1 and once full, throw rest into team 2
        randy = random.choice(inhouse_players)
        inhouse_players.remove(randy)
        inhouse_t1.append(randy)
        cur_t1_slots += 1

        # Enough players on team 1
        if cur_t1_slots == int(inhouse_t1_slots):

            # Fill rest players into team 2
            while inhouse_players:
                inhouse_t2.append(inhouse_players.pop())
            cur_t2_slots = inhouse_total - cur_t1_slots

    # Print team rosters
    t1_roster = ','.join(str(x.display_name) for x in inhouse_t1)
    t2_roster = ','.join(str(x.display_name) for x in inhouse_t2)
    await bot.say("**TEAM 1:** {0}\n\n**TEAM 2:** {1}".format(t1_roster, t2_roster))

    # Move players into their respective inhouse voice channels
    for player in inhouse_t1:
        await bot.move_member(player, ih_channel_1)
    for player in inhouse_t2:
        await bot.move_member(player, ih_channel_2)
    return

@inhouse.command(pass_context=True)
async def end(ctx):
    """Concludes a match"""
    global inhouse_active
    global inhouse_started
    global inhouse_ready
    global inhouse_players

    # Role Check
    member = ctx.message.author  # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Check for active inhouse
    if inhouse_active is False:
        await bot.say('There is no active inhouse currently going.\nPlease refer to **!help inhouse**')
        return

    # Check if there is an inhouse in-progress
    if inhouse_started is False:
        await bot.say('There is no inhouse in-progress currently.')
        return

    # Check if inhouse is full and ready to go
    if inhouse_ready is False:
        await bot.say('There are not enough players ready.')
        return

    inhouse_started = False
    # Move members back to the main lobby channel
    ih_lobby_channel = bot.get_channel("321826783173410826") # nyaa.si
    for player in inhouse_t1:
        await bot.move_member(player, ih_lobby_channel)
    for player in inhouse_t2:
        await bot.move_member(player, ih_lobby_channel)

    # Reset team 1 and team 2 rosters
    while inhouse_t1:
        inhouse_players.append(inhouse_t1.pop())
    while inhouse_t2:
        inhouse_players.append(inhouse_t2.pop())

    await bot.say('`Ended Inhouse session`')
    return

@inhouse.command(pass_context=True)
async def join(ctx):
    """Joins the queue for the inhouse"""
    global inhouse_players
    global inhouse_current

    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Check if readied already
    if member in inhouse_players:
        await bot.say('{0} has already joined this queue.'.format(member.display_name))
        return

    # Check for active inhouse
    if inhouse_active is False:
        await bot.say('There is no active inhouse currently going.\nPlease refer to **!help inhouse**')
        return

    # Check if inhouse is already full
    if(inhouse_current == inhouse_total):
        await bot.say("Sorry the inhouse is currently full. Baka!")
        return

    # Update player list and counters
    inhouse_players.append(member)
    inhouse_current += 1

    await bot.say('**{0}** has joined the queue, [{1} / {2}] players remaining'.format(member.display_name, inhouse_current, inhouse_total))

    # Check for if enough players have ready'd post-addition
    if(inhouse_current == inhouse_total):
        global inhouse_ready
        inhouse_ready = True
        await bot.say('`Inhouse is ready to commence\nWhoever the mod is, type in \'!inhouse start\' to begin`'.format(inhouse_current, inhouse_total))

@inhouse.command(pass_context=True)
async def unjoin(ctx):
    """Leaves the queue for the inhouse"""
    global inhouse_ready
    global inhouse_players
    global inhouse_current

    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Check if member readied originally
    if member not in inhouse_players:
        await bot.say('{0} never joined this queue in the first place.'.format(member.display_name))
        return

    # Check for active inhouse
    if inhouse_active is False:
        await bot.say('There is no active inhouse currently going.\nPlease refer to **!help inhouse**')
        return

    # Update player list and counters
    inhouse_players.remove(member)
    inhouse_current -= 1

    await bot.say('**{0}** has left the queue, [{1} / {2}] players remaining'.format(member.display_name, inhouse_current, inhouse_total))

    if inhouse_ready is True:
        inhouse_ready = False

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
        
        logger.info("Loop Counter: " + str(int(counter)) + ",Picked a new status: " + status)
        counter += 1
        await bot.change_presence(game=discord.Game(name=status, type=1), status=discord.Status.online)
        await asyncio.sleep(12) # loops every 12 seconds

@bot.command()
async def rtd(min_number : str ,max_number: str):
    """ Roll the Dice """
    try:
        dice_number = random.randint(int(str(min_number)), int(str(max_number)))
    except Exception:
        await bot.say('Invalid Input, Please enter numbers only')
        return

    await bot.say('You rolled ' + str(int(dice_number)))

@bot.command()
async def rps(user_hand : str):
    """ Rock Paper Scissors
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
    """ Flips a coin """
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
# NOTE: REMOVE TOKEN BEFORE COMMIT
bot.run('')

    
    
