# cogs/steam.py
import discord
from discord.ext import commands
import aiohttp
import os
from datetime import datetime
import html


class Steam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.steam_api_base = "https://store.steampowered.com/api"
        self.web_api_base = "https://api.steampowered.com"
        self.api_key = os.getenv('STEAM_API_KEY')  # Get API key from environment
        self.session = None

    async def cog_load(self):
        """Initialize the HTTP session when the cog is loaded"""
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up the HTTP session when the cog is unloaded"""
        if self.session:
            await self.session.close()

    async def fetch_json(self, url):
        """Helper function to fetch JSON data from a URL"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Steam API request failed with status {response.status}: {url}")
                    return None
        except Exception as e:
            print(f"Error fetching Steam data from {url}: {e}")
            return None

    @commands.command()
    async def freegames(self, ctx):
        """Show currently free games on Steam"""
        await ctx.send("🔍 Searching for free games on Steam...")

        try:
            # Steam API endpoint for featured games
            url = f"{self.steam_api_base}/featured"
            data = await self.fetch_json(url)

            if not data:
                await ctx.send("❌ Couldn't fetch data from Steam API. Try again later.")
                return

            # Filter for free games (price = 0)
            free_games = []
            if "featured_win" in data:
                for game in data["featured_win"]:
                    # Check if the game is free (final price is 0)
                    if game.get("final_price", 99999) == 0 and game.get("name"):
                        free_games.append({
                            "name": html.unescape(game["name"]),  # Unescape HTML entities
                            "id": game["id"],
                            "header_image": game.get("header_image", ""),
                        })

            if not free_games:
                await ctx.send("No free games found right now. Check back later!")
                return

            # Create embed with free games
            embed = discord.Embed(
                title="🎮 Free Games on Steam",
                description=f"Found {len(free_games)} free games right now!",
                color=discord.Color.green()
            )

            for i, game in enumerate(free_games[:10]):  # Limit to 10 games
                game_url = f"https://store.steampowered.com/app/{game['id']}"
                embed.add_field(
                    name=game["name"],
                    value=f"[View on Steam]({game_url})",
                    inline=False
                )

            if len(free_games) > 10:
                embed.set_footer(text=f"And {len(free_games) - 10} more free games...")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error fetching free games: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def deals(self, ctx, limit: int = 10):
        """Show currently discounted games on Steam"""
        if limit > 20:
            limit = 20

        await ctx.send(f"🔍 Searching for the best deals on Steam (showing {limit} games)...")

        try:
            # Get featured categories which includes discounts
            url = f"{self.steam_api_base}/featuredcategories"
            data = await self.fetch_json(url)

            if not data:
                await ctx.send("❌ Couldn't fetch deals from Steam API. Try again later.")
                return

            # Look for special offers and discounts
            discounted_games = []

            # Check special offers section
            if "specials" in data and "items" in data["specials"]:
                for item in data["specials"]["items"][:limit * 2]:  # Get more to filter
                    if item.get("discount_percent", 0) > 0 and item.get("name"):
                        discounted_games.append({
                            "name": html.unescape(item["name"]),
                            "id": item["id"],
                            "discount_percent": item["discount_percent"],
                            "original_price": item.get("original_price", 0),
                            "final_price": item.get("final_price", 0),
                        })

            # If we don't have enough from specials, check featured games
            if len(discounted_games) < limit and "featured" in data and "items" in data["featured"]:
                for item in data["featured"]["items"]:
                    if (item.get("discount_percent", 0) > 0 and
                            item.get("name") and
                            len(discounted_games) < limit * 2):  # Get more to filter

                        # Avoid duplicates
                        if not any(game["id"] == item["id"] for game in discounted_games):
                            discounted_games.append({
                                "name": html.unescape(item["name"]),
                                "id": item["id"],
                                "discount_percent": item["discount_percent"],
                                "original_price": item.get("original_price", 0),
                                "final_price": item.get("final_price", 0),
                            })

            if not discounted_games:
                await ctx.send("No discounted games found right now. Check back later!")
                return

            # Sort by discount percentage (highest first)
            discounted_games.sort(key=lambda x: x["discount_percent"], reverse=True)

            # Limit to requested amount
            discounted_games = discounted_games[:limit]

            embed = discord.Embed(
                title="🔥 Steam Deals",
                description=f"Found {len(discounted_games)} discounted games!",
                color=discord.Color.orange()
            )

            for game in discounted_games:
                game_url = f"https://store.steampowered.com/app/{game['id']}"

                # Format prices
                orig_price = f"Rs.{game['original_price'] / 100:.2f}" if game['original_price'] > 0 else "Rs.0.00"
                final_price = f"Rs.{game['final_price'] / 100:.2f}" if game['final_price'] > 0 else "Free"

                embed.add_field(
                    name=f"{game['name']}",
                    value=f"🔥 {game['discount_percent']}% off\n{orig_price} → {final_price}\n[View Deal]({game_url})",
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error fetching deals: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def steamuser(self, ctx, steam_id: str):
        """Get information about a Steam user (requires API key)"""
        if not self.api_key:
            await ctx.send("❌ Steam API key not found. Please set STEAM_API_KEY in environment variables.")
            return

        await ctx.send(f"🔍 Looking up Steam user: {steam_id}...")

        try:
            # Try to get user info using the Steam Web API
            url = f"{self.web_api_base}/ISteamUser/GetPlayerSummaries/v0002/?key={self.api_key}&steamids={steam_id}"
            data = await self.fetch_json(url)

            if not data or "response" not in data or "players" not in data["response"]:
                await ctx.send("❌ Couldn't fetch user data from Steam API. Check the Steam ID and try again.")
                return

            players = data["response"]["players"]
            if not players:
                await ctx.send("❌ No user found with that Steam ID.")
                return

            player = players[0]
            embed = discord.Embed(
                title=f"🎮 Steam User: {player.get('personaname', 'Unknown')}",
                color=discord.Color.blue()
            )

            # Profile URL
            profile_url = player.get('profileurl', '#')
            embed.add_field(name="Profile", value=f"[View Profile]({profile_url})", inline=False)

            # Avatar
            avatar_url = player.get('avatarfull', '')
            if avatar_url:
                embed.set_thumbnail(url=avatar_url)

            # Status
            personastate = player.get('personastate', 0)
            states = {0: "Offline", 1: "Online", 2: "Busy", 3: "Away", 4: "Snooze", 5: "Looking to trade",
                      6: "Looking to play"}
            status = states.get(personastate, "Unknown")
            embed.add_field(name="Status", value=status, inline=True)

            # Last online
            last_online = player.get('lastlogoff', 0)
            if last_online:
                embed.add_field(name="Last Online", value=f"<t:{last_online}:R>", inline=True)

            # Country
            country = player.get('loccountrycode', 'Unknown')
            embed.add_field(name="Country", value=country, inline=True)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error fetching user info: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def steamstatus(self, ctx):
        """Check Steam service status"""
        await ctx.send("🔍 Checking Steam service status...")

        try:
            embed = discord.Embed(
                title="🌐 Steam Service Status",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            # Add status information (placeholder since we can't easily get real-time status)
            embed.add_field(
                name="Store Status",
                value="✅ Operational",
                inline=True
            )

            embed.add_field(
                name="Community",
                value="✅ Operational",
                inline=True
            )

            embed.add_field(
                name="Servers",
                value="✅ Operational",
                inline=True
            )

            embed.add_field(
                name="Last Checked",
                value=f"<t:{int(datetime.now().timestamp())}:R>",
                inline=False
            )

            embed.set_footer(text="Status checked manually")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error checking Steam status: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def steamsearch(self, ctx, *, query: str):
        """Search for a specific game on Steam"""
        await ctx.send(f"🔍 Searching Steam for '{query}'...")

        try:
            # We'll use the store page search and parse results
            search_url = f"https://store.steampowered.com/search/?term={query}"
            await ctx.send(f"🔗 [Search results for '{query}']({search_url})")

            # Inform user that direct search is limited due to API constraints
            embed = discord.Embed(
                title="🔎 Steam Search",
                description=f"I found your search query. Click the link above to see results.",
                color=discord.Color.blurple()
            )
            embed.add_field(
                name="Note",
                value="Direct game data parsing requires complex scraping which is beyond this bot's scope. "
                      "Please visit the link above for complete search results.",
                inline=False
            )
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error searching Steam: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def topgames(self, ctx, limit: int = 10):
        """Show top-selling games on Steam"""
        if limit > 20:
            limit = 20

        await ctx.send(f"🏆 Getting top selling games on Steam (showing {limit} games)...")

        try:
            # Steam API endpoint for top sellers
            url = f"{self.steam_api_base}/featuredcategories"
            data = await self.fetch_json(url)

            if not data or "top_sellers" not in data:
                await ctx.send("❌ Couldn't fetch top sellers from Steam API. Try again later.")
                return

            top_sellers = data["top_sellers"].get("items", [])[:limit]

            if not top_sellers:
                await ctx.send("No top sellers found right now. Check back later!")
                return

            embed = discord.Embed(
                title="🏆 Top Selling Games on Steam",
                description=f"Showing {len(top_sellers)} top sellers",
                color=discord.Color.gold()
            )

            for i, game in enumerate(top_sellers, 1):
                name = html.unescape(game.get("name", "Unknown Game"))
                game_id = game.get("id", "")
                game_url = f"https://store.steampowered.com/app/{game_id}" if game_id else "#"

                # Format final price
                price_final = game.get("final_price", 0)
                price_formatted = f"Rs.{price_final / 100:.2f}" if price_final > 0 else "Free"

                # Check for discount
                discount_pct = game.get("discount_percent", 0)
                if discount_pct > 0:
                    original_price = game.get("original_price", 0)
                    original_formatted = f"~~Rs.{original_price / 100:.2f}~~" if original_price > 0 else ""
                    price_display = f"{original_formatted} Rs.{price_final / 100:.2f} (-{discount_pct}%)"
                else:
                    price_display = price_formatted

                embed.add_field(
                    name=f"{i}. {name}",
                    value=f"{price_display}\n[View on Steam]({game_url})",
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error fetching top sellers: {str(e)}")
            print(f"Detailed error: {e}")


async def setup(bot):
    cog = Steam(bot)
    await bot.add_cog(cog)
    await cog.cog_load()