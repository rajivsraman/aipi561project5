# API Documentation for Bedrock Titan LLM Wrapper

This FastAPI application exposes two endpoints that wrap Amazon Bedrock's Titan model. Use it to send prompts, receive generated responses, and monitor performance.

---

## Base URL

```
http://<YOUR_EC2_PUBLIC_IP>:8000
```

---

##  POST `/generate`

### Description:
Sends a text prompt to the Titan model hosted via Amazon Bedrock and returns the model's response.

### Endpoint:
```
POST /generate
```

### Request (form-data):
| Field   | Type   | Required | Description              |
|---------|--------|----------|--------------------------|
| prompt | string | Yes   | Input text prompt       |

### Example with `curl`:
```bash
curl -X POST http://<YOUR_EC2_PUBLIC_IP>:8000/generate \
     -F "prompt=Explain quantum computing to a child"
```

### Example with Python `requests`:
```python
import requests
res = requests.post("http://<YOUR_EC2_PUBLIC_IP>:8000/generate", data={"prompt": "Write a poem about AI."})
print(res.json())
```

### Response:
```json
{
  "cached": false,
  "response": "Quantum computing is like magic calculators...",
  "latency_sec": 1.23
}
```

---

## GET `/metrics`

### Description:
Returns API usage statistics and performance metrics.

### Endpoint:
```
GET /metrics
```

### Example:
```bash
curl http://<YOUR_EC2_PUBLIC_IP>:8000/metrics
```

### Response:
```json
{
  "total_requests": 10,
  "cache_hits": 4,
  "avg_latency_sec": 1.12,
  "model": "amazon.titan-tg1-large"
}
```

---

## Notes
- The API uses in-memory caching to speed up repeated requests.
- Model responses are streamed internally but returned as full text.
- You must configure your AWS credentials and Bedrock permissions for this to work.

---
