# src/services/gemini_test.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


def setup_gemini():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("GEMINI_API_KEY not found in .env")
        return False

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    return model
