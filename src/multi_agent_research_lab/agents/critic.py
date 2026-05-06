"""Critic agent implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self):
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""

        # =========================
        # Guard: cần có answer
        # =========================
        if not state.final_answer:
            raise ValueError("❌ CriticAgent requires final_answer")

        # =========================
        # Prompt design
        # =========================
        system_prompt = (
            "You are a critical reviewer and fact-checker. "
            "Your job is to evaluate the quality, correctness, and reliability of an answer."
        )

        user_prompt = f"""
        Evaluate the following answer:

        Question:
        {state.request.query}

        Answer:
        {state.final_answer}

        Research context:
        {state.research_notes}

        Your tasks:
        1. Check factual correctness (based on research notes)
        2. Identify possible hallucinations or unsupported claims
        3. Evaluate whether the answer is well-supported by evidence
        4. Suggest improvements

        Output format:

        ## Fact Check
        - ...

        ## Possible Issues
        - ...

        ## Evidence Coverage
        - ...

        ## Suggestions
        - ...

        ## Final Verdict
        - (Good / Needs Improvement / Poor)
        """

        # =========================
        # Call LLM
        # =========================
        response = self.llm.complete(system_prompt, user_prompt)

        critique = response.content

        # =========================
        # Append vào state (không overwrite answer)
        # =========================
        if hasattr(state, "critique") and state.critique:
            state.critique += "\n\n" + critique
        else:
            state.critique = critique

        # =========================
        # Trace
        # =========================
        if hasattr(state, "trace"):
            state.trace.append("CriticAgent: critique completed")

        print("\n[CriticAgent DONE]")

        return state