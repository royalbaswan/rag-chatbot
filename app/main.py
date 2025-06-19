from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
import os
import shutil
import tempfile

from app.ingestion import load_and_split, get_embeddings
from app.collection import get_or_create_collection, query_collection
from app.prompt import generate_answer


app = FastAPI()

class QueryRequest(BaseModel):
    question: str = Field(..., max_length=1000, description="The question to ask, max 1000 characters.")
    session_id: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        texts = load_and_split(tmp_path)
        if not texts:
            raise HTTPException(status_code=400, detail="Failed to extract any text from document")

        embeddings = get_embeddings(texts)
        session_id = str(uuid4())

        collection = get_or_create_collection(session_id)
        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=[{"source": file.filename}] * len(texts),
            ids=[f"{session_id}_{i}" for i in range(len(texts))]
        )

        return {"session_id": session_id, "message": "File uploaded and indexed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during upload: {e}")

@app.post("/query")
def query_question(req: QueryRequest):
    try:
        collection = get_or_create_collection(req.session_id)
        results = query_collection(collection, req.question)
        final_answer = generate_answer(req.question, results)
        return {"question": req.question, "answer": final_answer, "chunks": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during query: {e}")

@app.get("/")
def root():
    return {"message": "RAG QA Chatbot is up and running!"}
