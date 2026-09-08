import streamlit as st

from api_client import check_health


def render_sidebar() -> None:
    with st.sidebar:
        st.title("🤖 R2D2")
        st.caption("Your local AI-powered assistant")

        if check_health():
            st.success("Backend connected", icon="✅")
        else:
            st.error("Backend unreachable", icon="⚠️")
            st.caption("Start the FastAPI server, then refresh this page.")

        username = st.session_state.get("username")
        if username:
            st.caption(f"👤 {username}")
            if st.button("Log out", key="logout_button", width="stretch"):
                st.session_state.pop("auth_token", None)
                st.session_state.pop("username", None)
                st.rerun()

        st.divider()
