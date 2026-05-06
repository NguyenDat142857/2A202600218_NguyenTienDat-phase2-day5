"""Benchmark report rendering."""

from typing import List
from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def _safe(val, fmt="{:.2f}"):
    if val is None:
        return ""
    try:
        return fmt.format(val)
    except Exception:
        return str(val)


def _generate_insights(metrics: List[BenchmarkMetrics]) -> list[str]:
    """Auto-generate simple insights comparing runs."""

    if len(metrics) < 2:
        return ["Not enough runs to compare."]

    insights = []

    # assume first = baseline, second = multi-agent
    base = metrics[0]
    multi = metrics[1]

    # Latency
    if base.latency_seconds and multi.latency_seconds:
        if multi.latency_seconds > base.latency_seconds:
            insights.append(
                f"Multi-agent is slower (+{multi.latency_seconds - base.latency_seconds:.2f}s) due to multiple LLM calls."
            )
        else:
            insights.append("Multi-agent is faster (unexpected, investigate caching or prompt size).")

    # Quality
    if base.quality_score and multi.quality_score:
        if multi.quality_score > base.quality_score:
            insights.append("Multi-agent improves answer quality with structured reasoning.")
        else:
            insights.append("Quality did not improve — prompts or agent roles may need tuning.")

    # Cost
    if base.cost_usd and multi.cost_usd:
        if multi.cost_usd > base.cost_usd:
            insights.append("Multi-agent increases cost due to multiple steps.")
        else:
            insights.append("Cost is comparable or lower than baseline.")

    # Citation
    if hasattr(base, "citation_coverage") and hasattr(multi, "citation_coverage"):
        if (multi.citation_coverage or 0) > (base.citation_coverage or 0):
            insights.append("Multi-agent improves citation grounding.")

    return insights


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown (enhanced)."""

    lines = [
        "# 📊 Benchmark Report",
        "",
        "## 1. Summary Table",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Citation | Error | Notes |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]

    for item in metrics:
        cost = _safe(getattr(item, "cost_usd", None), "{:.6f}")
        quality = _safe(getattr(item, "quality_score", None), "{:.1f}")
        citation = _safe(getattr(item, "citation_coverage", None), "{:.4f}")
        error = "Yes" if getattr(item, "error_rate", 0) else "No"

        lines.append(
            f"| {item.run_name} | "
            f"{_safe(item.latency_seconds)} | "
            f"{cost} | "
            f"{quality} | "
            f"{citation} | "
            f"{error} | "
            f"{getattr(item, 'notes', '')} |"
        )

    # =========================
    # Insights
    # =========================
    lines.extend(
        [
            "",
            "## 2. Key Insights",
            "",
        ]
    )

    insights = _generate_insights(metrics)
    for ins in insights:
        lines.append(f"- {ins}")

    # =========================
    # Detailed Analysis
    # =========================
    lines.extend(
        [
            "",
            "## 3. Detailed Analysis",
            "",
            "### Latency",
            "- Multi-agent systems typically have higher latency due to multiple sequential LLM calls.",
            "",
            "### Quality",
            "- Multi-agent improves reasoning by separating research, analysis, and writing.",
            "",
            "### Cost",
            "- Cost increases as more tokens are consumed across agents.",
            "",
            "### Citation & Grounding",
            "- Multi-agent systems tend to include citations, reducing hallucination risk.",
        ]
    )

    # =========================
    # Failure Modes
    # =========================
    lines.extend(
        [
            "",
            "## 4. Failure Modes",
            "",
            "- Weak or irrelevant search results → poor downstream reasoning",
            "- Analyst misinterprets research → incorrect conclusions",
            "- Writer ignores citations → hallucination risk",
            "- Supervisor routing too early to 'done'",
        ]
    )

    # =========================
    # Improvements
    # =========================
    lines.extend(
        [
            "",
            "## 5. Suggested Improvements",
            "",
            "- Improve search quality (filter + ranking)",
            "- Add reflection loop (critic → rewrite)",
            "- Tune prompts for each agent",
            "- Add caching to reduce latency",
        ]
    )

    return "\n".join(lines) + "\n"