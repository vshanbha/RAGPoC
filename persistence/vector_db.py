import os
import faiss
from langchain.indexes import SQLRecordManager, index
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

class FAISSManager:
    def __init__(self, openai_api_key, database_dir="database", index_file="faiss_db"):
        self.openai_api_key = openai_api_key
        self.database_dir = database_dir
        self.index_path = os.path.join(database_dir, index_file)
        self.namespace = f"FAISS/{index_file}"
        self.record_manager = SQLRecordManager(
            self.namespace, db_url=f"sqlite:///{database_dir}/record_manager_cache.sql"
        )
        self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        self.vector_store = None
        
        # Initialize FAISS index
        self._init_faiss()

    def _init_faiss(self):
        """Initialize the FAISS index or create a new one if it doesn't exist."""
        if not os.path.isdir(self.database_dir):
            os.mkdir(self.database_dir)

        try:
            self.vector_store = FAISS.load_local(
                self.index_path, self.embeddings, allow_dangerous_deserialization=True
            )
            print("FAISS index loaded successfully.")
        except RuntimeError as e:
            if "could not open" in str(e):
                self.record_manager.create_schema()
                print(f"FAISS index file not found at {self.index_path}. Creating a new index.")
                idx = faiss.IndexFlatL2(len(self.embeddings.embed_query("OpenAIEmbeddings")))
                self.vector_store = FAISS(
                    index=idx, 
                    embedding_function=self.embeddings,
                    docstore=InMemoryDocstore(),
                    index_to_docstore_id={},
                )
                self._clear()
                print("New FAISS index created and saved.")
            else:
                raise e

    def _clear(self):
        """Clear the index completely."""
        print(index([], self.record_manager, self.vector_store, cleanup="full", source_id_key="source", force_update=True))

    def insert_document(self, name, content, metadata=None):
        """Insert a document into the FAISS vector store."""
        metadata = {} if metadata is None else metadata
        metadata["source"] = name
        document = Document(page_content=content, metadata=metadata)
        documents = [document]
        
        # Index and save
        print(index(documents, self.record_manager, self.vector_store, cleanup="incremental", source_id_key="source"))
        self.vector_store.save_local(self.index_path)

    def list_documents(self):
        """List all documents by calling search with an empty query."""
        return self.search("")

    def search(self, query, top_k=100):
        """Search documents in the FAISS vector store."""
        results = self.vector_store.search(query, search_type="similarity", top_k=top_k, include_metadata=True)
        return results

    def delete_document(self, source_name):
        docs = self.list_documents()

        new_docs = []
        for d in docs:
            metadata = d.metadata
            if metadata["source"] == source_name:
                print(self.record_manager.list_keys(group_ids=[source_name]))
                continue
            document = Document(page_content=d.page_content, metadata=d.metadata)
            print(document.metadata["source"])
            new_docs.append(document)
        
        # TODO how to clean up unwanted documents
        print(index(new_docs, self.record_manager, self.vector_store, cleanup="full", source_id_key="source"))
        self.vector_store.save_local(self.index_path)
        
        print(f"Document with source '{source_name}' deleted successfully.")
