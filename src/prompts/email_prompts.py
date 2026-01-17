# src/prompts/email_prompts.py

ANALYZE_EMAILS_PROMPT = """
    Analyze these emails and suggest folder categories.

    Emails:
    {emails}

    Requirements:
    - Group similar emails together (by sender, topic, or purpose)
    - Suggest clear, descriptive folder names
    - Each email should belong to exactly one category

    Return JSON with categories:
    {{
        "categories": [
            {{
                "name": "folder_name",
                "description": "brief description of why these emails belong together",
                "email_ids": ["id1", "id2"],
                "count": 5
            }}
        ]
    }}
"""


def get_analyze_prompt(emails_text: str) -> str:
    """Returns a prompt for analizing of emails."""
    return ANALYZE_EMAILS_PROMPT.format(emails=emails_text)