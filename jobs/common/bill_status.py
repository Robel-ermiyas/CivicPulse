"""
Pure (no-Spark) bill status/topic derivation logic, shared by
transform_bills.py's Spark UDFs and by the unit tests in tests/. Kept
dependency-free on purpose: this is the one piece of transform logic that's
worth testing without spinning up a Spark session.

Known gap flagged in Phase 1 (docs/phase1-setup-summary.md section 4): the
Open States bulk export has no direct `status` field — status must be
derived from `actions[].classification`, the chronological action log each
bill carries.
"""

from __future__ import annotations

from datetime import datetime, timezone

# Open States action classifications -> CivicPulse status vocabulary.
# Order matters: later matches in a bill's action history win (most recent
# classification wins over earlier ones).
STATUS_CLASSIFICATION_MAP = {
    "introduction": "introduced",
    "reading-1": "introduced",
    "committee-referral": "committee",
    "committee-passage": "committee",
    "reading-2": "hearing_scheduled",
    "committee-passage-favorable": "hearing_scheduled",
    "passage": "passed",
    "signed": "passed",
    "executive-signature": "passed",
    "veto": "failed",
    "failure": "failed",
    "withdrawal": "failed",
}

TOPIC_LEXICON = {
    "housing": ["rent", "landlord", "tenant", "eviction", "housing", "zoning"],
    "small_business": ["small business", "licensing", "permit fee", "chamber of commerce"],
    "schools": ["school", "education", "student", "curriculum", "teacher"],
    "transit": ["transit", "transportation", "highway", "public transportation", "bus", "rail"],
    "healthcare": ["health care", "healthcare", "medicaid", "hospital", "insurance"],
}


def derive_status(actions: list[dict]) -> str:
    """Walk a bill's chronological actions[] and return the latest known CivicPulse status."""
    if not actions:
        return "introduced"
    status = "introduced"
    for action in sorted(actions, key=lambda a: a.get("date", "")):
        for classification in action.get("classification", []) or []:
            mapped = STATUS_CLASSIFICATION_MAP.get(classification)
            if mapped:
                status = mapped
    return status


def derive_next_hearing_date(actions: list[dict]):
    """Best-effort: the earliest future-dated action that looks like a hearing/reading."""
    hearing_like = {"reading-2", "committee-passage", "committee-passage-favorable"}
    today = datetime.now(timezone.utc).date().isoformat()
    candidates = [
        a["date"] for a in (actions or [])
        if a.get("date", "") >= today
        and set(a.get("classification", []) or []) & hearing_like
    ]
    return min(candidates) if candidates else None


def tag_topics(text: str) -> list[str]:
    text_lower = (text or "").lower()
    return [topic for topic, keywords in TOPIC_LEXICON.items() if any(k in text_lower for k in keywords)]
