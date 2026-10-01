# Multi-Agent AI Research System

A research automation project built using **Python, LangChain, Google Gemini, Tavily and Streamlit**.

The system takes a research topic, searches the web for relevant information, scrapes a useful webpage, generates a structured research report and then reviews the report using a critic chain.

## Workflow

```text
Research Topic
      ↓
Search Agent → Tavily Web Search
      ↓
Reader Agent → Web Scraping
      ↓
Writer → Gemini Report
      ↓
Critic → Score & Feedback
```

## Tech Stack

* Python
* LangChain
* Google Gemini
* Tavily
* BeautifulSoup
* Requests
* Streamlit
* uv

## Key Features

* Live web search using Tavily
* Tool-using LangChain agents
* Webpage content extraction
* Gemini-based research report generation
* Automated report scoring and feedback
* Source extraction and raw research view
* Streamlit interface with pipeline progress
* Markdown report download

## Project Files

```text
agents.py    → Search/reader agents, writer and critic chains
tool.py      → Web search and scraping tools
pipeline.py  → End-to-end research workflow
app.py       → Streamlit application
```

## Setup

Install dependencies:

```bash
uv sync
```

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API=your_tavily_api_key
```

Run the application:

```bash
uv run streamlit run app.py
```

## Future Improvements

* Automatic report revision using critic feedback
* Multi-source research
* Citation verification
* Parallel research agents

## Author

**Syed Usman Zaid**
