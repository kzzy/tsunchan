import discord
from discord.ext import commands
import random

'''Command Prefix'''
bot = commands.Bot(command_prefix='!')

'''Called on bot done preparing data, NOT FIRST always'''
@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)
    print('Bot ID: ' + bot.user.id)
    await bot.change_status(game=discord.Game(name='with Rem')) 

@bot.command()
async def rtd(min_number : str ,max_number: str):
    """Rolls the Dice function, takes in integers"""
    random.seed()
    
    try:
        dice_number = random.randint(int(str(min_number)), int(str(max_number)))
    except Exception:
        await bot.say('Invalid Input, Please enter numbers only')
        return

    await bot.say('You rolled ' + str(int(dice_number))) 

'''Bot execution using token'''
bot.run('MTcxNTQ0NzI2MTU4MTgwMzU0.CsZ7hA.j8pERaIZY0SObQujX2C0Yyb8HIU')

    
    
