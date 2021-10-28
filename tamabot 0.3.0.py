#tamabot
#version 0.3.0
#date 28/10/2021

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

#bot login
@bot.event
async def on_ready():
  print('We have logged in as {0-user}'.format(bot))
