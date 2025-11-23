# src/agents/email_analyzer.py
from typing import List, Dict
from src.agents.base_agent import BaseAgent
import json

from src.services.email_data_service import EmailDataService
from src.services.gmail_service import fetch_recent_emails_for_analysis


class EmailAnalyzer(BaseAgent):
    """Email parsing agent"""

    def __init__(self, gemini_model, gmail_service):
        super().__init__("EmailAnalyzer", gemini_model)
        self.data_service = EmailDataService(gmail_service)

    def execute(self, num_emails: int = 100) -> Dict:
        """Analyzes emails and suggests categories."""
        emails = self.data_service.fetch_emails(num_emails)
        self.log(f"Analyzing {emails} emails...")

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

        try:
            result = json.loads(response.text)
            self.log(f"Found {len(result['categories'])} categories")
            return result
        except json.JSONDecodeError:
            self.log("Failed to parse Gemini response")
            return {"categories": []}

