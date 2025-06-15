import unittest
import os
import json
from cache import (
    load_cache,
    save_cache,
    prompt_hash,
    get_cached_response,
    store_response,
    CACHE_FILE
)

class TestCacheUtils(unittest.TestCase):

    def setUp(self):
        # Ensure cache file is clean before each test
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()

    def tearDown(self):
        # Clean up after tests
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()

    def test_prompt_hash_consistency(self):
        prompt = "hello world"
        h1 = prompt_hash(prompt)
        h2 = prompt_hash(prompt)
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, str)
        self.assertEqual(len(h1), 64)  # SHA-256 produces 64-char hex string

    def test_store_and_get_cached_response(self):
        prompt = "What is the capital of France?"
        response = "Paris"
        store_response(prompt, response)
        cached = get_cached_response(prompt)
        self.assertEqual(cached, response)

    def test_load_cache_empty(self):
        cache = load_cache()
        self.assertIsInstance(cache, dict)
        self.assertEqual(len(cache), 0)

    def test_save_and_load_cache(self):
        fake_cache = {"abc": "def"}
        save_cache(fake_cache)
        loaded = load_cache()
        self.assertEqual(loaded, fake_cache)

if __name__ == "__main__":
    unittest.main()
