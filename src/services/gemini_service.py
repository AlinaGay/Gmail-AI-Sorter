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
    model = genai.GenerativeModel('gemini-2.0-flash')

    return model


def classify_email_with_gemini(model, email: dict) -> str:
    prompt = f"""
        You are an email classification assistant.

        Classify the following email into one of the categories:
        - PERSONAL
        - WORK
        - NEWSLETTER
        - PROMOTION
        - SOCIAL
        - FINANCE
        - OTHER

        Return only the category name, nothing else.

        From:{email.get('form')}
        Subject: {email.get('subject')}
        Snippet: {email.get('snippet')}
        Existing Gmail labels: {", ".join(email.get('labels', []))}"""

    response = model.generate_content(prompt)
    category = response.text.strip()

    return category
