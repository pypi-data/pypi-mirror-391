import logging
from core.config import LOG_FILE

logger = logging.getLogger('omga')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Only log to file, not console to avoid clutter
logger.addHandler(file_handler)