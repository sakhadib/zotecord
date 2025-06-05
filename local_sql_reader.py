# local_sql_reader.py

import sqlite3

# Replace korbe nijer Zotero profile folder name & username
ZOT_DB_PATH = r"C:\Users\sakha\AppData\Roaming\Zotero\Zotero\Profiles\abc12345.default\zotero.sqlite"

conn = sqlite3.connect(f"file:{ZOT_DB_PATH}?mode=ro", uri=True)
cursor = conn.cursor()

def get_item_id_from_key(item_key):
    cursor.execute("SELECT itemID FROM items WHERE itemKey = ?", (item_key,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return None

def get_annotations_by_itemID(item_id):
    sql = """
    SELECT annotationText, annotationColor
    FROM itemAnnotations
    WHERE parentItemID = ?
      AND annotationText IS NOT NULL
      AND annotationText != ''
    """
    cursor.execute(sql, (item_id,))
    rows = cursor.fetchall()
    annotations = []
    for text, color_hex in rows:
        c_name = hex_to_name(color_hex)
        if not c_name:
            continue
        annotations.append({
            'text': text.strip(),
            'color': c_name
        })
    return annotations

def hex_to_name(hex_color):
    if not hex_color or not hex_color.startswith("#"):
        return None
    c = hex_color.lower().lstrip("#")
    if len(c) == 3:
        c = "".join([ch*2 for ch in c])
    try:
        r = int(c[0:2], 16)
        g = int(c[2:4], 16)
        b = int(c[4:6], 16)
    except:
        return None
    if r > 240 and g > 240 and b < 100:
        return 'yellow'
    elif g > 200 and r < 100 and b < 100:
        return 'green'
    elif b > 200 and r < 100 and g < 100:
        return 'blue'
    elif r > 200 and g < 100 and b < 100:
        return 'red'
    elif r > 100 and b > 100 and g < 100:
        return 'purple'
    else:
        return None

if __name__ == "__main__":
    ikey = input("Enter Zotero itemKey (e.g. RFCM2DHI): ").strip()
    iid = get_item_id_from_key(ikey)
    if not iid:
        print(f"No itemID found for key {ikey}.")
    else:
        print("Numeric itemID:", iid)
        anns = get_annotations_by_itemID(iid)
        if not anns:
            print("No annotations found under this item.")
        else:
            print("Found annotations:")
            for ann in anns:
                print(f"  • [{ann['color']}] {ann['text'][:60]}…")
    conn.close()
