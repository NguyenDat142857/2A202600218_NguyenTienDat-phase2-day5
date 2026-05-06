"""Benchmark for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable
import re

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


Runner = Callable[[str], ResearchState]


# =========================
# Helpers
# =========================
def _estimate_cost(state: ResearchState) -> float:
    """Aggregate cost from all LLM calls if stored in state."""
    total = 0.0

    # bạn có thể mở rộng nếu lưu nhiều chỗ
    for attr in ["research_notes", "analysis_notes", "final_answer"]:
        value = getattr(state, attr, None)
        if hasattr(value, "cost_usd") and value.cost_usd:
            total += value.cost_usd

    return total


def _citation_coverage(text: str) -> float:
    """Simple heuristic: count (Source X) appearances."""
    if not text:
        return 0.0

    citations = re.findall(r"\(Source\s*\d+\)", text)
    return len(citations) / max(len(text.split()), 1)


def _has_error(state: ResearchState) -> bool:
    """Check if workflow had errors."""
    if not hasattr(state, "trace"):
        return False

    for t in state.trace:
        if isinstance(t, str) and "error" in t.lower():
            return True
        if isinstance(t, dict) and t.get("error"):
            return True

    return False


def _llm_quality_score(query: str, answer: str) -> float:
    """Use LLM to roughly score answer quality (0–10)."""

    if not answer:
        return 0.0

    llm = LLMClient()

    system_prompt = "You are an evaluator. Score answer quality from 0 to 10."

    user_prompt = f"""
    Question:
    {query}

    Answer:
    {answer}

    Criteria:
    - correctness
    - completeness
    - clarity

    Return ONLY a number from 0 to 10.
    """

    try:
        response = llm.complete(system_prompt, user_prompt)
        score_text = response.content.strip()

        score = float(re.findall(r"\d+(\.\d+)?", score_text)[0])
        return min(max(score, 0), 10)

    except Exception:
        return 0.0


# =========================
# Main benchmark
# =========================
def run_benchmark(
    run_name: str,
    query: str,
    runner: Runner,
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Run benchmark with multiple metrics."""

    print(f"\n📊 Running benchmark: {run_name}")

    started = perf_counter()

    try:
        state = runner(query)
        error = False
    except Exception as e:
        print(f"❌ Error during run: {e}")
        state = ResearchState(request=None)
        error = True

    latency = perf_counter() - started

    # =========================
    # Metrics
    # =========================
    final_answer = getattr(state, "final_answer", "") or ""

    quality = _llm_quality_score(query, final_answer)
    citation = _citation_coverage(final_answer)
    cost = _estimate_cost(state)
    error_flag = error or _has_error(state)

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        quality_score=quality,
        cost_usd=cost,
        citation_coverage=citation,
        error_rate=1.0 if error_flag else 0.0,
    )

    # =========================
    # Print summary
    # =========================
    print("\n📈 Benchmark Result:")
    print(f"Latency: {latency:.2f}s")
    print(f"Quality: {quality:.2f}/10")
    print(f"Cost: ${cost:.6f}")
    print(f"Citation coverage: {citation:.4f}")
    print(f"Error: {error_flag}")

    return state, metrics