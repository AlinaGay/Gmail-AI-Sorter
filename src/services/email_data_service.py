# src/services/email_data_service.py
from typing import List, Dict, Optional
from dataclasses import dataclass
import json

from src.services.gmail_service import fetch_recent_emails_for_analysis

@dataclass
class Email:
    """Dataclass for email"""
    id: str
    thread_id: str
    subject: str
    from_addr: str
    snippet: str
    labels: List[str]
    date: str

    def to_prompt_format(self) -> str:
        """Formatting for prompt"""
        return f"""
        ID: {self.id}
        From: {self.from_addr}
        Subject: {self.subject}
        Labels: {', '.join(self.labels)}
        Preview: {self.snippet[:100]}
        """


class EmailDataService:
    """A unified service for working with email data"""

    def __init__(self, gmail_service):
        self.gmail_service = gmail_service
        self._cache = {}

    def fetch_emails(self, max_results: int = 100, use_cache: bool = True) -> List[Email]:
        """Receives emails with caching"""
        cache_key = f"emails_{max_results}"

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        emails_data = fetch_recent_emails_for_analysis(
            self.gmail_service,
            max_results
        )

        emails = [
            Email(
                id=email['id'],
                thread_id=email.get('threadId', ''),
                subject=email.get('subject', ''),
                from_addr=email.get('from', ''),
                snippet=email.get('snippet', ''),
                labels=email.get('labels', []),
                date=email.get('date', '')
            )
            for email in emails_data
        ]

        if use_cache:
            self._cache[cache_key] = emails

        return emails

    def format_for_gemini(self, emails: List[Email], max_emails: int = 50) -> str:
        """Formats emails for the Gemini prompt"""
        formatted = [email.to_prompt_format() for email in emails[:max_emails]]
        return '\n---\n'.join(formatted)

    def get_emails_by_ids(self, email_ids: List[str]) -> List[Email]:
        """Receives emails by ID from the cache"""
        all_emails = self._cache.get('emails_100', [])
        return [e for e in all_emails if e.id in email_ids]
