#tamabot
#version v0.2.6
#date 03/10/2021

import discord
from discord.ext import commands
from webserver import keep_alive
import os
import random
import asyncio

#bot command
client = commands.Bot(command_prefix=">")
cooldown = []

#removing default help command
client.remove_command("help")

#logging in the bot
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


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
        
    a = 0 #a is message loop.
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
        elif user_message.lower() == "what's for dinner":
            await message.channel.send(f'your mom')
            return
        elif user_message.lower() == 'f':
            await message.channel.send(f'f')
            return
        elif user_message.lower() == "fire":
            await message.channel.send(f'🔥')
            return
        #bot reactions
        elif "check" in message.content:
            await msg.add_reaction("✔️")
        #automod
        filtered_words = ["carl wheezer"]
        for word in filtered_words:
            if word in message.content:
                await message.delete()
            await client.process_commands(message)

        
#bot status cycle
@client.event
async def status_cycle():
    await client.wait_until_ready()
    statuses = [
        f"on {len(client.guilds)} servers | >help","your mom",">help","GTA 6","Minecraft 2","souls of the innocent","Terraria: Otherworld","Half Life 3","on the PS5","your dad"]
    while not client.is_closed():
        status = random.choice(statuses)
        await client.change_presence(activity=discord.Game(name=status))
        await asyncio.sleep(30)
client.loop.create_task(status_cycle())


#error handling
@client.event
async def on_command(ctx,error):
  if isinstance(error,commands.MissingPermissions):
    await ctx.send("You are missing some perms bro xD")
  elif isinstance(error,commands.MissingRequiredArgument):
    await ctx.send("You are missing some required arguments dude lmao")
  #command cooldown
  elif isinstance(error, commands.CommandOnCooldown):
        error = (
            'Wait right there, buster! ({:.1f}s remaining)'
        ).format(error.retry_after)
        await ctx.send(error)
  else:
    raise error


#the help command
@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(title = "Help", description = "List of commands!")
    embed.add_field(name = "Fun", value = "greet, gun, joke") 
    embed.add_field(name = "Sample", value = "dm, embed")
    embed.add_field(name = "Moderation", value = "purge, kick, ban, unban")
    embed.add_field(name = "Technical", value = "ping, support, changelog")
    await ctx.send(embed=embed)

        
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

#poll
@client.command()
async def poll(ctx,*,msg):
  channel = ctx.channel
  try:
    op1,op2 = msg.split("or")
    txt = f"React with ✔️ for {op1} or ❌ for {op2}"
  except:
    await channel.send("correct syntax : [choice 1] or [choice 2]")
    return
  
  embed = discord.Embed(title = 'Poll', description = txt)
  message_ = await channel.send(embed = embed)
  await message_.add_reaction("✔️")
  await message_.add_reaction("❌")
  await ctx.message.delete()

    
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

    
#moderation commands
#purge
@client.command(aliases=['c'])
@commands.has_permissions(manage_messages = True)
async def purge(ctx,amount=2):
  await ctx.channel.purge(limit = amount)
  
#kick
@client.command(aliases=['k'])
@commands.has_permissions(kick_members = True)
async def kick(ctx,member : discord.Member,*,reason="No reason provided."):
  try:
    await member.send("You have been kicked from the server because: " + reason)
  except:
    await ctx.send(member.name + " has been kicked from the server because: " + reason)
    await member.kick(reason=reason)

#ban (note: this command deletes all messages from previous 24hours)
@client.command(aliases=['b'])
@commands.has_permissions(ban_members = True)
async def ban(ctx,member : discord.Member,*,reason="No reason provided."):
  try:
    await member.send("You have been banned from the server because: " + reason)
  except:
    await ctx.send(member.name + " has been banned from the server because: " + reason)
    await member.ban(reason=reason)

#unban
@client.command(aliases=['ub'])
@commands.has_permissions(ban_members = True)
async def unban(ctx,*,member): #unban name#tagno
    banned_users = await ctx.guild.bans()
    member_name, member_disc = member.split('#')
    for banned_entry in banned_users:
        user = banned_entry.user
        if(user.name, user.discriminator)==(member_name, member_disc):
            await ctx.guild.unban(user)
            await ctx.send(member_name + " has been unbanned.")
            return
        else:
            await ctx.send(member_name + " was not found.")

#mute (only used on tamabot dev server)
@client.command(aliases=['m'])
@commands.has_permissions(kick_members = True)
async def mute(ctx, member : discord.Member):
  muted_role = ctx.guild.get_role(894218462623326288)
  await member.add_roles(muted_role)
  await ctx.send(member.mention + " has been muted. lol!")

#unmute (only used on tamabot server)
@client.command(aliases=['um'])
@commands.has_permissions(kick_members = True)
async def unmute(ctx, member : discord.Member):
  muted_role = ctx.guild.get_role(894218462623326288)
  await member.remove_roles(muted_role)
  await ctx.send(member.mention + " has been unmuted.")
              
              
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
                          description = "Version 0.2.6 Patch Notes: \n -Added new commands: mute, unmute, poll \n -Added automod, it removes any message with 'carl wheezer' \n -Added error handling. \n -Added bot reactions! The bot now reacts to certain messages. \n -Added new bot messages. \n -The commands 'kick' and 'ban' will work now if the user's DMs are closed. #futureproof")
    await ctx.send(embed=embed)


#hosting
keep_alive()
my_secret = os.environ['TOKEN']

client.run(my_secret)
