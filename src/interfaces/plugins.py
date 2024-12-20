# src/interfaces/plugins.py

from utils.logger import get_logger
from core.metadata import MetadataEngine
import os

logger = get_logger(__name__)

class CMSPlugin:
    """
    A plugin to integrate with a CMS, automatically embedding metadata into files
    processed by the CMS.
    """
    def __init__(self, cms_name, ledger=None):
        self.cms_name = cms_name
        self.engine = MetadataEngine(ledger=ledger)
        self.engine.load_private_key()
        self.engine.load_public_key()

    def process_file(self, file_path):
        """
        Processes a file by embedding suggested metadata into a sidecar.
        """
        if not self.engine._private_key:
            logger.error("Private key not found. Cannot embed metadata.")
            return False

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        try:
            with open(file_path, "r", errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Unable to read file {file_path}: {e}")
            return False

        suggestions = self.engine.suggest_metadata(content)
        signed_meta = self.engine.embed_metadata(file_path, suggestions, self.engine._private_key)
        if signed_meta:
            self.engine.log_to_ledger(f"CMS '{self.cms_name}' embedded metadata into {file_path}")
            logger.info(f"CMS '{self.cms_name}' embedded metadata into {file_path}")
            return True
        else:
            logger.error(f"CMS '{self.cms_name}' failed to embed metadata into {file_path}")
            return False
