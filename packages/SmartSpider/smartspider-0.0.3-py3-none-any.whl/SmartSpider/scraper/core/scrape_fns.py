from bs4 import BeautifulSoup

import openai
from anthropic import Anthropic

import os

from ...models import Page, Url

def href_scrape_fn(page:Page) -> list[Url]:
    parser = BeautifulSoup(page.html if isinstance(page,Page) else "","html.parser")
    links = []

    for tag in parser.find_all("a", href=True):
        try:
            if not tag.has_attr("href"):
                continue
            
            relative_url = str(tag.get("href"))

            new_url = page._url + relative_url
        except ValueError:
            continue

        if new_url.domain == page.domain:
            links.append(new_url)
    
    return links

def gpt_scrape_fn(page:Page, query:str):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
    You are a web scraping assistant.
    The user will describe what data they want extracted.
    Use the provided HTML to find it.

    Return ONLY a JSON array — no text, no explanation.
    Each item should be an object with descriptive keys.

    Example:
    User request: "Get all book titles and prices"
    Output: [{{"title": "...", "price": "..."}}]

    ---
    User request: {query}
    HTML Summary:
    {page.html}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    raw_output = response.choices[0].message.content
    
    return raw_output

def claude_scrape_fn(page:Page, query:str):
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""
    You are a web scraping assistant.
    The user will describe what data they want extracted.
    Use the provided HTML to find it.

    Return ONLY a JSON array — no text, no explanation.
    Each item should be an object with descriptive keys.

    Example:
    User request: "Get all book titles and prices"
    Output: [{{"title": "...", "price": "..."}}]

    ---
    User request: {query}
    HTML Summary:
    {page.html}
    """

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        messages=[
            {"role": "user", 
             "content": prompt}
        ]
    )

    return message.content[0].text
