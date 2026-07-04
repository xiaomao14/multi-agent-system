import os
from dotenv import load_dotenv

load_dotenv()

from utils.logger import setup_logger
logger = setup_logger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL").strip()
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

logger.info(f"Model: {OPENAI_MODEL}")
logger.info(f"Base URL: {OPENAI_BASE_URL}")
