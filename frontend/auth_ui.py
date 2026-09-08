import requests
import streamlit as st

from api_client import login, register


def require_login() -> None:
    if st.session_state.get("auth_token"):
        return

    st.title("🤖 R2D2")
    st.caption("Sign in to continue.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")

            if submitted:
                try:
                    with st.spinner("Logging in..."):
                        token = login(username, password)
                    st.session_state.auth_token = token
                    st.session_state.username = username
                    st.rerun()
                except requests.HTTPError as exc:
                    if exc.response is not None and exc.response.status_code == 401:
                        st.error("Incorrect username or password.")
                    else:
                        st.error(f"Login failed: {exc}")
                except Exception as exc:
                    st.error(f"Login failed: {exc}")

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Choose a username")
            new_password = st.text_input("Choose a password (min 8 characters)", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Register")

            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        with st.spinner("Creating your account..."):
                            register(new_username, new_password)
                            token = login(new_username, new_password)
                        st.session_state.auth_token = token
                        st.session_state.username = new_username
                        st.success("Account created!")
                        st.rerun()
                    except requests.HTTPError as exc:
                        if exc.response is not None and exc.response.status_code == 400:
                            st.error("That username is already taken.")
                        else:
                            st.error(f"Registration failed: {exc}")
                    except Exception as exc:
                        st.error(f"Registration failed: {exc}")

    st.stop()
