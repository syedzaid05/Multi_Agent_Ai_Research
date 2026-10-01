from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print
load_dotenv()


tavily=TavilyClient(api_key=os.getenv("TAVILY_API"))

@tool
def web_search(query:str)-> str:
    """
    Search the web for recent and reliable information on a topic .Return Titles,URLs and snippits
    """
    results=tavily.search(query=query,max_results=10)

    out=[]

    for r in results['results']:
        out.append(
            f"Title:{r['title']}\n URL:{r['url']}\nSnippits:{r['content'][:3000]}\n"
        )

    return "\n------\n".join(out)




# web scrappingtree 
@tool
def scrape_url(url:str)->str:
    """
    scrape and return clean content from a given URL for deeper readings

    """
    try:
        resp=requests.get(url,timeout=12,headers={"User-Agent":"Mozilla/5.0"})
        soup=BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script","style","nav","footer"]):
            tag.decompose()
        return soup.get_text(separator=" ",strip=True)[:10000]
    except Exception as e:
        return f"could not scrape Url:{str(e)}"
