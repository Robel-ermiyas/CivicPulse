"""CivicPulse App — tracked-issues dashboard with urgency sort and a status funnel."""

from __future__ import annotations

import os
import sys

sys.path.append("../..")
import streamlit as st

MOCK_MODE = os.environ.get("CIVICPULSE_MOCK_MODE", "true").lower() == "true"

MOCK_TRACKED_ISSUES = [
    {"issue_id": "mock-issue-0001", "bill_id": "AL-SB214", "source_type": "bill",
     "status": "hearing_scheduled", "next_hearing_date": "2026-08-14"},
]


def render(profile: dict) -> None:
    st.header("Tracked issues")

    if MOCK_MODE:
        issues = MOCK_TRACKED_ISSUES
        st.caption("Showing demo data (CIVICPULSE_MOCK_MODE=true) — connect Lakebase for live data.")
    else:
        from app import lakebase_client
        issues = lakebase_client.list_tracked_issues(profile["user_id"])

    if not issues:
        st.info("Nothing tracked yet — track a bill from the Feed or Bill detail view.")
        return

    st.table(issues)

    st.subheader("Status funnel")
    stage_order = ["introduced", "committee", "hearing_scheduled", "passed", "failed"]
    counts = {stage: sum(1 for i in issues if i["status"] == stage) for stage in stage_order}
    st.bar_chart(counts)
