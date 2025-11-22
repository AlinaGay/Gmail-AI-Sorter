# main.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

from src.services.gmail_service import (
    get_gmail_service
)
from src.services.gemini_service import (
    setup_gemini,
    classify_email_with_gemini
)
from src.services.email_data_service import EmailDataService
from src.agents.email_analyzer import EmailAnalyzer

load_dotenv()


def main():
    """Simple analyze of emails"""

    print("Connecting to Gmail ...")
    gmail_service = get_gmail_service()

    print("Analyzing with Gemini")
    gemini_model = setup_gemini()

    analyzer = EmailAnalyzer(gemini_model, gmail_service)
    results = analyzer.execute(num_emails=50)

    print(f"Found categories: {results}")


if __name__ == "__main__":
    main()
