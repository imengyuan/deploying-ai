"""
Service 1: PubMed API via NCBI E-utilities
"""

import requests
import xml.etree.ElementTree as ET

ESEARCH_URL  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL   = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
HEADERS      = {"User-Agent": "CancerResearchBot/1.0"}


def search_pubmed(query: str, max_results: int = 5) -> str:
    """
    Search PubMed by keyword and return a formatted list of articles.
    Results include title, authors, journal, year, and a link.
    The raw API response is transformed — not returned verbatim.
    """
    # get matching PMIDs
    try:
        r = requests.get(ESEARCH_URL, params={
            "db": "pubmed",
            "term": f"({query}) AND cancer[MeSH Terms]",
            "retmax": max(1, min(max_results, 10)),
            "retmode": "json",
            "sort": "relevance",
        }, headers=HEADERS, timeout=10)
        r.raise_for_status()
        pmids = r.json().get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        return f"PubMed search error: {e}"

    if not pmids:
        return "No PubMed articles found for that query."

    # fetch article summaries
    try:
        r = requests.get(ESUMMARY_URL, params={
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
        }, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json().get("result", {})
    except Exception as e:
        return f"PubMed summary error: {e}"

    # format results
    lines = [f"**PubMed results for '{query}'** ({len(pmids)} articles)\n"]
    for pmid in pmids:
        article  = data.get(pmid, {})
        title    = article.get("title", "No title").rstrip(".")
        authors  = article.get("authors", [])
        author   = authors[0].get("name", "Unknown") if authors else "Unknown"
        if len(authors) > 1:
            author += f" et al."
        journal  = article.get("source", "Unknown journal")
        pub_date = article.get("pubdate", "n.d.")
        lines.append(
            f"- **PMID {pmid}**: {title}\n"
            f"  {author} | *{journal}* | {pub_date}\n"
            f"  https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        )

    return "\n".join(lines)


def fetch_pubmed_abstract(pmid: str) -> str:
    """
    Fetch the full abstract for a single article by PMID.
    Returns a formatted string with title, authors, journal, and abstract text.
    """
    try:
        r = requests.get(EFETCH_URL, params={
            "db": "pubmed",
            "id": pmid.strip(),
            "rettype": "abstract",
            "retmode": "xml",
        }, headers=HEADERS, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except Exception as e:
        return f"PubMed fetch error: {e}"

    article = root.find(".//PubmedArticle/MedlineCitation/Article")
    if article is None:
        return f"No article found for PMID {pmid}."

    # title
    title_node = article.find("ArticleTitle")
    title = "".join(title_node.itertext()).strip() if title_node is not None else "No title"

    # authors (first 3)
    author_list = article.findall(".//AuthorList/Author")
    authors = []
    for a in author_list[:3]:
        last = a.findtext("LastName", "")
        init = a.findtext("Initials", "")
        if last:
            authors.append(f"{last} {init}".strip())
    author_str = ", ".join(authors)
    if len(author_list) > 3:
        author_str += f" et al."

    # journal and year
    journal = root.findtext(".//Journal/Title", default="Unknown journal")
    year    = root.findtext(".//PubDate/Year", default="n.d.")

    # abstract text
    abstract_nodes = article.findall(".//AbstractText")
    if abstract_nodes:
        parts = []
        for node in abstract_nodes:
            label = node.get("Label")
            text  = "".join(node.itertext()).strip()
            parts.append(f"**{label}:** {text}" if label else text)
        abstract = "\n".join(parts)
    else:
        abstract = "No abstract available."

    return (
        f"**{title}**\n"
        f"*{author_str}*\n"
        f"{journal}, {year} | PMID: {pmid}\n"
        f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/\n\n"
        f"{abstract}"
    )
