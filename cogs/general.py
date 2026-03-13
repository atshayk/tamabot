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
    async def help(self, ctx, command_name: str = None):
        """Display all available commands or get help for a specific command"""
        if command_name is None:
            # Display general help
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
                "`>diagnose_model` - Check AI model status\n"
                "`>talktoforge <message>` - Talk to TaskForge bot directly"
            )
            embed.add_field(name="🧠 AI Chat Commands", value=llm_commands, inline=False)

            # Steam Commands
            steam_commands = (
                "`>freegames` - Show currently free games on Steam\n"
                "`>deals [limit]` - Show discounted games on Steam\n"
                "`>topgames [limit]` - Show top selling games\n"
                "`>steamstatus` - Check Steam service status\n"
                "`>steamsearch <query>` - Search for games on Steam\n"
                "`>steamuser <steam_id>` - Get Steam user info"
            )
            embed.add_field(name="🎮 Steam Commands", value=steam_commands, inline=False)

            # News Commands
            news_commands = (
                "`>news [query]` - Get top headlines or search news\n"
                "`>technews` - Get latest technology news\n"
                "`>businessnews` - Get latest business news\n"
                "`>newssearch <query>` - Search for news on a specific topic\n"
                "`>newssources` - List available news sources"
            )
            embed.add_field(name="📰 News Commands", value=news_commands, inline=False)

            embed.set_footer(text="Use >help <command> for more information about a specific command")
            await ctx.send(embed=embed)
        else:
            # Display specific command help
            command = self.bot.get_command(command_name)
            if command is None:
                await ctx.send(f"❌ Command `{command_name}` not found.")
                return

            embed = discord.Embed(
                title=f"📖 Help: {command_name}",
                color=discord.Color.green()
            )

            # Add command description
            if command.help:
                embed.description = command.help
            else:
                embed.description = "No description available."

            # Add command usage
            if command.signature:
                embed.add_field(
                    name="Usage",
                    value=f"`>{command_name} {command.signature}`",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Usage",
                    value=f"`>{command_name}`",
                    inline=False
                )

            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))