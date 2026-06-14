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

### Why this is the correct fix:
1. **No syntax errors:** By using `base64.b64encode`, characters like `]`, `[`, or `"` inside the user's obfuscated script are converted into standard letters and numbers. The Luau runner will never see a "malformed string" because your injection string is now just a clean line of text.
2. **Native decoding:** Using `require("@lune/base64")` is the standard way to handle data in Lune.
3. **Clean code:** Your `env.py` remains focused on bot logic, and `beautified.luau.txt` remains focused on logging.
