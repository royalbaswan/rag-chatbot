import chromadb

def get_or_create_collection(session_id: str):
    chroma_client = chromadb.Client()
    return chroma_client.get_or_create_collection(f"session_{session_id}")

def query_collection(collection, query: str, top_k: int = 5):
    results = collection.query(query_texts=[query], n_results=top_k)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]

    return [
        {"id": id_, "document": doc, "metadata": meta}
        for doc, meta, id_ in zip(documents, metadatas, ids)
    ]