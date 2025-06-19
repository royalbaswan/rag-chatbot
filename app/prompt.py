import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")

def generate_answer(question: str, chunks: list) -> str:
    context = "\n\n".join([c["document"] for c in chunks])

    prompt = f"""You are an intelligent assistant. Use the following context to answer the question:

    Context:
    {context}

    Question: {question}
    Answer:
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()
