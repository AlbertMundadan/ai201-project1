import os
import re
import pdfplumber
from bs4 import BeautifulSoup
from config import (
    DOCS_PATH,
    CHUNK_SIZE,
    MAX_CHUNK_SIZE,
    CHUNK_OVERLAP,
    MIN_CHUNK_LENGTH,
)

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
    """Extract text from a PDF using pdfplumber."""
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text)
    return "\n\n".join(pages)


def _read_html(filepath):
    """Extract the main body text from an HTML page.
    Strips all markup so only the readable article text
    remains. Targets the page's main content container when one exists and
    falls back to <body> otherwise.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Drop non-content elements
    for tag in soup(["script", "style", "noscript", "nav", "header",
                     "footer", "aside", "form", "button", "svg", "iframe"]):
        tag.decompose()

    # Prefer the semantic main-content container; fall back to <body>, then the whole document if needed.
    content = (soup.find("main")
               or soup.find("article")
               or soup.body
               or soup)

    # separator="\n" to keep block-level elements on their own lines
    return content.get_text(separator="\n")


def load_documents():
    """Load all documents from the docs folder and process based on file type.
    Supports .txt and .pdf files. Returns a list of dicts with the document
    title (derived from the filename), the original filename for source
    attribution, and the cleaned full text."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        filepath = os.path.join(DOCS_PATH, filename)

        if filename.endswith(".txt"):
            text = _read_txt(filepath)
        elif filename.endswith(".pdf"):
            text = _read_pdf(filepath)
        elif filename.endswith((".html")):
            text = _read_html(filepath)
        else:
            print(f"  Skipping {filename}: unsupported file type.")
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


# A heading line: a contract section number ("1.", "2.1", "6.10 ROOM CHANGES"),
# or a short ALL-CAPS / Title-Case line with no terminal punctuation. 
_SECTION_NUM_RE = re.compile(r"^\d+(\.\d+)*\.?\s+\S")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _is_heading(line):
    """Return True if a line looks like a section heading rather than body prose."""
    line = line.strip()
    if not line or len(line) > 90:
        return False
    if _SECTION_NUM_RE.match(line):
        return True
    # ALL-CAPS or Title-Case heading with no sentence-ending punctuation.
    if line[-1] not in ".!?:," and len(line.split()) <= 10:
        letters = [c for c in line if c.isalpha()]
        if letters and (line.isupper() or line.istitle()):
            return True
    return False


def _split_blocks(text):
    """Split text into semantic blocks on blank lines and heading boundaries.

    A heading line starts a new block and stays attached to the body that
    follows it, so a section's title travels with its content.
    """
    blocks = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        current = []
        for line in para.split("\n"):
            if _is_heading(line) and current:
                blocks.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            blocks.append("\n".join(current).strip())
    return [b for b in blocks if b]


def _split_oversized(block):
    """Break a block longer than MAX_CHUNK_SIZE into pieces on sentence
    boundaries, packing sentences up to CHUNK_SIZE with CHUNK_OVERLAP carried
    over. Falls back to a hard character split for a single giant sentence."""
    sentences = _SENTENCE_RE.split(block)
    pieces = []
    current = ""
    for sent in sentences:
        if not current:
            current = sent
        elif len(current) + 1 + len(sent) <= CHUNK_SIZE:
            current += " " + sent
        else:
            pieces.append(current)
            # Carry the last CHUNK_OVERLAP chars forward for continuity,
            # snapped to a word boundary so the overlap doesn't start mid-word.
            tail = current[-CHUNK_OVERLAP:] if CHUNK_OVERLAP else ""
            if " " in tail:
                tail = tail[tail.find(" ") + 1:]
            current = (tail + " " + sent).strip() if tail else sent
        # Last resort: a single sentence still over the hard ceiling.
        while len(current) > MAX_CHUNK_SIZE:
            pieces.append(current[:MAX_CHUNK_SIZE])
            current = current[MAX_CHUNK_SIZE - CHUNK_OVERLAP:]
    if current:
        pieces.append(current)
    return pieces


def chunk_document(text, title, filename):
    """Split a document's text into chunks ready for embedding.

    Strategy (structure-aware recursive):
      1. Split into blocks on blank lines and heading boundaries.
      2. Pack consecutive small blocks together up to CHUNK_SIZE so short
         headings merge with their body instead of being dropped.
      3. Split any block over MAX_CHUNK_SIZE on sentence boundaries, with
         CHUNK_OVERLAP carried between pieces.

    Returns a list of dicts, each with:
      - "text"     : the chunk text (str)
      - "title"    : the document title, e.g. "Housing Contract" (str)
      - "filename" : the source file, for attribution (str)
      - "section"  : the nearest heading, or "" (str)
      - "chunk_id" : a unique id, e.g. "housing_contract_0" (str)
    """
    slug = title.lower().replace(" ", "_")
    chunks = []

    def emit(piece, section):
        piece = piece.strip()
        if len(piece) < MIN_CHUNK_LENGTH:
            return
        chunks.append({
            "text": piece,
            "title": title,
            "filename": filename,
            "section": section,
            "chunk_id": f"{slug}_{len(chunks)}",
        })

    buffer = ""          # accumulates small blocks up to CHUNK_SIZE
    buffer_section = ""  # heading that opened the current buffer

    for block in _split_blocks(text):
        section = block.split("\n", 1)[0].strip() if _is_heading(block.split("\n", 1)[0]) else ""

        if len(block) > MAX_CHUNK_SIZE:
            # Flush whatever is buffered, then sentence-split the big block.
            if buffer:
                emit(buffer, buffer_section)
                buffer, buffer_section = "", ""
            for piece in _split_oversized(block):
                emit(piece, section)
            continue

        if not buffer:
            buffer, buffer_section = block, section
        elif len(buffer) + 2 + len(block) <= CHUNK_SIZE:
            buffer += "\n\n" + block
        else:
            emit(buffer, buffer_section)
            buffer, buffer_section = block, section

    if buffer:
        emit(buffer, buffer_section)
    return chunks

if __name__ == "__main__":
    docs = load_documents()
    total = sum(len(chunk_document(d["text"], d["title"], d["filename"])) for d in docs)
    print(f"Total chunks across {len(docs)} document(s): {total}")
