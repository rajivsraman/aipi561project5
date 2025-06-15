import unittest
from fastapi.testclient import TestClient
from main import app, clear_cache, save_cache, load_cache, hash_prompt

client = TestClient(app)

class TestMainAPI(unittest.TestCase):

    def setUp(self):
        clear_cache()

    def test_root_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_cache_hashing_consistency(self):
        prompt = "Test prompt"
        h1 = hash_prompt(prompt)
        h2 = hash_prompt(prompt)
        self.assertEqual(h1, h2)

    def test_cache_storage_and_retrieval(self):
        prompt = "Hello world"
        response = "Mock response"
        from main import store_response, get_cached_response
        store_response(prompt, response)
        cached = get_cached_response(prompt)
        self.assertEqual(cached, response)

    def test_clear_cache_endpoint(self):
        prompt = "A prompt"
        from main import store_response
        store_response(prompt, "Some response")
        r1 = client.post("/clear_cache")
        self.assertEqual(r1.status_code, 200)
        cache = load_cache()
        self.assertEqual(cache, {})

    def test_chat_endpoint_cache_and_source(self):
        # Manually inject cache
        prompt = "What is 2 + 2?"
        from main import store_response
        store_response(prompt, "Four")
        
        response = client.post("/chat", data={"prompt": prompt})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["response"], "Four")
        self.assertEqual(data["source"], "cache")
        self.assertEqual(data["latency"], 0.0)

    def test_metrics_endpoint(self):
        response = client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_cache_entries", data)
        self.assertIn("valid_cache_entries", data)
        self.assertIn("ttl_seconds", data)

if __name__ == "__main__":
    unittest.main()
