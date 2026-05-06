"""Command-line entrypoint for the lab starter."""

from typing import Annotated
import time

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab CLI")
console = Console()


# =========================
# Init
# =========================
def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


# =========================
# Baseline (Single Agent)
# =========================
@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a real single-agent baseline."""

    _init()

    request = ResearchQuery(query=query)
    state = ResearchState(request=request)

    llm = LLMClient()

    system_prompt = "You are a helpful research assistant."
    user_prompt = f"Answer the following question clearly and concisely:\n{query}"

    console.print("\n🚀 Running Single-Agent Baseline...\n")

    start = time.time()
    response = llm.complete(system_prompt, user_prompt)
    latency = time.time() - start

    state.final_answer = response.content

    # =========================
    # Output Answer
    # =========================
    console.print(Panel.fit(state.final_answer, title="Single-Agent Answer"))

    # =========================
    # Metrics Table
    # =========================
    table = Table(title="Baseline Metrics")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Latency (s)", f"{latency:.2f}")
    table.add_row("Input Tokens", str(response.input_tokens or "N/A"))
    table.add_row("Output Tokens", str(response.output_tokens or "N/A"))
    table.add_row(
        "Cost (USD)",
        f"{response.cost_usd:.6f}" if response.cost_usd else "N/A",
    )

    console.print(table)


# =========================
# Multi-Agent
# =========================
@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""

    _init()

    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()

    console.print("\n🚀 Starting Multi-Agent Workflow...\n")

    start = time.time()

    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc

    latency = time.time() - start

    # =========================
    # Output Answer
    # =========================
    console.print(
        Panel.fit(result.final_answer or "No answer", title="Multi-Agent Answer")
    )

    # =========================
    # Trace
    # =========================
    if hasattr(result, "trace") and result.trace:
        console.print(
            Panel.fit("\n".join(result.trace), title="Execution Trace")
        )

    # =========================
    # Route History
    # =========================
    if hasattr(result, "route_history") and result.route_history:
        console.print(
            Panel.fit(
                " → ".join(result.route_history),
                title="Route History",
            )
        )

    # =========================
    # Metrics Table
    # =========================
    table = Table(title="Multi-Agent Metrics")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Latency (s)", f"{latency:.2f}")

    console.print(table)


if __name__ == "__main__":
    app()