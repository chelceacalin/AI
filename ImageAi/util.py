import os
import time
from typing import List
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def send_request(query: str, img64: str, agree, context: str, magic_options):
    print("Querying Image API...")
    base64_image = img64
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    query = query + "\n" if query is not None and len(query) > 2 else "\n Help me solve the following image \n"
    if agree:
        query += ("\n You can use your previous answer to guide you. "
                  "Your previous answer is " + context + " \n")

    if magic_options:
        query += "\n Also, I'll give you some context for the question: " + magic_options + "\n"

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers = headers, json = payload)
    response_data = response.json()
    if "choices" in response_data:
        return response_data["choices"][0]["message"]["content"], query
    else:
        return "Error: " + response_data.get("error", {}).get("message", "Unknown error")


def send_text_request(query: str, context: str, agree: bool, magic_options):
    print("Querying Text API...")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    if query is not None and len(query) > 2:
        formatted_query = query + "\n"
    else:
        formatted_query = "\n Help me with the following text query \n"

    if agree:
        formatted_query += ("\n You can use your previous answer to guide you. " + context + " \n")

    if magic_options:
        formatted_query += "\n Also, I'll give you some context for the question: " + magic_options + "\n"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": formatted_query
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers = headers, json = payload)
    response_data = response.json()

    print("respo ", response_data)
    if "choices" in response_data:
        return response_data["choices"][0]["message"]["content"], formatted_query
    else:
        return "Error: " + response_data.get("error", {}).get("message", "Unknown error"), "Error"


def print_spaces(lines: int):
    for _ in range(lines):
        st.text("")


def stream_data(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


def get_predefined_query() -> List[str]:
    return ["Help me solve the following problem received as an image with a concise answer",
            "Give me just the right answer to the following grid question ",
            "Answer the following question correctly and concisely"]


def get_magic_options() -> List[str]:
    return ["The language is Java using Spring Framework",
            "You are an useful assistant that responds to the question accurately"]
