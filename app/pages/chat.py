"""CivicPulse App — persistent agent chat panel."""

from __future__ import annotations

import sys

sys.path.append("../..")
import streamlit as st

from agent.agent import CivicPulseAgent


def render(profile: dict) -> None:
    st.header("Ask CivicPulse")

    if "agent" not in st.session_state or st.session_state.get("agent_user_id") != profile["user_id"]:
        st.session_state["agent"] = CivicPulseAgent(user_id=profile["user_id"])
        st.session_state["agent_user_id"] = profile["user_id"]
        st.session_state["chat_log"] = []

    for role, text in st.session_state["chat_log"]:
        with st.chat_message(role):
            st.write(text)

    user_input = st.chat_input("Ask about a bill, a topic, or say 'track that one'...")
    if user_input:
        st.session_state["chat_log"].append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)

        reply = st.session_state["agent"].chat(user_input)
        st.session_state["chat_log"].append(("assistant", reply))
        with st.chat_message("assistant"):
            st.write(reply)
