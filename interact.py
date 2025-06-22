import requests
import traceback
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

API_URL = "http://localhost:8000"

def upload_documents(file_paths):
    files = []
    for path in file_paths:
        if not os.path.isfile(path):
            print(f"[ERROR] File not found: {path}")
            continue
        files.append(("files", (os.path.basename(path), open(path, "rb"))))

    if not files:
        print("[ERROR] No valid files to upload.")
        return None

    try:
        response = requests.post(f"{API_URL}/upload", files=files)
        response.raise_for_status()
        data = response.json()
        print(f"{data}")
    except Exception as e:
        print(f"[UPLOAD FAILED] {e}")
        traceback.print_exc()
        return None
    finally:
        # Close all file objects
        for _, (_, file_obj) in files:
            file_obj.close()

def query_question(question):
    try:
        payload = {
            "question": question
        }
        response = requests.post(f"{API_URL}/query", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"{data}")
    except Exception as e:
        print(f"[QUERY FAILED] {e}")
        traceback.print_exc()

def main():
    print("="*60)
    print("📄  Welcome to the RAG Chatbot Tester")
    print("="*60)
    print("Instructions:")
    print("- Type `upload <file1> <file2> ...` to upload multiple PDFs.")
    print("- Type `ask <your question>` to query the document(s).")
    print("- Type `quit` to exit the program.")
    print("="*60)

    while True:
        user_input = input("\n>> ").strip()

        if user_input.lower() == "quit":
            print("👋 Exiting. Goodbye!")
            break

        if user_input.startswith("upload "):
            file_paths = user_input[len("upload "):].strip().split()
            upload_documents(file_paths)

        elif user_input.startswith("ask "):
            question = user_input[len("ask "):].strip()
            query_question(question)

        else:
            print("[ERROR] Invalid command. Use `upload <files...>` or `ask <question>`.")

if __name__ == "__main__":
    main()
