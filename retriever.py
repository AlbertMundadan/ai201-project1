import os
import re
from config import DOCS_PATH

def load_documents():
    """Load all documents from the docs folder and process based on file type."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            game_name = filename.replace(".txt", "").replace("_", " ").title()
            documents.append({
                "game": game_name,
                "filename": filename,
                "text": text,
            })            
    print(f"Loaded {len(documents)} rule document(s): {[d['game'] for d in documents]}")
    return documents
