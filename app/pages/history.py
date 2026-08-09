"""CivicPulse App — every testimony draft the user has ever produced."""

from __future__ import annotations

import os
import sys

sys.path.append("../..")
import streamlit as st

MOCK_MODE = os.environ.get("CIVICPULSE_MOCK_MODE", "true").lower() == "true"

MOCK_DRAFTS = [
    {"draft_id": "mock-draft-0001", "issue_id": "mock-issue-0001",
     "draft_text": "As a renter of six years, I support SB-214's 5% annual cap under Section 3...",
     "tone": "renter", "created_at": "2026-08-09", "submitted": False},
]


def render(profile: dict) -> None:
    st.header("Draft history")

    if MOCK_MODE:
        drafts = MOCK_DRAFTS
        st.caption("Showing demo data (CIVICPULSE_MOCK_MODE=true) — connect Lakebase for live data.")
    else:
        from app import lakebase_client
        drafts = lakebase_client.list_testimony_drafts(profile["user_id"])

    if not drafts:
        st.info("No drafts yet — ask the agent to draft testimony from the Bill detail or Chat view.")
        return

    for draft in drafts:
        with st.container(border=True):
            st.markdown(f"**{draft['tone'] or 'general'}** — {draft['created_at']}")
            st.write(draft["draft_text"])
            st.download_button("Copy / export", draft["draft_text"], key=f"export_{draft['draft_id']}")
