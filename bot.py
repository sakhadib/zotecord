import discord
import asyncio
from zotero_reader import get_annotations_by_key, get_item_metadata, get_full_metadata
from google_sheets import append_to_sheet  # NEW
import config

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

SAKHA_ID = config.DISCORD_USER_ID
user_mention = f"<@{SAKHA_ID}>"

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user} (ID: {client.user.id})")
    print("Bot is ready to receive \\pull and \\push commands.")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    content = message.content.strip()

    # ──────────────────────────
    # HANDLE: \pull <item_key>
    # ──────────────────────────
    if content.lower().startswith(r"\pull "):
        parts = content.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await message.channel.send("⚠️ Usage: `\\pull <ZoteroAttachmentKey>` (e.g. `\\pull RFCM2DHI`)")
            return

        item_key = parts[1].strip()
        await message.channel.send(f"🔍 Pulling annotations for Zotero itemKey: **{item_key}** ...")

        try:
            annotations = get_annotations_by_key(item_key)
        except FileNotFoundError as e:
            await message.channel.send(f"❌ Zotero DB not found. ({e})")
            return
        except Exception as e:
            await message.channel.send(f"❌ Unexpected error: {e}")
            return

        if not annotations:
            await message.channel.send("⚠️ No annotations found.")
            return

        buckets = { "yellow": [], "green": [], "blue": [], "purple": [], "red": [] }
        for ann in annotations:
            color = ann["color"]
            text  = ann["text"]
            if color in buckets:
                buckets[color].append(text)

        metadata = get_item_metadata(item_key)
        title = metadata.get("title") or item_key
        url = metadata.get("url")

        for color_name, texts in buckets.items():
            if not texts:
                continue
            channel_id_str = config.COLOR_CHANNEL_MAP.get(color_name)
            if not channel_id_str:
                continue
            try:
                target_channel = client.get_channel(int(channel_id_str)) or await client.fetch_channel(int(channel_id_str))
            except Exception:
                await message.channel.send(f"⚠️ Could not find Discord channel for color '{color_name}'")
                continue

            label = config.COLOR_LABEL_MAP.get(color_name, color_name)
            intro = f"{user_mention} found '{label}' in the paper {f'[{title}]({url})' if url else title}"
            await target_channel.send(f"{intro} ")

            # chunked messages for Discord limit
            max_len = 2000
            bullet_chunks, current_chunk, current_len = [], [], 0
            for idx, text in enumerate(texts, start=1):
                bullet = f"{idx}. {text}"
                if current_len + len(bullet) + 1 > max_len:
                    bullet_chunks.append(current_chunk)
                    current_chunk, current_len = [], 0
                current_chunk.append(bullet)
                current_len += len(bullet) + 1
            if current_chunk:
                bullet_chunks.append(current_chunk)
            for chunk in bullet_chunks:
                await target_channel.send("\n".join(chunk))
            await target_channel.send("\u200b")

        await message.channel.send("✅ Finished pushing all found highlights.")
        return

    # ──────────────────────────
    # HANDLE: \push <item_key>
    # ──────────────────────────
    if content.lower().startswith(r"\push "):
        parts = content.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await message.channel.send("⚠️ Usage: `\\push <ZoteroAttachmentKey>` (e.g. `\\push RFCM2DHI`)")
            return

        item_key = parts[1].strip()
        await message.channel.send(f"📤 Pushing Zotero item **{item_key}** to Google Sheets...")

        try:
            data = get_full_metadata(item_key)
            if not data:
                await message.channel.send("⚠️ No metadata found for this key.")
                return
        except Exception as e:
            await message.channel.send(f"❌ Error extracting metadata: {e}")
            return

        # Fill the row for the sheet
        row = [
            config.USER_EMAIL,  # Email
            data.get("title"),
            "",  # Relevance (manual)
            data.get("authors"),
            data.get("year"),
            data.get("venue"),
            data.get("doi"),
            "",  # Tag (manual)
            data.get("claims"),
            data.get("limitations"),
            data.get("contributions"),
            data.get("methodology"),
            data.get("result"),
            "",  # Links (manual)
            "",  # Notes (manual)
        ]

        try:
            append_to_sheet(row)
            await message.channel.send("✅ Row added to Google Sheet successfully.")
        except Exception as e:
            await message.channel.send(f"❌ Failed to write to Google Sheet: {e}")


if __name__ == "__main__":
    client.run(config.DISCORD_TOKEN)