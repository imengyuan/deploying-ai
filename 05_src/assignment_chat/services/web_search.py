"""
Service 3: web search for recent cancer news using OpenAI's web search tool
"""

import os
from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "placeholder"),
    default_headers={"x-api-key": os.getenv("API_GATEWAY_KEY", "")}
)


def search_recent_news(query: str) -> str:
    """
    Search the web for recent cancer research news and return a short summary.
    The result is rephrased into bullet points — not returned verbatim.
    """

    system_prompt = (
        "You are a cancer research news summariser. "
        "Given web search results, write 3-5 bullet points summarising the key findings. "
        "Include the source name and date for each point. "
        "Do not copy text directly from sources — rephrase in your own words."
    )

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=system_prompt,
            tools=[{"type": "web_search_preview"}],
            input=f"Find recent cancer research news about: {query}",
        )
        return response.output_text.strip()

    except Exception as e:
        return f"Web search error: {e}"
