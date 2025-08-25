#!/usr/bin/env python
"""Test script to verify environment variables are loading correctly."""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Check critical environment variables
env_vars = [
    "OPENROUTER_API_KEY",
    "DATABASE_URL", 
    "REDIS_URL",
    "MINIO_ENDPOINT"
]

print("=" * 50)
print("Environment Variable Check")
print("=" * 50)

for var in env_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive data
        if "KEY" in var or "PASSWORD" in var:
            display_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
        else:
            display_value = value
        print(f"[OK] {var}: {display_value}")
    else:
        print(f"[MISSING] {var}: NOT SET")

print("=" * 50)

# Try to import and test the settings
try:
    from app.core.config import settings
    print("\n[OK] Settings loaded successfully!")
    print(f"   API Key present: {bool(settings.OPENROUTER_API_KEY)}")
    print(f"   API Key length: {len(settings.OPENROUTER_API_KEY) if settings.OPENROUTER_API_KEY else 0}")
except Exception as e:
    print(f"\n[ERROR] Error loading settings: {e}")