# src/services/gemini_test.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("GEMINI_API_KEY not found in .env")
        return False

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    response = model.generate_content(
        "Categorize this email subject: 'Your Amazon order has shipped'"
    )

    print("Gemini connected successfully!")
    print(f"Response: {response.text[:200]}...")

    return True


if __name__ == "__main__":
    test_gemini()
