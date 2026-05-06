"""Analyst agent implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""

        # =========================
        # Guard: need research first
        # =========================
        if not state.research_notes:
            raise ValueError("❌ AnalystAgent requires research_notes")

        # =========================
        # Prompt Design
        # =========================
        system_prompt = (
            "You are an expert analyst. "
            "Your job is to turn raw research into structured insights."
        )

        user_prompt = f"""
        Based on the research below, perform a deep analysis.

        Research Notes:
        {state.research_notes}

        Your task:
        1. Extract key claims (main ideas)
        2. Compare different viewpoints (if any)
        3. Identify strengths and weaknesses of the evidence
        4. Highlight missing information or uncertainty

        Output format:

        ## Key Claims
        - ...

        ## Comparison
        - ...

        ## Strengths
        - ...

        ## Weaknesses / Gaps
        - ...
        """

        # =========================
        # Call LLM
        # =========================
        response = self.llm.complete(system_prompt, user_prompt)

        # =========================
        # Update state
        # =========================
        state.analysis_notes = response.content

        # =========================
        # Trace (important for lab)
        # =========================
        if hasattr(state, "trace"):
            state.trace.append("AnalystAgent: analysis completed")

        print("\n[AnalystAgent DONE]")

        return state