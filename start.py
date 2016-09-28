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

@client.event
async def on_message(message):
    if message.content.startswith('baka'):
        await client.send_message(message.channel, 'you baka')

'''Bot execution using token'''
bot.run('MTcxNTQ0NzI2MTU4MTgwMzU0.CsZ7hA.j8pERaIZY0SObQujX2C0Yyb8HIU')

    
    
