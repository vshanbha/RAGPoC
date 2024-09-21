# 📄 Document question answering template

A simple Streamlit app that answers questions about an uploaded document via OpenAI's GPT-3.5.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://document-question-answering-template.streamlit.app/)

### How to run it on your own machine

## Prerequisites ##
Python version 3.12

## Dev Setup ##

1. Create Python venv Open a terminal and run:

   ```
   python3.12 -m venv .venv
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

## Troubleshooting ##
The application uses Apache Tika port of Python for extracting text from Documents. 
To run this, system requires Java 7+ installed on the machine.
For MacOS running the code might cause below exception at time of uploading document(s)
   ```
   ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)
   ```
To resolve consider go through the steps provided on this [Stackoverflow](https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error) question
