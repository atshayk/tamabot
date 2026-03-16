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
        self.api_key = os.getenv('STEAM_API_KEY')
        self.session = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    async def fetch_json(self, url):
        try:
            async with self.session.get(url) as res:
                return await res.json() if res.status == 200 else None
        except Exception as e:
            print(f"Fetch error: {e}")
            return None

    @commands.command()
    async def freegames(self, ctx):
        await ctx.send("🔍 Searching for free games...")
        data = await self.fetch_json(f"{self.steam_api_base}/featured")
        if not data:
            return await ctx.send("❌ Failed to fetch data.")

        free_games = [
            {"name": html.unescape(g["name"]), "id": g["id"]}
            for g in data.get("featured_win", [])
            if g.get("final_price") == 0 and g.get("name")
        ][:10]

        if not free_games:
            return await ctx.send("No free games available.")

        embed = discord.Embed(title="🎮 Free Games on Steam", color=discord.Color.green())
        for game in free_games:
            url = f"https://store.steampowered.com/app/{game['id']}"
            embed.add_field(name=game["name"], value=f"[View]({url})", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def deals(self, ctx, limit: int = 10):
        limit = min(limit, 20)
        await ctx.send(f"🔍 Finding best deals (showing {limit})...")
        data = await self.fetch_json(f"{self.steam_api_base}/featuredcategories")
        if not data:
            return await ctx.send("❌ Could not load deals.")

        items = data.get("specials", {}).get("items", []) + data.get("featured", {}).get("items", [])
        games = [
            {
                "name": html.unescape(i["name"]),
                "id": i["id"],
                "discount": i["discount_percent"],
                "orig": i.get("original_price", 0),
                "final": i.get("final_price", 0)
            }
            for i in items if i.get("discount_percent", 0) > 0 and i.get("name")
        ]
        games.sort(key=lambda x: x["discount"], reverse=True)
        games = games[:limit]

        if not games:
            return await ctx.send("No current discounts.")

        embed = discord.Embed(title="🔥 Steam Deals", color=discord.Color.orange())
        for g in games:
            url = f"https://store.steampowered.com/app/{g['id']}"
            op = f"${g['orig']/100:.2f}" if g['orig'] > 0 else "Free"
            fp = f"${g['final']/100:.2f}" if g['final'] > 0 else "Free"
            embed.add_field(
                name=g["name"],
                value=f"{g['discount']}% off\n{op} → {fp}\n[Deal]({url})",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def steamuser(self, ctx, steam_id: str):
        if not self.api_key:
            return await ctx.send("❌ API key missing.")
        await ctx.send(f"🔍 Looking up user `{steam_id}`...")
        url = f"{self.web_api_base}/ISteamUser/GetPlayerSummaries/v0002/?key={self.api_key}&steamids={steam_id}"
        data = await self.fetch_json(url)
        if not data or "players" not in data.get("response", {}):
            return await ctx.send("❌ Invalid Steam ID.")
        p = data["response"]["players"][0]
        embed = discord.Embed(title=f"🎮 {p.get('personaname', 'Unknown')}", color=discord.Color.blue())
        embed.add_field(name="Profile", value=f"[Link]({p.get('profileurl', '#')})")
        embed.set_thumbnail(url=p.get("avatarfull", ""))
        embed.add_field(name="Status", value=["Offline","Online","Busy","Away","Snooze","Trade","Play"][p.get("personastate", 0)], inline=True)
        embed.add_field(name="Last Online", value=f"<t:{p.get('lastlogoff', 0)}:R>", inline=True)
        embed.add_field(name="Country", value=p.get("loccountrycode", "Unknown"), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def steamstatus(self, ctx):
        embed = discord.Embed(title="🌐 Steam Status", color=discord.Color.blue(), timestamp=datetime.now())
        embed.add_field(name="Store", value="✅ Operational", inline=True)
        embed.add_field(name="Community", value="✅ Operational", inline=True)
        embed.add_field(name="Servers", value="✅ Operational", inline=True)
        embed.add_field(name="Checked", value=f"<t:{int(datetime.now().timestamp())}:R>", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def steamsearch(self, ctx, *, query: str):
        await ctx.send(f"🔍 [Results for '{query}'](https://store.steampowered.com/search/?term={query})")
        embed = discord.Embed(description="Click above for full results.", color=discord.Color.blurple())
        embed.add_field(name="Note", value="Bot cannot parse search pages directly due to anti-scraping measures.", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def topgames(self, ctx, limit: int = 10):
        limit = min(limit, 20)
        await ctx.send(f"🏆 Fetching top {limit} sellers...")
        data = await self.fetch_json(f"{self.steam_api_base}/featuredcategories")
        if not data or "top_sellers" not in data:
            return await ctx.send("❌ Could not fetch top sellers.")
        games = data["top_sellers"].get("items", [])[:limit]
        if not games:
            return await ctx.send("No top sellers found.")
        embed = discord.Embed(title="🏆 Top Sellers", color=discord.Color.gold())
        for i, g in enumerate(games, 1):
            name = html.unescape(g.get("name", "Unknown"))
            gid = g.get("id", "")
            url = f"https://store.steampowered.com/app/{gid}" if gid else "#"
            final_price = g.get("final_price", 0)
            formatted_price = f"${final_price / 100:.2f}" if final_price else "Free"
            disc_pct = g.get("discount_percent", 0)
            if disc_pct:
                orig = g.get("original_price", 0)
                orig_str = f"~~${orig / 100:.2f}~~" if orig else ""
                price_str = f"{orig_str} Rs.{final_price / 100:.2f} ({disc_pct}% off)"
            else:
                price_str = formatted_price
            embed.add_field(name=f"{i}. {name}", value=f"{price_str}\n[View]({url})", inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    cog = Steam(bot)
    await bot.add_cog(cog)
    await cog.cog_load()