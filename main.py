# main.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
#import webserver  # Import web server for Render hosting / Will be implemented later...
import asyncio
import aiohttp
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.voice_states = True  # Required for music functionality

bot = commands.Bot(command_prefix='>', intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f'{bot.user} has logged in!')
    print('Bot is ready to use!')
    print(f'Currently in {len(bot.guilds)} guilds')


@bot.event
async def on_disconnect():
    print("Bot disconnected from Discord. Attempting to reconnect...")


@bot.event
async def on_resumed():
    print("Bot connection resumed!")


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Bot error in {event}: {sys.exc_info()}")


# Error handling
@bot.event
async def on_command_error(ctx, error):
    # Print the full error to console for debugging
    print(f"Command error: {error}")
    import traceback
    traceback.print_exception(type(error), error, error.__traceback__)

    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found!')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all required arguments.')
    elif isinstance(error, commands.CommandInvokeError):
        original_error = error.original
        print(f"Original error: {original_error}")
        await ctx.send(f'An error occurred: {str(original_error)}')
    else:
        await ctx.send('An error occurred while processing your command.')


async def create_bot_session():
    """Create a custom session with better connection settings"""
    connector = aiohttp.TCPConnector(
        limit=100,
        limit_per_host=30,
        ttl_dns_cache=300,
        use_dns_cache=True,
        ssl=False,  # Disable SSL verification if having SSL issues
    )
    return aiohttp.ClientSession(connector=connector)


async def connect_with_retry(bot, token, max_retries=5):
    """Attempt to connect with retry logic and better error handling"""
    # Create custom session for better stability
    # Note: We won't actually use the session here since discord.py handles its own sessions
    # But the concept is sound for future enhancements

    for attempt in range(max_retries):
        try:
            print(f"Connection attempt {attempt + 1}/{max_retries}")
            await bot.start(token)
            return True
        except discord.errors.DiscordServerError as e:
            if "503" in str(e) or "overflow" in str(e).lower():
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"503/Overflow error on attempt {attempt + 1}, waiting {wait_time} seconds before retry...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                continue
            else:
                print(f"Discord server error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                continue
        except Exception as e:
            print(f"Other error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
            continue
    return False


# Run the bot and web server
async def main():
    # Start web server for Render hosting
    try:
        # webserver.keep_alive()  # Uncomment for production
        # print("Web server started successfully")
        print("Web server would start here (temporarily disabled for testing)")
    except Exception as e:
        print(f"Warning: Could not start web server: {e}")

    # Load cogs (modules)
    initial_extensions = [
        'cogs.general',
        'cogs.llm',
        'cogs.music',
        'cogs.steam',
        'cogs.news'
        # 'cogs.admin' # WIP
    ]

    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            logger.info(f'Loaded extension: {extension}')
        except Exception as e:
            logger.error(f'Failed to load extension {extension}: {e}')

    # Run bot
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please check your .env file.")
        return

    # Attempt to connect with retry logic
    try:
        print("Attempting to connect to Discord...")
        success = await connect_with_retry(bot, token, max_retries=5)
        if not success:
            print("Failed to connect after all retries. Check your token and network connection.")
    except KeyboardInterrupt:
        print("Bot shutdown requested by user")
        await bot.close()
    except Exception as e:
        print(f"Failed to start bot: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")