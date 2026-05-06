"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass
import time
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

# load .env
load_dotenv()


# =========================
# Response Schema
# =========================
@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None


# =========================
# LLM Client
# =========================
class LLMClient:
    """Provider-agnostic LLM client."""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 3,
        timeout_seconds: int = 30,
    ):
        # =========================
        # Load config from .env
        # =========================
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")  # dùng cho OpenRouter
        env_model = os.getenv("OPENAI_MODEL")

        # =========================
        # Validate API key
        # =========================
        if not api_key:
            raise ValueError(
                "❌ OPENAI_API_KEY not found. Check your .env file location and content."
            )

        # =========================
        # Init OpenAI client
        # =========================
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,  # 🔥 QUAN TRỌNG cho OpenRouter
        )

        self.model = model or env_model or "gpt-4o-mini"
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

        # Debug info
        print("\n[LLM INIT]")
        print(f"Model: {self.model}")
        print(f"Base URL: {base_url}")
        print(f"API Key loaded: {'YES' if api_key else 'NO'}")

    # =========================
    # Cost Estimation (simple)
    # =========================
    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Rough cost estimation (adjust if needed)
        """
        input_cost_per_1k = 0.00015
        output_cost_per_1k = 0.0006

        return (
            (input_tokens / 1000) * input_cost_per_1k
            + (output_tokens / 1000) * output_cost_per_1k
        )

    # =========================
    # Main API
    # =========================
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion with retry + timeout + logging."""

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                start_time = time.time()

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.temperature,
                    timeout=self.timeout_seconds,
                )

                latency = time.time() - start_time

                content = response.choices[0].message.content

                usage = getattr(response, "usage", None)

                input_tokens = usage.prompt_tokens if usage else None
                output_tokens = usage.completion_tokens if usage else None

                cost = None
                if input_tokens and output_tokens:
                    cost = self._estimate_cost(input_tokens, output_tokens)

                # =========================
                # Logging
                # =========================
                print("\n[LLM CALL]")
                print(f"Model: {self.model}")
                print(f"Latency: {latency:.2f}s")
                print(f"Input tokens: {input_tokens}")
                print(f"Output tokens: {output_tokens}")
                print(
                    f"Estimated cost: ${cost:.6f}" if cost else "Cost: N/A"
                )

                return LLMResponse(
                    content=content,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=cost,
                )

            except Exception as e:
                last_exception = e
                print(f"[Retry {attempt + 1}/{self.max_retries}] Error: {e}")
                time.sleep(1)

        # =========================
        # Fail after retries
        # =========================
        raise RuntimeError(f"LLM failed after retries: {last_exception}")