#!/usr/bin/env python3
"""Test simple query example from README"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.iflow_sdk import query

async def main():
    response = await query("What is the capital of France?")
    assert response, "Should receive a response"
    assert len(response) > 0, "Response should not be empty"
    print(f"Response: {response[:100]}...")  # Print first 100 chars
    print("✅ Simple query test passed")

if __name__ == "__main__":
    asyncio.run(main())