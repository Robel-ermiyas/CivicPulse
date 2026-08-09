"""CivicPulse App — personalized feed ("N new bills match your tracked topics")."""

from __future__ import annotations

import sys

sys.path.append("../..")
import streamlit as st

from agent.tools import get_vote_history, search_bills_semantic


def render(profile: dict) -> None:
    st.header("Your feed")
    st.caption(f"Matching your tracked topics: {', '.join(profile['topics'])}")

    for topic in profile["topics"]:
        results = search_bills_semantic(query=topic.replace("_", " "), state=profile["state"], topics=[topic])
        if not results:
            continue
        st.subheader(topic.replace("_", " ").title())
        for r in results:
            with st.container(border=True):
                st.markdown(f"**{r['parent_id']}**  \n{r['chunk_text']}")
                col1, col2 = st.columns([1, 1])
                col1.button("Track", key=f"track_{r['chunk_id']}")
                col2.button("View detail", key=f"detail_{r['chunk_id']}")

    with st.expander("Has anything like this passed nearby?"):
        history_rows = get_vote_history(topic=profile["topics"][0]) if profile["topics"] else []
        if history_rows:
            st.table(history_rows)
        else:
            st.write("No comparable outcomes found yet.")
