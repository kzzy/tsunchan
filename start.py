import asyncio
import discord
from discord.ext import commands
import logging
import random
import threading
import time

"""Command Prefix"""
bot = commands.Bot(command_prefix='!')

# LOGGING 
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@bot.event
async def on_ready():
    """Called on bot done preparing data, NOT FIRST always"""
    print('Logged in as: ' + bot.user.name)
    print('Bot ID: ' + bot.user.id)
    bot.loop.create_task(pick_status())

async def pick_status():
    """Randomly generates a new status on duration"""
    random.seed()
    loop = asyncio.get_event_loop()
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
                                "with kazu", # yaya
                                "with Indekkusu"])
        
        print("Loop Counter: " + str(int(counter)) + ",Picked a new status: " + status)
        counter += 1
        await bot.change_status(game=discord.Game(name=status))
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
"""Makes a choice for the user"""
async def choice(*options : str):
    bot_option_choice = random.choice(options)
    await bot.say("I'd choose " + bot_option_choice)
    
"""Bot execution using token"""
bot.run('MTcxNTQ0NzI2MTU4MTgwMzU0.CsZ7hA.j8pERaIZY0SObQujX2C0Yyb8HIU')

    
    
