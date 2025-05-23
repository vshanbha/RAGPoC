import streamlit as st
import json
from menu import menu_with_redirect
from persistence.vector_db import FAISSManager

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def start_chat(ct):
    ct.subheader("Ask a question about the document!")
    ct.markdown("A few sample questions")
    history = ct.container(height=400)
    if "messages" not in st.session_state or ct.button("Clear conversation history"):
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        history.chat_message(msg["role"]).write(msg["content"])


    level = st.select_slider(
        "Response Level",
        options=["Basic", "Advanced", "Expert"],
        value="Advanced"  # Default selection
    )

    if prompt := ct.chat_input(placeholder="Can you give me a short summary?"):
        next_msg = '{prompt}'
        st.session_state.messages.append({"role": "user", "content": prompt})
        with open("prompts/prompt.json", "r") as infile:
            data = json.load(infile)
            system_prompt = data["system_prompt"]
        sys_prompt = system_prompt + "Use the level of knowledge specifiec by: " + level + """
            here are is the context: {context}
        """

        system_prompt = SystemMessagePromptTemplate.from_template(sys_prompt)
        human_prompt = HumanMessagePromptTemplate.from_template(next_msg)
        chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
        history.chat_message("user").write(prompt)

        # https://python.langchain.com/docs/tutorials/rag/#retrieval-and-generation-retrieve
        retriever = vector_db.get_retriever()

        rag_chain = (
            {"context": retriever | format_docs, "prompt": RunnablePassthrough() }
            | chat_prompt
            | llm
            | StrOutputParser()
        )

        response = ""
        for chunk in rag_chain.stream(prompt):
            response = response + chunk

        with history.chat_message("assistant"):
            st.session_state.messages.append({"role": "assistant", "content": response})
            history.write(response)


# Redirect to app.py if not logged in, otherwise show the navigation menu
menu_with_redirect()

st.title(":wrench: Document Assistant")
openai_api_key = None

# Check if Ollama configuration is available in secrets
if "ollama" in st.secrets:
    ollama_config = st.secrets["ollama"]
    ollama_host = ollama_config.get("host", "http://localhost:11434")
    ollama_model = ollama_config.get("model", "mistral")  # Default model

    llm = Ollama(base_url=ollama_host, model=ollama_model)  # Initialize Ollama
    llm_backend = "ollama"
    backend_config =  {"host": ollama_host, "model": ollama_model} # Only pass host and model
    st.sidebar.success("Using Ollama server")
else:

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
        llm = ChatOpenAI( openai_api_key=openai_api_key, temperature=0.5, max_tokens=300)
        llm_backend = "openai"
        backend_config = {"api_key": openai_api_key}
        st.sidebar.success("Using OpenAI")

if llm:
    vector_db = FAISSManager(llm_backend=llm_backend, backend_config=backend_config)
    start_chat(st)