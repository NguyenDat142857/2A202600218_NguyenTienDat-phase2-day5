from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.services.llm_client import LLMClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self):
        self.search_client = SearchClient()
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        query = state.request.query

        if not query:
            raise ValueError("❌ ResearcherAgent requires a query")

        # =========================
        # 1. Search documents
        # =========================
        documents = self.search_client.search(query=query, max_results=5)

        if not documents:
            raise ValueError("❌ No documents found from search")

        state.sources = documents

        # =========================
        # 2. Prepare context (FIX HERE)
        # =========================
        formatted_sources = ""

        for i, doc in enumerate(documents, 1):
            formatted_sources += f"""
Source {i}:
Title: {doc.title}
Snippet: {doc.snippet}
URL: {doc.url}
"""

        # =========================
        # 3. Generate research notes
        # =========================
        system_prompt = (
            "You are a professional research assistant. "
            "You synthesize multiple sources into structured notes."
        )

        user_prompt = f"""
Research query:
{query}

Sources:
{formatted_sources}

Your task:
1. Extract key facts
2. Merge overlapping info
3. Keep concise
4. Use citations like (Source 1)

Output:

## Key Facts
- ...

## Insights
- ...

## Sources
- [1] Title (URL)
"""

        response = self.llm.complete(system_prompt, user_prompt)

        state.research_notes = response.content

        # =========================
        # 4. Trace
        # =========================
        if hasattr(state, "trace"):
            state.trace.append("ResearcherAgent: done")

        print("\n[ResearcherAgent DONE]")

        return state