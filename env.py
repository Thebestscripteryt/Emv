import discord
from discord.ext import commands
import subprocess
import os
import tempfile
import re
import aiohttp
from dotenv import load_dotenv
import os

print("FILES:", os.listdir("."))
print("LUNE EXISTS:", os.path.exists("./lune.txt"))

# --- Load ENV ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

BEAUTIFIER_FILE = "beautified.luau.txt"
LUNE_PATH = "./lune.txt"  # change if needed

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# --- ENV COMMAND (PUBLIC) ---
@bot.command(name="env")
async def env(ctx, *, args: str = None):
    target_code = ""

    # 1. Attachment
    if ctx.message.attachments:
        try:
            attachment = ctx.message.attachments[0]
            target_code = (await attachment.read()).decode("utf-8", errors="ignore")
        except Exception as e:
            await ctx.send(f"❌ File error: {e}")
            return

    # 2. Code block
    elif args and "```" in args:
        match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", args)
        target_code = match.group(1) if match else args.replace("```", "")

    # 3. URL
    elif args and args.startswith(("http://", "https://")):
        url = args.replace("pastebin.com/", "pastebin.com/raw/")
        msg = await ctx.send("🌐 Fetching script...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as res:
                    if res.status == 200:
                        target_code = await res.text()
                        await msg.delete()
                    else:
                        await msg.edit(content=f"❌ Failed ({res.status})")
                        return
        except Exception as e:
            await msg.edit(content=f"❌ Error: {e}")
            return

    # 4. Raw text
    elif args:
        target_code = args

    if not target_code.strip():
        await ctx.send("❌ Provide code / file / URL")
        return

    if not os.path.exists(BEAUTIFIER_FILE):
        await ctx.send(f"❌ Missing `{BEAUTIFIER_FILE}`")
        return

    with open(BEAUTIFIER_FILE, "r", encoding="utf-8") as f:
        framework = f.read()

    msg = await ctx.send("⚙️ Running sandbox...")

    combined = f"""
{framework}

local targetPayload = [===[{target_code}]===]
local chunk, err = loadstring(targetPayload)

if chunk then
    pcall(chunk)
else
    print("[ERROR] " .. tostring(err))
end
"""

    temp_path = None
    out_path = None

    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".luau", mode="w", encoding="utf-8") as tmp:
            tmp.write(combined)
            temp_path = tmp.name

        # Run LUNE
        result = subprocess.run(
            [LUNE_PATH, "run", temp_path],
            capture_output=True,
            text=True,
            timeout=15
        )

        output = (result.stdout + result.stderr).strip()
        if not output:
            output = "No output."

        # Save output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as out:
            out.write(output[:19000])  # limit size
            out_path = out.name

        await msg.delete()
        await ctx.send(file=discord.File(out_path, "dump.txt"))

    except Exception as e:
        await msg.edit(content=f"❌ Error: {e}")

    finally:
        for p in [temp_path, out_path]:
            if p and os.path.exists(p):
                os.remove(p)

# --- Start Bot ---
if not TOKEN:
    print("❌ DISCORD_TOKEN not found")
else:
    bot.run(TOKEN)
