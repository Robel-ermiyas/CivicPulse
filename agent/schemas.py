"""
CivicPulse — agent tool contracts.

Exact 8 tool definitions from phase1-architecture.md section 6, imported by
agent.py to register with the LLM's function-calling API, and by tools.py so
the Python function signatures never drift from what's registered. Phase 1
verified all 8 as mock-data stubs; Phase 2 (this repo) implements the real
bodies in tools.py behind these same signatures.
"""

TOOL_CONTRACTS: list[dict] = [
    {
        "name": "search_bills_semantic",
        "description": "Semantic search over bill and agenda text for a topic or question.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "state": {"type": "string", "description": "Optional two-letter state code filter"},
                "topics": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["query"],
        },
        "returns": "Array of {chunk_id, parent_id, parent_type, chunk_text, score}",
    },
    {
        "name": "get_bill_status",
        "description": "Get the current structured status of a specific bill.",
        "parameters": {
            "type": "object",
            "properties": {"bill_id": {"type": "string"}},
            "required": ["bill_id"],
        },
        "returns": "{bill_id, status, sponsor, last_action_date, next_hearing_date, topics}",
    },
    {
        "name": "get_vote_history",
        "description": "Look up past bill outcomes on a topic, optionally scoped to a state.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "state": {"type": "string"},
            },
            "required": ["topic"],
        },
        "returns": "Array of {bill_id, state, outcome, vote_date, vote_margin}",
    },
    {
        "name": "get_user_profile",
        "description": "Load the requesting user's location, topics, and stated stake.",
        "parameters": {
            "type": "object",
            "properties": {"user_id": {"type": "string", "format": "uuid"}},
            "required": ["user_id"],
        },
        "returns": "{user_id, state, city, topics, stake_statement}",
    },
    {
        "name": "track_issue",
        "description": "Add a bill or agenda item to the user's watchlist. Write action.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "format": "uuid"},
                "bill_id": {"type": "string"},
                "source_type": {"type": "string", "enum": ["bill", "agenda_item"]},
            },
            "required": ["user_id", "bill_id", "source_type"],
        },
        "returns": "{issue_id, status: 'tracked'}",
    },
    {
        "name": "save_testimony_draft",
        "description": "Persist an agent-drafted public comment, grounded in retrieved bill text. Write action.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "format": "uuid"},
                "issue_id": {"type": "string", "format": "uuid"},
                "draft_text": {"type": "string"},
                "tone": {"type": "string"},
                "cited_sections": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["user_id", "issue_id", "draft_text"],
        },
        "returns": "{draft_id, status: 'saved'}",
    },
    {
        "name": "update_issue_status",
        "description": "Refresh a tracked issue's status after checking the source of truth. Write action.",
        "parameters": {
            "type": "object",
            "properties": {
                "issue_id": {"type": "string", "format": "uuid"},
                "new_status": {"type": "string"},
            },
            "required": ["issue_id", "new_status"],
        },
        "returns": "{issue_id, status: 'updated'}",
    },
    {
        "name": "create_notification",
        "description": "Flag an approaching deadline or status change to the user. Write action.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "format": "uuid"},
                "issue_id": {"type": "string", "format": "uuid"},
                "message": {"type": "string"},
                "due_date": {"type": "string", "format": "date"},
            },
            "required": ["user_id", "message"],
        },
        "returns": "{notification_id, status: 'created'}",
    },
]

TOOL_NAMES = [t["name"] for t in TOOL_CONTRACTS]
READ_TOOLS = {"search_bills_semantic", "get_bill_status", "get_vote_history", "get_user_profile"}
WRITE_TOOLS = {"track_issue", "save_testimony_draft", "update_issue_status", "create_notification"}
