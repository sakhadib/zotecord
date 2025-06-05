# import sqlite3
# import os

# # ───────────────────────────────────────────────────────────────────────────────
# # UPDATE THIS TO THE EXACT PATH OF YOUR Zotero sqlite DB (read-only).
# # For example (Windows):
# #    r"C:\Users\<YourUser>\Zotero\zotero.sqlite"
# # Or (macOS/Linux):
# #    "/Users/<YourUser>/Zotero/zotero.sqlite"
# ZOTERO_DB_PATH = r"C:\Users\sakha\Zotero\zotero.sqlite"
# # ───────────────────────────────────────────────────────────────────────────────

# def get_attachment_id_from_key(item_key: str) -> int | None:
#     """
#     Given a Zotero itemKey (e.g. "RFCM2DHI") that corresponds to a PDF‐attachment
#     (itemTypeID = 3 in your dump), return the numeric itemID from items.key.
#     Returns None if not found or not an attachment.
#     """
#     if not os.path.isfile(ZOTERO_DB_PATH):
#         raise FileNotFoundError(f"Zotero DB not found at: {ZOTERO_DB_PATH}")

#     conn = sqlite3.connect(f"file:{ZOTERO_DB_PATH}?mode=ro", uri=True)
#     cur = conn.cursor()
#     # Filter on itemTypeID = 3 to ensure it's an attachment
#     cur.execute("""
#         SELECT itemID
#         FROM items
#         WHERE key = ?
#           AND itemTypeID = 3
#     """, (item_key,))
#     row = cur.fetchone()
#     conn.close()
#     return row[0] if row else None


# def get_annotations_by_key(item_key: str) -> list[dict]:
#     """
#     Given a Zotero PDF‐attachment key, fetch all highlight annotations for that
#     attachment (annotation.type = 1) from itemAnnotations.
#     Returns a list of dicts: [ { "text": "...", "color": "yellow" }, ... ]
#     """
#     attachment_id = get_attachment_id_from_key(item_key)
#     if not attachment_id:
#         # No such attachment key (or not type=3)
#         return []

#     conn = sqlite3.connect(f"file:{ZOTERO_DB_PATH}?mode=ro", uri=True)
#     cur = conn.cursor()

#     # Fetch all highlight‐type rows for this attachment
#     cur.execute("""
#         SELECT annotationID,
#                text,
#                color
#         FROM itemAnnotations
#         WHERE parentItemID = ?
#           AND type = 1
#     """, (attachment_id,))
#     rows = cur.fetchall()
#     conn.close()

#     annotations = []
#     for annotation_id, raw_text, raw_color in rows:
#         color_name = hex_to_name(raw_color)
#         if color_name:
#             annotations.append({
#                 "annotationID": annotation_id,
#                 "text": raw_text.strip() if raw_text else "",
#                 "color": color_name
#             })
#     return annotations


# def hex_to_name(hex_color: str) -> str | None:
#     """
#     Convert a Zotero highlight color (hex string, e.g. "#ffd400", "#ff6666")
#     into one of: 'yellow', 'green', 'blue', 'purple', 'red'. Returns None if no match.

#     NB: We explicitly map both "#ffd400" (yellow) and "#ff6666" (orange/red)
#         into the "yellow" bucket (i.e. methods) because you requested that
#         yellow+orange both go → methods.
#     """
#     if not hex_color or not hex_color.startswith("#"):
#         return None

#     # Normalize to lowercase, strip '#'
#     h = hex_color.lstrip("#").lower()
#     # Expand 3-digit shorthand (e.g. "#fc0") to 6-digit ("ffcc00")
#     if len(h) == 3:
#         h = "".join(ch * 2 for ch in h)

#     mapping = {
#         "ffd400": "yellow",   # Zotero's default yellow
#         "ff6666": "yellow",   # Zotero's default red/orange  → remap to "yellow"
#         "5fb236": "green",    # Zotero's default green
#         "2ea8e5": "blue",     # Zotero's default blue
#         "a28ae5": "purple",   # Zotero's default purple
#         # (If you ever see new hex codes, add them here.)
#     }
#     return mapping.get(h)


import sqlite3
import os

# ───────────────────────────────────────────────────────────────────────────────
# UPDATE THIS TO THE EXACT PATH OF YOUR Zotero sqlite DB (read-only).
# For example (Windows):
#    r"C:\Users\<YourUser>\Zotero\zotero.sqlite"
# Or (macOS/Linux):
#    "/Users/<YourUser>/Zotero/zotero.sqlite"
ZOTERO_DB_PATH = r"C:\Users\sakha\Zotero\zotero.sqlite"
# ───────────────────────────────────────────────────────────────────────────────

def get_attachment_id_from_key(item_key: str) -> int | None:
    """
    Given a Zotero itemKey (e.g. "RFCM2DHI") that corresponds to a PDF attachment
    (itemTypeID = 3), return the numeric itemID from items.key.
    Returns None if not found or not an attachment.
    """
    if not os.path.isfile(ZOTERO_DB_PATH):
        raise FileNotFoundError(f"Zotero DB not found at: {ZOTERO_DB_PATH}")

    conn = sqlite3.connect(f"file:{ZOTERO_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()
    # itemTypeID = 3 means “attachment” in your dump
    cur.execute("""
        SELECT itemID
        FROM items
        WHERE key = ?
          AND itemTypeID = 3
    """, (item_key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_annotations_by_key(item_key: str) -> list[dict]:
    """
    Given a Zotero PDF-attachment key, fetch all highlight annotations for that
    attachment (type = 1) from itemAnnotations. Returns a list of dicts:
      [ { 'itemID': ..., 'text': "...", 'color': "yellow" }, ... ]
    """
    attachment_id = get_attachment_id_from_key(item_key)
    if not attachment_id:
        # No such attachment key (or not itemTypeID=3)
        return []

    conn = sqlite3.connect(f"file:{ZOTERO_DB_PATH}?mode=ro", uri=True)
    cur = conn.cursor()

    # Fetch all highlight‐type rows for this attachment
    # In your dump, `type = 1` means “highlight”
    cur.execute("""
        SELECT 
            itemID,    -- this is the primary key in itemAnnotations
            text,
            color
        FROM itemAnnotations
        WHERE parentItemID = ?
          AND type = 1
    """, (attachment_id,))
    rows = cur.fetchall()
    conn.close()

    annotations = []
    for ann_item_id, raw_text, raw_color in rows:
        color_name = hex_to_name(raw_color)
        # Only keep ones that map into our five buckets
        if color_name:
            annotations.append({
                "itemID": ann_item_id,
                "text": raw_text.strip() if raw_text else "",
                "color": color_name
            })
    return annotations


def hex_to_name(hex_color: str) -> str | None:
    """
    Convert a Zotero highlight color (hex string, e.g. "#ffd400", "#ff6666")
    into one of: 'yellow', 'green', 'blue', 'purple', 'red'. Returns None if no match.

    NB: We explicitly map both "#ffd400" (yellow) and "#ff6666" (orange/red)
        into the "yellow" bucket (i.e. methods) because you requested that
        yellow + orange both map → methods.
    """
    if not hex_color or not hex_color.startswith("#"):
        return None

    # Normalize to lowercase, strip '#'
    h = hex_color.lstrip("#").lower()
    # Expand 3‐digit shorthand (e.g. "#fc0") to 6‐digit ("ffcc00")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)

    # Exact‐match mapping of the five colors you saw in the dump
    mapping = {
        "ffd400": "yellow",   # Zotero's default yellow
        "ff6666": "yellow",   # Zotero's default red/orange → remapped to "yellow"
        "5fb236": "green",    # Zotero's default green
        "2ea8e5": "blue",     # Zotero's default blue
        "a28ae5": "purple",   # Zotero's default purple
        # If Zotero ever uses a different hex code, add it here.
    }
    return mapping.get(h)
