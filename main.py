# main.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

from src.services.gmail_service import (
    get_gmail_service,
    fetch_recent_emails_for_analysis
)
from src.services.gemini_service import (
    setup_gemini,
    classify_email_with_gemini
)

load_dotenv()


def emails_classification():
    """Simple analyze of emails"""

    print("Connecting to Gmail ...")
    service = get_gmail_service()
    print("Fetching emails ...")
    emails = fetch_recent_emails_for_analysis(service)

    print("Analyzing with Gemini")
    model = setup_gemini()

    for email in emails:
        category = classify_email_with_gemini(model, email)
        print("---------------")
        print(f"Subject: {email['subject']}")
        print(f"From:    {email['from']}")
        print(f"Labels:  {email['labels']}")
        print(f"Snippet: {email['snippet'][:120]}...")
        print(f"Gemini category: {category}")

    return True


if __name__ == "__main__":
    emails_classification()
