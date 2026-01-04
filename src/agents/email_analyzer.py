# src/agents/email_analyzer.py
from typing import Dict
from src.agents.base_agent import BaseAgent
import json

from src.services.email_data_service import EmailDataService


class EmailAnalyzer(BaseAgent):
    """Email parsing agent"""

    def __init__(self, gemini_model, gmail_service):
        super().__init__("EmailAnalyzer", gemini_model)
        self.data_service = EmailDataService(gmail_service)

    def execute(self, num_emails: int = 100) -> Dict:
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
        response = self.gemini_model.generate_content(prompt)
        raw = response.text
        self.log(f"Raw Gemini response: {repr(raw)}")

        try:
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1:
                raise json.JSONDecodeError("No JSON object found", raw, 0)

            json_str = raw[start:end + 1]
            result = json.loads(json_str)

            self.log(f"Found {len(result.get('categories', []))} categories")
            return result
        except json.JSONDecodeError:
            self.log("Failed to parse Gemini response")
            return {"categories": []}
