from pyzotero import zotero
from config import ZOTERO_API_KEY, ZOTERO_USER_ID
import fitz  # PyMuPDF
import os

zot = zotero.Zotero(ZOTERO_USER_ID, 'user', ZOTERO_API_KEY)

# Hardcoded for now — replace with your synced Zotero folder if using ZotFile
ZOTERO_PDF_DIR = "C:\Users\sakha\Zotero\storage"

def get_annotations_by_doi(doi):
    items = zot.items(q=doi, qmode='everything')
    if not items:
        return []

    parent = items[0]
    title = parent['data']['title']
    link = f"https://doi.org/{doi}"

    # Get attachments (PDFs) of this item
    attachments = zot.children(parent['key'], itemType='attachment')
    pdf_path = None
    for att in attachments:
        if att['data']['linkMode'] == 'imported_file' and 'filename' in att['data']:
            pdf_file = att['data']['filename']
            storage_key = att['data']['key']
            pdf_path = os.path.join(ZOTERO_PDF_DIR, storage_key, pdf_file)
            break

    if not pdf_path or not os.path.exists(pdf_path):
        print(f"⚠️ PDF not found: {pdf_path}")
        return []

    return parse_annotations(pdf_path, title, link)

def parse_annotations(pdf_path, title, link):
    doc = fitz.open(pdf_path)
    annotations = []

    for page in doc:
        for annot in page.annots() or []:
            if annot.type[0] != 8:
                continue  # Skip non-highlight

            color_name = get_color_name(annot.colors['stroke'])
            if not color_name:
                continue

            text = page.get_text("text", clip=annot.rect).strip()
            if not text:
                continue

            annotations.append({
                'color': color_name,
                'text': text,
                'title': title,
                'link': link
            })

    return annotations

def get_color_name(rgb):
    """Convert RGB (0.0-1.0) to color name. Adjust thresholds if needed."""
    r, g, b = [round(x * 255) for x in rgb.values()]
    if r > 240 and g > 240 and b < 100:
        return 'yellow'
    elif r < 100 and g > 200 and b < 100:
        return 'green'
    elif r < 100 and g < 100 and b > 200:
        return 'blue'
    elif r > 200 and g < 100 and b < 100:
        return 'red'
    elif r > 100 and b > 100 and g < 100:
        return 'purple'
    else:
        return None
