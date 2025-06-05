import discord
import re
from config import DISCORD_TOKEN, COLOR_CHANNEL_MAP
from zotero_reader import get_annotations_by_doi

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Only respond to commands starting with \pull
    if message.content.startswith("\\pull "):
        doi_match = re.search(r'\\pull\s+(.+)', message.content)
        if not doi_match:
            await message.channel.send("❌ Invalid format. Use `\\pull <doi>`")
            return

        doi = doi_match.group(1).strip()
        await message.channel.send(f"🔍 Pulling annotations for DOI: `{doi}`...")

        annotations = get_annotations_by_doi(doi)
        if not annotations:
            await message.channel.send("⚠️ No annotations found or DOI not in Zotero.")
            return

        for ann in annotations:
            color = ann['color']
            channel_id = COLOR_CHANNEL_MAP.get(color)
            if channel_id:
                target_channel = client.get_channel(int(channel_id))
                await target_channel.send(
                    f"📄 From [{ann['title']}]({ann['link']}) as `{color}` annotation:\n\n>>> {ann['text']}"
                )

        await message.channel.send("✅ Done sending annotations.")

client.run(DISCORD_TOKEN)
