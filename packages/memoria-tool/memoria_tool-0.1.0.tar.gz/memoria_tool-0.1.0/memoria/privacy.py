from .core import MemoryVault
import logging


class PrivacyManager:
    """Manages privacy rules and audit logs."""

    def __init__(self, vault: MemoryVault, log_file: str = 'audit.log'):
        self.vault = vault
        self.exclusions = {}  # e.g., {'folders': ['/private']}
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        self.logger = logging.getLogger('memoria_audit')

    def set_privacy_rules(self, rules: dict):
        """Set exclusion/privacy rules."""
        self.exclusions = rules

    def audit_access_log(self) -> list[str]:
        """Return audit log lines from log file."""
        try:
            log_path = self.logger.handlers[0].baseFilename
            with open(log_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            # In case log file is missing or inaccessible
            return [f"Failed to read audit log: {e}"]

    def log_action(self, action: str, details: str):
        """Log an audited action with details."""
        self.logger.info(f"{action}: {details}")

