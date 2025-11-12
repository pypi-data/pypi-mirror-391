# memoria/exporter.py

import json
from .core import MemoryVault, Memory
from .utils import decrypt_data

try:
    from notion_client import Client  # type: ignore
except ImportError:
    # notion-client is optional; export_to_notion will raise a clear error if not installed
    Client = None


class Exporter:
    """Handles exporting memories in various formats."""

    def __init__(self, vault: MemoryVault):
        self.vault = vault

    def export_to_json(self, filepath: str):
        """Export all memories to a JSON file."""
        session = self.vault.Session()
        try:
            memories = session.query(Memory).all()
            data = []
            for m in memories:
                decrypted = decrypt_data(self.vault.key, m.encrypted_content)
                data.append({
                    'content': decrypted,
                    'timestamp': m.timestamp.isoformat(),
                    'source': m.source
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        finally:
            session.close()

    def export_to_notion(self, token: str, parent_page_id: str):
        """
        Export memories to a Notion page.

        Requires integration token and parent page ID.
        Setup guide: https://developers.notion.com/docs/create-a-notion-integration
        """
        if Client is None:
            raise ImportError(
                "notion-client package is required for export_to_notion; "
                "install with 'pip install notion-client'"
            )
        
        client = Client(auth=token)

        session = self.vault.Session()
        try:
            db_memories = session.query(Memory).all()
            memories = []
            for m in db_memories:
                decrypted = decrypt_data(self.vault.key, m.encrypted_content)
                memories.append({
                    'content': decrypted,
                    'timestamp': m.timestamp.isoformat(),
                    'source': m.source
                })
        finally:
            session.close()

        for mem in memories:
            client.blocks.children.append(
                block_id=parent_page_id,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"{mem['timestamp']}: {mem['content']} ({mem['source']})"
                                    }
                                }
                            ]
                        }
                    }
                ]
            )

    def export_to_text(self, filepath: str):
        """Export all memories to a plain text file."""
        session = self.vault.Session()
        try:
            memories = session.query(Memory).all()
            with open(filepath, 'w', encoding='utf-8') as f:
                for m in memories:
                    decrypted = decrypt_data(self.vault.key, m.encrypted_content)
                    f.write(f"Timestamp: {m.timestamp.isoformat()}\n")
                    f.write(f"Source: {m.source}\n")
                    f.write(f"Content: {decrypted}\n")
                    f.write("-" * 80 + "\n\n")
        finally:
            session.close()

    def export_to_csv(self, filepath: str):
        """Export all memories to a CSV file."""
        import csv
        
        session = self.vault.Session()
        try:
            memories = session.query(Memory).all()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Source', 'Content'])
                
                for m in memories:
                    decrypted = decrypt_data(self.vault.key, m.encrypted_content)
                    writer.writerow([
                        m.timestamp.isoformat(),
                        m.source,
                        decrypted
                    ])
        finally:
            session.close()