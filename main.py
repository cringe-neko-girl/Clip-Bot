import logging
import os
import asyncio
from setup import discord, commands
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create a bot instance
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'), help_command=None, intents=intents)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    await setup_cogs()

# Define the setup function for cogs
async def setup_cogs():
    logger.info("Setting up cogs")
    cog_dir = "Cogs"
    for filename in os.listdir(cog_dir):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            logger.debug(f"Loading cog: {cog_name}")
            cog_module = __import__(f"{cog_dir}.{cog_name}", fromlist=[""])
            for obj_name in dir(cog_module):
                obj = getattr(cog_module, obj_name)
                if isinstance(obj, commands.CogMeta):
                    await bot.add_cog(obj(bot))
                    logger.info(f"{obj.qualified_name} cog setup completed")

# Function to start the bot
async def start_bot():
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(start_bot())
