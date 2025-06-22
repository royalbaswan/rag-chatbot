from langchain_ollama import OllamaLLM
from interact import upload_documents
import pytest_check as check
import requests
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

API_URL = "http://localhost:8000"

EVAL_PROMPT = """Expected Response: {expected_response}
Actual Response: {actual_response}
---
(Answer with 'true' or 'false') Does the actual response match the expected response? 
"""

# Uploading PDFs once before tests
def setup_module(module):
    print("...uploading docs of respective testcases.")
    upload_documents(["sample_docs/monopoly.pdf"])
    upload_documents(["sample_docs/ticket_to_ride.pdf"])
    upload_documents(["sample_docs/financial.pdf"])
    print("-------------------all files uploaded.")
    

def test_monopoly_rules():
    check.is_true(query_and_validate(
        question="How much total money does a player start with in Monopoly? (Answer with the number only)",
        expected_response="$1500",
    ))
    check.is_true(query_and_validate(
        question="How much salary does a player collect when passing GO in Monopoly? (Only the amount)",
        expected_response="$200",
    ))
    check.is_true(query_and_validate(
        question="How much is the fine to get out of jail in Monopoly? (Answer only the amount)",
        expected_response="$50",
    ))
    check.is_true(query_and_validate(
        question="How much players can play in Monopoly? (Answer only the amount)",
        expected_response="2 to 8 Players",
    ))

def test_ticket_to_ride_rules():
    check.is_true(query_and_validate(
        question="How many points does the longest continuous train get in Ticket to Ride? (Answer with the number only)",
        expected_response="10 points",
    ))
    check.is_true(query_and_validate(
        question="When did all friends meet? (Return only the date)",
        expected_response="October 2, 1900",
    ))
    check.is_true(query_and_validate(
        question="what is the objective of the ticket to ride game?",
        expected_response="to score the highest number of total points",
    ))
    check.is_true(query_and_validate(
        question="how much amount Phileas Fogg won?",
        expected_response="£20,000",
    ))

def test_financial_chapter():
    check.is_true(query_and_validate(
        question="What are the two main financial statements covered in the chapter? (return only the names)",
        expected_response="Income Statement and Balance Sheet",
    ))
    check.is_true(query_and_validate(
        question="What is the income tax percentage of BCR Co. Ltd for 2015-16 in its financial statement?",
        expected_response="35%",
    ))
    check.is_true(query_and_validate(
        question="In the comparative statement of Madhu Co. Ltd., what is the revenue from operations in 2016-17?",
        expected_response="20,00,000",
    ))
    check.is_true(query_and_validate(
        question="what are the various tools of financial analysis? (Give only and all the names of these tools)",
        expected_response="Comparative Statements, Ratio Analysis,  Horizontal analysis, and Vertical analysis",
    ))

def query_and_validate(question: str, expected_response: str):
    payload = {"question": question}
    response = requests.post(f"{API_URL}/query", json=payload)
    response.raise_for_status()
    data = response.json()
    prompt = EVAL_PROMPT.format(
        expected_response=expected_response, actual_response=data
    )

    model = OllamaLLM(model="llama3")
    evaluation_results_str = model.invoke(prompt)
    evaluation_results_str_cleaned = evaluation_results_str.strip().lower()

    print("\nquestion: ",question,'\n',prompt,sep='')

    if "true" in evaluation_results_str_cleaned:
        print("\033[92m" + f"Response: {evaluation_results_str_cleaned}" + "\033[0m")
        return True
    elif "false" in evaluation_results_str_cleaned:
        print("\033[91m" + f"Response: {evaluation_results_str_cleaned}" + "\033[0m")
        return False
    else:
        raise ValueError(
            f"Invalid evaluation result. Cannot determine if 'true' or 'false'."
        )
