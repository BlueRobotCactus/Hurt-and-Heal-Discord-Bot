import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables from the .env file
load_dotenv()

# Access the bot token from the .env file
TOKEN = os.getenv("DISCORD_TOKEN")

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True # Required to read text commands
bot = commands.Bot(command_prefix="!", intents=intents)

# Game Variables
max_hp = 10
characters = {
    "Character1": max_hp,
    "Character2": max_hp,
    "Character3": max_hp
}
cooldowns = {}  # Store user cooldowns
cooldown_time = timedelta(seconds=1)  # Set cooldown period

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command()
async def status(ctx):
    """Show the current status of all characters."""
    status_message = "Current HP of characters:\n"
    for character, hp in characters.items():
        status_message += f"- {character}: {hp} HP\n"
    await ctx.send(status_message)

@bot.command()
async def hurtheal(ctx, hurt_character: str, heal_character: str):
    """Hurt one character and heal another."""
    user = ctx.author

    # Check cooldown
    if user in cooldowns and cooldowns[user] > datetime.now():
        remaining_time = cooldowns[user] - datetime.now()
        await ctx.send(f"You're on cooldown! Try again in {remaining_time.seconds} seconds.")
        return

    # Validate characters
    if hurt_character not in characters:
        await ctx.send(f"{hurt_character} is not a valid character!")
        return
    if heal_character not in characters:
        await ctx.send(f"{heal_character} is not a valid character!")
        return
    if hurt_character == heal_character:
        await ctx.send("You cannot hurt and heal the same character!")
        return

    # Update HP
    if characters[hurt_character] > 0:  # Only hurt if character isn't eliminated
        characters[hurt_character] -= 1
    characters[heal_character] += 1

    # Check for elimination
    if characters[hurt_character] == 0:
        await ctx.send(f"{hurt_character} has been eliminated!")

    # Set cooldown
    cooldowns[user] = datetime.now() + cooldown_time

    # Send update
    await ctx.send(f"{user.display_name} hurt {hurt_character} and healed {heal_character}!")
    await status(ctx)

@bot.command()
@commands.has_role("Game Master")  # Must have "Game Master" role to reset the game
async def reset(ctx):
    """Reset the game."""
    global characters, cooldowns
    characters = {key: max_hp for key in characters.keys()}  # Reset characters' HP
    cooldowns = {}  # Clear cooldowns
    await ctx.send("The game has been reset!")
    await status(ctx)

@reset.error
async def reset_error(ctx, error):
    """Handle errors for the reset command."""
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to reset the game!")

# Run the bot
bot.run(TOKEN)
