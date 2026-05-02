"""
web_search_simple.py

Simple web search service using OpenAI.
Returns a short summary of recent cancer-related news.
"""

import os
from openai import OpenAI

# create client once
client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)


def search_recent_news(query: str) -> str:
    """
    Perform a simple web search and return a short summary.
    """

    prompt = (
        f"Find recent cancer research news about: {query}. "
        "Summarize the key findings in 3-5 bullet points. "
        "Include source names and dates if available. "
        "Do not copy text directly."
    )

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            tools=[{"type": "web_search_preview"}],
            input=prompt,
        )

        return response.output_text.strip()

    except Exception as e:
        return f"Error during web search: {e}"
