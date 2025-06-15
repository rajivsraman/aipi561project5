# cache.py
import hashlib
import json
from pathlib import Path

CACHE_FILE = Path("cache_store.json")

# Load existing cache
def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

# Save cache
def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

# Generate hash key from prompt
def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()

# Check cache
def get_cached_response(prompt: str):
    cache = load_cache()
    key = prompt_hash(prompt)
    return cache.get(key)

# Store to cache
def store_response(prompt: str, response: str):
    cache = load_cache()
    key = prompt_hash(prompt)
    cache[key] = response
    save_cache(cache)
