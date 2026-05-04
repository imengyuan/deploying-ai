# Cancer Research Chatbot
This is a chatbot for exploring cancer research literature. It can search PubMed, query a local dataset of cancer abstracts, and find recent news on cancer research topics.

The user interface is built with Gradio. The chatbot's tone is academic and concise.

## How to run the app

```bash
# build the vector store from the cancer abstracts csv
cd 05_src/assignment_chat
python embed_abstracts.py --csv data/cancer_abstracts.csv

# launch the app
python app.py
```

Environment variables (e.g., `API_GATEWAY_KEY`) and dependencies are the same as the standard course setup.

## Dataset for semantic query

The dataset is a subset of the [Biomedical Research Abstracts 2024–2026](https://www.kaggle.com/datasets/kanchana1990/biomedical-research-abstracts-20242026) dataset on Kaggle, filtered to abstracts mentioning cancer. The final dataset has 13,122 entries.

```bash
grep 'cancer' biomedical_research_abstracts_2024_2026.csv > cancer_abstracts.csv
```

Embeddings were generated using `sentence-transformers/all-MiniLM-L6-v2` via ChromaDB's built-in embedding function using `chromadb.PersistentClient`. The embedding is implented in `embed_abstracts.py` and embedding vectors are then stored at `./chroma_db/`

```bash
python embed_abstracts.py --csv path/to/cancer_abstracts.csv
```

## Services

### Service 1: PubMed API

Implemented in `services/pubmed.py`.

PubMed is a free public database of biomedical research papers. The service provides two functions: `search_pubmed()` searches for papers by keyword and returns a formatted list of results (title, authors, journal, PMID), and `fetch_pubmed_abstract()` retrieves the full abstract for a specific PMID. 

### Service 2: Semantic Search

Implemented in `services/semantic_search.py`.

Abstracts are embedded with `all-MiniLM-L6-v2` and stored in a persistent ChromaDB collection. At query time, the user's question is embedded with the same model and matched against the collection using cosine similarity. 

### Service 3: Web Search

Implemented in `services/web_search.py`.

Uses OpenAI's built-in `web_search_preview` tool to find recent cancer research news. A single non-agentic search call is made.

## Other considerations

### Guardrails

Implemented in `guardrails.py`.

Guardrails are included to prevent users from accessing/revealing the system prompt, modifying the system prompt directly, or respond to questions on certain restricted topics listed in the assignment requirement (e.g.,Cats or dogs, Horoscopes or Zodiac Signs, Taylor Swift).

### Memory

Conversation history is stored as a list of `{"role", "content"}` dicts in Gradio and passed to `run_agent()` on each turn.

## Future improvement

Need to write more test cases to run.
