import json
from .core import MemoryVault
from notion_client import Client
from .utils import decrypt_data  # Assuming decrypt_data is in utils


class Exporter:
    """Handles exporting memories in various formats."""

    def __init__(self, vault: MemoryVault):
        self.vault = vault

    def export_to_json(self, filepath: str):
        """Export all memories to a JSON file."""
        session = self.vault.Session()
        memories = session.query(self.vault.Memory).all()
        data = []
        for m in memories:
            decrypted = decrypt_data(self.vault.key, m.encrypted_content)
            data.append({
                'content': decrypted,
                'timestamp': str(m.timestamp),
                'source': m.source
            })
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        session.close()

    def export_to_notion(self, token: str, parent_page_id: str):
        """
        Export memories to a Notion page.

        Requires integration token and parent page ID.
        Setup guide: https://developers.notion.com/docs/create-a-notion-integration
        """
        client = Client(auth=token)

        session = self.vault.Session()
        db_memories = session.query(self.vault.Memory).all()
        memories = []
        for m in db_memories:
            decrypted = decrypt_data(self.vault.key, m.encrypted_content)
            memories.append({
                'content': decrypted,
                'timestamp': str(m.timestamp),
                'source': m.source
            })
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
