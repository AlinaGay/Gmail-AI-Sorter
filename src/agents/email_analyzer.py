# src/agents/email_analyzer.py
import json
import time

from typing import Dict, List, Optional
from google.api_core.exceptions import ResourceExhausted
from src.agents.base_agent import BaseAgent

from src.services.email_data_service import EmailDataService
from src.models.email_analysis import EmailAnalysis
from src.prompts.email_prompts import get_analyze_prompt
from src.utils.retry import retry_on_quota


class EmailAnalyzer(BaseAgent):
    """Email parsing and categorizing agent"""

    def __init__(self, gemini_model, email_service: EmailDataService):
        super().__init__("EmailAnalyzer", gemini_model)
        self.email_service = email_service

    def execute(self, num_emails: int = 100, max_retries: int = 3) -> Dict:
        """Analyzes emails and suggests categories."""
        emails = self.email_service.fetch_emails(num_emails)

        if not emails:
            self.log("No emails found.")
            return EmailAnalyzer(categories=[], error="No emails found.")
        self._log_emails(emails)

        email_text = self.email_service.format_for_prompt(emails)
        prompt = get_analyze_prompt(email_text)

        response = self._call_model(prompt)

        if response is None:
            return EmailAnalysis(categories=[], error="Failed to get model response.")

        return self._parse_response(response)

    @retry_on_quota(max_retries=3, wait_time=60)
    def _call_model(self, prompt: str) -> Optional[str]:
        """Calls model with retry when quota is overload."""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as error:
            self.log(f"Quota exceed. Model call failed: {error}")
            return None


        # log_output = self.data_service.format_emails_for_log(emails)
        # self.log(f"Analyzing {len(emails)} emails: \n\n{log_output}")

        # email_text = self.data_service.format_for_gemini(emails)

        
        # response = None
        # for attempt in range(max_retries):
            

        # if response is None:
        #     self.log("Failed to get response from Gemini")
        #     return {"categories": [], "error": "No response"}

        # raw = response.text
        # self.log(f"Raw Gemini response: {repr(raw)}")

        # try:
        #     start = raw.find("{")
        #     end = raw.rfind("}")
        #     if start == -1 or end == -1:
        #         raise json.JSONDecodeError("No JSON object found", raw, 0)

        #     json_str = raw[start:end + 1]
        #     result = json.loads(json_str)

        #     categories = result.get('categories', [])
        #     self.log(f"Found {len(categories)} categories")

        #     if categories:
        #         formatted_categories = self._format_categories_for_log(categories)
        #         self.log(formatted_categories)
            
        #     return result
        # except json.JSONDecodeError:
        #     self.log("Failed to parse Gemini response")
        #     return {"categories": []}

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
