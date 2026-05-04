"""
Agent that routes user queries to the right service
"""

import os
import re
from openai import OpenAI

from services.pubmed import search_pubmed, fetch_pubmed_abstract
from services.semantic_search import semantic_search
from services.web_search import search_recent_news

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "placeholder"),
    default_headers={"x-api-key": os.getenv("API_GATEWAY_KEY", "")}
)

SYSTEM_PROMPT = """
You are ONCOSEARCH, a cancer research assistant.
Be concise and academic. Use bullet points when listing results.
Always cite sources (PMID, journal, or URL).
Do not give clinical advice.
"""


def run_agent(user_query: str, history: list) -> str:
    """
    Two-step agent:
      1. Ask the LLM which tool to call.
      2. Call the tool, then ask the LLM to write the final answer.
    History is passed so the LLM has conversation context.
    """

    # Build conversation history for context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for human, assistant in history:
        if human:
            messages.append({"role": "user", "content": human})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})

    # Step 1: decide which tool to use
    routing_prompt = f"""Which tool should I use for this query? Return only the tool name.

Query: {user_query}

Tools:
- pubmed_search   (find papers by keyword)
- fetch_abstract  (get full abstract for a specific PMID number)
- semantic_search (search local dataset by meaning/topic)
- web_search      (recent news and breakthroughs)
- none            (general question, no tool needed)
"""

    decision = client.responses.create(
        model="gpt-4o-mini",
        input=messages + [{"role": "user", "content": routing_prompt}]
    ).output_text.strip().lower()

    # Step 2: call the chosen tool
    if "fetch_abstract" in decision:
        # Extract the PMID number from the user query
        pmid_match = re.search(r"\b\d{6,9}\b", user_query)
        if pmid_match:
            result = fetch_pubmed_abstract(pmid_match.group())
        else:
            result = "Please provide a valid PMID number (e.g. 'fetch abstract for PMID 36807484')."

    elif "pubmed_search" in decision:
        result = search_pubmed(user_query)

    elif "semantic_search" in decision:
        result = semantic_search(user_query)

    elif "web_search" in decision:
        result = search_recent_news(user_query)

    else:
        result = None

    # Step 3: generate the final answer
    if result:
        final_input = messages + [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": f"[Tool result]\n{result}"},
            {"role": "user", "content": "Write a clear, concise answer using the tool result above."}
        ]
    else:
        final_input = messages + [{"role": "user", "content": user_query}]

    response = client.responses.create(
        model="gpt-4o-mini",
        input=final_input
    )

    return response.output_text.strip()
