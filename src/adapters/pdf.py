import pikepdf
import json
from utils.logger import get_logger

logger = get_logger(__name__)

class PDFAdapter:
    def embed_metadata(self, file_path, metadata):
        try:
            with pikepdf.Pdf.open(file_path, allow_overwriting_input=True) as pdf:
                info = pdf.docinfo
                info["/METADATA_JSON"] = json.dumps(metadata)
                pdf.save(file_path)
            logger.info(f"Metadata embedded into PDF: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to embed metadata in PDF: {e}")
            return False

    def extract_metadata(self, file_path):
        try:
            with pikepdf.Pdf.open(file_path) as pdf:
                info = pdf.docinfo
                meta_json = info.get("/METADATA_JSON")
                if meta_json:
                    return json.loads(meta_json)
            return {}
        except Exception as e:
            logger.error(f"Failed to extract metadata from PDF: {e}")
            return {}
