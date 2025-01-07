import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
import discord
from discord.ext import commands

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Variables
characters = {"Character1": 10, "Character2": 10, "Character3": 10}  # Replace with your fandom characters
cooldowns = {}  # Store user cooldowns
cooldown_time = timedelta(seconds=1)  # Set cooldown period (e.g., 30 seconds)

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
    if characters[hurt_character] > 0:  # Only allow hurting if character is not eliminated
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
async def reset(ctx):
    """Reset the game."""
    global characters, cooldowns
    characters = {key: 25 for key in characters.keys()}  # Reset characters' HP to 25
    cooldowns = {}  # Clear cooldowns
    await ctx.send("The game has been reset!")
    await status(ctx)

# Run the bot
load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))
