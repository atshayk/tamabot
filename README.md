# Tamabot - Discord Bot

![VERSION](https://img.shields.io/badge/version-0.4.2-green.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Mistral](https://img.shields.io/badge/mistral-ai-violet.svg)
![DISCORD](https://img.shields.io/badge/discord-1f2933?logo=discord&logoColor=ffffff)


A general-purpose, feature-rich Discord bot with AI chat capabilities, music playback, Steam game information, and news aggregation.


## Features

### 🤖 AI Chat
- Interactive conversations with Mistral models
- Context-aware responses with conversation memory
- Multiple AI models to choose from
- Personality: Sassy yet helpful assistant

### 🎵 Music Player
- Play music from YouTube URLs or search terms
- Queue management system
- Voice channel controls (join/leave, pause/resume, skip, stop)
- Display current queue and now playing information

### 🎮 Steam Integration
- Find free games currently available on Steam
- Browse discounted games and deals
- View top selling games on Steam
- Search for specific games on Steam
- Look up Steam user profiles

### 📰 News Aggregation
- Top headlines from around the world
- Technology and business news
- Search news by keywords
- News categorized by source

### ✍️ More features in active development!
- Fun and creative commands
- Admin actions
- Agentic tooling
- Economy features and minigames
- External database connection
- Even more additions to existing features!

## Commands

### General Commands
- `>hello` - Friendly greeting
- `>ping` - Check bot latency
- `>info` - Display bot information
- `>help` - Show all available commands

### AI Chat Commands
- `@tamabot Hey, who's Newton?` - mention the bot to initiate a conversation!
- `>ask <question>` - Ask the AI anything
- `>clear_memory` - Reset your conversation history
- `>list_models` - See available AI models
- `>set_model [model]` - Switch AI models
- `>diagnose_model` - Check AI service status
- `>talktoforge` - Talks to [TaskForge](https://github.com/Mohit-Mano06/TaskForge-Bot), a rival bot developed by my friend Momo.

### Music Commands
- `>join` - Join your voice channel
- `>leave` - Leave the voice channel
- `>play [query]` - Play a song from YouTube
- `>skip` - Skip the current song
- `>pause` - Pause playback
- `>resume` - Resume playback
- `>stop` - Stop playback and clear queue
- `>queue` - Show current music queue

### Steam Commands
- `>freegames` - Show currently free games
- `>deals [limit]` - Show discounted games
- `>topgames [limit]` - Show top selling games
- `>steamstatus` - Check Steam service status
- `>steamsearch [query]` - Search for games
- `>steamuser <steam_id>` - Get user info

### News Commands
- `>news [query]` - Get top headlines or search for news
- `>newssearch [query]` - Better searching for news
- `>technews` - Get latest technology news
- `>businessnews` - Get latest business news
- `>newsources` - List available news sources

## Installation

1. Clone the repository
2. Install required dependencies
3. Set up your environment variables in a `.env` file
4. Run the bot: `python main.py`

### Requirements
- Python 3.13
- FFmpeg installed on system
- Discord bot token
- Mistral AI API key
- Steam API key
- NewsAPI key
- See more below VVV

## Technical Specifications

### Core Technologies
- **Python 3.13**
- **discord.py** - Discord API wrapper
- **Mistral AI** - Language model integration
- **yt-dlp** - YouTube audio streaming
- **FFmpeg** - Audio processing

### Libraries & Dependencies
- `discord.py` - Discord bot framework
- `mistralai` - Mistral AI API client
- `yt-dlp` - YouTube downloading library
- `python-dotenv` - Environment variable management
- `aiohttp` - Asynchronous HTTP requests
- `newsapi-python` - NewsAPI client

### Hosting
- **Render**
- **UptimeRobot** for keep-alive monitoring
- Locally hosted currently.

---

*Made with ❤ by @atshayk*
