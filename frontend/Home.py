import streamlit as st

from sidebar import render_sidebar

st.set_page_config(page_title="AiProject", page_icon="🤖", layout="wide")
render_sidebar()

st.title("Home")
st.info("Dashboard stats coming in a later subtask.")
