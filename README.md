                                LLM based RAG chatbot for question-answering

This project builds a containerized Retrieval-Augmented Generation (RAG) chatbot using FastAPI, ChromaDB, and OpenAI GPT.

## Features
- Supports PDF, TXT, CSV document ingestion
- Embeddings via Sentence Transformers
- Semantic search with ChromaDB
- REST API for QA interaction
- Dockerized for deployment

## Setup

```bash
git clone <repo-url>
cd rag-chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Start the App/Run the API in a separate tmux session
- Assuming you are at the root dir of the model and env is activated
- when the app is started, exit from the tmux session using ctrl+ B and D (linux)
```bash
tmux new -s chat_server
uvicorn app.main:app --reload --port 8898
```

## Example 

1. Place documents in `data/` directory
2. Start the API
3. Use Postman or cURL:
```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question": "What is this document about?"}'
```

## Docker

```bash
docker build -t rag-chatbot .
docker run -p 8898:8898 rag-chatbot
```

## License
MIT
