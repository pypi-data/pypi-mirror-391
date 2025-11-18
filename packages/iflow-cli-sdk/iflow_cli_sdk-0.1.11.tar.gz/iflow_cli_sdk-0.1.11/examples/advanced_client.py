#!/usr/bin/env python3
"""Advanced example using IFlowClient directly.

This example demonstrates full control over the conversation flow
with bidirectional communication, tool call handling, and interrupts.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pathlib import Path
from typing import List, Optional
from src.iflow_sdk import (
    IFlowClient,
    IFlowOptions,
    AssistantMessage,
    ToolCallMessage,
    TaskFinishMessage,
    ErrorMessage,
    ApprovalMode,
    ToolCallStatus,
    ToolCallConfirmationOutcome,
)


async def basic_conversation():
    """Basic conversation with IFlowClient."""
    print("=" * 50)
    print("Basic Conversation Example")
    print("=" * 50)

    async with IFlowClient() as client:
        # Send a message
        await client.send_message("What is Python and why is it popular?")

        # Receive and process response
        response_text = []
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                if message.chunk.text:
                    response_text.append(message.chunk.text)
                    print(message.chunk.text, end="", flush=True)
            elif isinstance(message, TaskFinishMessage):
                print("\n✅ Task completed")
                break
            elif isinstance(message, ErrorMessage):
                print(f"\n❌ Error: {message.message}")
                break

    print("\n")


async def conversation_with_files():
    """Conversation including file context."""
    print("=" * 50)
    print("Conversation with Files Example")
    print("=" * 50)

    # Create a sample file for demonstration
    sample_file = Path("sample_code.py")
    sample_file.write_text(
        """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
"""
    )

    try:
        async with IFlowClient() as client:
            # Send message with file
            await client.send_message(
                "Can you optimize this Fibonacci implementation?", files=[sample_file]
            )

            # Receive response
            async for message in client.receive_messages():
                if isinstance(message, AssistantMessage):
                    if message.chunk.text:
                        print(message.chunk.text, end="", flush=True)
                elif isinstance(message, TaskFinishMessage):
                    print("\n✅ Analysis completed")
                    break
    finally:
        # Clean up
        sample_file.unlink(missing_ok=True)

    print("\n")


async def manual_tool_confirmation():
    """Example with manual tool call confirmation."""
    print("=" * 50)
    print("Manual Tool Confirmation Example")
    print("=" * 50)

    # Configure for manual permission mode
    options = IFlowOptions(approval_mode=ApprovalMode.DEFAULT)

    async with IFlowClient(options) as client:
        await client.send_message("Create a file called hello.txt with 'Hello World' content")

        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                if message.chunk.text:
                    print(f"Assistant: {message.chunk.text}", end="", flush=True)

            elif isinstance(message, ToolCallMessage):
                print(f"\n🔧 Tool Call: {message.label}")
                print(f"   Status: {message.status.value}")

                # In manual mode, we need to approve/reject tool calls
                if message.confirmation:
                    # Simulate user approval (in real app, ask user)
                    print("   ⚠️  Tool requires confirmation")
                    print("   Auto-approving for demo...")
                    await client.approve_tool_call(message.id, ToolCallConfirmationOutcome.ALLOW)

            elif isinstance(message, TaskFinishMessage):
                print("\n✅ Task completed")
                break

    print("\n")


async def interrupt_example():
    """Example showing interrupt capability."""
    print("=" * 50)
    print("Interrupt Example")
    print("=" * 50)

    async with IFlowClient() as client:
        # Send a request that would generate a long response
        await client.send_message("Write a detailed essay about machine learning")

        # Receive some response then interrupt
        char_count = 0
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                if message.chunk.text:
                    print(message.chunk.text, end="", flush=True)
                    char_count += len(message.chunk.text)

                    # Interrupt after 200 characters
                    if char_count > 200:
                        print("\n\n⚡ Interrupting generation...")
                        await client.interrupt()
                        break

            elif isinstance(message, TaskFinishMessage):
                print("\n✅ Completed")
                break

    print("\n")


async def multi_turn_conversation():
    """Multi-turn interactive conversation."""
    print("=" * 50)
    print("Multi-turn Conversation Example")
    print("=" * 50)

    async with IFlowClient() as client:
        # Turn 1
        print("User: What is recursion?")
        await client.send_message("What is recursion?")

        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                if message.chunk.text:
                    print(message.chunk.text, end="", flush=True)
            elif isinstance(message, TaskFinishMessage):
                break

        print("\n\nUser: Can you give a Python example?")
        # Turn 2 - Follow-up in same conversation
        await client.send_message("Can you give a Python example?")

        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                if message.chunk.text:
                    print(message.chunk.text, end="", flush=True)
            elif isinstance(message, TaskFinishMessage):
                print("\n✅ Conversation completed")
                break

    print("\n")


async def sandbox_mode():
    """Example using sandbox mode."""
    print("=" * 50)
    print("Sandbox Mode Example")
    print("=" * 50)

    # Configure for sandbox
    options = IFlowOptions().for_sandbox()

    try:
        async with IFlowClient(options) as client:
            await client.send_message("Hello from sandbox mode!")

            async for message in client.receive_messages():
                if isinstance(message, AssistantMessage):
                    if message.chunk.text:
                        print(message.chunk.text, end="", flush=True)
                elif isinstance(message, TaskFinishMessage):
                    print("\n✅ Sandbox test completed")
                    break
                elif isinstance(message, ErrorMessage):
                    print(f"\n⚠️  Sandbox not available: {message.message}")
                    break
    except Exception as e:
        print(f"⚠️  Sandbox connection failed: {e}")
        print("Make sure you have sandbox access configured")

    print("\n")


async def main():
    """Run all examples."""
    # Basic examples
    await basic_conversation()
    await conversation_with_files()

    # Advanced examples
    await manual_tool_confirmation()
    await interrupt_example()
    await multi_turn_conversation()

    # Sandbox (may fail if not configured)
    await sandbox_mode()

    print("=" * 50)
    print("🎉 All examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
