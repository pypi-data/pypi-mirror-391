#!/usr/bin/env python3
"""Quick start example for iFlow SDK.

This example demonstrates the simplest way to use the iFlow SDK
for sending queries and receiving responses.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.iflow_sdk import query, query_sync, query_stream


async def main():
    """Run quick start examples."""

    # Example 1: Simple query with async/await
    print("Example 1: Simple async query")
    print("-" * 40)
    response = await query("What is 2 + 2?")
    print(f"Response: {response}")
    print()

    # Example 2: Query with files
    print("Example 2: Query with files")
    print("-" * 40)
    # Uncomment and update path to test with actual files
    # response = await query(
    #     "Explain this code",
    #     files=["path/to/your/file.py"]
    # )
    # print(f"Response: {response}")
    print("(Skipped - add file paths to test)")
    print()

    # Example 3: Streaming response
    print("Example 3: Streaming response")
    print("-" * 40)
    print("Assistant: ", end="", flush=True)
    async for chunk in query_stream("Tell me a short joke"):
        print(chunk, end="", flush=True)
    print("\n")

    # Example 4: Query with sandbox
    print("Example 4: Sandbox query")
    print("-" * 40)
    from src.iflow_sdk import IFlowOptions

    # Create options for sandbox
    sandbox_options = IFlowOptions().for_sandbox()

    # Uncomment to test with sandbox (requires sandbox access)
    # response = await query(
    #     "Hello from sandbox!",
    #     options=sandbox_options
    # )
    # print(f"Response: {response}")
    print("(Skipped - requires sandbox access)")
    print()


def sync_example():
    """Example using synchronous wrapper."""
    print("Example 5: Synchronous query")
    print("-" * 40)
    response = query_sync("What is the capital of France?")
    print(f"Response: {response}")
    print()


if __name__ == "__main__":
    # Run async examples
    asyncio.run(main())

    # Run sync example
    sync_example()

    print("✅ Quick start examples completed!")
