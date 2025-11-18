#!/usr/bin/env python3
"""Test automatic mode example from README"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.iflow_sdk import IFlowClient

async def main():
    # iFlow will be automatically started if not running
    async with IFlowClient() as client:
        await client.send_message("Hello, iFlow!")
        # Wait for a response to verify connection
        received = False
        async for message in client.receive_messages():
            received = True
            break  # Just test connection
        
        assert received, "Should receive at least one message"
        print("✅ Automatic mode test passed")

if __name__ == "__main__":
    asyncio.run(main())