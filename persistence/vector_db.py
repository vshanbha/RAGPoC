import os
import faiss

from langchain.indexes import SQLRecordManager, index
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

index_path = "database/faiss_db"
namespace = f"FAISS/faiss_db"
record_manager = SQLRecordManager(
    namespace, db_url="sqlite:///database/record_manager_cache.sql"
)

# TODO Refactor so this should likely be a class
def init(openai_api_key):
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    try:
        vector_store = FAISS.load_local(
            index_path, embeddings, allow_dangerous_deserialization=True
        )
        print("FAISS index loaded successfully.")
    except RuntimeError as e:
        if "could not open" in str(e):
            record_manager.create_schema()
            print(f"FAISS index file not found at {index_path} faiss. Creating a new index.")
            # Creating an empty index
            idx = faiss.IndexFlatL2(len(embeddings.embed_query("OpenAIEmbeddings")))
            vector_store = FAISS(index=idx, 
                                embedding_function=embeddings,     
                                docstore=InMemoryDocstore(),
                                index_to_docstore_id={},
                            )

            # Save the newly created empty index for future use
            _clear(vector_store)            
            print("New FAISS index created and saved.")
        else:
            # Raise the exception if it's not a file-not-found issue
            raise e
    return vector_store

def _clear(vector_store):
    """Hacky helper method to clear content. See the `full` mode section to to understand why it works."""
    index([], record_manager, vector_store, cleanup="full", source_id_key="source")

def insert_document(openai_api_key, name, content, metadata):
    metadata={"source": name}
    document = Document(page_content=content, metadata=metadata)
    documents = [document]
    vector_store = init(openai_api_key)
    index(documents, record_manager, vector_store, cleanup="incremental", source_id_key="source")    
    vector_store.save_local(index_path)

def list(openai_api_key):
    return search(openai_api_key,"")


def search(openai_api_key, query, top_k=100):
    vector_store = init(openai_api_key)
    results = vector_store.search(query,search_type="similarity", top_k=top_k, include_metadata=True)
    return results
    