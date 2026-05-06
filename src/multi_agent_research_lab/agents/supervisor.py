"""Supervisor / router implementation."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self, max_iterations: int = 6):
        self.max_iterations = max_iterations

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""

        # =========================
        # Init route history
        # =========================
        if not hasattr(state, "route_history") or state.route_history is None:
            state.route_history = []

        if not hasattr(state, "trace"):
            state.trace = []

        # =========================
        # Guard: max iterations
        # =========================
        if len(state.route_history) >= self.max_iterations:
            next_step = "done"
            state.trace.append("Supervisor: max iterations reached → done")

        # =========================
        # Routing logic
        # =========================
        elif not state.research_notes:
            next_step = "researcher"

        elif not state.analysis_notes:
            next_step = "analyst"

        elif not state.final_answer:
            next_step = "writer"

        else:
            # Optional: run critic before done
            if hasattr(state, "critique") and not state.critique:
                next_step = "critic"
            else:
                next_step = "done"

        # =========================
        # Update state
        # =========================
        state.route_history.append(next_step)
        state.trace.append(f"Supervisor: route → {next_step}")

        print(f"\n[Supervisor] Next step: {next_step}")

        return state