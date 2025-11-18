import os

# Configuration
# Server starts without requiring env vars (allows server to start)
# When accessed from Claude Desktop, env vars are provided per-user from Claude config
# This allows multi-user support - each Claude user has their own API key

MY_API_BASE_URL = os.getenv("MY_API_BASE_URL", "https://qa.servicenex.io/api")
MY_API_KEY = os.getenv("MY_API_KEY", "57b8a33d55c80aa5e8c3ad365534aabdded44af77b52d343b4d2a176d2febcef")  # Default for local testing