"""Contains the search agent for the financial search."""

from datetime import datetime
import requests
import json

def _search_serper(query: str, num_results=1) -> list[str]:

    url = "https://google.serper.dev/shopping"

    payload = json.dumps({
    "q": query,
    "gl": "in"
    })
    headers = {
    'X-API-KEY': 'a7c4396a7edac6dce34aeace51826617c1e3cb7b',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = response.json()
    return data["shopping"][0]["link"]

# query ="Basics Men Blue T-shirt"
# data=_search_serper(query,1)
# print(data["shopping"][0]["link"])



