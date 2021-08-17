#tamabot
#version v0.2.3 demo 16/08/2021

import discord
from discord.ext import commands
from webserver import keep_alive
import os
import time
import random
import asyncio

#bot command
client = commands.Bot(command_prefix = ">")

#logging in the bot
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#bot responses
@client.event
async def on_message(message):
  await client.process_commands(message)
  username = str(message.author).split('#')[0]
  user_message = str(message.content)
  channel = str(message.channel.name)
  print(f'{username}: {user_message} ({channel})')

  global cooldown
  if message.content == 'hi' and cooldown.count(message.author.id) == 0:
        cooldown.append(message.author.id)
        await message.channel.send(f'Sup {username}')
        time.sleep(5)
        cooldown.remove(message.author.id)  

#bot status cycle        
@client.event
async def status_cycle():
    await client.wait_until_ready()
    statuses = [f"on {len(client.guilds)} servers | >help","with your mom",">help", "with and feeding on the souls of the innocent"]
    while not client.is_closed():
        status = random.choice(statuses)
        await client.change_presence(activity=discord.Game(name=status))
        await asyncio.sleep(10)
client.loop.create_task(status_cycle())

#commands
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def greet(ctx):
    username_cmd = str(ctx.author).split("#")[0]
    await ctx.send(f"sup {username_cmd}")

@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def joke(ctx):
    await ctx.send("you're the joke stupid bitch")
  
@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def gun(ctx):
  username_cmd = str(ctx.author).split("#")[0]
  await ctx.send(f"{username_cmd} phat se headshot")

@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def dm(ctx):
  await ctx.message.author.send("im not a girl sorry")

@client.command()
async def embed(ctx):
  embed=discord.Embed(
  title="Click me for a surprise!", 
  url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  description="Click the link, Fool", 
  color=discord.Color.gold())

  embed.set_author(
  name="[REDACTED]",
  icon_url="https://art.pixilart.com/284dd75b8ac19a4.png?v=1487022662")

  await ctx.send(embed=embed)

@client.command()
async def ping(ctx):
  await ctx.send(f'Ping: {round (client.latency * 1000)} ms')

#hosting
keep_alive()
my_secret = os.environ['TOKEN']

client.run(my_secret)
