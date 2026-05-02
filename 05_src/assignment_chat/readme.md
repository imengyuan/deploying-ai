# Cancer research paper chatbot

This is a chatbot to ask questions about recent research in cancer research. The dataset is based on the abstracts of research papers mentioning cancer from 2024 - 2026. 

The user interface of the chatbot is implemented using Gradio. The tone of the chatbot is academic and concise.

## How to run the app
```bash
# generate vector from text csv file
cd 05_src/assignment_chat
python3 embed_abstracts.py --csv data/cancer_abstracts.csv

# run the app
python app.py
```
The environment variables (e.g., API_GATEWAY_KEY) and software dependencies are the same with the basic course setup.


## Dataset for semantic query
The dataset used to build this chatbox is from this public dataset of biomedical research abstracts on [Kaggle](https://www.kaggle.com/datasets/kanchana1990/biomedical-research-abstracts-20242026). I used a subset of the dataset to specifically focus on cancer research. The final dataset `cancer_abstracts` has 13122 entries.

>This `biomedical_research_abstracts` dataset contains 126,832 cleaned biomedical research abstracts sourced from the NCBI PubMed database, covering publications from January 2024 to March 2026.

```
grep 'cancer' biomedical_research_abstracts_2024_2026.csv > cancer_abstracts.csv

```

## Services


### Service 1: Pubmed API

Access to the Pubmed API is implemented in `services/pubmed.py`.

Pubmed is a public database for research papers in biology and bio-medicine. Users can search paper abstracts using keywords, and the chatbot will return a markdown formatted answer about the details of the paper like titles, authors, etc.


### Service 2: semantic query

Text embedding generation is implented in `embed_abstracts.py`:
```bash
python embed_abstracts.py --csv path/to/cancer_abstracts.csv
```
Embedding vectors are then stored at `./chroma_db/`

The semantic search service is implemented in `services/semantic_search.py`. 


### Service 3: web search

Web search using openAI's web_search tool is implemented in `services/web_search.py`.

Web search topics are limited to cancer research related topics.


## Other considerations

### Guardrails

Implemented in `guardrails.py`.

Guardrails are included to prevent users from accessing/revealing the system prompt, modifying the system prompt directly, or respond to questions on certain restricted topics listed in the assignment requirement (e.g.,Cats or dogs, Horoscopes or Zodiac Signs, Taylor Swift).



