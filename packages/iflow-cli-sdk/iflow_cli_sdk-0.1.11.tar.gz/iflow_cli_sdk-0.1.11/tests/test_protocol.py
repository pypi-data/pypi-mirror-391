"""Protocol compliance tests for iFlow SDK."""

import asyncio
import pytest
from typing import Set, Dict, Any
from src.iflow_sdk import (
    IFlowClient,
    AssistantMessage,
    ToolCallMessage,
    PlanMessage,
    UserMessage,
    TaskFinishMessage,
    ToolCallStatus,
)


@pytest.mark.asyncio
async def test_message_types():
    """Test that all protocol message types are properly handled."""
    message_types_seen: Set[str] = set()

    async with IFlowClient() as client:
        await client.send_message("Hello, please create a simple plan")

        timeout = 5
        start_time = asyncio.get_event_loop().time()

        async for message in client.receive_messages():
            if asyncio.get_event_loop().time() - start_time > timeout:
                break

            message_types_seen.add(type(message).__name__)

            if isinstance(message, TaskFinishMessage):
                break

        # Should see at least assistant messages
        assert "AssistantMessage" in message_types_seen
        assert "TaskFinishMessage" in message_types_seen


@pytest.mark.asyncio
async def test_agent_id_support():
    """Test that agent_id is properly supported in messages."""
    async with IFlowClient() as client:
        await client.send_message("Test message")

        timeout = 3
        start_time = asyncio.get_event_loop().time()

        async for message in client.receive_messages():
            if asyncio.get_event_loop().time() - start_time > timeout:
                break

            # Check that agent_id attribute exists on relevant messages
            if isinstance(message, (AssistantMessage, ToolCallMessage)):
                assert hasattr(message, "agent_id")
                # agent_id can be None for main agent
                assert message.agent_id is None or isinstance(message.agent_id, str)

            if isinstance(message, TaskFinishMessage):
                break


@pytest.mark.asyncio
async def test_tool_call_status():
    """Test tool call status values match protocol."""
    valid_statuses = {
        ToolCallStatus.PENDING,
        ToolCallStatus.IN_PROGRESS,
        ToolCallStatus.COMPLETED,
        ToolCallStatus.FAILED,
    }

    async with IFlowClient() as client:
        await client.send_message("List files")

        timeout = 5
        start_time = asyncio.get_event_loop().time()

        async for message in client.receive_messages():
            if asyncio.get_event_loop().time() - start_time > timeout:
                break

            if isinstance(message, ToolCallMessage):
                assert message.status in valid_statuses
                assert message.status.value in ["pending", "in_progress", "completed", "failed"]

            if isinstance(message, TaskFinishMessage):
                break


@pytest.mark.asyncio
async def test_message_serialization():
    """Test that messages can be serialized to dict/JSON."""
    async with IFlowClient() as client:
        await client.send_message("Hello")

        timeout = 3
        start_time = asyncio.get_event_loop().time()

        async for message in client.receive_messages():
            if asyncio.get_event_loop().time() - start_time > timeout:
                break

            # Check that to_dict method exists and works
            if hasattr(message, "to_dict"):
                message_dict = message.to_dict()
                assert isinstance(message_dict, dict)
                assert "type" in message_dict

            if isinstance(message, TaskFinishMessage):
                break


@pytest.mark.asyncio
async def test_plan_message():
    """Test PlanMessage structure."""
    from src.iflow_sdk import PlanEntry

    # Create a plan message manually
    entries = [
        PlanEntry(content="Step 1", priority="high", status="completed"),
        PlanEntry(content="Step 2", priority="medium", status="in_progress"),
        PlanEntry(content="Step 3", priority="low", status="pending"),
    ]

    plan_msg = PlanMessage(entries)

    # Test structure
    assert len(plan_msg.entries) == 3
    assert plan_msg.entries[0].priority == "high"
    assert plan_msg.entries[1].status == "in_progress"
    assert plan_msg.entries[2].content == "Step 3"

    # Test serialization
    plan_dict = plan_msg.to_dict()
    assert plan_dict["type"] == "plan"
    assert len(plan_dict["entries"]) == 3
    assert plan_dict["entries"][0]["priority"] == "high"


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_message_types())
    asyncio.run(test_agent_id_support())
    asyncio.run(test_tool_call_status())
    asyncio.run(test_message_serialization())
    asyncio.run(test_plan_message())
    print("✅ All protocol tests passed!")
