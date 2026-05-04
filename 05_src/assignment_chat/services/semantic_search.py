"""
Service 2: semantic search over the local cancer abstracts dataset
Need to run embed_abstracts.py first
"""

import os
import chromadb
from chromadb.utils import embedding_functions

# use __file__ so the path works regardless of where you run the script from
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
COLLECTION_NAME = "cancer_abstracts"

# use the same embedding model as embed_abstracts.py
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# lazy-load the collection on first use
_collection = None


def _get_collection():
    global _collection
    if _collection is not None:
        return _collection

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"ChromaDB not found at '{DB_PATH}'. Run embed_abstracts.py first."
        )

    client = chromadb.PersistentClient(path=DB_PATH)
    _collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
    return _collection


def semantic_search(query: str, n_results: int = 5) -> str:
    """
    Find the most relevant abstracts for a query using cosine similarity.
    Returns a formatted string with titles, sources, and abstract snippets.
    """

    try:
        collection = _get_collection()
    except FileNotFoundError as e:
        return f"Semantic search unavailable: {e}"

    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        return f"Search error: {e}"

    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    if not docs:
        return "No results found."

    output = [f"Top {len(docs)} results for '{query}':\n"]

    for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
        title     = meta.get("title", "Untitled")
        source    = meta.get("source", "Unknown journal")
        year      = meta.get("year", "n.d.")
        pmid      = meta.get("pmid", "")
        relevance = round((1 - dist) * 100, 1)

        snippet = doc[:250] + "..." if len(doc) > 250 else doc

        pmid_line = f"\n   https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
        output.append(
            f"{i}. **{title}** ({relevance}% match)\n"
            f"   *{source}*, {year}{pmid_line}\n"
            f"   {snippet}"
        )

    return "\n\n".join(output)
