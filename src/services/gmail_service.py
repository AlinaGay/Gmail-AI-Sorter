# src/services/gmail_test.py
import pickle
import os
import time

from typing import Dict, List, Optional
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from src.models.email import Email


NUMBER_OF_EMAILS = 10

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.modify'
    ]

DEFAULT_HEADERS = ['From', 'Subject', 'Date']


def get_gmail_service():
    """Takes authorized Gmail API client."""
    creds = None
    token_file = 'token.pickle'

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                os.remove(token_file)
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def fetch_recent_emails_for_analysis(service, max_results: int = NUMBER_OF_EMAILS) -> List[Dict]:
    label_list = service.users().labels().list(userId='me').execute()
    labels = {
        label['id']: label['name']
        for label in label_list.get('labels', [])
    }

    message_list = service.users().messages().list(
        userId='me',
        maxResults=max_results
    ).execute()

    messages = message_list.get('messages', [])
    emails = []

    for message in messages:
        msg_id = message['id']
        msg = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()

        headers = msg.get('payload', {}).get('headers', [])
        headers_dict = {header['name']: header['value'] for header in headers}

        email_data = {
            "id": msg_id,
            "thread_id": msg.get("threadId"),
            "labels": [labels.get(lid, lid) for lid in msg.get('labelIds', [])],
            "from_addr": headers_dict.get('From'),
            "subject": headers_dict.get('Subject'),
            "date": headers_dict.get('Date'),
            "snippet": msg.get('snippet', ''),
        }

        emails.append(email_data)
    return emails


class GmailAPIClient:
    """Low-level client for Gmail API."""
    def __init__(self, service: Resource):
        self.service = service
        self._labels_cache: Optional[Dict[str, str]] = None