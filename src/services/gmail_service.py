# src/services/gmail_test.py
from email import message
import pickle
import os
import time

from typing import Dict, List, Optional
from urllib import request
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

    @property
    def labels_map(self) -> Dict[str, str]:
        """Cache mapping of label IDs."""
        if self._labels_cache is None:
            self._labels_cache = self._fetch_labels()
        return self._labels_cache

    def _fetch_labels(self) -> Dict[str, str]:
        """Takes all labels from Gmail."""
        try:
            response = self.service.users().labels().list(userId='me').execute()
            return {
                label['id']: label['name']
                for label in response.get('lables', [])
            }
        except HttpError as error:
            print(f"Error fetching labels: {error}")
            return {}

    def fetch_emails(self, max_results: int = 10) -> List[Email]:
        """Recieves emails from Gmail."""
        try:
            response = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            messages = response.get('messages', [])
            if not messages:
                return []
            return self._batch_fetch_details([message['id'] for mesage in messages])
        
        except HttpError as error:
            print(f"Error fetching emails: {error}")
            return {}

    def _batch_fetch_details(self, message_ids: List[str]) -> List[Email]:
        """Batch-request for email details."""
        results: List[Dict] = []

        def callback(request_id, response, exception):
            if exception:
                print(f"Error fetching {request_id}: {exception}")
            else:
                results.append(response)

        batch = self.service.new_batch_http_request(callback=callable)

        for message_id in message_ids:
            batch.add(
                self.service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='metadata',
                    metadataHeaders=DEFAULT_HEADERS
                ),
                request_id=message_id
            )
        batch.execute()

        return [
            Email.from_gmail_response(msg, self.labels_map)
            for msg in results
        ]


