import discord
from config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == "general":
                try:
                    await channel.send("hey i'm here to help you manage zotero connection, developed by @sakhadib")
                except Exception as e:
                    print(f"Failed to send message in {channel.name}: {e}")

client.run(DISCORD_TOKEN)
