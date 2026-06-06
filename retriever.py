import os
import re
import pdfplumber
from config import DOCS_PATH

def _clean_spaces(text):
    """Normalize whitespace from extracted text, especially for PDFs.
    """
    # Collapse spaces and tabs (but keep newlines so paragraph breaks survive).
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3+ newlines down to a paragraph break.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing spaces on each line.
    text = re.sub(r" *\n", "\n", text)
    return text.strip()


def _read_txt(filepath):
    """Read a plain-text document."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def _read_pdf(filepath):
    """Extract text from a PDF, page by page, using pdfplumber.
    """
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text)
    return "\n\n".join(pages)


def load_documents():
    """Load all documents from the docs folder and process based on file type.
    Supports .txt and .pdf files. Returns a list of dicts with the document
    title (derived from the filename), the original filename for source
    attribution, and the cleaned full text.
    """
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        filepath = os.path.join(DOCS_PATH, filename)

        if filename.endswith(".txt"):
            text = _read_txt(filepath)
        elif filename.endswith(".pdf"):
            text = _read_pdf(filepath)
        else:
            continue

        text = _clean_spaces(text)
        if not text:
            print(f"  Skipping {filename}: no extractable text.")
            continue

        title = os.path.splitext(filename)[0].title()
        documents.append({
            "title": title,
            "filename": filename,
            "text": text,
        })

    print(f"Loaded {len(documents)} document(s): {[d['title'] for d in documents]}")
    return documents


# if __name__ == "__main__":
#     docs = load_documents()
#     for doc in docs:
#         print(f"\n=== {doc['title']} ({doc['filename']}) — {len(doc['text'])} chars ===")
#         print(doc["text"][:1000])
