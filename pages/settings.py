import streamlit as st
from menu import menu_with_redirect

st.header("Settings")
st.write(f"You are logged in as {st.session_state.role}.")

menu_with_redirect()