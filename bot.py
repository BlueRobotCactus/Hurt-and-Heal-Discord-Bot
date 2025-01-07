import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
import discord
from discord import app_commands

# Load environment variables from the .env file
load_dotenv()

# Access the bot token from the .env file
TOKEN = os.getenv("DISCORD_TOKEN")

# Create bot instance
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Game Variables
max_hp = 2
characters = {
    "Character1": max_hp,
    "Character2": max_hp,
    "Character3": max_hp
}
cooldowns = {}  # Store user cooldowns
cooldown_time = timedelta(seconds=1)  # Set cooldown period

@bot.event
async def on_ready():
    """Triggered when the bot is ready."""
    await tree.sync()  # Sync slash commands with Discord
    print(f"Logged in as {bot.user.name}", flush=True)
    print(f"Bot is connected to {len(bot.guilds)} server(s).", flush=True)

@tree.command(name="status", description="Show the current status of all characters.")
async def status(interaction: discord.Interaction):
    """Show the current status of all characters."""
    status_message = "Current HP of characters:\n"
    for character, hp in characters.items():
        status_message += f"- **{character}**: {hp} HP\n"
    await interaction.response.send_message(status_message)

@tree.command(name="hurtheal", description="Hurt one character and heal another.")
@app_commands.describe(hurt_character="Character to hurt", heal_character="Character to heal")
async def hurtheal(interaction: discord.Interaction, hurt_character: str, heal_character: str):
    """Hurt one character and heal another."""
    user = interaction.user

    # Check cooldown
    if user in cooldowns and cooldowns[user] > datetime.now():
        remaining_time = cooldowns[user] - datetime.now()
        await interaction.response.send_message(f"You're on cooldown! Try again in {remaining_time.seconds} seconds.", ephemeral=True)
        return

    # Validate characters
    if hurt_character not in characters:
        await interaction.response.send_message(f"**{hurt_character}** is not a valid character!", ephemeral=True)
        return
    if heal_character not in characters:
        await interaction.response.send_message(f"**{heal_character}** is not a valid character!", ephemeral=True)
        return
    if hurt_character == heal_character:
        await interaction.response.send_message("You cannot hurt and heal the same character!", ephemeral=True)
        return

    # Update HP
    if characters[hurt_character] > 0:  # Only hurt if character isn't eliminated
        characters[hurt_character] -= 2
    characters[heal_character] += 1

    # Check for elimination
    if characters[hurt_character] <= 0:
        await interaction.response.send_message(f"**{hurt_character}** has been eliminated!")

    # Set cooldown
    cooldowns[user] = datetime.now() + cooldown_time

    # Send update
    await interaction.response.send_message(f"**{user.display_name}** hurt **{hurt_character}** and healed **{heal_character}**!")
    await status(interaction)

@tree.command(name="reset", description="Reset the game.")
@app_commands.checks.has_role("Game Master")
async def reset(interaction: discord.Interaction):
    """Reset the game."""
    global characters, cooldowns
    characters = {key: max_hp for key in characters.keys()}  # Reset characters' HP
    cooldowns = {}  # Clear cooldowns
    await interaction.response.send_message("The game has been reset!")
    await status(interaction)

@reset.error
async def reset_error(interaction: discord.Interaction, error):
    """Handle errors for the reset command."""
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have permission to reset the game!", ephemeral=True)

# Run the bot
bot.run(TOKEN)
