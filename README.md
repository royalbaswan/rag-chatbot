                                LLM based RAG chatbot for question-answering

This project builds a containerized Retrieval-Augmented Generation (RAG) chatbot using FastAPI, ChromaDB, and Ollama LLM.

NOTE: Although with Ollama you can run this locally but it is not advised to run it on CPU. You might face errors/issues. Use good quality GPU for creating inference.
## Features
- Supports PDF, TXT document ingestion
- Embeddings via Sentence Transformers
- Semantic search with ChromaDB
- REST API for QA interaction
- Dockerized for deployment

## Setup

```python
git clone <repo-url>
cd rag-chatbot
python3 -m venv env
source env/bin/activate
pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
# install ollama and download the model
curl -fsSL https://ollama.com/install.sh | sh
ollama --version # Verify installation
ollama pull llama3  # Downloads Meta's Llama 3.
ollama list # Should show llama3 in the list.
```

## Interacting with the chatbot

First of all start the App/Run the API in a separate tmux session (linux)
- Assuming you are at the root dir of the model
- when the app is started, exit from the tmux session using ctrl+ B and D
```python
tmux new -s chat_server
source env/bin/activate   # if env is not activated
uvicorn app.main:app --log-config log_config.yaml --port 8000
```

#### Two ways to interact with the app
1. Through `Interact.py` (Recommended)

- After all the setup has been done, you can upload your documents and ask questions to the chatbot through `interact.py` in the root directory. Sample docs have been provided in `sample_docs` directory.
    - Just Run it with `python interact.py` and it will guide you to upload and ask questions.
    - Examples are as follows:
        1. For uploading the pdfs you can just write `upload <file_path_1>` or `upload <file_path_1> <file_path_2>`. It has the functionality to upload 1 or multiple files as showed with the command. You will receive a message like this: "File uploaded and indexed successfully."
            - Example `upload sample_docs/monopoly.pdf`
        2. After the files have been uploaded you can ask your query by typing `ask query`. 
            - Example `ask How much total money does a player start with in Monopoly? (Answer with the number only)`
- The process in iterative in nature like you can upload more documents and ask questions iteractively and freely as you want.

2. Through Postman or cURL:

- upload the document
```python
curl -X POST http://localhost:8000/upload -F "files=@<file_path_1>" -F "files=@<file_path_2>"
# example usage
curl -X POST http://localhost:8000/upload -F "files=@sample_docs/monopoly.pdf"
```

- you will receive a message like this: "File uploaded and indexed successfully."

- asking your questions to the chatbot based on the pdfs uploaded
```python
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question": "your-query"}'
# example usage
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question": "How much total money does a player start with in Monopoly? (Answer with the number only"}'
```

## Instructions for testing the chatbot responsiveness and accuracy (test script)

1. Ensure the app is up and running, otherwise you can start it by following the steps in Interacting with the chatbot section.
2. With `test_cases.py` you can test the responsiveness and accuracy. 
3. This file includes sample prompts and their expected outputs. 
4. command to run: `pytest -s`
5. It first upload all the 3 pdf files included in `sample_docs` folder and with pytest starts testing with the testcases added for each pdf file.
6. If you want to test with your prompts, you can do that with `interact.py` as explained above.


## Step-by-step Docker Workflow
Note: Skip 1 and 2 if already done in the steup instructions.

1. Installing ollama
```python
RUN curl -fsSL https://ollama.com/install.sh | sh
```
2. Download ollam3 model
```python
ollama pull llama3 
```

3. Build the Docker image from the docker file.
```bash
docker build -t rag_chatbot:chatbot .
```

4. Finally, run the Docker container
```bash
docker run -p 127.0.0.1:8000:8000 rag_chatbot:chatbot
```

## License
MIT
