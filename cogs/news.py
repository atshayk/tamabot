# cogs/news.py
import discord
from discord.ext import commands
import os
from newsapi.newsapi_client import NewsApiClient


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('NEWS_API_KEY')
        self.newsapi = None

        if self.api_key:
            try:
                self.newsapi = NewsApiClient(api_key=self.api_key)
                print("News API client configured successfully")
            except Exception as e:
                print(f"Error configuring News API client: {e}")
        else:
            print("NEWS_API_KEY not found in environment variables!")

    def _create_article_embed(self, articles, title, color):
        """Helper function to create embed from articles"""
        embed = discord.Embed(
            title=title,
            description=f"Found {len(articles)} articles",
            color=color
        )

        for i, article in enumerate(articles[:5], 1):  # Show top 5 articles
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            url = article.get('url', '#')
            source = article.get('source', {}).get('name', 'Unknown source')

            # Truncate description if too long
            if description and len(description) > 200:
                description = description[:200] + "..."

            embed.add_field(
                name=f"{i}. {title}",
                value=f"{description}\n📝 {source} | [Read more]({url})",
                inline=False
            )

        embed.set_footer(text="Powered by NewsAPI")
        return embed

    @commands.command()
    async def news(self, ctx, *, query: str = None):
        """Get top headlines. Optionally search for a specific topic."""
        if not self.api_key:
            await ctx.send("NEWS_API_KEY not found in environment variables!")
            return

        if not self.newsapi:
            await ctx.send("News API client is not properly configured.")
            return

        await ctx.send("🔍 Fetching latest news...")

        try:
            # Get top headlines
            if query:
                # Search for specific topic
                top_headlines = self.newsapi.get_top_headlines(
                    q=query,
                    language='en',
                    page_size=10
                )
            else:
                # Get general top headlines
                top_headlines = self.newsapi.get_top_headlines(
                    language='en',
                    page_size=10
                )

            if not top_headlines or top_headlines.get('status') != 'ok':
                await ctx.send("❌ Couldn't fetch news articles. Try again later.")
                return

            articles = top_headlines.get('articles', [])
            if not articles:
                await ctx.send("No news articles found.")
                return

            # Create embed with news articles
            embed = self._create_article_embed(articles, "📰 Top Headlines", discord.Color.red())
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error fetching news: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def technews(self, ctx):
        """Get latest technology news"""
        if not self.api_key:
            await ctx.send("NEWS_API_KEY not found in environment variables!")
            return

        if not self.newsapi:
            await ctx.send("News API client is not properly configured.")
            return

        await ctx.send("🔍 Fetching latest technology news...")

        try:
            # Get technology news
            tech_news = self.newsapi.get_top_headlines(
                category='technology',
                language='en',
                page_size=10
            )

            if not tech_news or tech_news.get('status') != 'ok':
                await ctx.send("❌ Couldn't fetch technology news. Try again later.")
                return

            articles = tech_news.get('articles', [])
            if not articles:
                await ctx.send("No technology articles found.")
                return

            # Create embed with tech news
            embed = self._create_article_embed(articles, "💻 Technology News", discord.Color.blue())
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error fetching technology news: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def businessnews(self, ctx):
        """Get latest business news"""
        if not self.api_key:
            await ctx.send("NEWS_API_KEY not found in environment variables!")
            return

        if not self.newsapi:
            await ctx.send("News API client is not properly configured.")
            return

        await ctx.send("🔍 Fetching latest business news...")

        try:
            # Get business news
            business_news = self.newsapi.get_top_headlines(
                category='business',
                language='en',
                page_size=10
            )

            if not business_news or business_news.get('status') != 'ok':
                await ctx.send("❌ Couldn't fetch business news. Try again later.")
                return

            articles = business_news.get('articles', [])
            if not articles:
                await ctx.send("No business articles found.")
                return

            # Create embed with business news
            embed = self._create_article_embed(articles, "💼 Business News", discord.Color.gold())
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error fetching business news: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def newssearch(self, ctx, *, query: str):
        """Search for news on a specific topic"""
        if not self.api_key:
            await ctx.send("NEWS_API_KEY not found in environment variables!")
            return

        if not self.newsapi:
            await ctx.send("News API client is not properly configured.")
            return

        if not query:
            await ctx.send("Please provide a search term. Usage: `>newssearch <topic>`")
            return

        await ctx.send(f"🔍 Searching news for '{query}'...")

        try:
            # Search for articles
            all_articles = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=10
            )

            if not all_articles or all_articles.get('status') != 'ok':
                await ctx.send("❌ Couldn't search news articles. Try again later.")
                return

            articles = all_articles.get('articles', [])
            if not articles:
                await ctx.send(f"No articles found for '{query}'.")
                return

            # Create embed with search results
            embed = self._create_article_embed(articles, f"🔍 News Search: {query}", discord.Color.purple())
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error searching news: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def newssources(self, ctx):
        """List available news sources"""
        if not self.api_key:
            await ctx.send("NEWS_API_KEY not found in environment variables!")
            return

        if not self.newsapi:
            await ctx.send("News API client is not properly configured.")
            return

        await ctx.send("🔍 Fetching news sources...")

        try:
            # Get sources
            sources_response = self.newsapi.get_sources(language='en')

            if not sources_response or sources_response.get('status') != 'ok':
                await ctx.send("❌ Couldn't fetch news sources. Try again later.")
                return

            sources = sources_response.get('sources', [])
            if not sources:
                await ctx.send("No news sources found.")
                return

            # Create embed with sources
            embed = discord.Embed(
                title="📡 News Sources",
                description=f"Found {len(sources)} sources",
                color=discord.Color.green()
            )

            # Group sources by category
            categories = {}
            for source in sources:
                category = source.get('category', 'other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(source.get('name', 'Unknown'))

            for category, source_list in categories.items():
                if len(source_list) > 10:  # Limit to 10 sources per category
                    source_list = source_list[:10] + [f"...and {len(source_list) - 10} more"]

                embed.add_field(
                    name=category.title(),
                    value=", ".join(source_list),
                    inline=False
                )

            embed.set_footer(text="Powered by NewsAPI")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error fetching news sources: {str(e)}")
            print(f"Detailed error: {e}")


async def setup(bot):
    await bot.add_cog(News(bot))