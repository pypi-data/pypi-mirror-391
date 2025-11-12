import os
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import browserhistory
from .core import MemoryVault

# Optional imports for API integrations
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    Credentials = None
    build = None

try:
    from slack_sdk import WebClient
except ImportError:
    WebClient = None


class WhatsAppIngestor(Ingestor):
    """Example subclass for WhatsApp ingestion."""

    def ingest_whatsapp(self, token: str, phone_id: str, limit: int = 10):
        """
        Ingest WhatsApp messages. Requires WhatsApp Business API setup.
        """
        # Assuming WhatsApp is imported from whatsapp-python lib
        whatsapp = WhatsApp(token, phone_id)
        messages = whatsapp.get_messages(limit=limit)  # Pseudo-code; adapt to actual lib
        for msg in messages:
            content = msg['body']
            timestamp = datetime.fromisoformat(msg['timestamp'])
            self.vault.add_memory(content, timestamp, source=f"whatsapp:{msg['id']}")


class FileHandler(FileSystemEventHandler):
    """Watches file changes and ingests content."""

    def __init__(self, vault: MemoryVault):
        self.vault = vault

    def on_modified(self, event):
        if not event.is_directory:
            try:
                with open(event.src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.vault.add_memory(content, datetime.now(), source=event.src_path)
            except Exception as e:
                print(f"Failed to read file {event.src_path}: {e}")


class Ingestor:
    """Handles data ingestion from various sources."""

    def __init__(self, vault: MemoryVault):
        self.vault = vault
        self.observer = None

    def start_monitoring(self, paths: list[str] = None, sources: list[str] = None):
        """
        Start watching file system paths and ingest configured sources.
        
        :param paths: List of directory paths to watch.
        :param sources: List of data source types e.g. ['files', 'browser', 'gmail', 'slack'].
        """
        if sources is None:
            sources = []
        if paths is None:
            paths = []

        if 'files' in sources and paths:
            self.observer = Observer()
            for path in paths:
                self.observer.schedule(FileHandler(self.vault), path=path, recursive=True)
            self.observer.start()

        if 'browser' in sources:
            self.ingest_browser_history()

    def ingest_from_source(self, source_type: str, data: dict):
        """Ingest custom data given as dict."""
        if source_type == 'custom':
            self.vault.add_memory(
                data['content'],
                data.get('timestamp', datetime.now()),
                data.get('source', 'custom')
            )

    def ingest_browser_history(self):
        """Ingest browsing history from installed browsers."""
        try:
            history = browserhistory.get_browserhistory()
            for browser, entries in history.items():
                for url, title, timestamp in entries:
                    content = f"Visited {url}: {title}"
                    self.vault.add_memory(content, datetime.fromtimestamp(timestamp), source=browser)
        except Exception as e:
            print(f"Failed to ingest browser history: {e}")

    def ingest_gmail(self, credentials_file: str, labels: list[str] = ['INBOX'], max_results: int = 10):
        """
        Ingest emails from Gmail using OAuth credentials.
        Setup: https://developers.google.com/gmail/api/quickstart/python
        """
        if not Credentials or not build:
            raise ImportError("Google API client libraries are not installed.")
        creds = Credentials.from_authorized_user_file(credentials_file, ['https://www.googleapis.com/auth/gmail.readonly'])
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=labels, maxResults=max_results).execute()
        messages = results.get('messages', [])

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            content = msg_data.get('snippet', '')  # Could be enhanced to parse full email body
            timestamp = datetime.fromtimestamp(int(msg_data.get('internalDate', '0')) / 1000)
            self.vault.add_memory(content, timestamp, source=f"gmail:{msg['id']}")

    def ingest_slack(self, token: str, channel_id: str, limit: int = 10):
        """
        Ingest messages from Slack channel using bot token.
        Setup: https://api.slack.com/docs
        """
        if not WebClient:
            raise ImportError("slack_sdk is not installed.")
        client = WebClient(token=token)
        response = client.conversations_history(channel=channel_id, limit=limit)
        for msg in response.get('messages', []):
            content = msg.get('text', '')
            timestamp = datetime.fromtimestamp(float(msg.get('ts', '0')))
            self.vault.add_memory(content, timestamp, source=f"slack:{msg.get('ts')}")

    def stop_monitoring(self):
        """Stop watching file changes."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
