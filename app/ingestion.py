from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()
EMBEDDING_MODEL_NAME= os.getenv("EMBEDDING_MODEL_NAME")

def load_and_split(file_path: str, chunk_size: int = 3000, chunk_overlap: int = 100):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    return [t.page_content for t in texts]

def get_embeddings(content_list: list[str]) -> list[list[float]]:
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return model.encode(content_list, convert_to_numpy=True).tolist()

