"""
CivicPulse — Databricks App entrypoint (Streamlit).

Renders the five views from the architecture doc's app design (feed, bill
detail, chat, tracked-issues dashboard, draft history) behind a simple
sidebar nav. Talks to the agent (agent/agent.py) for chat/testimony drafting
and to Lakebase directly (app/lakebase_client.py) for the dashboard/history
reads, matching the separation described in phase1-architecture.md section 5:
"the agent bridges the two stores at query time."

Run locally:      streamlit run app/main.py
Run as a Databricks App: this file is the configured entrypoint (see
                          resources/app.yml).
"""

from __future__ import annotations

import sys

sys.path.append("..")
import streamlit as st

from app.pages import bill_detail, chat, dashboard, feed, history

st.set_page_config(page_title="CivicPulse", page_icon="\U0001F3DB\uFE0F", layout="wide")

DEMO_PROFILES = {
    "Renter (demo)": {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "state": "AL",
        "city": "Demo City",
        "topics": ["housing", "rent_control"],
        "stake_statement": "I rent my apartment and have lived here for six years.",
    },
    "Small-business owner (demo)": {
        "user_id": "00000000-0000-0000-0000-000000000002",
        "state": "AL",
        "city": "Demo City",
        "topics": ["small_business", "housing"],
        "stake_statement": "I own a small bakery and lease my storefront.",
    },
}


def main() -> None:
    st.sidebar.title("CivicPulse")
    st.sidebar.caption("Your legislative staffer, for free.")

    profile_name = st.sidebar.selectbox("Demo profile", list(DEMO_PROFILES.keys()))
    profile = DEMO_PROFILES[profile_name]
    st.session_state["active_profile"] = profile

    page = st.sidebar.radio(
        "View",
        ["Feed", "Bill detail", "Agent chat", "Tracked issues", "Draft history"],
    )

    if page == "Feed":
        feed.render(profile)
    elif page == "Bill detail":
        bill_detail.render(profile)
    elif page == "Agent chat":
        chat.render(profile)
    elif page == "Tracked issues":
        dashboard.render(profile)
    elif page == "Draft history":
        history.render(profile)


if __name__ == "__main__":
    main()
