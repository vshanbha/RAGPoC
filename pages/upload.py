import streamlit as st

from menu import menu_with_redirect
from tika import parser
from persistence.vector_db import FAISSManager

# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

# Initialize Database
if "API_KEY" in st.secrets:
    openai_api_key = st.secrets["API_KEY"]
    vector_db = FAISSManager(openai_api_key=openai_api_key)
else:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.sidebar.info("Please add your OpenAI API key to continue.")

st.title("Document Upload")
st.write(
    "Upload a document for use as reference "
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
    doc = parsed_document['content']
    st.session_state["Document"] = doc

    # TODO Consider splitting document into multiple files before sending to vector store
    vector_db.insert_document(uploaded_file.name, doc, parsed_document['metadata'])

st.subheader("Previously Uploaded Documents")
# TODO how to list documents uploaded to Vector store with option to delete
docs = vector_db.list_documents()
for d in docs:
    fname = d.metadata["source"]
    left, middle, right = st.columns(3)
    left.write(fname)
    middle.write(d.metadata["Content-Length"])
    if right.button(":wastebasket:", key=fname):
        right.markdown("You deleted the emoji button {}".format(fname))
#        vector_db.delete_document(fname)
