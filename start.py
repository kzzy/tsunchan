import asyncio
import discord
from discord.ext import commands
import logging
import random
import subprocess
import re

# DOCS http://discordpy.readthedocs.io/
""" TO DO """
# Rematch function
# Captains mode [Manual pick of captains 1-2-2-1-1]

""" HISTORY"""
# Organized text outputs into a single print function
# Updated inhouse swap to match upper/lower and auto-filling is considered
# Updated Team printing to a nicer output
# Updated unjoin to include unjoining for given input players [Considering admin roles?]

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
inhouse_channels = {'Lobby' : '395892786999721986',     # Lobby     ID
                    'Channel 1' : '395897418094215168', # Channel 1 ID
                    'Channel 2' : '395897458032377859'  # Channel 2 ID
                    }

# EVENT LISTENERS #
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
    """ Helper function to validate given member with given target role"""
    for role in member.roles:
        if str(role) == target:
            return True
    return False

async def print_ih(instruct: str, input_1="", input_2="", input_3="", input_4=""):
    """ Helper Function to organize text printing"""

    if instruct == "teams":
        t1 = "TEAM 1"
        t2 = "TEAM 2"
        await bot.say("`{:<35}{}`".format(t1, t2))
        for player_t1, player_t2 in zip(inhouse_t1, inhouse_t2):
            await bot.say("`{:<35}{}`".format(player_t1.display_name, player_t2.display_name))

    elif instruct == "ready_help":
        await bot.say( "```Commands\n!inhouse move to start the match\n!inhouse scramble to randomize teams again.\n!inhouse swap <p1> <p2> to swap specific players.```")

    elif instruct == "help":
        await bot.say('Invalid inhouse command\nPlease refer to **!help inhouse**')

    elif instruct == "improper_permissions":
        await bot.say('You do not have the proper permissions to join/manage the inhouse')

    elif instruct == "inactive_inhouse":
        await bot.say('There is no active inhouse currently going.\nPlease refer to **!help inhouse**')

    elif instruct == "init_inhouse":
        await bot.say('**{0}** has started an inhouse.\n```{1}\t({2} VS {3})```'.format(input_1, input_2, input_3, input_4))

    elif instruct == "commence_inhouse":
        await bot.say('**Inhouse is ready to commence**\n\n`Type in \'!inhouse start\' to begin`')

    elif instruct == "inprogress_inhouse":
        await bot.say('There is an inhouse in-progress. Please wait until it\'s done.')

    elif instruct == "no_inprogress_inhouse":
        await bot.say('There is no inhouse in-progress.')

    elif instruct == "end_match":
        await bot.say('The current match has ended... Moving players back to the Lobby')

    elif instruct == "not_enough_queue":
        await bot.say('There are not enough players in the queue.')

    elif instruct == "full_inhouse":
        await bot.say('Sorry the inhouse is currently full. Baka!')

    elif instruct == "end_inhouse":
        await bot.say('The current inhouse session ended.')

    elif instruct == "not_found":
        await bot.say("There are no players found with your search key: **{0}**".format(input_1))

    # Unique Cases #
    elif instruct == "init_illegal_team_slots":
        await bot.say("The team numbers are illegal, must be > 0")

    elif instruct == "swap_too_many_cases":
        await bot.say("There are numerous players with the same names in Team 1. (**{0}**)\nRefine your search, then try again.".format(input_1))

    elif instruct == "swap_result":
        await bot.say("Swapped Players: **{0}** and **{1}**".format(input_1, input_2))

    elif instruct == "scramble":
        await bot.say('{0} has scrambled the teams! The new teams are below.\n'.format(input_1))

    elif instruct == "join_queue":
        await bot.say('**{0}** has joined the queue, [{1} / {2}] players needed'.format(input_1, input_2, input_3))

    elif instruct == "leave_queue_too_many_cases":
        await bot.say('There are numerous players with the same names in the queue. (**{0}**)\nRefine your search, then try again.'.format(input_1))

    elif instruct == "leave_queue":
        await bot.say('**{0}** has left the queue, [{1} / {2}] players needed'.format(input_1, input_2, input_3))

    elif instruct == "leave_queue_auto":
        await bot.say('**{0}** has automatically left the queue, [{1} / {2}] players needed\n`Left the inhouse channels`'.format(input_1, input_2, input_3))

    elif instruct == "already_in_queue":
        await bot.say('{0} has already joined this queue.'.format(input_1))

    elif instruct == "not_in_queue":
        await bot.say('{0} never joined the queue in the first place.'.format(input_1))

@bot.group(pass_context=True)
async def inhouse(ctx):
    """Inhouse System"""
    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        await print_ih("improper_permissions")
        return

    # Validate subcommand usage
    if ctx.invoked_subcommand is None:
        await print_ih("help")
    return

@inhouse.command(pass_context=True)
async def init(ctx, game: str, t1_slots: str, t2_slots: str):
    """Initializes inhouse"""
    global inhouse_active
    global inhouse_total
    global inhouse_t1_slots
    global inhouse_t2_slots
    global inhouse_game

    # Parameter Check
    if int(t1_slots) < 1 or int(t2_slots) < 1:
        await print_ih('init_illegal_team_slots')
        return

    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Check for active inhouse
    if inhouse_active is True:
        await print_ih('inactive_inhouse')
        return

    inhouse_active = True
    inhouse_game = game
    inhouse_t1_slots = t1_slots
    inhouse_t2_slots = t2_slots
    inhouse_total = int(t1_slots) + int(t2_slots)

    await print_ih('init_inhouse', member.display_name, inhouse_game, t1_slots, t2_slots)
    return

@inhouse.command(pass_context=True)
async def finish(ctx):
    """Concludes inhouse"""
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
        await print_ih('end_inhouse')
    else:
        await print_ih('inactive_inhouse')
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
        await print_ih('inactive_inhouse')
        return

    # Check if inhouse is full and ready to go
    if inhouse_ready is False:
        await print_ih('not_enough_queue')
        return

    # Check if there is an inhouse in-progress
    if inhouse_started is True:
        await print_ih('inprogress_inhouse')
        return

    cur_t1_slots = 0
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

    # Print team rosters
    #  Sort alphabetically
    inhouse_t1.sort(key=lambda x: x.display_name)
    inhouse_t2.sort(key=lambda x: x.display_name)
    await print_ih("ready_help")
    await print_ih("teams")
    return

@inhouse.command(pass_context=True)
async def swap(ctx, t1_name: str, t2_name: str):
    """Swaps two players"""
    global inhouse_t1
    global inhouse_t2

    # Role Check
    member = ctx.message.author  # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Check for active inhouse
    if inhouse_active is False:
        await print_ih('inactive_inhouse')
        return

    # Check if inhouse is full and ready to go
    if inhouse_ready is False:
        await print_ih('not_enough_queue')
        return

    # Check if there is an inhouse in-progress
    if inhouse_started is False:
        await print_ih('no_inprogress_inhouse')
        return

    # Find Team 1 PLAYER #
    t1_player = None # Team 1 Target Player
    # Regex to match all found names for team 1
    p1_pattern = r'((' + re.escape(t1_name.lower()) + r')+(.)*)'
    t1_matches = [x for x, x in enumerate(inhouse_t1) if re.search(p1_pattern, x.display_name.lower())]

    # Return first player match of exact string
    for x in t1_matches:
        if x.display_name.lower() == t1_name.lower() or len(t1_matches) == 1:
            t1_player = x
            break

    # If numerous matches, but no name exactly matches the given string
    if len(t1_matches) > 1 and t1_player is None:
        t1_dupe = ','.join(str(x.display_name) for x in t1_matches)
        await print_ih('swap_too_many_cases', t1_dupe)
        return
    elif len(t1_matches) < 1:
        await print_ih('not_found', t1_name)
        return

    # Find Team 2 PLAYER #
    t2_player = None  # Team 2 Target Player
    # Regex to match all found names for team 2
    p2_pattern = r'((' + re.escape(t2_name.lower()) + r')+(.)*)'
    t2_matches = [x for x, x in enumerate(inhouse_t2) if re.search(p2_pattern, x.display_name.lower())]

    # Return first player match of exact string
    for x in t2_matches:
        if x.display_name.lower() == t2_name.lower() or len(t2_matches) == 1:
            t2_player = x
            break

    # If numerous matches, but no name exactly matches the given string
    if len(t2_matches) > 1 and t2_player is None:
        t2_dupe = ','.join(str(x.display_name) for x in t2_matches)
        await print_ih('swap_too_many_cases', t2_dupe)
        return
    elif len(t2_matches) < 1:
        await print_ih('not_found', t2_name)
        return

    # Swap respective players and print new teams
    if t1_player is not None and t2_player is not None:
        p1_index = inhouse_t1.index(t1_player)
        p2_index = inhouse_t2.index(t2_player)

        inhouse_t2.append(inhouse_t1.pop(p1_index))
        inhouse_t1.append(inhouse_t2.pop(p2_index))

        # Print updated teams
        inhouse_t1.sort()  # Sort alphabetically
        inhouse_t2.sort()
        await print_ih('ready_help')
        await print_ih('swap_result', t1_player.display_name, t2_player.display_name)
        await print_ih('teams')
    return

@inhouse.command(pass_context=True)
async def move(ctx):
    """Moves teams"""
    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return
        
    # Check for active inhouse
    if inhouse_active is False:
        await print_ih('inactive_inhouse')
        return

    # Check if inhouse is full and ready to go
    if inhouse_ready is False:
        await print_ih('not_enough_queue')
        return

    # Check if there is an inhouse in-progress
    if inhouse_started is False:
        await print_ih('no_inprogress_inhouse')
        return

    # Move players into their respective inhouse voice channels
    for player in inhouse_t1:
        await bot.move_member(player, bot.get_channel(inhouse_channels.get("Channel 1")))
    for player in inhouse_t2:
        await bot.move_member(player, bot.get_channel(inhouse_channels.get("Channel 2")))
    return

@inhouse.command(pass_context=True)
async def scramble(ctx):
    """Scrambles teams"""

    # Role Check
    member = ctx.message.author  # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Check for active inhouse
    if inhouse_active is False:
        await print_ih('inactive_inhouse')
        return

    # Check if inhouse is full and ready to go
    if inhouse_ready is False:
        await print_ih('not_enough_queue')
        return

    # Check if there is an inhouse in-progress
    if inhouse_started is False:
        await print_ih('no_inprogress_inhouse')
        return

    await print_ih('scramble', member.display_name)
    cur_t1_slots = 0
    
    # Reset team 1 and team 2 rosters
    while inhouse_t1:
        inhouse_players.append(inhouse_t1.pop())
    while inhouse_t2:
        inhouse_players.append(inhouse_t2.pop())
        
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

    # Print team rosters
    inhouse_t1.sort() # Sort alphabetically
    inhouse_t2.sort()
    await print_ih('ready_help')
    await print_ih("teams")
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
        await print_ih('inactive_inhouse')
        return

    # Check if there is an inhouse in-progress
    if inhouse_started is False:
        await print_ih('no_inprogress_inhouse')
        return

    # Check if inhouse is full and ready to go
    if inhouse_ready is False:
        await print_ih('not_enough_queue')
        return

    inhouse_started = False
    # Move members back to the main lobby channel
    for player in inhouse_t1:
        await bot.move_member(player, bot.get_channel(inhouse_channels.get("Lobby")))
    for player in inhouse_t2:
        await bot.move_member(player, bot.get_channel(inhouse_channels.get("Lobby")))

    # Reset team 1 and team 2 rosters
    while inhouse_t1:
        inhouse_players.append(inhouse_t1.pop())
    while inhouse_t2:
        inhouse_players.append(inhouse_t2.pop())

    await print_ih('end_match')
    return

@inhouse.command(pass_context=True)
async def join(ctx):
    """Joins the queue"""
    global inhouse_players
    global inhouse_current

    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Check if readied already
    if member in inhouse_players:
        await print_ih('already_in_queue', member.display_name)
        return

    # Check for active inhouse
    if inhouse_active is False:
        await print_ih('inactive_inhouse')
        return

    # Check if inhouse is already full
    if(inhouse_current == inhouse_total):
        await print_ih('full_inhouse')
        return

    # Update player list and counters
    inhouse_players.append(member)
    inhouse_current += 1

    await print_ih('join_queue', member.display_name, inhouse_current, inhouse_total)

    # Check for if enough players have ready'd post-addition
    if(inhouse_current == inhouse_total):
        global inhouse_ready
        inhouse_ready = True
        await print_ih('commence_inhouse')

@inhouse.command(pass_context=True)
async def unjoin(ctx, player = None):
    """Leaves the queue"""
    global inhouse_ready
    global inhouse_players
    global inhouse_current

    # Role Check
    member = ctx.message.author     # Fetch author user and permissions
    if check_role(member, "Inhouse") is False:
        return

    # Find player if optional arg is given #
    if player is not None:
        target = ""
        # Regex to match all found names for team 1
        player_pattern = r'((' + re.escape(player.lower()) + r')+(.)*)'
        matches = [x for x, x in enumerate(inhouse_players) if re.search(player_pattern, x.display_name.lower())]

        # Return first player match of exact string
        for x in matches:
            if x.display_name.lower() == player.lower() or len(matches) == 1:
                target = x
                break

        # If numerous matches, but no name exactly matches the given string
        if len(matches) > 1 and not target:
            dupe = ','.join(str(x.display_name) for x in matches)
            await print_ih('leave_queue_too_many_cases', dupe)
            return
        elif len(matches) < 1:
            await print_ih('not_found', player)
            return

        # Set player to actual member object if pass all checks
        player = target

    # Check if member readied originally
    if member not in inhouse_players and player is None:
        await print_ih('not_in_queue', member.display_name)
        return

    # Check for active inhouse
    if inhouse_active is False:
        await print_ih('inactive_inhouse')
        return

    # Update player list and counters
    if player is not None:
        inhouse_players.remove(player)
        inhouse_current -= 1
        await print_ih('leave_queue', player.display_name, inhouse_current, inhouse_total)
    else:
        inhouse_players.remove(member)
        inhouse_current -= 1
        await print_ih('leave_queue', member.display_name, inhouse_current, inhouse_total)

    # Update inhouse status
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
    """ Rates a given waifu from 1-10 """
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