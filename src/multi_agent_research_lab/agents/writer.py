"""Writer agent implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        # =========================
        # Guard: cần research + analysis
        # =========================
        if not state.research_notes:
            raise ValueError("❌ WriterAgent requires research_notes")

        if not state.analysis_notes:
            raise ValueError("❌ WriterAgent requires analysis_notes")

        # =========================
        # Prompt design
        # =========================
        system_prompt = (
            "You are an expert technical writer. "
            "Your job is to produce a clear, well-structured, and accurate answer."
        )

        user_prompt = f"""
        Write a high-quality answer for the following query:

        Question:
        {state.request.query}

        Research Notes:
        {state.research_notes}

        Analysis Notes:
        {state.analysis_notes}

        Requirements:
        1. Provide a clear and structured explanation
        2. Combine insights from research and analysis
        3. Use simple but precise language
        4. Include references like (Source 1), (Source 2) where relevant
        5. Avoid repetition

        Output format:

        ## Final Answer
        (well-written explanation)

        ## Key Takeaways
        - ...
        - ...
        """

        # =========================
        # Call LLM
        # =========================
        response = self.llm.complete(system_prompt, user_prompt)

        state.final_answer = response.content

        # =========================
        # Trace
        # =========================
        if hasattr(state, "trace"):
            state.trace.append("WriterAgent: final answer generated")

        print("\n[WriterAgent DONE]")

        return state