"""
Library of default GPT-5 prompt bundles for Phase 2 evaluators.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass(frozen=True)
class PromptBundle:
    """A reusable prompt template + metadata for LLM evaluators."""

    key: str
    title: str
    description: str
    prompt_template: str
    parser: str = "first_number_1_10"
    sample_response: str = ""

    def with_header(self) -> str:
        """Return prompt template with a standard header comment."""

        header = (
            f"# {self.title}\n"
            "# Provide a JSON-friendly rating from 1-10 inclusive.\n"
            "# Respond using the format: 'Score: <number>/10\\nReason: <short explanation>'\n"
        )
        return header + self.prompt_template.strip()


def _score_instructions(metric: str) -> str:
    return (
        "Score each criterion from **1 (very poor)** to **10 (excellent)**. "
        "A score of 7 or higher indicates the agent met the expectation."
        f" Focus on {metric} when judging.\n"
        "Output format:\n"
        "Score: <number>/10\n"
        "Reason: <one sentence summary>\n"
        "Only produce the score and reason lines."
    )


PROMPT_BUNDLES: Dict[str, PromptBundle] = {
    "intent_recognition": PromptBundle(
        key="intent_recognition",
        title="Intent Recognition Quality Review",
        description="Judge if the agent correctly inferred the user's intent and responded accordingly.",
        prompt_template="""
System role:
You are an expert QA analyst reviewing customer-support conversations.

Context:
- Persona: {persona}
- User input: {input}
- Agent output: {output}
- Additional metadata: {metadata}

Task:
Evaluate how accurately the agent identified the user's intent and aligned the response with that intent.
Consider:
1. Does the response address the true intent behind the request?
2. Are any key goals or constraints ignored?
3. Does the tone match the persona expectations?

Return your verdict.

{score_instructions}
""".replace(
            "{score_instructions}", _score_instructions("intent recognition")
        ),
        sample_response="Score: 9/10\nReason: Response addresses the refund intent explicitly and guides next steps.",
    ),
    "response_consistency": PromptBundle(
        key="response_consistency",
        title="Response Consistency Review",
        description="Evaluate whether the agent's response is consistent with project guidelines and previous answers.",
        prompt_template="""
System role:
You ensure agents keep answers aligned with established guidance and past explanations.

Context:
- Persona: {persona}
- Current user input: {input}
- Agent output: {output}
- Conversation history (if any): {history}
- Project notes: {guidelines}

Task:
Judge the response for consistency and coherence.
Consider:
1. Are statements compatible with prior agent replies?
2. Does the messaging stay aligned with the supplied project guidelines?
3. Are there contradictions or shifts in policy?

Provide a rating.

{score_instructions}
""".replace(
            "{score_instructions}", _score_instructions("response consistency")
        ),
        sample_response="Score: 7/10\nReason: Output stays aligned but omits the standard escalation phrase found earlier.",
    ),
    "response_clarity": PromptBundle(
        key="response_clarity",
        title="Response Clarity Review",
        description="Assess clarity, structure, and helpfulness of the agent's answer.",
        prompt_template="""
System role:
You review answers for clarity and actionable guidance.

Context:
- Persona: {persona}
- User input: {input}
- Agent output: {output}

Task:
Judge whether the response is easy to understand and provides actionable next steps.
Consider:
1. Clarity of language (avoids jargon, structured explanation).
2. Completeness of steps or explanations.
3. Tone appropriateness for the persona.

Give your evaluation.

{score_instructions}
""".replace(
            "{score_instructions}", _score_instructions("response clarity")
        ),
        sample_response="Score: 6/10\nReason: Explanation is mostly clear but misses a concrete next action.",
    ),
    "information_completeness": PromptBundle(
        key="information_completeness",
        title="Information Completeness Review",
        description="Determine whether the agent included all required information or follow-up details.",
        prompt_template="""
System role:
You verify that responses include all critical information for the user to succeed.

Context:
- Persona: {persona}
- User request: {input}
- Agent output: {output}
- Required artifacts or data: {requirements}

Task:
Assess whether the response covers all required facts, steps, and caveats.
Consider:
1. Does the agent supply each required data point?
2. Are there missing disclaimers or next actions?
3. Would the user need additional clarification?

Respond with your score.

{score_instructions}
""".replace(
            "{score_instructions}", _score_instructions("information completeness")
        ),
        sample_response="Score: 5/10\nReason: Response misses the billing URL and fails to mention timeline requirements.",
    ),
}


def list_prompt_bundles() -> Iterable[PromptBundle]:
    """Return all available prompt bundles."""

    return PROMPT_BUNDLES.values()


def get_prompt_bundle(key: str) -> PromptBundle:
    """Retrieve a prompt bundle by identifier."""

    if key not in PROMPT_BUNDLES:
        available = ", ".join(sorted(PROMPT_BUNDLES))
        raise KeyError(f"Unknown prompt bundle '{key}'. Available: {available}")
    return PROMPT_BUNDLES[key]


__all__ = ["PromptBundle", "get_prompt_bundle", "list_prompt_bundles", "PROMPT_BUNDLES"]


