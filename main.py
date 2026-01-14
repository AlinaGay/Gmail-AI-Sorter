# main.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

from src.services.gmail_service import get_gmail_service, GmailAPIClient
from src.services.email_data_service import EmailDataService
from src.agents.email_analyzer import EmailAnalyzer

load_dotenv()


def main():
    """Simple analyze of emails"""

    print("Connecting to Gmail ...")
    service = get_gmail_service()
    gmail_client = GmailAPIClient(service)
    email_service = EmailDataService(gmail_client)

    print("Connecting with Gemini")
    gemini_model = setup_gemini()

    print("Analyzing with Gemini")
    analyzer = EmailAnalyzer(gemini_model, gmail_service)
    results = analyzer.execute(num_emails=10)

    print(f"Found categories: {results}")


if __name__ == "__main__":
    main()
