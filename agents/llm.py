"""
GANGU shared LLM client.

Provides a drop-in `Client()` that returns a configured `google.genai.Client`.
Uses a pool of Gemini API keys and randomly selects one per client instantiation
to distribute the load across multiple keys and avoid rate limits.
"""

import os
import random
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

# Load .env from project root, then from cwd.
_GANGU_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=_GANGU_ROOT / ".env")
load_dotenv()

DEFAULT_MODEL = "gemini-3.6-flash"

# The pool of Gemini API keys (loaded from .env)
# Provide multiple keys separated by commas in your .env file like:
# GEMINI_API_KEYS="key1,key2,key3"
raw_keys = os.environ.get("GEMINI_API_KEYS", os.environ.get("GEMINI_API_KEY", ""))
GEMINI_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

# Fallback if no keys provided
if not GEMINI_KEYS:
    GEMINI_KEYS = ["DUMMY_KEY_PLEASE_SET_IN_ENV"]

def get_model_name() -> str:
    """Resolve the model id from env, falling back to gemini-3.6-flash."""
    return os.environ.get("LLM_MODEL", DEFAULT_MODEL)

def Client(*args: Any, **kwargs: Any) -> genai.Client:
    """
    Returns a configured google.genai.Client instance.
    Randomly selects a key from the pool to distribute requests.
    """
    # Pick a random key from the pool
    api_key = random.choice(GEMINI_KEYS)
    
    # Initialize the real Gemini client with this key
    client = genai.Client(api_key=api_key)
    
    return client
