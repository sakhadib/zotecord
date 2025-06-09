import sqlite3
import os

# Update this path to match your Zotero installation
ZOTERO_DB_PATH = r"C:\Users\sakha\Zotero\zotero.sqlite"

def get_attachment_id_from_key(item_key: str) -> int | None:
    if not os.path.isfile(ZOTERO_DB_PATH):
        raise FileNotFoundError(f"Zotero DB not found at: {ZOTERO_DB_PATH}")

    conn = sqlite3.connect(f"file:{ZOTERO_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("""
        SELECT itemID
        FROM items
        WHERE key = ?
          AND itemTypeID = 3
    """, (item_key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def hex_to_name(hex_color: str) -> str | None:
    if not hex_color or not hex_color.startswith("#"):
        return None
    h = hex_color.lstrip("#").lower()
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    mapping = {
        "ffd400": "yellow",
        "ff6666": "red",
        "5fb236": "green",
        "2ea8e5": "blue",
        "a28ae5": "purple",
    }
    return mapping.get(h)

def get_annotations_by_key(item_key: str) -> list[dict]:
    attachment_id = get_attachment_id_from_key(item_key)
    if not attachment_id:
        return []

    conn = sqlite3.connect(f"file:{ZOTERO_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("""
        SELECT itemID, text, color
        FROM itemAnnotations
        WHERE parentItemID = ?
          AND type = 1
    """, (attachment_id,))
    rows = cur.fetchall()
    conn.close()

    annotations = []
    for ann_item_id, raw_text, raw_color in rows:
        color_name = hex_to_name(raw_color)
        if color_name:
            annotations.append({
                "itemID": ann_item_id,
                "text": raw_text.strip() if raw_text else "",
                "color": color_name
            })
    return annotations

def get_item_metadata(item_key: str) -> dict[str, str | None]:
    attach_id = get_attachment_id_from_key(item_key)
    if not attach_id:
        return {"title": None, "url": None}

    conn = sqlite3.connect(f"file:{ZOTERO_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()

    cur.execute("SELECT parentItemID FROM itemAttachments WHERE itemID = ?", (attach_id,))
    row = cur.fetchone()
    parent_id = row[0] if row else None
    if not parent_id:
        conn.close()
        return {"title": None, "url": None}

    def fetch_field(field_name: str):
        cur.execute("""
            SELECT v.value
            FROM itemData d
            JOIN itemDataValues v ON d.valueID = v.valueID
            JOIN fieldsCombined f ON d.fieldID = f.fieldID
            WHERE d.itemID = ?
              AND f.fieldName = ?
        """, (parent_id, field_name))
        row = cur.fetchone()
        return row[0] if row else None

    title = fetch_field("title")
    url = fetch_field("url")
    conn.close()
    return {"title": title, "url": url}

def format_bullets(texts: list[str]) -> str:
    bullets = [f"{idx}. {text}" for idx, text in enumerate(texts, start=1)]
    if bullets:
        return "\n\n".join(bullets) + "\n\n"
    return ""

def get_full_metadata(item_key: str) -> dict:
    attach_id = get_attachment_id_from_key(item_key)
    if not attach_id:
        return {}

    conn = sqlite3.connect(f"file:{ZOTERO_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT parentItemID FROM itemAttachments WHERE itemID = ?", (attach_id,))
    row = cur.fetchone()
    parent_id = row[0] if row else None
    if not parent_id:
        conn.close()
        return {}

    def fetch_field(field_name: str):
        cur.execute("""
            SELECT v.value
            FROM itemData d
            JOIN itemDataValues v ON d.valueID = v.valueID
            JOIN fieldsCombined f ON d.fieldID = f.fieldID
            WHERE d.itemID = ?
              AND f.fieldName = ?
        """, (parent_id, field_name))
        row = cur.fetchone()
        return row[0] if row else None

    def fetch_authors():
        cur.execute("""
            SELECT c.firstName, c.lastName
            FROM itemCreators ic
            JOIN creators c ON ic.creatorID = c.creatorID
            WHERE ic.itemID = ?
            ORDER BY ic.orderIndex
        """, (parent_id,))
        return [f"{fn} {ln}".strip() for fn, ln in cur.fetchall()]

    metadata = {
        "title": fetch_field("title"),
        "url": fetch_field("url"),
        "authors": ", ".join(fetch_authors()),
        "year": fetch_field("date"),
        "venue": fetch_field("publicationTitle"),
        "doi": fetch_field("DOI"),
    }

    annotations = get_annotations_by_key(item_key)
    color_map = {"yellow": [], "green": [], "blue": [], "purple": [], "red": []}
    for ann in annotations:
        color_map[ann["color"]].append(ann["text"])

    # Combine multiple highlights in a cell
    metadata.update({
        "methodology": format_bullets(color_map["yellow"]),
        "contributions": format_bullets(color_map["green"]),
        "result": format_bullets(color_map["blue"]),
        "claims": format_bullets(color_map["purple"]),
        "limitations": format_bullets(color_map["red"]),
    })

    conn.close()
    return metadata
