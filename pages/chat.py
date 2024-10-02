import streamlit as st
from menu import menu_with_redirect
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from tika import parser

def start_chat(document, ct):
    ct.subheader("Now ask a question about the document!")
    ct.markdown("A few sample questions")
    history = ct.container(height=400)
    if "messages" not in st.session_state or ct.button("Clear conversation history"):
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        history.chat_message(msg["role"]).write(msg["content"])

    if prompt := ct.chat_input(placeholder="Can you give me a short summary?"):
        next_msg = '{prompt}'
        st.session_state.messages.append({"role": "user", "content": prompt})
        sys_prompt = """
            You are a Technical Troubleshooting Assistant. 
            When a user starts chatting with you, treat each chat thread as an attempt to troubleshoot a technical issue.
            Ask questions if necessary to get more information about the problem at hand.
            Provide useful suggestions to help with troubleshooting the problem.
            User any document provided as relevant to the troubleshooting question asked. 
            Include relevant infromation or excerpt from the document to aid the troubleshooting effort.
            Here is the document: {document}
        """
        system_prompt = SystemMessagePromptTemplate.from_template(sys_prompt)
        human_prompt = HumanMessagePromptTemplate.from_template(next_msg)
        chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
        request = chat_prompt.format_prompt(document = document, prompt = prompt).to_messages()
        history.chat_message("user").write(prompt)
        response = llm.invoke(request)

        with history.chat_message("assistant"):
            st.session_state.messages.append({"role": "assistant", "content": response.content})
            history.write(response.content)


# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

st.title(":wrench: Doocument QnA")
st.write(
    "Upload a document below and ask a question about it. AI will answer! "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
if "API_KEY" in st.secrets:
    openai_api_key = st.secrets["API_KEY"]
else:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.sidebar.info("Please add your OpenAI API key to continue.")
else:
    llm = ChatOpenAI( openai_api_key=openai_api_key, temperature=0.2, max_tokens=300)

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
        start_chat(document,st)