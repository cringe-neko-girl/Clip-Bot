import os
import asyncio
import setup
from setup import discord, commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a bot instance
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'), help_command=None, intents=intents)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Bannana!')
    await setup_cogs()

# Define the setup function for cogs
async def setup_cogs():
    print("\n===== Setting up Cogs =====\n")

    cog_dir = "Cogs"  # Specify the directory where your cogs are located

    # Iterate through files in the cog directory
    for filename in os.listdir(cog_dir):
        if filename.endswith(".py"):  # Only Python files
            cog_name = filename[:-3]  # Remove the file extension
            cog_module = __import__(f"{cog_dir}.{cog_name}", fromlist=[""])

            # Check and add the cog
            for obj_name in dir(cog_module):
                obj = getattr(cog_module, obj_name)
                if isinstance(obj, commands.CogMeta):
                    await bot.add_cog(obj(bot))
                    print(f"🛠️  {obj.qualified_name} Cog setup completed.")

    print("\n===== Setup Completed =====\n")

# Function to start the bot
async def start_bot():
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    # Run the bot with the token from environment variables
    asyncio.run(start_bot())
