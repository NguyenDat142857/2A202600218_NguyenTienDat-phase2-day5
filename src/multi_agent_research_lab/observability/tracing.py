"""Tracing hooks with simple logging + state integration."""

from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any, Optional
import json
import os


@contextmanager
def trace_span(
    name: str,
    attributes: Optional[dict[str, Any]] = None,
    state: Optional[Any] = None,
) -> Iterator[dict[str, Any]]:
    """Lightweight tracing span.

    Features:
    - measure latency
    - print logs
    - attach to state.trace
    - optionally export to JSON
    """

    started = perf_counter()

    span: dict[str, Any] = {
        "name": name,
        "attributes": attributes or {},
        "duration_seconds": None,
    }

    print(f"\n[TRACE START] {name}")

    try:
        yield span

    except Exception as e:
        span["error"] = str(e)
        print(f"[TRACE ERROR] {name}: {e}")
        raise

    finally:
        duration = perf_counter() - started
        span["duration_seconds"] = duration

        print(f"[TRACE END] {name} ({duration:.2f}s)")

        # =========================
        # Attach to state
        # =========================
        if state is not None and hasattr(state, "trace"):
            state.trace.append(span)

        # =========================
        # Optional: save to file
        # =========================
        if os.getenv("ENABLE_TRACE_FILE", "false").lower() == "true":
            os.makedirs("traces", exist_ok=True)
            file_path = os.path.join("traces", "trace_log.json")

            try:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = []

                data.append(span)

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)

            except Exception as e:
                print(f"[TRACE SAVE ERROR] {e}")