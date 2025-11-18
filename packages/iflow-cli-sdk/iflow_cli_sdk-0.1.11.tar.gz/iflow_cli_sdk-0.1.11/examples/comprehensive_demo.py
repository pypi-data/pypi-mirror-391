#!/usr/bin/env python3
"""Comprehensive demo of iFlow SDK features."""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import logging
from typing import Dict, List
from src.iflow_sdk import (
    IFlowClient,
    IFlowOptions,
    RawDataClient,
    query,
    AssistantMessage,
    ToolCallMessage,
    PlanMessage,
    TaskFinishMessage,
    ApprovalMode,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def basic_conversation():
    """Demonstrate basic conversation with iFlow."""
    print("\n" + "=" * 60)
    print("1. BASIC CONVERSATION")
    print("=" * 60)

    async with IFlowClient() as client:
        # Send a simple message
        await client.send_message("What is the capital of France?")

        print("\nResponse from iFlow:")
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                if message.chunk.text:
                    print(message.chunk.text, end="", flush=True)
            elif isinstance(message, TaskFinishMessage):
                print("\n\n✅ Conversation completed")
                break


async def tool_interaction():
    """Demonstrate tool call handling."""
    print("\n" + "=" * 60)
    print("2. TOOL INTERACTION")
    print("=" * 60)

    # Use manual permission mode for demonstration
    options = IFlowOptions(approval_mode=ApprovalMode.AUTO_EDIT)

    async with IFlowClient(options) as client:
        await client.send_message("Create a file called demo.txt with 'Hello World' content")

        tool_calls: List[Dict] = []

        async for message in client.receive_messages():
            if isinstance(message, ToolCallMessage):
                print(f"\n🔧 Tool Call: {message.label}")
                print(f"   Status: {message.status.value}")
                print(f"   ID: {message.id}")

                tool_calls.append({"label": message.label, "status": message.status.value})

            elif isinstance(message, AssistantMessage):
                if message.chunk.text:
                    print(f"\n💬 Assistant: {message.chunk.text}")

            elif isinstance(message, TaskFinishMessage):
                print(f"\n✅ Task completed with {len(tool_calls)} tool calls")
                break


async def agent_tracking():
    """Demonstrate SubAgent tracking."""
    print("\n" + "=" * 60)
    print("3. SUBAGENT TRACKING")
    print("=" * 60)

    async with IFlowClient() as client:
        await client.send_message("Analyze this project structure and suggest improvements")

        agents_seen = set()
        timeout = 10
        start_time = asyncio.get_event_loop().time()

        async for message in client.receive_messages():
            if asyncio.get_event_loop().time() - start_time > timeout:
                print("\n⏱️ Timeout reached")
                break

            # Track agent IDs
            if hasattr(message, "agent_id") and message.agent_id:
                agents_seen.add(message.agent_id)
                print(f"\n[Agent: {message.agent_id[:8]}...]", end=" ")
            else:
                print("\n[Main Agent]", end=" ")

            if isinstance(message, AssistantMessage):
                if message.chunk.text:
                    print(message.chunk.text[:50] + "...", end="")

            elif isinstance(message, ToolCallMessage):
                print(f"🔧 {message.label}", end="")

            elif isinstance(message, TaskFinishMessage):
                print(f"\n\n✅ Completed with {len(agents_seen)} SubAgent(s)")
                break


async def plan_execution():
    """Demonstrate plan message handling."""
    print("\n" + "=" * 60)
    print("4. PLAN EXECUTION")
    print("=" * 60)

    async with IFlowClient() as client:
        await client.send_message(
            "Create a plan to build a simple web application with "
            "authentication, database, and API endpoints"
        )

        plans_received = []

        async for message in client.receive_messages():
            if isinstance(message, PlanMessage):
                print("\n📋 Plan received with entries:")
                for i, entry in enumerate(message.entries, 1):
                    status_icon = {"completed": "✅", "in_progress": "🔄", "pending": "⏳"}.get(
                        entry.status, "❓"
                    )

                    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                        entry.priority, "⚪"
                    )

                    print(f"   {i}. {status_icon} {priority_icon} {entry.content}")

                plans_received.append(message)

            elif isinstance(message, AssistantMessage):
                if message.chunk.text:
                    print(message.chunk.text, end="", flush=True)

            elif isinstance(message, TaskFinishMessage):
                print(f"\n\n✅ Planning completed ({len(plans_received)} plan(s))")
                break


async def raw_data_access():
    """Demonstrate raw data access for debugging."""
    print("\n" + "=" * 60)
    print("5. RAW DATA ACCESS (Advanced)")
    print("=" * 60)

    async with RawDataClient() as client:
        await client.send_message("What is 2 + 2?")

        print("\n📡 Raw protocol messages:")

        raw_count = 0
        timeout = 3
        start_time = asyncio.get_event_loop().time()

        async for raw_msg in client.receive_raw_messages():
            if asyncio.get_event_loop().time() - start_time > timeout:
                break

            raw_count += 1
            print(f"\nMessage #{raw_count}:")
            print(f"  Type: {raw_msg.message_type}")

            if raw_msg.json_data:
                if "method" in raw_msg.json_data:
                    print(f"  Method: {raw_msg.json_data['method']}")
                if "update" in raw_msg.json_data:
                    update = raw_msg.json_data["update"]
                    if "sessionUpdate" in update:
                        print(f"  Update: {update['sessionUpdate']}")

        # Get protocol statistics
        stats = client.get_protocol_stats()
        print(f"\n📊 Protocol Statistics:")
        print(f"  Total messages: {stats['total_messages']}")
        print(f"  JSON messages: {stats['json_messages']}")
        print(f"  Control messages: {stats['control_messages']}")


def simple_query():
    """Demonstrate simple synchronous query."""
    print("\n" + "=" * 60)
    print("6. SIMPLE QUERY (Synchronous)")
    print("=" * 60)

    # Simple one-liner query
    response = query("What is the meaning of life?")
    print(f"\nResponse: {response}")


async def main():
    """Run all demonstrations."""
    print(
        """
╔════════════════════════════════════════════════════════════╗
║            iFlow SDK - Comprehensive Demo                  ║
║                                                            ║
║  This demo showcases all major features of the SDK        ║
╚════════════════════════════════════════════════════════════╝
    """
    )

    try:
        # Run demonstrations
        await basic_conversation()
        await tool_interaction()
        await agent_tracking()
        await plan_execution()
        await raw_data_access()
        simple_query()

        print("\n" + "=" * 60)
        print("✨ All demonstrations completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
