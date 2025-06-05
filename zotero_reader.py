from pyzotero import zotero
from config import ZOTERO_API_KEY, ZOTERO_USER_ID
import fitz  # PyMuPDF

zot = zotero.Zotero(ZOTERO_USER_ID, 'user', ZOTERO_API_KEY)

def get_pdf_attachments():
    items = zot.items(itemType='attachment', limit=10)
    attachments = []
    for item in items:
        if 'pdf' in item['data'].get('filename', '').lower():
            attachments.append(item)
    return attachments

def parse_highlights_from_pdf(file_path):
    doc = fitz.open(file_path)
    highlights = []
    for page in doc:
        for annot in page.annots() or []:
            if annot.type[0] == 8:  # Highlight type
                info = annot.info
                color = str(annot.colors['stroke']).lower()
                text = annot.vertices
                quad_points = annot.vertices
                highlight_text = page.get_text("text", clip=annot.rect)
                highlights.append({
                    'color': color,
                    'text': highlight_text,
                    'page': page.number + 1
                })
    return highlights
