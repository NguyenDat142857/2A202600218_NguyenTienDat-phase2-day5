"""Multi-agent workflow implementation."""

from multi_agent_research_lab.core.state import ResearchState

from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.agents.critic import CriticAgent


class MultiAgentWorkflow:
    """Builds and runs the multi-agent system."""

    def __init__(self):
        # =========================
        # Init agents
        # =========================
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()

    # =========================
    # Optional (not used)
    # =========================
    def build(self) -> object:
        """Kept for compatibility with skeleton."""
        return None

    # =========================
    # Main execution loop
    # =========================
    def run(self, state: ResearchState) -> ResearchState:
        """Execute multi-agent loop."""

        print("\n🚀 Starting Multi-Agent Workflow...\n")

        # =========================
        # Init state
        # =========================
        if not hasattr(state, "trace") or state.trace is None:
            state.trace = []

        if not hasattr(state, "route_history") or state.route_history is None:
            state.route_history = []

        # =========================
        # Loop
        # =========================
        while True:
            # 1. Supervisor decides next step
            state = self.supervisor.run(state)
            next_step = state.route_history[-1]

            # 2. Stop condition
            if next_step == "done":
                print("\n✅ Workflow finished\n")
                break

            # 3. Route to agent
            try:
                if next_step == "researcher":
                    state = self.researcher.run(state)

                elif next_step == "analyst":
                    state = self.analyst.run(state)

                elif next_step == "writer":
                    state = self.writer.run(state)

                elif next_step == "critic":
                    state = self.critic.run(state)

                else:
                    raise ValueError(f"❌ Unknown step: {next_step}")

            except Exception as e:
                # =========================
                # Fallback handling
                # =========================
                error_msg = f"⚠️ Error in {next_step}: {e}"
                print(error_msg)

                state.trace.append(error_msg)

                # fallback: skip step and end
                print("⚠️ Fallback → stopping workflow")
                break

        # =========================
        # Final logging
        # =========================
        print("\n📊 ROUTE HISTORY:")
        print(" → ".join(state.route_history))

        print("\n🧠 TRACE:")
        for t in state.trace:
            print("-", t)

        return state