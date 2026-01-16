# src/services/gmail_test.py
import pickle
import os

from typing import Dict, List, Optional
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest
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

DEFAULT_HEADERS = ['From', 'To', 'Subject', 'Date']


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
            response = self.service.users().labels().list(
                userId='me').execute()
            return {
                label['id']: label['name']
                for label in response.get('labels', [])
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
            return self._batch_fetch_details(
                [
                    message['id'] for message in messages
                ]
            )

        except HttpError as error:
            print(f"Error fetching emails: {error}")
            return []

    def _batch_fetch_details(self, message_ids: List[str]) -> List[Email]:
        """Batch-request for email details."""
        results: List[Dict] = []

        def callback(request_id, response, exception):
            if exception:
                print(f"Error fetching {request_id}: {exception}")
            else:
                results.append(response)

        batch = BatchHttpRequest(callback=callback)

        for message_id in message_ids:
            request = self.service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='metadata',
                    metadataHeaders=DEFAULT_HEADERS
                )
            batch.add(request, request_id=message_id)

        try:
            batch.execute()
        except Exception as error:
            print(f"Batch execution failed: {error}")

        return [
            Email.from_gmail_response(message, self.labels_map)
            for message in results
        ]

    def get_all_labels(self) -> List[Dict]:
        """Takes whole list of labels."""
        labels = self._fetch_labels()
        return [
            {'id': label_id, 'name': name}
            for label_id, name in labels.items()
        ]

    def create_label(self, name: str) -> Dict:
        """Create a new label."""
        for label_id, label_name in self.labels_map.items():
            if label_name.lower() == name.lower():
                return {'id': label_id, 'name': label_name, 'created': False}

        body = {
            'name': name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        result = self.service.users().labels().create(
            userId='me', body=body
        ).execute()

        self.labels_map[result['id']] = result['name']

        return {'id': result['id'], 'name': result['name'], 'created': True}

    def move_emails(self, email_ids: List[str], label_id: str) -> Dict:
        """Moves emails to label."""
        success, failed = [], []
        for email_id in email_ids:
            try:
                self.service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={'addLabelIds': [label_id]}
                ).execute()
                success.append(email_id)
            except HttpError as error:
                failed.append({'id': email_id, 'error': str(error)})

        return {'success': success, 'failed': failed}
