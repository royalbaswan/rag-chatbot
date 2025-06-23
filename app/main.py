from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import os
import shutil
import tempfile
import traceback
import logging
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from app.ingestion import load_document, chunk_documents, get_or_create_collection, get_embeddings, add_chunks_to_db
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

app = FastAPI()
logger = logging.getLogger("fastapi")

PROMPT_TEMPLATE= """You are a helpful AI assistant that answers questions using only the given context.

    Instructions:
    - Answer the question based solely on the context provided.
    - If the answer is not found in the context, respond with 'The answer is not available in the provided document.'"
    - Be concise and factual.
    - Do not make up or include information not present in the context.
    
    Context:
    {context}
    ---
    Question:
    {question}
    """

class QueryRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    try:
        doc_list= []
        for file in files:
            logger.info(f"Received file: {file.filename}")
            suffix = os.path.splitext(file.filename)[1].lower()
            logger.info(f"File extension: {suffix}")
            
            with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
                shutil.copyfileobj(file.file, tmp, length=8192) 
                doc = load_document(tmp.name, file.filename, suffix)
            logger.info(f"{file} loaded successfully")
            doc_list.extend(doc)
        # creating chunks
        chunks= chunk_documents(doc_list, chunk_size=500, chunk_overlap=50)
        logger.info(f"chunks created: {len(chunks)}")
        if not chunks:
            raise HTTPException(status_code=400, detail="No text could be extracted from the document.")
        
        # adding chunks to db if does not exist in db
        collection = get_or_create_collection()
        add_chunks_to_db(collection, chunks) # first check then add
        logger.info(f"Document successfully indexed in collection.")
        return "Files uploaded and indexed successfully."

    except Exception as e:
        logger.error(f"ERROR: Upload failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/query")
async def generate_response(req: QueryRequest):
    try:
        logger.info(f"Received question: {req.question}")
        # generating embeddings for the query
        query_embeddings = get_embeddings([req.question])
        logger.info(f"Embedding generated for the question asked.")
        
        # retrieving top 3 relevant chunks based on embeddings of query
        collection = get_or_create_collection()
        retrieved_texts = collection.query(query_embeddings= query_embeddings, n_results=5)
        logger.info("Retrieved vector store collection based on the query.")
        logger.info(f"Retrieved top {len(retrieved_texts['documents'][0])} relevant chunks.")
        
        # creating final prompt with retieved context and query
        context_text = "\n\n---\n\n".join([text for text in retrieved_texts['documents'][0]])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=req.question)
        
        # generating the response
        model = OllamaLLM(model='llama3', temperature=0)
        response_text = model.invoke(prompt)
        formatted_response = f"Response: {response_text}\nSources: {retrieved_texts['ids'][0]}"
        logger.info(f"Generated final answer using LLM\n{formatted_response}")
        return response_text

    except Exception as e:
        logger.error(f"ERROR: Query failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error during query: {traceback.format_exc()}")
        
@app.on_event("shutdown")
async def cleanup_resources():
    logger.info("Cleaning up ChromaDB/other resources...")
    if os.path.exists('chroma'):
        shutil.rmtree('chroma')
        logger.info("deleted the chroma database.")
        
    