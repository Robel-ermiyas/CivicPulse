"""CivicPulse App — single bill: status timeline, cited summary, Track / Draft testimony."""

from __future__ import annotations

import sys

sys.path.append("../..")
import streamlit as st

from agent.agent import CivicPulseAgent
from agent.tools import get_bill_status, save_testimony_draft, track_issue

STATUS_STAGES = ["introduced", "committee", "hearing_scheduled", "passed", "failed"]


def render(profile: dict) -> None:
    st.header("Bill detail")
    bill_id = st.text_input("Bill ID", value="AL-SB214")

    if not bill_id:
        return

    status = get_bill_status(bill_id)
    st.subheader(f"{bill_id} — {status.get('status', 'unknown').replace('_', ' ').title()}")

    stage_idx = STATUS_STAGES.index(status["status"]) if status.get("status") in STATUS_STAGES else 0
    st.progress((stage_idx + 1) / len(STATUS_STAGES))
    st.write(f"Sponsor: {status.get('sponsor', 'n/a')}  |  Next hearing: {status.get('next_hearing_date', 'n/a')}")

    col1, col2 = st.columns(2)
    if col1.button("Track this bill"):
        result = track_issue(user_id=profile["user_id"], bill_id=bill_id, source_type="bill")
        st.success(f"Tracked — issue {result['issue_id']}")

    if col2.button("Draft testimony"):
        agent = CivicPulseAgent(user_id=profile["user_id"])
        reply = agent.chat(
            f"Draft testimony for {bill_id}. My stake: {profile['stake_statement']}. Keep it short."
        )
        st.markdown("**Draft:**")
        st.write(reply)
