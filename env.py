import discord
from discord.ext import commands
import subprocess
import os
import tempfile
import re
import aiohttp
import base64
from dotenv import load_dotenv

# --- Load ENV ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

BEAUTIFIER_FILE = "beautified.luau.txt"
LUNE_PATH = "./lune.txt"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command(name="env")
async def env(ctx, *, args: str = None):
    target_code = ""

    # 1. Attachment
    if ctx.message.attachments:
        try:
            target_code = (await ctx.message.attachments[0].read()).decode("utf-8", errors="ignore")
        except Exception as e:
            await ctx.send(f"❌ File error: {e}")
            return
    # 2. Code block
    elif args and "```" in args:
        match = re.search(r"
http://googleusercontent.com/immersive_entry_chip/0
