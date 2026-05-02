# Cancer research paper chatbot

This is a chatbot to ask questions about recent research in cancer research. The dataset is based on the abstracts of papers from 2024-2026.

## How to run
```
#
cd 05_src/assignment_chat
python3 embed_abstracts.py --csv data/cancer_abstracts.csv

#
python app.py
```

## Dataset for semantic query
The dataset used to build this chatbox is from this public dataset on [Kaggle](https://www.kaggle.com/datasets/kanchana1990/biomedical-research-abstracts-20242026). I used a subset of the dataset which now has 13122 entries.

```
grep 'cancer' biomedical_research_abstracts_2024_2026.csv > cancer_abstracts.csv

```

## Services


### Service 1: Pubmed API

### Service 2: semantic query

### Service 3: web search


## Other considerations

