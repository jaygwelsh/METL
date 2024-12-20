from docx import Document
import json
from utils.logger import get_logger

logger = get_logger(__name__)

class DOCXAdapter:
    def embed_metadata(self, file_path, metadata):
        try:
            doc = Document(file_path)
            meta_json = json.dumps(metadata)
            doc.core_properties.comments = meta_json
            doc.save(file_path)
            logger.info(f"Metadata embedded into DOCX: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to embed metadata in DOCX: {e}")
            return False

    def extract_metadata(self, file_path):
        try:
            doc = Document(file_path)
            meta_json = doc.core_properties.comments
            if meta_json:
                return json.loads(meta_json)
            return {}
        except Exception as e:
            logger.error(f"Failed to extract metadata from DOCX: {e}")
            return {}
