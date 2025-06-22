__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from typing import List
import chromadb
import pytesseract
import logging
import os

logger = logging.getLogger(__name__)
chroma_client = chromadb.PersistentClient("chroma")

def get_or_create_collection(name: str = "chroma", get=True):
    """ Creates or retrieves the chroma database with 
    a name. By default: chroma """ 
    return chroma_client.get_or_create_collection(name)

def get_embeddings(content_list: list[str])-> list[int]:
    """ Generates embeddings for a list of text. """
    
    embed_model= SentenceTransformer("all-MiniLM-L6-v2")
    return embed_model.encode(content_list)

def load_document(file_path: str, original_name: str, ext: str) -> List[Document]:
    """
    Enhanced document loader with:
    - PDF corruption handling [fallback to pytesseract OCR]
    - Metadata preservation
    
    Args:
        file_path: Temporary system path to the file
        original_name: Original filename for metadata
        ext: File extension (.pdf, .txt)
    
    Returns:
        List of LangChain Documents with preserved metadata
    """
    try:
        if ext == ".pdf":
            try:
                doc= []
                reader = PdfReader(file_path)
                for i, page in enumerate(reader.pages, start=1):
                    doc.append(Document(
                        page_content= page.extract_text(),
                        metadata={"source": original_name, "page_label": i}))
                logger.info(f"PDF parsed successfully: {original_name}")
            except Exception as e:
                logger.warning(f"PDF corrupted/scanned, using OCR: {original_name}")
                doc = pdf_ocr_fallback(file_path, original_name)
        
        elif ext == ".txt":
            loader = TextLoader(file_path)
            doc = loader.load()
            logger.info(f"Text file loaded: {original_name}")
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        for d in doc:
            d.metadata["source"]= original_name # assigning original name for sources in final answer
        
        return doc

    except Exception as e:
        logger.error(f"Failed to load {original_name}: {str(e)}", exc_info=True)
        return []

def pdf_ocr_fallback(file_path: str, original_name: str) -> List[Document]:
    """Fallback to pytesseract OCR for scanned/corrupted PDFs
    
    Args:
    file_path: Temporary system path to the file
    original_name: Original filename for metadata
    
    Returns:
        List of LangChain Documents with preserved metadata
    """
    try:
        pages = []
        images = convert_from_path(file_path)
        for page_num, img in enumerate(images, start=1):
            text = pytesseract.image_to_string(img)
            pages.append(Document(
                page_content=text,
                metadata={"source": original_name, "page_label": page_num}
            ))
    except Exception as e:
        logger.error(f"OCR failed for {original_name}: {str(e)}")
        return []
    return pages

def chunk_documents(documents: list, chunk_size: int = 1000, chunk_overlap: int = 100):
    """ Splits all documenst into respective chunks recursively using 
    langchain RecursiveCharacterTextSplitter.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents)
    return chunks

def calculate_chunk_ids(chunks):
    """This will create IDs like "data/monopoly.pdf:6:2"
    format= Page Source : Page Number : Chunk Index 
    
    Args:
    chunks: original chunks
    
    Returns:
    chunks: modified chunks with unique ids for each chunk
    """
    
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page_label")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, incrementing the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculating the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Adding it to the page meta-data.
        chunk.metadata["id"] = chunk_id
    return chunks

def add_chunks_to_db(collection, chunks: list[str]):
    """ Adds chunks to chroma database. Checks if its a new file or already
    uploaded file with the help of unique ids for each chunks. Adds chunks
    if new else addition is skipped. 
    
    Args:
    collection: database
    chunks: chunks
    """
    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = collection.get()  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    logger.info(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only adding documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)
    
    if len(new_chunks):
        logger.info(f"Adding new documents: {len(new_chunks)}")
        chunk_content= [t.page_content for t in new_chunks]
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        collection.add(documents=chunk_content, ids=new_chunk_ids)
    else:
        logger.info("No new documents to add")
        
