# src/services/email_data_service.py
from typing import List, Dict, Optional

from src.models.email import Email
from src.services.gmail_service import GmailAPIClient


class EmailDataService:
    """Highlevel service for working with email data."""

    def __init__(self, gmail_client: GmailAPIClient):
        self.gmail_client = gmail_client
        self._cache: Dict[str, List[Email]] = {}

    def fetch_emails(
        self,
        max_results: int = 10,
        use_cache: bool = True
    ) -> List[Email]:
        """Receives emails with caching."""
        cache_key = f"emails_{max_results}"

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        emails = self.gmail_client.fetch_emails(max_results)

        if use_cache:
            self._cache[cache_key] = emails

        return emails

    def get_emails_by_ids(self, email_ids: List[str]) -> List[Email]:
        """Receives emails by ID from the cache"""
        all_cached = []
        for emails in self._cache.values():
            all_cached.extend(emails)

        seen = set()
        result = []
        for email in all_cached:
            if email.id in email_ids and email.id not in seen:
                result.append(email)
                seen.add(email.id)

        return result

    def clear_cache(self):
        """Clear cache."""
        self._cache.clear()

    def format_for_prompt(
        self,
        emails: List[Email],
        max_emails: int = 10
    ) -> str:
        """Formats emails for AI prompt"""
        formatted = [email.to_prompt_format() for email in emails[:max_emails]]
        return '\n---\n'.join(formatted)

    def format_for_gemini(
        self,
        emails: List[Email],
        max_emails: int = 10
    ) -> str:
        """Alias for format_for_prompt."""
        return self.format_for_prompt(emails, max_emails)

    def format_for_log(self, emails: List[Email]) -> str:
        """Formats emails for logging"""
        return '\n\n'.join(str(email) for email in emails)

    def get_folders(self) -> List[Dict]:
        """Takes list of folders."""
        labels = self.gmail_client.get_all_labels()

        return [label for label in labels if not label['name'].startswith('CTEGORY_')]

    def create_folder(self, name: str) -> Dict:
        """Create folder."""
        return self.gmail_client.create_label(name)

    def sort_emails(self, email_ids: List[str], folder_name: str) -> Dict:
        """Sorts emails to folders."""
        folder = self.create_folder(folder_name)
        result = self.gmail_client.move_emails(email_ids, folder['id'])
        result['folder'] = folder_name

        return result
