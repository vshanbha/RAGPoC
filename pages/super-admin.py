import streamlit as st
import json
from menu import menu_with_redirect

# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

# Verify the user's role
if st.session_state.role not in ["admin","super-admin"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

st.title("System Prompt Configuration")
st.markdown(f"You are currently logged with the role of {st.session_state.role}.")

with open("prompts/prompt.json", "r") as infile:
    data = json.load(infile)
    system_prompt = data["system_prompt"]

default_prompt = """You are a bot named "Doku Mental" and you do what the user asks you.
You use reference documentss given to you to help answer the questions.
"""

prompt = st.text_area(
    label="Change Sytem Prompt",
    value=system_prompt if system_prompt else default_prompt,
    height=400
)

with open("prompts/prompt.json", "w") as outfile:
    json.dump({"system_prompt": prompt}, outfile)