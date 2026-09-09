import requests
import streamlit as st

from api_client import forgot_password, login, register, reset_password


def _render_reset_password_form(token: str) -> None:
    st.caption("Set a new password.")
    with st.form("reset_password_form"):
        new_password = st.text_input("New password (min 8 characters)", type="password")
        confirm_password = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Reset password")

        if submitted:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                try:
                    with st.spinner("Resetting password..."):
                        reset_password(token, new_password)
                    st.session_state.password_reset_done = True
                    st.rerun()
                except requests.HTTPError as exc:
                    if exc.response is not None and exc.response.status_code == 400:
                        st.error("This reset link is invalid or has expired. Please request a new one.")
                    else:
                        st.error(f"Reset failed: {exc}")
                except Exception as exc:
                    st.error(f"Reset failed: {exc}")

    if st.session_state.get("password_reset_done"):
        st.success("Password reset! You can now log in with your new password.")
        if st.button("Continue to login"):
            st.session_state.pop("password_reset_done", None)
            st.query_params.clear()
            st.rerun()


def require_login() -> None:
    if st.session_state.get("auth_token"):
        return

    st.title("🤖 R2D2")

    reset_token = st.query_params.get("reset_token")
    if reset_token:
        _render_reset_password_form(reset_token)
        st.stop()

    st.caption("Sign in to continue.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username (your email)")
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

        with st.expander("Forgot password?"):
            with st.form("forgot_password_form"):
                forgot_username = st.text_input("Your username (email)")
                forgot_submitted = st.form_submit_button("Send reset link")
                if forgot_submitted:
                    if not forgot_username.strip():
                        st.error("Enter your username first.")
                    else:
                        try:
                            with st.spinner("Sending reset email..."):
                                forgot_password(forgot_username.strip())
                            st.success(
                                "If that account exists, a reset link has been sent to your email."
                            )
                        except Exception as exc:
                            st.error(f"Something went wrong: {exc}")

    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Your email (used as your username, and for password resets)")
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
