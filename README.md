# 📄 Document question answering template

A simple Streamlit app that answers questions about an uploaded document via OpenAI's GPT-3.5.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ragpoc.streamlit.app/)

### How to run it on your own machine

## Prerequisites ##
- Python version 3.13

- Java 7 or higher version installed

## Dev Setup ##

1. Create Python venv Open a terminal and run:

   ```
   python3.13 -m venv .venv
   source .venv/bin/activate
   ```


2. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

## Users and Roles ##
Create a file called `secrets.toml` inside the `.streamlit` director and add the following information.
   ```
   API_KEY="<your-OpenAI-api-key>"

   [passwords]
   # Follow the rule: username = "password"
   <user> = "<password>"

   [roles]
   # Follow the rule: username = "role"
   <user> = "<role>"
   ```
Replace `<user>` with actual user names for login to the application. 
Replace `<role>` with one of `user`, `admin` or `super-admin`

## Troubleshooting ##
1. Certificate issues preventing text extraction
The application uses the Apache Tika port of Python for extracting text from Documents. 
To run this, the system requires Java 7+ installed on the machine.
For MacOS running the code might cause the below exception at the time of uploading the document(s)
   ```
   ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)
   ```
To resolve, consider going through the steps provided on this [Stackoverflow](https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error) question

## Known Issues ##
1. Token Limit
At the moment the application tries to embed the whole document text into one single document in the Vector DB. If the document size hits the token limit for the embedding model then document upload does not work. 

2. Chat Errors due to Token Limit
At the moment no attempt has been made to strip down the quantum of content sent to the AI for RAG. The code does limit the number of documents sent for RAG, but if the sum of tokens for all the documents is more than the limit of the model, we get an error.

3. Delete buttons work but the solution is not efficient. Need to figure out how to efficiently delete individual documents from FAISS when the indexing was done using the Langchain Indexing APIs

## References ##
[Streamlit Docs](https://docs.streamlit.io/)

[Langchain How To Guides](https://python.langchain.com/docs/how_to/)

[Langchain Docs on RAG](https://python.langchain.com/docs/how_to/indexing/)

[Medium Blog Links](https://medium.com/gopenai/how-to-perform-crud-operations-with-vector-database-using-langchain-2df3f7fb48aa)

