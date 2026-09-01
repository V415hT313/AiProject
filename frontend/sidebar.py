import streamlit as st

from api_client import check_health


def render_sidebar() -> None:
    with st.sidebar:
        st.title("🤖 AiProject")
        st.caption("Your local AI-powered assistant")

        if check_health():
            st.success("Backend connected", icon="✅")
        else:
            st.error("Backend unreachable", icon="⚠️")
            st.caption("Start the FastAPI server, then refresh this page.")

        st.divider()
