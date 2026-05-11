import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv
from google import genai

# ======================
# LOAD ENV
# ======================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ======================
# GEMINI CLIENT
# ======================
client = genai.Client(api_key=GEMINI_API_KEY)

# ======================
# DISCORD SETUP
# ======================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# MEMORY SYSTEM
# ======================
MEMORY_FILE = "memory.txt"

def save_memory(text):
    if text and len(text) > 2:
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(random.sample(lines, min(len(lines), 20)))
    except:
        return ""

# ======================
# MESSAGE COUNTER
# ======================
message_counter = 0

# ======================
# READY EVENT
# ======================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ======================
# MAIN BOT LOGIC
# ======================
@bot.event
async def on_message(message):

    global message_counter

    if message.author == bot.user:
        return

    save_memory(message.content)
    message_counter += 1

    # ======================
    # TRIGGERS
    # ======================
    is_mentioned = bot.user in message.mentions

    is_reply_to_bot = (
        message.reference
        and message.reference.resolved
        and message.reference.resolved.author == bot.user
    )

    random_talk = message_counter >= 5 and random.random() < 0.4

    should_reply = is_mentioned or is_reply_to_bot or random_talk

    # ======================
    # AI RESPONSE
    # ======================
    if should_reply:

        message_counter = 0

        learned_style = load_memory()

        prompt = f"""
You are a friendly Discord AI bot.

You talk casually like server members:
- short replies
- slang
- emojis
- natural tone

Here are example messages from the server:
{learned_style}

User message:
{message.content}
"""

        async with message.channel.typing():
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                text = response.text

                if not text or text.strip() == "":
                    await message.channel.send("I tried to respond but got nothing 🤔")
                    return

                await message.channel.send(text[:2000])

            except Exception as e:
                await message.channel.send(f"Error: {str(e)}")

    await bot.process_commands(message)

# ======================
# RUN BOT
# ======================
bot.run(DISCORD_TOKEN)