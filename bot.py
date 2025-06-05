import discord
import asyncio
from zotero_reader import get_annotations_by_key
import config

# ───────────────────────────────────────────────────────────────────────────────
# Make sure config.py contains:
#   DISCORD_TOKEN (your bot token)
#   COLOR_CHANNEL_MAP = {
#       "yellow": "<channel_id_for_methods>",
#       "green":  "<channel_id_for_contribution>",
#       "blue":   "<channel_id_for_results>",
#       "purple": "<channel_id_for_claims>",
#       "red":    "<channel_id_for_limitations>"
#   }
# ───────────────────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True   # <-- Required to read message.content
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user} (ID: {client.user.id})")
    print("Bot is ready to receive \\pullkey commands.")


@client.event
async def on_message(message: discord.Message):
    # Ignore messages from ourselves
    if message.author == client.user:
        return

    # Optional debug print—uncomment if you want to see every incoming message:
    # print(f"[debug] Got message: '{message.content}' from {message.author} in {message.channel}")

    content = message.content.strip()
    # Only respond to messages that start exactly with "\pullkey "
    if not content.lower().startswith(r"\pullkey "):
        return

    parts = content.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.channel.send("⚠️ Usage: `\\pullkey <ZoteroAttachmentKey>` (e.g. `\\pullkey RFCM2DHI`)")
        return

    item_key = parts[1].strip()
    await message.channel.send(f"🔍 Pulling annotations for Zotero itemKey: **{item_key}** ...")

    # Fetch all highlight annotations for this attachment key
    try:
        annotations = get_annotations_by_key(item_key)
    except FileNotFoundError as e:
        await message.channel.send(f"❌ Error: Zotero database not found. ({e})")
        return
    except Exception as e:
        await message.channel.send(f"❌ Unexpected error while reading Zotero DB: {e}")
        return

    if not annotations:
        await message.channel.send("⚠️ No annotations found (maybe invalid key or no highlights extracted).")
        return

    # Bucket by color name
    buckets = {
        "yellow": [],
        "green": [],
        "blue": [],
        "purple": [],
        "red": []
    }
    for ann in annotations:
        color = ann["color"]
        text  = ann["text"]
        if color in buckets:
            buckets[color].append(text)

    # Post each bucket to its designated channel
    for color_name, texts in buckets.items():
        if not texts:
            continue  # skip empty buckets

        channel_id_str = config.COLOR_CHANNEL_MAP.get(color_name)
        if not channel_id_str:
            continue  # no channel configured for this color

        # Attempt to get the channel from cache or via API
        try:
            target_channel = client.get_channel(int(channel_id_str))
        except Exception:
            target_channel = None

        if target_channel is None:
            try:
                target_channel = await client.fetch_channel(int(channel_id_str))
            except Exception:
                await message.channel.send(
                    f"⚠️ Could not find Discord channel for color '{color_name}'. Check COLOR_CHANNEL_MAP."
                )
                continue

        # Send a header + each highlight as its own message
        header = f"📌 **{color_name.upper()}** highlights for **{item_key}**:"
        await target_channel.send(header)
        for highlight_text in texts:
            snippet = highlight_text if len(highlight_text) <= 1900 else highlight_text[:1900] + "…"
            await target_channel.send(f"> {snippet}")

        # Short pause so Discord doesn’t rate-limit us
        await asyncio.sleep(0.5)

    # Notify the user that we’re done
    await message.channel.send("✅ Finished pushing all found highlights.")


if __name__ == "__main__":
    client.run(config.DISCORD_TOKEN)
