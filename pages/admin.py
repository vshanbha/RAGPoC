import streamlit as st
from menu import menu_with_redirect
from tika import parser

# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

# Verify the user's role
if st.session_state.role not in ["admin", "super-admin"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

st.title("Document Upload")
st.write(
    "Upload a document below and ask a question about it. AI will answer! "
)
# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .md)",
    type=("txt", "md","xls","csv","doc","ppt","xlsx","docx","pptx","pdf"),
)

if uploaded_file:
    # Process the uploaded file and question.
    # document = uploaded_file.read().decode()
    parsed_document = parser.from_file(uploaded_file)
    document = parsed_document['content']
    st.session_state["Document"] = document
