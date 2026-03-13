# cogs/music.py
import discord
from discord.ext import commands
import yt_dlp
import asyncio
import logging

# Set up logging for this cog
logger = logging.getLogger(__name__)


def format_duration(duration):
    """Format duration in seconds to HH:MM:SS or MM:SS"""
    if duration is None:
        return "Unknown"

    minutes, seconds = divmod(int(duration), 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"


def get_video_info(query):
    """Extract video info from YouTube"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'source_address': '0.0.0.0',
        'default_search': 'auto'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if query.startswith('http'):
            info = ydl.extract_info(query, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)

        return info


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.now_playing = {}

    @commands.command()
    async def join(self, ctx):
        """Join the user's voice channel"""
        try:
            if ctx.author.voice is None:
                await ctx.send("You need to be in a voice channel to use this command!")
                return

            channel = ctx.author.voice.channel
            if ctx.voice_client is not None:
                if ctx.voice_client.channel == channel:
                    await ctx.send("I'm already in your voice channel!")
                    return
                await ctx.voice_client.move_to(channel)
                await ctx.send(f"Moved to {channel.name}")
            else:
                await channel.connect()
                await ctx.send(f"Joined {channel.name}")

        except discord.Forbidden:
            await ctx.send("I don't have permission to join that voice channel!")
        except discord.ClientException as e:
            await ctx.send(f"Voice connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Join command error: {e}", exc_info=True)
            await ctx.send(f"An unexpected error occurred: {str(e)}")

    @commands.command()
    async def leave(self, ctx):
        """Leave the current voice channel"""
        try:
            if ctx.voice_client is None:
                await ctx.send("I'm not in a voice channel!")
                return

            # Clear queue for this guild
            if ctx.guild.id in self.queues:
                self.queues[ctx.guild.id] = []

            if ctx.guild.id in self.now_playing:
                self.now_playing[ctx.guild.id] = None

            await ctx.voice_client.disconnect()
            await ctx.send("Left the voice channel")

        except Exception as e:
            logger.error(f"Leave command error: {e}", exc_info=True)
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command()
    async def play(self, ctx, *, query):
        """Play a song from YouTube"""
        if ctx.voice_client is None:
            await ctx.send("I'm not in a voice channel! Use `>join` first.")
            return

        try:
            await ctx.send(f"Searching for: {query}")

            # Get video info
            info = await asyncio.get_event_loop().run_in_executor(None, get_video_info, query)

            # Handle playlist vs single video
            if 'entries' in info and info['entries']:
                video = info['entries'][0]
            else:
                video = info

            url = video.get('url', '')
            title = video.get('title', 'Unknown Title')
            duration = video.get('duration', 0)
            duration_str = format_duration(duration)

            # Add to queue
            if ctx.guild.id not in self.queues:
                self.queues[ctx.guild.id] = []

            self.queues[ctx.guild.id].append({
                'url': url,
                'title': title,
                'duration': duration_str,
                'requester': ctx.author.name
            })

            queue_pos = len(self.queues[ctx.guild.id])
            # Only play immediately if nothing is currently playing
            if not ctx.voice_client.is_playing():
                # Play the first song in queue without sending duplicate message
                await self.play_immediate(ctx)
            else:
                await ctx.send(f"➕ Added to queue: **{title}** (Position: {queue_pos})")

        except Exception as e:
            logger.error(f"Play command error: {e}", exc_info=True)
            await ctx.send(f"Error playing song: {str(e)}")

    async def play_immediate(self, ctx):
        """Play the first song in queue immediately"""
        try:
            if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
                song = self.queues[ctx.guild.id][0]  # Get first song but don't remove it yet

                # Update now playing
                self.now_playing[ctx.guild.id] = song['title']

                # Send the "Now playing" message
                await ctx.send(
                    f"🎵 Now playing: **{song['title']}** ({song['duration']}) requested by {song['requester']}")

                # Actually play the song
                await self._play_song(ctx, song)
            else:
                await ctx.send("⏹️ Queue is empty!")
        except Exception as e:
            logger.error(f"Play immediate error: {e}", exc_info=True)
            await ctx.send(f"Error playing song: {str(e)}")

    async def _play_song(self, ctx, song):
        """Actually play a song"""
        try:
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }

            player = discord.FFmpegPCMAudio(song['url'], **ffmpeg_options)

            def after_playing(error):
                if error:
                    logger.error(f"Player error: {error}")
                # Remove the song from queue after it finishes
                if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
                    if self.queues[ctx.guild.id]:
                        self.queues[ctx.guild.id].pop(0)
                # Schedule next song
                fut = asyncio.run_coroutine_threadsafe(self.play_next_callback(ctx), self.bot.loop)

            ctx.voice_client.play(player, after=after_playing)
        except Exception as e:
            logger.error(f"Play song error: {e}", exc_info=True)
            await ctx.send(f"Error playing song: {str(e)}")

    async def play_next_callback(self, ctx):
        """Callback for playing next song"""
        try:
            await self.play_next_in_queue(ctx)
        except Exception as e:
            logger.error(f"Error in play_next_callback: {e}", exc_info=True)

    async def play_next_in_queue(self, ctx):
        """Play the next song in the queue"""
        try:
            if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
                # The current song was already removed in after_playing callback
                if self.queues[ctx.guild.id]:  # Check if there are more songs
                    song = self.queues[ctx.guild.id][0]  # Get next song

                    # Update now playing
                    self.now_playing[ctx.guild.id] = song['title']

                    # Send the "Now playing" message
                    await ctx.send(
                        f"🎵 Now playing: **{song['title']}** ({song['duration']}) requested by {song['requester']}")

                    # Actually play the song
                    await self._play_song(ctx, song)
                else:
                    # Queue is empty
                    self.now_playing[ctx.guild.id] = None
                    await ctx.send("⏹️ Queue is empty! Add more songs with `>play`")
            else:
                # Queue is empty
                self.now_playing[ctx.guild.id] = None
                await ctx.send("⏹️ Queue is empty! Add more songs with `>play`")
        except Exception as e:
            logger.error(f"Play next error: {e}", exc_info=True)
            await ctx.send(f"Error playing next song: {str(e)}")

    @commands.command()
    async def skip(self, ctx):
        """Skip the current song"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("I'm not playing anything right now!")
            return

        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped the current song!")

    @commands.command()
    async def queue(self, ctx):
        """Show the current queue"""
        if ctx.guild.id not in self.queues or not self.queues[ctx.guild.id]:
            await ctx.send("The queue is empty!")
            return

        queue_list = self.queues[ctx.guild.id]
        embed = discord.Embed(title="Music Queue", color=discord.Color.blue())

        # Show now playing
        if ctx.guild.id in self.now_playing and self.now_playing[ctx.guild.id]:
            embed.add_field(name="Now Playing", value=self.now_playing[ctx.guild.id], inline=False)

        # Show queue
        queue_text = ""
        for i, song in enumerate(queue_list[:10], 1):  # Show only first 10
            queue_text += f"{i}. {song['title']} (requested by {song['requester']})\n"

        if len(queue_list) > 10:
            queue_text += f"\n... and {len(queue_list) - 10} more songs"

        embed.add_field(name="Up Next", value=queue_text or "Queue is empty", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def stop(self, ctx):
        """Stop playback and clear the queue"""
        if ctx.voice_client is None:
            await ctx.send("I'm not in a voice channel!")
            return

        # Clear queue
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id] = []

        if ctx.guild.id in self.now_playing:
            self.now_playing[ctx.guild.id] = None

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        await ctx.send("⏹️ Stopped playback and cleared the queue!")

    @commands.command()
    async def pause(self, ctx):
        """Pause the current song"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("I'm not playing anything right now!")
            return

        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused the current song!")

    @commands.command()
    async def resume(self, ctx):
        """Resume the paused song"""
        if ctx.voice_client is None:
            await ctx.send("I'm not in a voice channel!")
            return

        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed the current song!")
        else:
            await ctx.send("Nothing is paused!")


async def setup(bot):
    await bot.add_cog(Music(bot))