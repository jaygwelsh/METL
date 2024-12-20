from PIL import Image, PngImagePlugin
import json
from utils.logger import get_logger

logger = get_logger(__name__)

class ImageAdapter:
    def embed_metadata(self, file_path, metadata):
        try:
            img = Image.open(file_path)
            metadata_str = json.dumps(metadata)
            if file_path.lower().endswith(".png"):
                meta = PngImagePlugin.PngInfo()
                meta.add_text("METL_METADATA", metadata_str)
                img.save(file_path, pnginfo=meta)
            elif file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg"):
                img.info["comment"] = metadata_str
                img.save(file_path, "JPEG", quality=95)
            else:
                logger.error("Unsupported image format")
                return False
            logger.info(f"Metadata embedded into image: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to embed metadata in image: {e}")
            return False

    def extract_metadata(self, file_path):
        try:
            img = Image.open(file_path)
            if file_path.lower().endswith(".png"):
                meta = img.info.get("METL_METADATA")
                return json.loads(meta) if meta else {}
            elif file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg"):
                meta = img.info.get("comment")
                return json.loads(meta) if meta else {}
            else:
                logger.error("Unsupported image format")
                return {}
        except Exception as e:
            logger.error(f"Failed to extract metadata from image: {e}")
            return {}
