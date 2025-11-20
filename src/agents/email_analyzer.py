# src/agents/email_analyzer.py
from typing import List, Dict
from src.agents.base_agent import BaseAgent
import json

from src.services.gmail_service import fetch_recent_emails_for_analysis


class EmailAnalyzer(BaseAgent):
    """Email parsing agent"""

    def __init__(self, gemini_model, gmail_service):
        super.__init__("EmailAnalyzer", gemini_model)
        self.gmail_service = gmail_service

    def execute(self, num_emails: int = 100) -> Dict:
        """Analyzes emails and suggests categories."""
        self.log(f"Analyzing {num_emails} emails...")

        emails = fetch_recent_emails_for_analysis(
            self.gmail_service,
            max_results=num_emails
        )

        self.log(f"Analyzing {len(emails)} emails ...")

        email_text = self._format_for_prompt(emails)

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
            return {"categories:" []}

    def _format_for_prompt(self, emails: List[Dict]) -> str:
        """Formats already received emails for prompting"""
        lines = []

        for email in emails[:50]:
            lines.append(f"""
                ID: {email['id']}
                From: From: {email.get('from', 'Unknown')}
                Subject: {email.get('subject', 'No subject')}
                Current Labels: {', '.join(email.get('labels', []))}
                Preview: {email.get('snippet', '')[:100]}
            ----""")
        return '\n'.join(lines)
