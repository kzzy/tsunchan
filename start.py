import discord
import asyncio

client = discord.Client()

'''Called on client done preparing data, NOT FIRST always'''
@client.event
async def on_ready():
    print('Logged in as: ' + client.user.name)
    print('Bot ID: ' + client.user.id)
    await client.change_status(game=discord.Game(name='with Rem')) 

@client.event
async def on_message(message):
    if message.content.startswith('baka'):
        await client.send_message(message.channel, 'you baka')

'''Bot execution using token'''
client.run('MTcxNTQ0NzI2MTU4MTgwMzU0.CsZ7hA.j8pERaIZY0SObQujX2C0Yyb8HIU')

    
    
