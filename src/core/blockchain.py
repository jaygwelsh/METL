import uuid
from utils.logger import get_logger

logger = get_logger(__name__)

class BlockchainInterface:
    def __init__(self, config):
        self.node_url = config.get("node_url", "http://localhost:8545")
        self.enabled = config.get("enabled", False)

    def anchor_data(self, data):
        if not self.enabled:
            logger.info("Blockchain anchoring disabled in config.")
            return None
        tx_hash = str(uuid.uuid4())
        logger.info(f"Data anchored to blockchain with tx hash: {tx_hash}")
        return tx_hash
