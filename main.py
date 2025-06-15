import os
import json
import time
import hashlib
import logging
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import boto3

# ------------------------------------------------------------------------------
# 🔧 CONFIGURATION
# ------------------------------------------------------------------------------
BEDROCK_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-tg1-large")
CACHE_FILE = "cache.json"
CACHE_TTL_SECONDS = 3600  # 1 hour TTL

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("titan-api")

bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# 📂 CACHING FUNCTIONS WITH TTL & HASHING
# ------------------------------------------------------------------------------

def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_cached_response(prompt: str):
    cache = load_cache()
    key = hash_prompt(prompt)
    entry = cache.get(key)
    if entry:
        timestamp = entry["timestamp"]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return entry["response"]
        else:
            logger.info("Cache expired for prompt.")
    return None

def store_response(prompt: str, response: str):
    cache = load_cache()
    key = hash_prompt(prompt)
    cache[key] = {
        "response": response,
        "timestamp": time.time()
    }
    save_cache(cache)

def clear_cache():
    save_cache({})
    logger.info("Cache cleared.")

# ------------------------------------------------------------------------------
# 🧠 BEDROCK API CALL
# ------------------------------------------------------------------------------

def call_titan_model(prompt: str):
    body = {"inputText": prompt}
    start = time.time()
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )
    latency = time.time() - start
    response_body = response["body"].read().decode("utf-8")
    parsed = json.loads(response_body)
    output = parsed.get("results", [{}])[0].get("outputText", "No output returned.")
    return output, latency

# ------------------------------------------------------------------------------
# 📍 API ROUTES
# ------------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Titan Bedrock API with caching + metrics + TTL"}

@app.post("/chat")
def chat(prompt: str = Form(...)):
    logger.info(f"Received prompt: {prompt}")
    cached = get_cached_response(prompt)
    if cached:
        return {
            "response": cached,
            "latency": 0.0,
            "source": "cache"
        }

    try:
        response_text, latency = call_titan_model(prompt)
    except Exception as e:
        logger.exception("Model call failed")
        raise HTTPException(status_code=500, detail=f"Model call failed: {str(e)}")

    store_response(prompt, response_text)

    return {
        "response": response_text,
        "latency": round(latency, 3),
        "source": "bedrock"
    }

@app.post("/clear_cache")
def clear_cache_endpoint():
    clear_cache()
    return {"message": "Cache cleared successfully."}

@app.get("/metrics")
def get_metrics():
    cache = load_cache()
    valid_entries = [v for v in cache.values() if time.time() - v["timestamp"] < CACHE_TTL_SECONDS]
    return {
        "total_cache_entries": len(cache),
        "valid_cache_entries": len(valid_entries),
        "ttl_seconds": CACHE_TTL_SECONDS
    }
