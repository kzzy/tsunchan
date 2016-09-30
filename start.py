import asyncio
import discord
from discord.ext import commands
import logging
import random

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
    await bot.change_status(game=discord.Game(name='with Ram'))

@bot.command()
async def rtd(min_number : str ,max_number: str):
    """ Rolls the Dice function, takes in integers """
    random.seed()
    
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
    random.seed()
    
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
    
"""Bot execution using token"""
bot.run('MTcxNTQ0NzI2MTU4MTgwMzU0.CsZ7hA.j8pERaIZY0SObQujX2C0Yyb8HIU')

    
    
