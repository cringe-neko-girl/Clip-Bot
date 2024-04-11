# main.py - Entry point for Clip Bot

import os
import asyncio
import setup
from setup import discord, commands
from dotenv import load_dotenv

# Load environment variables from .env file
# load_dotenv(dotenv_path='secrets/.env')  # Specify the correct path to .env file

# Create a bot instance
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('?'), help_command=None, intents=intents)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Bannana!')

@bot.event
async def setup(bot):
    print("\n")
    print("===== Setting up Cogs =====")
    print("\n")

    # Define the directory where your additional Cogs are located
    cog_dir = "Cogs"
    print("\n")
    print("===== Additional Cogs =====")
    print("\n")
    # Iterate through files in the cog directory
    additional_cogs = []
    for filename in os.listdir(cog_dir):
        if filename.endswith(".py"):  # Check if the file is a Python file
            cog_name = filename[:-3]  # Remove the ".py" extension
            cog_module = __import__(f"{cog_dir}.{cog_name}", fromlist=[""])
            num_commands = len([obj for obj in dir(cog_module) if isinstance(getattr(cog_module, obj), commands.Command)])
            additional_cogs.append(f"{cog_name.ljust(20)} | ✅")

            # Dynamically import the module
            cog_module = __import__(f"{cog_dir}.{cog_name}", fromlist=[""])

            # Iterate through objects in the module
            for obj_name in dir(cog_module):
                # Get the object
                obj = getattr(cog_module, obj_name)
                # Check if the object is a subclass of commands.Cog
                if isinstance(obj, commands.CogMeta):
                    # Add the Cog to the bot
                    await bot.add_cog(obj(bot))
                    additional_cogs.append(f"🛠️  {obj.qualified_name} Cog setup completed.")

    # Print additional cogs
    for cog in additional_cogs:
        print(cog)

    print("\n")
    print("===== Setup Completed =====")
    print("\n")

    
# Run setup function
asyncio.get_event_loop().run_until_complete(setup(bot))

async def start_bot():
    await bot.start(os.getenv('DISCORD_TOKEN'))
    
        
if __name__ == "__main__":
  # Run the bot with the token from environment variables
  asyncio.run(start_bot())
