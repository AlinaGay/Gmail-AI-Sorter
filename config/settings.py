# config/settings.py

"""
Application settings
Run with: uv run python config/settings.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


class Settings:
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"

    # API keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Gmail settings
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.labels',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    CREDENTIALS_FILE = BASE_DIR / "config" / "credentials.json"
    TOKEN_FILE = BASE_DIR / "config" / "token.pickle"

    # App settings
    MAX_EMAILS_TO_ANALYZE = 10
    MIN_EMAILS_PER_CATEGORY = 3
    MAX_CTEGORIES = 10

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        """Checking the obligatory settings"""
        errors = []

        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY not found in .env")
        if not cls.CREDENTIALS_FILE.exists():
            errors.append(
                f"Gmail credentials not found at {cls.CREDENTIALS_FILE}")
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))

        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

        return True


settings = Settings()

if __name__ == "__main__":
    print("Validating settings...")
    try:
        settings.validate()
        print("Settings OK!")
    except ValueError as e:
        print(f"{e}")
