# debug.py

import sqlite3
import os
import sys
import traceback

# ───────────────────────────────────────────────────────────────────────────────
# STEP 1: Change this to the exact path of your Zotero SQLite DB.
# For example (Windows):
#    r"C:\Users\<YourUser>\Zotero\zotero.sqlite"
# Or (macOS/Linux):
#    "/Users/<YourUser>/Zotero/zotero.sqlite"
ZOTERO_DB_PATH = r"C:\Users\sakha\Zotero\zotero.sqlite"
# ───────────────────────────────────────────────────────────────────────────────

OUTPUT_FILE = "debug_output.txt"


def log(line: str):
    """Append a line to debug_output.txt (and also print to console)."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def clear_log():
    """Erase any existing debug_output.txt before starting."""
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)


def lookup_item_id(conn: sqlite3.Connection, item_key: str) -> int | None:
    """
    Return itemID from 'items' table where key = item_key and itemTypeID = 35 (attachment).
    If not found, return None.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT itemID
        FROM items
        WHERE key = ?
          AND itemTypeID = 35
    """, (item_key,))
    row = cur.fetchone()
    return row[0] if row else None


def get_attachment_ids(conn: sqlite3.Connection, paper_id: int) -> list[int]:
    """
    Return a list of all attachment.itemID values whose parentItemID = paper_id.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT attachment.itemID
        FROM itemAttachments AS attachment
        WHERE attachment.parentItemID = ?
    """, (paper_id,))
    return [row[0] for row in cur.fetchall()]


def get_annotation_rows(conn: sqlite3.Connection, attachment_ids: list[int]) -> list[tuple]:
    """
    Given a list of attachmentIDs, fetch all rows from itemAnnotations where:
      parentItemID IN (the attachment_ids)
      AND annotationType = 1  (highlight)
    Returns a list of tuples (annotationID, parentItemID, annotationText, color).
    """
    if not attachment_ids:
        return []

    placeholders = ",".join("?" for _ in attachment_ids)
    query = f"""
        SELECT 
            annotationID,
            parentItemID,
            annotationText,
            color
        FROM itemAnnotations AS annotation
        WHERE annotation.parentItemID IN ({placeholders})
          AND annotation.annotationType = 1
    """
    cur = conn.cursor()
    cur.execute(query, attachment_ids)
    return cur.fetchall()


def main():
    clear_log()

    log("🔍 Starting Zotero debug run")
    log(f"→ Using Zotero DB at: {ZOTERO_DB_PATH}")

    # 1) Check that the DB file exists
    if not os.path.isfile(ZOTERO_DB_PATH):
        log("❌ ERROR: Zotero DB file not found at the specified path.")
        log("   Make sure ZOTERO_DB_PATH is correct and points to zotero.sqlite.")
        return

    # 2) Parse itemKey from command line
    if len(sys.argv) < 2:
        log("❌ ERROR: No itemKey provided.")
        log("   Usage: python debug.py <ZoteroItemKey>  (e.g. python debug.py RFCM2DHI)")
        return

    item_key = sys.argv[1].strip()
    log(f"→ Looking up itemKey: {item_key}")

    # 3) Open SQLite connection (read-only)
    try:
        conn = sqlite3.connect(f"file:{ZOTERO_DB_PATH}?mode=ro", uri=True)
    except Exception as e:
        log("❌ ERROR: Failed to open Zotero DB in read-only mode.")
        log(f"   Exception: {e}")
        traceback.print_exc(file=open(OUTPUT_FILE, "a"))
        return

    try:
        # 4) Lookup itemID
        paper_id = lookup_item_id(conn, item_key)
        if not paper_id:
            log(f"⚠️ No itemID found for key '{item_key}'.")
            log("   → Possible reasons: invalid key, or this item is not a PDF attachment (itemTypeID ≠ 35).")
            conn.close()
            return

        log(f"✅ Found itemID: {paper_id} for key '{item_key}'")

        # 5) Fetch attachment IDs under this paper_id
        attachment_ids = get_attachment_ids(conn, paper_id)
        if not attachment_ids:
            log(f"⚠️ No attachments found under itemID {paper_id}.")
            log("   → That means Zotero has no PDF‐attachment children for this item key.")
            conn.close()
            return

        log(f"✅ Attachment IDs under parentItemID={paper_id}:")
        for aid in attachment_ids:
            log(f"   • {aid}")
        log(f"   (total: {len(attachment_ids)})")

        # 6) Fetch highlight‐type annotations under those attachments
        annotation_rows = get_annotation_rows(conn, attachment_ids)
        if not annotation_rows:
            log("⚠️ No annotation rows found where annotationType = 1 (highlight).")
            log("   → Either you haven’t extracted highlights into Zotero,")
            log("     or the color codes aren’t standard, or annotationType ≠ 1.")
            conn.close()
            return

        log(f"✅ Found {len(annotation_rows)} annotation rows (annotationType=1).")
        log("⤷ Dumping each row's raw data below:")

        for idx, (annotation_id, parent_id, text, color) in enumerate(annotation_rows, start=1):
            log(f"   [{idx}] annotationID = {annotation_id}")
            log(f"         parentItemID = {parent_id}")
            # Truncate text if it's extremely long
            display_text = text.replace("\n", " ").strip()
            if len(display_text) > 200:
                display_text = display_text[:200] + "…(truncated)…"
            log(f"         annotationText = \"{display_text}\"")
            log(f"         color = \"{color}\"")
            log("   ────────────────────────────────────────────")

        # 7) Additionally, show distinct color values and counts
        log("\n🎨 Summarizing distinct color strings and their counts:")
        cur = conn.cursor()
        cur.execute("""
            SELECT color, COUNT(*) AS cnt
            FROM itemAnnotations
            WHERE parentItemID IN ({})
              AND annotationType = 1
            GROUP BY color
            ORDER BY cnt DESC
        """.format(",".join("?" for _ in attachment_ids)), attachment_ids)

        distincts = cur.fetchall()
        if not distincts:
            log("   (none)")
        else:
            for color_value, cnt in distincts:
                log(f"   • \"{color_value}\": {cnt} hits")

        conn.close()
        log("\n🏁 Debug run complete. See 'debug_output.txt' for full details.")

    except Exception as e:
        log("❌ ERROR during debug process:")
        log(f"   Exception: {e}")
        traceback.print_exc(file=open(OUTPUT_FILE, "a"))
        conn.close()


if __name__ == "__main__":
    main()
