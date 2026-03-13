# cogs/llm.py
from discord.ext import commands
import os
import asyncio
from mistralai.client import Mistral
import logging

logger = logging.getLogger(__name__)


class LLM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('MISTRAL_API_KEY')
        self.client = None
        self.model_name = 'open-mistral-7b'  # Default Mistral model
        self.conversations = {}  # Store conversation history per user

        if self.api_key:
            try:
                # Configure the Mistral client with proper API key
                self.client = Mistral(api_key=self.api_key)
                print("Mistral AI client configured successfully")
            except Exception as e:
                print(f"Error configuring Mistral AI client: {e}")
                self.client = None
        else:
            print("MISTRAL_API_KEY not found in environment variables!")

    @commands.command()
    async def ask(self, ctx, *, question):
        """Ask the bot a question using Mistral AI API"""
        await self._process_question(ctx, question)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Respond to mentions with AI functionality"""
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Check if bot is mentioned
        if self.bot.user.mentioned_in(message):
            # Extract the question content (remove bot mention)
            question = message.content
            for mention in message.mentions:
                question = question.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '')
            question = question.strip()

            # If there's actual content after removing mentions
            if question:
                # Create a context-like object for consistency
                class MockContext:
                    def __init__(self, messageInner):
                        self.message = messageInner
                        self.author = messageInner.author
                        self.channel = messageInner.channel
                        self.guild = messageInner.guild

                    async def send(self, content, **kwargs):
                        return await self.message.channel.send(content, **kwargs)

                ctx = MockContext(message)
                await self._process_question(ctx, question)

    async def _process_question(self, ctx, question):
        """Process a question using Mistral AI (shared between ask command and mentions)"""
        if not self.api_key:
            await ctx.send("MISTRAL_API_KEY not found in environment variables!")
            return

        if not self.client:
            await ctx.send("Mistral AI client is not properly configured.")
            return

        try:
            # Create a conversation key (user ID)
            user_id = str(ctx.author.id)
            channel_id = str(ctx.channel.id)
            conv_key = f"{channel_id}-{user_id}"

            # Initialize conversation history if not exists
            if conv_key not in self.conversations:
                self.conversations[conv_key] = []

            # Limit conversation history to last 10 messages to avoid context overflow
            conversation_history = self.conversations[conv_key][-10:] if self.conversations[conv_key] else []

            # Build conversation context
            system_prompt = "You are Tamabot, a quippy and helpful assistant. Be witty and conversational, striking a balance between friendly and sarcastic—never too sweet, never too rude. Keep it concise and fun."

            # Build the full conversation context
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history
            for msg in conversation_history:
                messages.append({"role": msg['role'].lower(), "content": msg['content']})

            # Add current question
            messages.append({"role": "user", "content": question})

            # Generate response with timeout
            response = await asyncio.wait_for(
                self.client.chat.complete_async(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000,
                ),
                timeout=30.0
            )

            if response and response.choices and response.choices[0].message.content:
                answer = response.choices[0].message.content
                # Limit response length for Discord
                if len(answer) > 500:
                    answer = answer[:500] + "... (response truncated)"

                await ctx.send(answer)

                # Store the conversation
                self.conversations[conv_key].append({"role": "User", "content": question})
                self.conversations[conv_key].append({"role": "Assistant", "content": answer})

                # Keep only last 20 messages (10 exchanges) to prevent memory bloat
                if len(self.conversations[conv_key]) > 20:
                    self.conversations[conv_key] = self.conversations[conv_key][-20:]
            else:
                await ctx.send("Received empty response from the AI model.")

        except asyncio.TimeoutError:
            await ctx.send("Sorry, the AI took too long to respond. Please try again.")
        except Exception as e:
            await ctx.send(f"Sorry, I encountered an error: {str(e)}")
            print(f"Detailed error: {e}")

    @commands.command()
    async def clear_memory(self, ctx):
        """Clear the conversation history for this user"""
        user_id = str(ctx.author.id)
        channel_id = str(ctx.channel.id)
        conv_key = f"{channel_id}-{user_id}"

        if conv_key in self.conversations:
            del self.conversations[conv_key]
            await ctx.send("Conversation memory cleared!")
        else:
            await ctx.send("No conversation history found.")

    @commands.command()
    async def list_models(self, ctx):
        """List available Mistral models"""
        await ctx.send("Available models you can try: open-mistral-7b, mistral-small-latest, mistral-large-latest")

    @commands.command()
    async def set_model(self, ctx, model_name: str):
        """Set the model to use"""
        available_models = ['open-mistral-7b', 'mistral-small-latest', 'mistral-large-latest']
        if model_name in available_models:
            self.model_name = model_name
            await ctx.send(f"Model set to: {model_name}")
        else:
            await ctx.send(f"Model {model_name} not available. Choose from: {', '.join(available_models)}")

    @commands.command()
    async def diagnose_model(self, ctx):
        """Diagnostic command to check Mistral library status"""
        try:
            if not self.client:
                await ctx.send("Mistral client not initialized")
                return

            # Test basic functionality
            await ctx.send(f"Mistral client is active. Current model: {self.model_name}")

        except Exception as e:
            await ctx.send(f"Diagnostic error: {str(e)}")


async def setup(bot):
    await bot.add_cog(LLM(bot))