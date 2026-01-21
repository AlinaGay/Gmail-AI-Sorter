# src/agents/email_analyzer.py
import json
import time

from typing import Dict, List
from google.api_core.exceptions import ResourceExhausted
from src.agents.base_agent import BaseAgent

from src.services.email_data_service import EmailDataService


class EmailAnalyzer(BaseAgent):
    """Email parsing agent"""

    def __init__(self, gemini_model, email_service: EmailDataService):
        super().__init__("EmailAnalyzer", gemini_model)
        self.email_service = email_service

    def _format_categories_for_log(self, categories: List[Dict]):
        """Formates categories for log output."""
        formatted = []
        for i, cat in enumerate(categories, 1):
            cat_str =f"""Category {i}:
            name: {cat.get('name', 'N/A')}
            description: {cat.get('description', 'N/A')}
            email_ids: {cat.get('email_ids', [])}
            count: {cat.get('count', 0)}"""
            formatted.append(cat_str)
        return '\n\n' + ('-' * 50 + '\n\n').join(formatted)

    def execute(self, num_emails: int = 100, max_retries: int = 3) -> Dict:
        """Analyzes emails and suggests categories."""
        emails = self.data_service.fetch_emails(num_emails)

        log_output = self.data_service.format_emails_for_log(emails)
        self.log(f"Analyzing {len(emails)} emails: \n\n{log_output}")

        email_text = self.data_service.format_for_gemini(emails)

        prompt = f"""
                Analyze these emails and suggest folder categories.

                Emails:
                {email_text}

                Return JSON with categories:
                {{
                    "categories": [
                        {{
                            "name": "folder_name",
                            "description": "why this folder",
                            "email_ids": ["id1", "id2"],
                            "count": 5
                        }}
                    ]
                }}
              """
        response = None
        for attempt in range(max_retries):
            try:
                response = self.gemini_model.generate_content(prompt)
                break
            except ResourceExhausted:
                wait_time = 60
                self.log(f"Quota exceed. Waiting {wait_time}s...(attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    self.log("Max retries reached. Aborting.")
                    return {"categories": [], "error": "Quota exceeded"}

        if response is None:
            self.log("Failed to get response from Gemini")
            return {"categories": [], "error": "No response"}

        raw = response.text
        self.log(f"Raw Gemini response: {repr(raw)}")

        try:
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1:
                raise json.JSONDecodeError("No JSON object found", raw, 0)

            json_str = raw[start:end + 1]
            result = json.loads(json_str)

            categories = result.get('categories', [])
            self.log(f"Found {len(categories)} categories")

            if categories:
                formatted_categories = self._format_categories_for_log(categories)
                self.log(formatted_categories)
            
            return result
        except json.JSONDecodeError:
            self.log("Failed to parse Gemini response")
            return {"categories": []}
