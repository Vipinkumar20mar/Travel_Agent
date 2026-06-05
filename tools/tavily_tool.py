import os
from dotenv import load_dotenv
from tavily import TavilyClient
load_dotenv()

client=TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

#response=client.search(
   # query="Best hotels in Dubai",
   # search_depth="advanced"
#
#test
#print(response['results'][0]["content"])


def tavily_search(query):

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    results = []

    for r in response["results"]:

        content = r.get("content", "").strip()

        if len(content) > 300:
            content = content[:300].rsplit(" ", 1)[0] + "..."

        results.append({
            "title": r.get("title", "Unknown"),
            "url": r.get("url", ""),
            "content": content
        })

    return results