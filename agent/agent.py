"""
CivicPulse — tool-calling agent loop.

Orchestrates the 8 read/write tools (schemas.py contracts, tools.py bodies)
around the Databricks Foundation Model API's function-calling (agent/llm.py).
This is the same loop
Phase 1 verified against mock tool data (docs/phase1-setup-summary.md
section 6: "multi-turn conversation correctly selects the right tool, passes
correct arguments, and carries context across turns"); Phase 2 only swapped
what the tools return, not the loop itself.

Usage:
    from agent.agent import CivicPulseAgent
    agent = CivicPulseAgent()
    reply = agent.chat("Anything happening with rent control this session?")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from agent.llm import chat_completion, parse_tool_call_args
from agent.prompts import SYSTEM_PROMPT
from agent.schemas import TOOL_CONTRACTS
from agent.tools import TOOL_IMPLEMENTATIONS

MAX_TOOL_HOPS = 6  # guard against a runaway tool-calling loop


@dataclass
class CivicPulseAgent:
    user_id: str | None = None
    history: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.history:
            self.history.append({"role": "system", "content": SYSTEM_PROMPT})

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        for _ in range(MAX_TOOL_HOPS):
            response = chat_completion(self.history, tools=[_to_function_declaration(t) for t in TOOL_CONTRACTS])

            if not response["tool_calls"]:
                self.history.append({"role": "assistant", "content": response["text"]})
                return response["text"]

            # Record the tool calls the model wants, then execute each and feed results back.
            for call in response["tool_calls"]:
                name = call["name"]
                args = parse_tool_call_args(call["arguments"])
                if self.user_id and "user_id" in TOOL_CONTRACTS_BY_NAME[name]["parameters"]["properties"]:
                    args.setdefault("user_id", self.user_id)

                result = TOOL_IMPLEMENTATIONS[name](**args)

                self.history.append({
                    "role": "assistant",
                    "content": f"[calling tool {name} with {json.dumps(args)}]",
                })
                self.history.append({
                    "role": "user",  # fed back as context for the next hop
                    "content": f"[tool result for {name}]: {json.dumps(result, default=str)}",
                })

        return "I wasn't able to finish that in a reasonable number of steps -- try rephrasing or narrowing the request."


TOOL_CONTRACTS_BY_NAME = {t["name"]: t for t in TOOL_CONTRACTS}


def _to_function_declaration(tool_contract: dict) -> dict:
    """Strip our internal `returns` doc field -- providers only want name/description/parameters."""
    return {
        "name": tool_contract["name"],
        "description": tool_contract["description"],
        "parameters": tool_contract["parameters"],
    }
