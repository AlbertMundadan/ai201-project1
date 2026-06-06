import chromadb
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS

_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection."""
    return _collection


def embed_and_store(chunks):
    """Embed a list of chunks and store them in the vector database.

    _collection.upsert() takes three parallel lists built from the chunks
    returned by chunk_document():
      - documents : raw text strings — ChromaDB's embedding function converts
                    these to vectors automatically using sentence-transformers
      - metadatas : one dict per chunk, stored alongside the vector so that
                    retrieve() can surface the source document, section, and
                    file for citation
      - ids       : the unique chunk_id strings used to identify each entry

    upsert (rather than add) makes re-running ingestion idempotent: existing
    chunk_ids are overwritten instead of raising a duplicate-id error.
    """
    if not chunks:
        print("No chunks to store.")
        return

    _collection.upsert(
        documents=[c["text"] for c in chunks],
        metadatas=[
            {
                "title": c["title"],
                "filename": c["filename"],
                "section": c["section"],
            }
            for c in chunks
        ],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


def retrieve(query, n_results=N_RESULTS):
    """Find the most relevant housing chunks for a user's question.

    Runs a semantic search over the vector store and returns a list of dicts,
    each with:
      - "text"     : the chunk text
      - "title"    : the source document title (for attribution)
      - "filename" : the source file name (for attribution)
      - "section"  : the nearest heading within that document, or ""
      - "distance" : cosine distance (lower = more similar)

    Returns an empty list if nothing has been ingested yet.
    """
    if _collection.count() == 0:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    # query() returns nested lists (one per query); we only have one query.
    return [
        {
            "text": doc,
            "title": meta.get("title", ""),
            "filename": meta.get("filename", ""),
            "section": meta.get("section", ""),
            "distance": dist,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


if __name__ == "__main__":
    import sys

    if _collection.count() == 0:
        print("Empty collection — ingesting documents...")
        from ingest import load_documents, chunk_document

        all_chunks = []
        for d in load_documents():
            all_chunks += chunk_document(d["text"], d["title"], d["filename"])
        embed_and_store(all_chunks)

    # Query from the command line, e.g.:
    query = " ".join(sys.argv[1:]) or "Are pets allowed in the dorms?"
    print(f"\nQuery: {query}\n")

    results = retrieve(query)
    if not results:
        print("No results.")
    for r in results:
        print(f"[distance={r['distance']:.3f}] {r['title']} — section={r['section']!r} ({r['filename']})")
        print(r["text"])
        print()
