"""Search client abstraction for ResearcherAgent."""

import os
from typing import List
from dotenv import load_dotenv

from multi_agent_research_lab.core.schemas import SourceDocument

load_dotenv()

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None


class SearchClient:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")

        if self.api_key and TavilyClient:
            self.client = TavilyClient(api_key=self.api_key)
            self.provider = "tavily"
        else:
            self.client = None
            self.provider = "mock"

        print(f"[SearchClient] Provider: {self.provider}")

    def search(self, query: str, max_results: int = 5) -> List[SourceDocument]:

        # =========================
        # REAL SEARCH (Tavily)
        # =========================
        if self.provider == "tavily":
            try:
                response = self.client.search(query=query, max_results=max_results)

                results = []
                for i, item in enumerate(response.get("results", []), start=1):
                    snippet = item.get("content") or item.get("snippet") or ""

                    results.append(
                        SourceDocument(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=snippet[:300],
                        )
                    )

                print(f"[Search] Found {len(results)} results from Tavily")
                return results[:max_results]

            except Exception as e:
                print(f"[Search ERROR] Tavily failed: {e}")

        # =========================
        # MOCK SEARCH (SAFE)
        # =========================
        print("[Search] Using MOCK data")

        return [
            SourceDocument(
                title="GraphRAG Overview",
                url="https://example.com/graphrag",
                snippet="GraphRAG extends RAG using graph structures for multi-hop reasoning.",
            ),
            SourceDocument(
                title="Traditional RAG Explained",
                url="https://example.com/rag",
                snippet="Traditional RAG retrieves independent documents without relationships.",
            ),
            SourceDocument(
                title="GraphRAG vs RAG",
                url="https://example.com/comparison",
                snippet="GraphRAG enables deeper reasoning, RAG is simpler but limited.",
            ),
        ][:max_results]