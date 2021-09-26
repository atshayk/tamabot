#tamabot
#version v0.3.0
#date 26/09/2021

import discord
from discord.ext import commands
from webserver import keep_alive
import os
import random
import asyncio
import json

#bot command
client = commands.Bot(command_prefix=">")
cooldown = []

#removing default help command
client.remove_command("help")

#logging in the bot
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#path for mainbank.json file
os.chdir("https://replit.com/@icybe/tamabot#mainbank.json")


#bot messages
@client.event
async def on_message(message):
    await client.process_commands(message)
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')

    if message.author == client.user:
        return
        
    a = 0
    if a == 0:
        if user_message.lower() == 'hi':
            await message.channel.send(f'sup {username}')
            return
        elif user_message.lower() == 'hello':
            await message.channel.send(f'sup {username}')
            return
        elif user_message.lower() == 'sup':
            await message.channel.send(f'sup back at u, {username}')
            return
        elif user_message.lower() == 'bye':
            await message.channel.send(f'bye then!')
            return
        elif user_message.lower() == 'also':
            await message.channel.send(f"also??? bruh they have more to say")
            return
        elif user_message.lower() == 'what are you':
            await message.channel.send(f"what do you think?")
            return
        elif user_message.lower() == 'fuck you':
            await message.channel.send(f'we do not care')
            return
        elif user_message.lower() == 'yo':
            await message.channel.send(f'yoyo mr mayo')
            return
        elif user_message.lower() == 'what am i?':
            await message.channel.send(f'your mom')
            return
        elif user_message.lower() == 'who are you':
            await message.channel.send(f'bot, tamabot.')
            return
            return
        elif user_message.lower() == 'heck':
            await message.channel.send(f'watch your language, {username}')
            return
        elif user_message.lower() == 'where are you':
            await message.channel.send(f'in yo mama')
            return
        elif user_message.lower() == 'fuck off':
            await message.channel.send(f'little baby bitch cannot handle me lol')
            return
        elif user_message.lower() == 'naruto':
            await message.channel.send(f'dattebayo!')
            return


#bot status cycle
@client.event
async def status_cycle():
    await client.wait_until_ready()
    statuses = [
        f"on {len(client.guilds)} servers | >help", "with your mom", ">help", "GTA 6", "Minecraft 2", "souls of the innocent", "Terraria: Otherworld", "Half Life 3"
    ]
    while not client.is_closed():
        status = random.choice(statuses)
        await client.change_presence(activity=discord.Game(name=status))
        await asyncio.sleep(30)
client.loop.create_task(status_cycle())


#the help command
@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(title = "Help", description = "List of commands!")
    embed.add_field(name = "Fun", value = "greet, gun, joke") 
    embed.add_field(name = "Sample", value = "dm, embed")
    embed.add_field(name = "Technical", value = "ping, support, changelog")
    await ctx.send(embed=embed)


#command cooldown
@client.event
async def on_command_error(
    ctx,
    error,
):
    if isinstance(error, commands.CommandOnCooldown):
        error = (
            'Wait right there, buster! ({:.1f}s remaining)'
        ).format(error.retry_after)
        await ctx.send(error)

        
#commands
#fun commands
#greet
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def greet(ctx):
    username_cmd = str(ctx.author).split("#")[0]
    await ctx.send(f"sup {username_cmd}")

#joke
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def joke(ctx):
    await ctx.send("you're the joke, but jokes are on the way. not like im selling you or anything. hehe.")

#gun
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def gun(ctx):
    username_cmd = str(ctx.author).split("#")[0]
    await ctx.send(f"{username_cmd}, put down the gun! let's talk this out. oh wait, i can't sustain a conversation.")



    
#sample commands
#dm
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def dm(ctx):
    await ctx.message.author.send("sup!")

#embed   
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def embed(ctx):
    embed = discord.Embed(title="Click me for a surprise!",
                          url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                          description="Click the link, Fool",
                          color=discord.Color.gold())

    embed.set_author(
        name="[REDACTED]",
        icon_url="https://art.pixilart.com/284dd75b8ac19a4.png?v=1487022662")

    await ctx.send(embed=embed)

    
#technical commands
#ping
@client.command()
async def ping(ctx):
    await ctx.send(f'Ping: {round (client.latency * 1000)} ms')

#support
@client.command()
async def support(ctx):
    await ctx.send(f'You can contact the dev: tama#4853')
    
#changelog
@client.command()
async def changelog(ctx):
    embed = discord.Embed(title = "Changelog",
                          url = "https://github.com/icybe/tamabot",
                          description = "Version 0.2.4 Patch Notes: \n-Replaced the default help command with '>help' that will display all the commands, in my style. \n-Commands are now arranged in categories: Fun, Sample, Technical. \n-Removed message cooldown system due to technical difficulties and unintended features. \-nAdded some new bot statuses! \n-Added new commands: support, changelog \n-Quality of life changes for bot messages. \n-Decreased cooldown for '>joke' command from 10s to 5s \n-Changed the cooldown warning message.")
    await ctx.send(embed=embed)
    

#economy commands
#balance
@client.command()
async def balance(ctx):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()
  wallet_amt = users[str(user.id)]["wallet"]
  bank_amt = users[str(user.id)]["bank"]
  
  embed = discord.Embed(title = f"{ctx.author.name}'s balance", color = discord.Color.red())
  embed.add_field(name = "wallet", value = wallet_amt)
  embed.add_field(name = "bank", value = bank_amt)
  await ctx.send(embed=embed)

#beg
@client.command()
async def beg(ctx):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_bank_data()
  earnings = random.randrange(101)
  await ctx.send(f"tamabot gave you {earnings} coins! filthy.")
  users[str(user.id)]["wallet"] += earnings

#economy helper functions
#open_account
async def open_account(user):
    users = await get_bank_data()
    
    if str(user.id) in users:
      return False
    else:
      users[str(user.id)] = {}
      users[str(user.id)]["wallet"] = 0
      users[str(user.id)]["bank"] = 0
      
    with open("mainbank.json","r") as f:
      json.dump(users, f)
    return True
  
 async def get_bank_data():
    with open("mainbank.json","r") as f:
      users = json.load(f)
    return users
  
#store_bank_data
async def store_bank_data():
    with open("mainbank.json","r") as f:
      json.dump(users, f)
  

#hosting
keep_alive()
my_secret = os.environ['TOKEN']

client.run(my_secret)
