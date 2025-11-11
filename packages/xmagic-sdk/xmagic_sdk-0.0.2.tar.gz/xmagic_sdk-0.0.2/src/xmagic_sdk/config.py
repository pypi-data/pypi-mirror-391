from pathlib import Path
import tempfile
import os
from dotenv import load_dotenv, find_dotenv
import httpx

# IMPORTANT: dont import logger here (circular import)

env_path = find_dotenv()
load_dotenv(env_path)


DEFAULT_HTTPX_TIMEOUT = httpx.Timeout(
    timeout=60.0, connect=60.0, read=60.0, write=60.0, pool=60.0
)


class Config:
    XMAGIC_BASE_PATH = os.environ.get(
        "XMAGIC_BASE_PATH", "https://api.xchat.stochastic.ai/xmagic-backend"
    )
    XCHAT_BASE_PATH = os.environ.get(
        "XCHAT_BASE_PATH", "https://api.xchat.stochastic.ai/xchat-backend"
    )
    XCHAT_AUTH_BASE_PATH = os.environ.get(
        "XCHAT_BASE_PATH", "https://api.xchat.stochastic.ai/auth"
    )
    XCHAT_API_KEY = os.environ.get("XCHAT_API_KEY")
    XCHAT_CONFIG_PATH: Path = Path.home() / ".xmagic" / "config"
    MCP_RUN_LOCALLY = os.environ.get("MCP_RUN_LOCALLY", "false").lower() in (
        "true",
        "1",
        "yes",
    )
    RUN_LOCALLY_FROM_CLI = os.environ.get("RUN_LOCALLY_FROM_CLI", "false").lower() in (
        "true",
        "1",
        "yes",
    )
    LOG_LEVEL = os.environ.get("XCHAT_LOG_LEVEL", "INFO").upper()
