# cogs/general.py
import discord
from discord.ext import commands
import asyncio

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        """Simple hello command"""
        await asyncio.sleep(0.1)
        await ctx.send('Hello there! I am your Discord bot!')

    @commands.command()
    async def ping(self, ctx):
        """Check bot latency"""
        await asyncio.sleep(0.1)
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! Latency: {latency}ms')

    @commands.command()
    async def info(self, ctx):
        """Display bot information"""
        await asyncio.sleep(0.1)
        embed = discord.Embed(
            title="Bot Information",
            description="Sassy, yet helpful chatbot",
            color=discord.Color.blue()
        )
        embed.add_field(name="Version", value="v0.4.0", inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Prefix", value=">", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        """Display all available commands"""
        embed = discord.Embed(
            title="🤖 Tamabot Commands",
            description="Here's a list of all available commands:",
            color=discord.Color.blurple()
        )

        # General Commands
        general_commands = (
            "`>hello` - Say hello to the bot\n"
            "`>ping` - Check bot latency\n"
            "`>info` - Display bot information\n"
            "`>help` - Show this help message"
        )
        embed.add_field(name="-General Commands-", value=general_commands, inline=False)

        # Music Commands
        music_commands = (
            "`>join` - Join your voice channel\n"
            "`>leave` - Leave the voice channel\n"
            "`>play <query>` - Play a song from YouTube\n"
            "`>skip` - Skip the current song\n"
            "`>pause` - Pause the current song\n"
            "`>resume` - Resume the paused song\n"
            "`>stop` - Stop playback and clear queue\n"
            "`>queue` - Show the current queue"
        )
        embed.add_field(name="🎵 Music Commands", value=music_commands, inline=False)

        # LLM Commands
        llm_commands = (
            "`>ask <question>` - Ask the AI a question\n"
            "`>clear_memory` - Clear your conversation history\n"
            "`>list_models` - List available AI models\n"
            "`>set_model <model>` - Set the AI model to use\n"
            "`>diagnose_model` - Check AI model status"
        )
        embed.add_field(name="🧠 AI Chat Commands", value=llm_commands, inline=False)

        # Steam Commands
        steam_commands = (
            "`>freegames` - Show currently free games on Steam\n"
            "`>deals [limit]` - Show discounted games on Steam\n"
            "`>topgames [limit]` - Show top selling games\n"
            "`>steamstatus` - Check Steam service status\n"
            "`>steamsearch <query>` - Search for games on Steam\n"
            "`>steamuser <steam_id>` - Get Steam user info (requires API key)"
        )
        embed.add_field(name="🎮 Steam Commands", value=steam_commands, inline=False)

        embed.set_footer(text="Use >help <command> for more information about a specific command")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))