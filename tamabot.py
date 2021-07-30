# tamabot.py

import discord
import random

TOKEN = "ODcwMjk1MzIzNDAxMTI1OTQ4.YQKrrg.swNkHUabcy0q2nN2Yi0gUBA7YVw"

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')

    if message.author == client.user:
        return
    a = 0
    if a == 0:
        if user_message.lower() == 'hello':
            await message.channel.send(f'sup {username}, you son of a bitch!')
            return
        elif user_message.lower() == 'hi':
            await message.channel.send(f'sup {username}, you son of a bitch!')
            return
        elif user_message.lower() == '!joke':
            await message.channel.send(f"you're the joke stupid bitch")
            return
        elif user_message.lower() == 'bye':
            await message.channel.send(f'fuck off wanker!')
            return
        elif user_message.lower() == '!random':
            response = f'This is your random number: {random.randrange(1000000)}'
            await message.channel.send(response)
            return
        elif user_message.lower() == 'also':
            await message.channel.send(f"also also, fucking bitch go marry tama stupid ass")
            return

    if user_message.lower() == '!anywhere':
        await message.channel.send('this can be used anywhere')
        return


client.run(TOKEN)
