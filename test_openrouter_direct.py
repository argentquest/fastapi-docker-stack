#!/usr/bin/env python3
"""
Direct test of OpenRouter to verify configuration
"""

import asyncio
import openai
from app.core.config import settings

async def test_direct():
    """Test OpenRouter with direct configuration"""
    print("Testing OpenRouter directly...")
    print(f"API Key: {settings.OPENROUTER_API_KEY[:10]}...{settings.OPENROUTER_API_KEY[-5:]}")
    print(f"Base URL: {settings.OPENROUTER_BASE_URL}")
    print(f"Model: {settings.OPENROUTER_DEFAULT_MODEL}")
    
    # Create client exactly as the service does
    client = openai.AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        default_headers={
            "Referer": settings.OPENROUTER_SITE_URL,
            "X-Title": settings.OPENROUTER_APP_NAME
        }
    )
    
    try:
        response = await client.chat.completions.create(
            model=settings.OPENROUTER_DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Say hello in exactly 3 words"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        print(f"SUCCESS: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct())
    if success:
        print("\n✓ OpenRouter configuration is correct!")
        print("The issue is with service initialization at server startup.")
    else:
        print("\n✗ OpenRouter configuration has issues.")