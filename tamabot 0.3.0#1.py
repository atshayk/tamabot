#tamabot ALPHA 3
#version 0.3.0 snapshot #1
#date 20/07/2022

#imports
import discord
from discord.ext import commands
from webserver import keep_alive
import os
import random
import asyncio

#bot declaration
bot = commands.Bot(command_prefix=">")
#cooldown list
cooldown = []
#removing default help command
bot.remove_command("help")

#bot login
@bot.event
async def on_ready():
    print('We have logged in as {0-user}'.format(bot))

#bot status cycle
@bot.event
async def status_cycle():
    await bot.wait_until_ready()
    statuses = [f"on {len(bot.guilds)} servers | >help","your mom",">help","GTA 6","Minecraft 2","souls of the innocent","Terraria: Otherworld","Half Life 3","on the PS5","your dad"]
    while not bot.is_closed():
        status = random.choice(statuses)
        await bot.change_presence(activity=discord.Game(name=status))
        await asyncio.sleep(30)
bot.loop.create_task(status_cycle())

#bot error handling
@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.MissingPermissions):
        await ctx.send("You are missing some perms bro xD")
    elif isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("You are missing some required arguments dude lmao")
    elif isinstance(error, commands.CommandOnCooldown):
        cooldown_message = ('Wait right there, buster! ({:.1f}s remaining)').format(cooldown_message.retry_after)
        await ctx.send(cooldown_message)
    else:
        raise error
    
#bot command cooldown
# @bot.event
# async def on_command_cooldown(ctx,cooldown_message):
#     if isinstance(cooldown_message, commands.CommandOnCooldown):
#         cooldown_message = ('Wait right there, buster! ({:.1f}s remaining)').format(cooldown_message.retry_after)
#         await ctx.send(cooldown_message)
        
#commands
#the help command
@bot.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(title = "Need help with the bot?", description = "Here's a list of commands to try out!")
    embed.add_field(name = "Fun", value = "greet, gun, joke") 
    embed.add_field(name = "Sample", value = "dm, embed")
    embed.add_field(name = "Moderation", value = "purge, kick, ban(note: this command deletes all messages from previous 24hours), unban")
    embed.add_field(name = "Technical", value = "ping, support, changelog")
    await ctx.send(embed=embed)
    
#hosting
keep_alive()
my_secret = os.environ['TOKEN']
bot.run(my_secret)
