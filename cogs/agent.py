from discord.ext import commands
from mistralai.client import Mistral
import os
import json
import aiohttp
from typing import Optional


class Agent(commands.Cog):
    """Agent cog that enables Mistral AI to interact with bot functions through function calling"""

    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")

        self.client = Mistral(api_key=self.api_key)
        self._setup_tools()

    def _setup_tools(self):
        """Initialize available tools for the agent"""
        self.tools = [
            self._create_tool("get_steam_deals", "Get current Steam deals and discounts"),
            self._create_tool("get_top_games", "Get currently popular/played games on Steam"),
            self._create_tool("get_free_games", "Get currently free games on Steam"),
            self._create_tool("get_news_headlines", "Get latest news headlines", {
                "category": {
                    "type": "string",
                    "description": "News category (business, entertainment, general, health, science, sports, technology)",
                    "enum": ["business", "entertainment", "general", "health", "science", "sports", "technology"]
                }
            })
        ]

    def _create_tool(self, name: str, description: str, parameters: dict = None):
        """Helper to create tool definitions"""
        tool = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters if parameters else {},
                    "required": []
                }
            }
        }
        return tool

    async def _fetch_data(self, url: str, params: dict = None) -> dict:
        """Generic data fetching helper"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            raise Exception(f"Failed to fetch data: {str(e)}")

    async def get_steam_deals(self) -> str:
        """Fetch current Steam deals"""
        try:
            if not os.getenv('STEAM_API_KEY'):
                return "Steam API key not configured"

            # Simplified implementation - would connect to actual deals API in production
            return "Steam deals functionality connected"
        except Exception as e:
            return f"Error: {str(e)}"

    async def get_top_games(self) -> str:
        """Fetch top games on Steam"""
        try:
            if not os.getenv('STEAM_API_KEY'):
                return "Steam API key not configured"

            # Simplified implementation
            return "Top games functionality connected"
        except Exception as e:
            return f"Error: {str(e)}"

    async def get_free_games(self) -> str:
        """Fetch free games on Steam"""
        try:
            if not os.getenv('STEAM_API_KEY'):
                return "Steam API key not configured"

            url = "https://store.steampowered.com/api/featuredcategories/?cc=US&l=en"
            data = await self._fetch_data(url)

            if "free_weekend" in data:
                return json.dumps(data["free_weekend"])
            else:
                return "No free weekend games currently available"
        except Exception as e:
            return f"Error: {str(e)}"

    async def get_news_headlines(self, category: Optional[str] = None) -> str:
        """Fetch news headlines"""
        try:
            news_api_key = os.getenv('NEWS_API_KEY')
            if not news_api_key:
                return "News API key not configured"

            base_url = "https://newsapi.org/v2/top-headlines"
            params = {"apiKey": news_api_key, "pageSize": 5}

            if category:
                params["category"] = category

            data = await self._fetch_data(base_url, params)

            if data.get("articles"):
                headlines = []
                for article in data["articles"][:5]:
                    headlines.append({
                        "title": article.get("title"),
                        "description": article.get("description", "")[:100] + "..." if article.get(
                            "description") else "",
                        "url": article.get("url")
                    })
                return json.dumps(headlines)
            else:
                return "No news articles found"
        except Exception as e:
            return f"Error: {str(e)}"

    async def process_with_tools(self, question: str, conversation_history: list = None) -> str:
        """Process a question using Mistral AI with tool calling capability"""
        try:
            messages = conversation_history if conversation_history else []
            messages.append({"role": "user", "content": question})

            response = await self.client.chat.complete_async(
                model="mistral-large-latest",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            # Handle tool calls if present
            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

                # Execute the appropriate function
                if function_name == "get_steam_deals":
                    result = await self.get_steam_deals()
                elif function_name == "get_top_games":
                    result = await self.get_top_games()
                elif function_name == "get_free_games":
                    result = await self.get_free_games()
                elif function_name == "get_news_headlines":
                    result = await self.get_news_headlines(arguments.get("category"))
                else:
                    result = "Function not found"

                # Add the tool response to messages
                messages.append(response.choices[0].message)
                messages.append({
                    "role": "tool",
                    "name": function_name,
                    "content": result,
                    "tool_call_id": tool_call.id
                })

                # Get final response
                final_response = await self.client.chat.complete_async(
                    model="mistral-large-latest",
                    messages=messages
                )

                return final_response.choices[0].message.content
            else:
                return response.choices[0].message.content

        except Exception as e:
            return f"Error processing with tools: {str(e)}"

    @commands.command(name='askagent')
    async def ask_agent(self, ctx, *, question: str):
        """Ask the AI agent which can access various bot functions"""
        try:
            await ctx.typing()
            response = await self.process_with_tools(question)
            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")


async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(Agent(bot))