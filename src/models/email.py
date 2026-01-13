# src/models/email.py
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Email:
    """Dataclass for email."""
    id: str
    thread_id: str
    subject: str
    from_addr: str
    snippet: str
    labels: List[str]
    date: str

    def __str__(self) -> str:
        """Standard method for string output."""
        return (
            f"id: {self.id}\n"
            f"thread_id: {self.thread_id}\n"
            f"subject: {self.subject}\n"
            f"from_addr: {self.from_addr}\n"
            f"snippet: {self.snippet[:100]}...\n"
            f"labels: {self.labels}\n"
            f"date: {self.date}"
        )

    def to_prompt_format(self) -> str:
        """Formatting for prompt."""
        return (
            f"ID: {self.id}\n"
            f"From: {self.from_addr}\n"
            f"Subject: {self.subject}\n"
            f"Labels: {', '.join(self.labels)}\n"
            f"Preview: {self.snippet[:100]}"
        )

    def to_dict(self) -> Dict:
        """Conversation to dictionary."""
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'subject': self.subject,
            'from_addr': self.from_addr,
            'snippet': self.snippet,
            'labels': self.labels,
            'date': self.date
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Email':
        """Creation from dictionary."""
        return cls(
            id=data['id'],
            thread_id=data.get('thread_id', ''),
            subject=data.get('subject', ''),
            from_addr=data.get('from_addr', ''),
            snippet=data.get('snippet', ''),
            labels=data.get('labels', []),
            date=data.get('date', '')
        )

    @classmethod
    def from_gmail_response(
        cls,
        message: Dict,
        labels_map: Dict[str, str]
    ) -> 'Email':
        """Creation from Gmail API response."""
        headers = message.get('payload', {}).get('headers', [])
        headers_dict = {header['name']: header['value'] for header in headers}

        return cls(
            id=message['id'],
            thread_id=message.get('hreadId', ''),
            subject=headers_dict.get('Subject', ''),
            from_addr=headers_dict.get('From', ''),
            snippet=message.get('snippet', ''),
            labels=(
                [
                  labels_map.get(label_id, label_id)
                  for label_id in message.get('labelIds', [])
                ]
            ),
            date=headers_dict.get('Date', '')
        )
